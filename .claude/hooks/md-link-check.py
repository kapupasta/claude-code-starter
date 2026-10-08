#!/usr/bin/env python3
"""This file owns the Stop hook that turns bare .md file paths in the final reply into clickable links.

Why: a file path printed as plain text in the terminal has to be copied by hand;
a `[name.md](file:///abs/path)` link opens with one click. A rule in memory alone
gets skipped in fresh sessions and subagent hand-offs, so this enforces it at
turn-end, deterministically.

Fires on the Stop event. Reads the final reply from the payload's
`last_assistant_message` (the transcript lags at Stop time, so reading it checks
the PREVIOUS reply), falling back to the transcript on older versions. Strips
code/links, and looks for PATH-like .md references (containing a `/`) that
are not already inside a markdown link. If any remain, it blocks once and tells
the model to convert them to `[name.md](file:///abs/path)`.

Design notes:
- Only PATHS (with a slash) are flagged. A bare `MEMORY.md` mention in prose is
  fine and is intentionally ignored -- the friction is pointing at a file location.
- Code spans are exempt EXCEPT when the span IS just a path: a lone path inside a
  fence, or a backticked path, is a file the user is meant to open. Shell output,
  diffs and code samples that merely contain .md paths stay quiet.
- stop_hook_active short-circuits to avoid loops: the model gets exactly one
  correction pass, then the turn is allowed through regardless.
- Any parsing error exits 0 silently -- this must never break a session.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_io import read_event  # noqa: E402

# Fenced code blocks, inline code, and full markdown links/images are stripped
# before scanning so legitimately-linked or code-quoted paths never match.
# Both code forms carve out one exception for paths the user is clearly being
# pointed at -- see _strip_fenced() and _strip_inline_code().
_FENCED = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`]*`")
_MD_LINK = re.compile(r"!?\[[^\]]*\]\([^)]*\)")

# Opening/closing markers a fenced block may use.
_FENCE_MARKERS = ("```", "~~~")

# A path-like token: contains at least one '/' and ends in .md (optional :line).
# Excludes whitespace and the bracket/paren chars that delimit markdown syntax.
_BARE_MD_PATH = re.compile(r"[~./A-Za-z0-9][^\s`)\]]*/[^\s`)\]]*\.md(?::\d+)?")


def last_assistant_text(transcript_path: str) -> str:
    """Return concatenated text blocks of the final assistant message, or ''."""
    with open(transcript_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        texts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        joined = "".join(texts).strip()
        if joined:
            return joined
    return ""


def current_reply_text(data: dict) -> str:
    """Return the reply that just ended, or '' if it cannot be found.

    Prefers the Stop payload's `last_assistant_message`: the docs warn the
    transcript "isn't guaranteed to include the final message at Stop time", and
    reading it made this hook check the previous reply. The transcript is only a
    fallback for Claude Code versions that predate the field.

    :param data: the decoded Stop hook payload.
    :return: the final assistant text, or ''.
    """
    message = data.get("last_assistant_message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return ""
    try:
        return last_assistant_text(transcript_path)
    except (OSError, ValueError):
        return ""


def _fence_body(block: str) -> str:
    """Return a fenced block's inner text, minus its markers and info string.

    Returns '' when the block is not a recognisable fence or has no body.
    """
    inner = block.strip()
    for marker in _FENCE_MARKERS:
        if (
            inner.startswith(marker)
            and inner.endswith(marker)
            and len(inner) >= 2 * len(marker)
        ):
            inner = inner[len(marker) : -len(marker)]
            break
    else:
        return ""
    # An info string (```text) can only exist when the fence spans >1 line.
    if "\n" in inner:
        inner = inner.split("\n", 1)[1]
    return inner.strip()


def _strip_fenced(text: str) -> str:
    """Drop fenced code blocks, but KEEP one whose whole body is a single
    path-like .md reference -- a lone path in a fence is a file the user is being
    pointed at, not incidental code. Multi-line fences (shell sessions, listings,
    diffs) stay exempt so .md paths that merely appear in output never match."""
    return _FENCED.sub(
        lambda m: (
            m.group(0)
            if _BARE_MD_PATH.fullmatch(_fence_body(m.group(0)))
            else ""
        ),
        text,
    )


def _strip_inline_code(text: str) -> str:
    """Drop inline-code spans, but KEEP any that contain a path-like .md reference,
    so a backticked path the user is meant to click still gets flagged. Fenced code
    blocks are stripped earlier and stay exempt, so inline shell snippets there are safe."""
    return _INLINE_CODE.sub(
        lambda m: m.group(0) if _BARE_MD_PATH.search(m.group(0)) else "",
        text,
    )


def find_bare_paths(text: str):
    """Bare .md paths remaining after code/link stripping, de-duped, in order."""
    stripped = _strip_fenced(text)
    stripped = _strip_inline_code(stripped)
    stripped = _MD_LINK.sub("", stripped)
    seen, out = set(), []
    for m in _BARE_MD_PATH.finditer(stripped):
        hit = m.group(0)
        if hit not in seen:
            seen.add(hit)
            out.append(hit)
    return out


def main() -> None:
    """Hook entry point: block once if the reply holds bare .md paths.

    :return: None (always exits 0).
    """
    data = read_event()
    if data is None:
        sys.exit(0)

    # One correction pass only -- never loop.
    if data.get("stop_hook_active"):
        sys.exit(0)

    text = current_reply_text(data)

    if not text:
        sys.exit(0)

    paths = find_bare_paths(text)
    if not paths:
        sys.exit(0)

    shown = ", ".join(paths[:5])
    reason = (
        "You referenced .md file path(s) as bare text: "
        f"{shown}. Every .md path you point "
        "the user to must be a clickable link: [name.md](file:///abs/path) (or a "
        "repo-relative markdown link). Rewrite those reference(s) as links, then finish."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
