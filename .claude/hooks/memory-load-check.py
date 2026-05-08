#!/usr/bin/env python3
"""PreToolUse hook: warn/block if no memory file Read this session AND user mentioned a project.

Triggered on Edit | Write | Bash. Read excluded (Reading memory IS the loading).

Memory dir is derived at runtime from the session cwd (path with / → -), so this
hook works without install-time configuration.

Mac Python is 3.9 — no `X | None`, no match/case.

Hook input (stdin JSON, per Claude Code hook spec).
Hook output (stdout JSON): {"decision": "approve" | "block", "reason": str}
"""
import json
import os
import re
import sys
from pathlib import Path

WARN_LIMIT = 3
STATE_FILE = Path.home() / ".claude/state/memory-load-check.json"


def memory_dir_for_cwd(cwd):
    if not cwd:
        return None
    slug = str(Path(cwd).resolve()).replace("/", "-")
    return Path.home() / ".claude/projects" / slug / "memory"


def load_active_project_names(memory_file):
    """Parse 'Active Projects' section of MEMORY.md and return set of lowercased project names."""
    if not memory_file or not memory_file.exists():
        return set()
    try:
        content = memory_file.read_text()
    except (OSError, IOError):
        return set()
    match = re.search(r"^## Active Projects.*?(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
    if not match:
        return set()
    section = match.group(0)
    names = set()
    for line in section.splitlines():
        m = re.match(r"^-\s*([A-Za-z][\w.-]*(?:\s[A-Za-z][\w.-]*)*?)\s*[—-]", line.strip())
        if m:
            name = m.group(1).strip().lower()
            names.add(name)
            first_word = name.split()[0] if name else ""
            if first_word:
                names.add(first_word)
    return names


def transcript_mentions_project(transcript_path, project_names):
    if not transcript_path or not Path(transcript_path).exists():
        return False
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = entry.get("role") or entry.get("message", {}).get("role")
                if role != "user":
                    continue
                content = entry.get("content") or entry.get("message", {}).get("content", "")
                if isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, dict):
                            parts.append(c.get("text", "") or "")
                    content = " ".join(parts)
                content_lower = str(content).lower()
                for name in project_names:
                    if name and name in content_lower:
                        return True
    except (OSError, IOError):
        return False
    return False


def transcript_loaded_memory(transcript_path):
    if not transcript_path or not Path(transcript_path).exists():
        return False
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = entry.get("content") or entry.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "tool_use" and item.get("name") == "Read":
                        path = item.get("input", {}).get("file_path", "")
                        if re.search(r"(MEMORY-[\w-]+\.md|project_[\w-]+\.md)", path):
                            return True
    except (OSError, IOError):
        return False
    return False


def get_warn_count(session_id):
    if not STATE_FILE.exists():
        return 0
    try:
        state = json.loads(STATE_FILE.read_text())
        return state.get(session_id, 0)
    except (json.JSONDecodeError, OSError):
        return 0


def increment_warn_count(session_id):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            state = {}
    state[session_id] = state.get(session_id, 0) + 1
    try:
        STATE_FILE.write_text(json.dumps(state))
    except (OSError, IOError):
        pass
    return state[session_id]


def emit(decision, reason=None):
    out = {"decision": decision}
    if reason:
        out["reason"] = reason
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        emit("approve")
        return

    session_id = event.get("session_id", "unknown")
    transcript_path = event.get("transcript_path", "")
    cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    memory_dir = memory_dir_for_cwd(cwd)
    if not memory_dir:
        emit("approve")
        return
    memory_file = memory_dir / "MEMORY.md"

    project_names = load_active_project_names(memory_file)
    if not project_names:
        emit("approve")
        return

    if not transcript_mentions_project(transcript_path, project_names):
        emit("approve")
        return

    if transcript_loaded_memory(transcript_path):
        emit("approve")
        return

    warn_count = get_warn_count(session_id)
    if warn_count < WARN_LIMIT:
        new_count = increment_warn_count(session_id)
        emit(
            "approve",
            "Memory not loaded for project work (warning {}/{}). Read project_<name>.md and matching MEMORY-gotchas-*.md before proceeding. Visible-loading announcement is required.".format(
                new_count, WARN_LIMIT
            ),
        )
    else:
        emit(
            "block",
            "Memory not loaded after {} warnings. STOP. Read project_<name>.md and matching MEMORY-gotchas-*.md, then retry the tool call.".format(
                WARN_LIMIT
            ),
        )


if __name__ == "__main__":
    main()
