#!/usr/bin/env python3
"""This file owns the memory-load backstop: warn, then block, project work done without loading memory.

PreToolUse hook on Edit | Write | Bash. Read is excluded on purpose: Reading
memory IS the loading.

A session counts as project work when a message the user typed names a project
from the roster (roster_file in starter-config.json, default PROJECTS.md at the
workspace root). It counts as "memory loaded" once the Read TOOL opened the
roster, any project_<name>.md, or any MEMORY-*.md bucket. Bash cat/head/sed do
not count: they are invisible to this check and to the Edit read-gate alike.

Ramp: the first WARN_LIMIT gated calls get a warning via additionalContext (shown
to Claude next to the tool result, no permission decision made); call
WARN_LIMIT + 1 is denied with the full explanation.

Fails open: missing config, missing roster, or an unreadable transcript all allow.

Python 3.9 compatible: no `X | None`, no match/case.
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_io import pretool_context, pretool_deny, read_event  # noqa: E402
from starter_config import load_config  # noqa: E402

WARN_LIMIT = 3
STATE_FILE = Path.home() / ".claude" / "state" / "memory-load-check.json"

# Roster bullets look like `- project-name — path — status`. Header/meta bullets
# (`- **Detail:** ...`) start with `**`, so the leading-letter requirement skips them.
ROSTER_LINE = re.compile(r"^-\s*([A-Za-z][\w.-]*(?:\s[A-Za-z][\w.-]*)*?)\s*[—-]")

# Basenames of files whose Read counts as loading memory (roster name added at runtime).
MEMORY_FILE_RE = r"MEMORY-[\w-]+\.md|project_[\w-]+\.md"

# `!` shell commands and slash-command echoes are injected into the transcript as
# user-role messages. Their *output* (e.g. `git status` listing project dirs) must
# NOT count as the user mentioning a project. Strip these blocks before scanning.
_INJECTED_BLOCK = re.compile(
    r"<(bash-input|bash-stdout|bash-stderr|local-command-stdout|local-command-stderr"
    r"|local-command-caveat|command-name|command-message|command-args)>.*?</\1>",
    re.DOTALL,
)


def load_project_names(roster_file: Optional[Path]) -> Set[str]:
    """Parse the roster bullets and return lowercased project names.

    :param roster_file: path to the roster markdown file, or None.
    :return: full names plus each name's first word; empty if the roster is missing.
    """
    if roster_file is None or not roster_file.exists():
        return set()
    try:
        content = roster_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    names = set()  # type: Set[str]
    for line in content.splitlines():
        m = ROSTER_LINE.match(line.strip())
        if m:
            name = m.group(1).strip().lower()
            names.add(name)
            # Also the first word alone ("site.example SEO" -> "site.example").
            first_word = name.split()[0] if name else ""
            if first_word:
                names.add(first_word)
    return names


def message_text(entry: dict) -> str:
    """Flatten a transcript entry's content into plain text.

    :param entry: one decoded JSONL transcript line.
    :return: the concatenated text parts.
    """
    content = entry.get("content") or entry.get("message", {}).get("content", "")
    if isinstance(content, list):
        content = " ".join((c.get("text", "") or "") for c in content if isinstance(c, dict))
    return str(content)


def transcript_mentions_project(transcript_path: str, project_names: Set[str]) -> bool:
    """Scan the user's typed messages in the transcript for any roster name.

    :param transcript_path: path to the session JSONL transcript.
    :param project_names: lowercased roster names.
    :return: True if a typed (non-isMeta) user message names a project.
    """
    if not transcript_path or not Path(transcript_path).exists():
        return False
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                role = entry.get("role") or entry.get("message", {}).get("role")
                if role != "user":
                    continue
                # Harness-injected user-role entries (skill bodies, subagent hand-backs,
                # system notices) carry isMeta=true and quote project names the user
                # never typed, which flagged unrelated sessions as project work.
                if entry.get("isMeta"):
                    continue
                text = _INJECTED_BLOCK.sub(" ", message_text(entry)).lower()
                for name in project_names:
                    if name and name in text:
                        return True
    except OSError:
        return False
    return False


def transcript_loaded_memory(transcript_path: str, roster_name: str) -> bool:
    """True if a Read tool call this session opened the roster or a memory file.

    :param transcript_path: path to the session JSONL transcript.
    :param roster_name: basename of the roster file (e.g. PROJECTS.md).
    :return: whether memory counts as loaded.
    """
    if not transcript_path or not Path(transcript_path).exists():
        return False
    pattern = re.compile("(" + MEMORY_FILE_RE + "|" + re.escape(roster_name) + ")")
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                content = entry.get("content") or entry.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "tool_use" and item.get("name") == "Read":
                        path = (item.get("input") or {}).get("file_path", "")
                        if pattern.search(path):
                            return True
    except OSError:
        return False
    return False


def read_state() -> dict:
    """Load the per-session warning counters.

    :return: {session_id: count}; empty on any error.
    """
    try:
        state = json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}
    return state if isinstance(state, dict) else {}


def increment_warn_count(session_id: str) -> int:
    """Bump and persist this session's warning counter.

    :param session_id: the hook payload's session id.
    :return: the new count.
    """
    state = read_state()
    state[session_id] = int(state.get(session_id, 0)) + 1
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state))
    except OSError:
        pass
    return state[session_id]


def main() -> None:
    """Hook entry point: allow, warn, or deny based on memory loading.

    :return: None (silence = no opinion; the normal permission flow runs).
    """
    event = read_event()
    if event is None:
        return

    config = load_config()
    if config is None or config.roster_file is None:
        return  # fail open: no config, nothing to check against

    project_names = load_project_names(config.roster_file)
    if not project_names:
        return

    transcript_path = event.get("transcript_path", "")
    if not transcript_mentions_project(transcript_path, project_names):
        return

    if transcript_loaded_memory(transcript_path, config.roster_file.name):
        return

    roster = str(config.roster_file)
    session_id = event.get("session_id", "unknown")
    count = int(read_state().get(session_id, 0))
    if count < WARN_LIMIT:
        new_count = increment_warn_count(session_id)
        pretool_context(
            "Memory not loaded for project work (warning {}/{}). Use the Read tool on {} "
            "to resolve the project, then its project_<name>.md and the matching "
            "MEMORY-gotchas-*.md, and start your reply with the visible "
            "'Loading memory: ...' line.".format(new_count, WARN_LIMIT, roster)
        )
        return

    pretool_deny(
        "Memory not loaded - no Read-TOOL call on a memory file this session, after {} "
        "warnings. Opening these with Bash (cat/head/sed/grep) does NOT register, even "
        "when the content is already in your context - only the Read tool counts. Use "
        "Read on {} (+ the matching project_<name>.md and MEMORY-gotchas-*.md), then "
        "retry the tool call.".format(WARN_LIMIT, roster)
    )


if __name__ == "__main__":
    main()
