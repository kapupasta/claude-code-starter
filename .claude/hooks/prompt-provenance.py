#!/usr/bin/env python3
"""This file owns UserPromptSubmit context injection for claim provenance.

Two independent checks, both fail-open:

1. HANDOFF PROVENANCE - a long structured prompt is often a handoff a previous
   session wrote and the user pasted back. Its factual claims are that agent's
   inferences wearing the user's authority. Verified by provenance (the text
   really appears in an earlier ASSISTANT turn of a past transcript), not by
   shape, so it has no false positives.

2. REPORT-SHAPED ASK - audits, reviews, reports and post-mortems are where
   overstated blast-radius claims land. Injects the VERIFIED / INFERRED rule.

The transcript corpus searched is the directory of the payload's own
transcript_path (this project's ~/.claude/projects/<slug>/), so no config is
needed. Exits 0 always; any failure prints nothing rather than blocking the prompt.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_io import read_event  # noqa: E402

# Check A is a full-corpus grep (seconds on a large history), so SHAPE decides
# whether to spend the CPU and PROVENANCE decides whether to warn. Shape-gating
# alone would give false positives; provenance alone would cost a grep on every
# pasted console dump.
MIN_PROMPT_CHARS = 800
MIN_PROMPT_LINES = 8
NEEDLE_MIN, NEEDLE_MAX = 40, 300
GREP_TIMEOUT_SECONDS = 20
MAX_FILES_TO_CONFIRM = 5

# Markdown scaffolding or a brief-writing phrase - what a handoff has and a
# pasted console dump, client email or stack trace does not.
STRUCTURE = re.compile(
    r"(^#{1,4} |^\d+\. |^[-*] |^\s*READ FIRST|^\s*Read first"
    r"|\bdo not (start|re-?derive|touch|edit)\b|\balready verified\b"
    r"|\bread first\b|\bin scope\b|\bnot in scope\b|\bout of scope\b"
    r"|\bdon'?t re-?derive\b|\bstart with\b.{0,40}\b(spec|plan|brainstorm)\b)",
    re.I | re.M)

REPORT_ASK = re.compile(
    r"\b(audit|review|report|insights?|sitrep|blast[- ]radius|post-?mortem"
    r"|what (would |could )?break|impact|assess|analys[ei]s|analyz)", re.I)

URLISH = re.compile(r"https?://|^\s*[-*#>|`]|^\s*/|\.(md|py|ts|js|json|php)\b")

HANDOFF_NOTE = (
    "PROMPT PROVENANCE: this prompt's text was found verbatim in an earlier "
    "ASSISTANT turn ({where}). It is a handoff a previous session wrote, which "
    "the user pasted back - not the user's own claim. Its factual assertions "
    "(paths, versions, counts, line numbers, \"already verified\" lists) are that "
    "session's inferences carrying the user's authority. Spot-check the "
    "load-bearing ones against the current tree before building on them, and say "
    "so if one has gone stale.")

REPORT_NOTE = (
    "REPORT-SHAPED ASK: tag every claim in the output VERIFIED (you ran a "
    "command, URL or query - name it) or INFERRED (you reasoned about it). Be "
    "conservative about blast radius and scope; an unnamed VERIFIED is an "
    "INFERRED.")


def pick_needle(prompt):
    """Return a distinctive prose line to search for, or None if none fits.

    :param prompt: the submitted prompt text.
    :return: the longest prose-like line within the needle length bounds, or None.
    """
    best = None
    for line in prompt.splitlines():
        line = line.strip()
        if not (NEEDLE_MIN <= len(line) <= NEEDLE_MAX):
            continue
        if URLISH.search(line) or len(line.split()) < 6:
            continue
        if best is None or len(line) > len(best):
            best = line
    return best


def transcripts(transcript_path, exclude_session):
    """Return every top-level transcript next to this session's, except its own.

    :param transcript_path: the live session's transcript path from the payload.
    :param exclude_session: the live session id (its file is skipped).
    :return: list of .jsonl paths; empty when the directory is unknown.
    """
    project_dir = os.path.dirname(transcript_path or "")
    if not project_dir:
        return []
    try:
        names = [n for n in os.listdir(project_dir) if n.endswith(".jsonl")]
    except OSError:
        return []
    return [os.path.join(project_dir, n) for n in names
            if not (exclude_session and n.startswith(exclude_session))]


def written_by_assistant(paths, needle):
    """Return a 'session, date' string if an assistant turn holds the needle.

    :param paths: transcript files to search.
    :param needle: exact text to look for.
    :return: a short location string, or None.
    """
    if not paths:
        return None
    try:
        found = subprocess.run(["grep", "-lF", "--", needle] + paths,
                               capture_output=True, timeout=GREP_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError):
        return None
    hits = [h for h in found.stdout.decode("utf-8", "replace").split("\n") if h]
    for path in hits[:MAX_FILES_TO_CONFIRM]:
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if needle not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") != "assistant":
                    continue
                stamp = (rec.get("timestamp") or "")[:10]
                name = os.path.basename(path)[:8]
                return "session %s%s" % (name, ", " + stamp if stamp else "")
    return None


def is_handoff_shaped(prompt):
    """True when a prompt is long and structured enough to be a pasted handoff.

    :param prompt: the submitted prompt text.
    :return: whether the provenance grep is worth running.
    """
    return (len(prompt) >= MIN_PROMPT_CHARS
            and prompt.count("\n") + 1 >= MIN_PROMPT_LINES
            and STRUCTURE.search(prompt) is not None)


def main():
    """Hook entry point: print additionalContext notes, or nothing.

    :return: None
    """
    payload = read_event()
    if payload is None:
        return
    prompt = payload.get("prompt") or ""
    if not prompt:
        return

    notes = []
    if REPORT_ASK.search(prompt):
        notes.append(REPORT_NOTE)

    if is_handoff_shaped(prompt):
        needle = pick_needle(prompt)
        if needle:
            where = written_by_assistant(
                transcripts(payload.get("transcript_path"), payload.get("session_id") or ""),
                needle)
            if where:
                notes.append(HANDOFF_NOTE.format(where=where))

    if not notes:
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n\n".join(notes),
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
