#!/usr/bin/env python3
"""Scope guard — block Read/Write/Edit/Glob/Grep/Bash that wander outside the
project Claude was invoked in.

Reads a PreToolUse hook payload on stdin. Exits 2 with a stderr message if the
tool targets a path outside the allow-list, which blocks the call and surfaces
the reason to Claude so it can ask the user for permission.

Always-allowed roots (regardless of project):
  - ~/.claude           (Claude's own state, memory, plugins, skills)
  - ~/.config           (config dirs for terminal emulators, editors, etc.)
  - /tmp, /private/tmp  (system scratch)
  - /private/var        (macOS tmp / system areas)
  - The current project root (from payload cwd)

Customize the EXTRA_ROOTS list below if you need extra always-allowed paths
(e.g. a shared "code" dir, an external scratch area).
"""

import json
import os
import re
import sys
from pathlib import Path

# Add extra always-allowed paths here. Use ~/ for home-relative.
EXTRA_ROOTS = [
    # "~/code",
    # "~/Local Sites",
]

PATH_PARAM_BY_TOOL = {
    "Read":         ["file_path"],
    "Write":        ["file_path"],
    "Edit":         ["file_path"],
    "MultiEdit":    ["file_path"],
    "NotebookEdit": ["notebook_path"],
    "Glob":         ["path"],
    "Grep":         ["path"],
}


def allowed_roots(project_root):
    home = Path.home()
    roots = [
        home / ".claude",
        home / ".config",
        Path("/tmp"),
        Path("/private/tmp"),
        Path("/private/var"),
        project_root,
    ]
    for extra in EXTRA_ROOTS:
        roots.append(Path(extra).expanduser())
    out = []
    for r in roots:
        try:
            out.append(r.resolve())
        except Exception:
            pass
    return out


def path_under(p, roots):
    for root in roots:
        try:
            p.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def resolve_safe(raw):
    try:
        return Path(raw).expanduser().resolve()
    except Exception:
        return None


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    project_root = Path(cwd).resolve()
    roots = allowed_roots(project_root)
    roots_human = "~/.claude, ~/.config, /tmp, project root"
    if EXTRA_ROOTS:
        roots_human += ", " + ", ".join(EXTRA_ROOTS)

    if tool_name in PATH_PARAM_BY_TOOL:
        for param in PATH_PARAM_BY_TOOL[tool_name]:
            raw = tool_input.get(param)
            if not raw:
                continue
            resolved = resolve_safe(raw)
            if resolved is None:
                continue
            if not path_under(resolved, roots):
                block(
                    f"Scope guard: {tool_name} targets a path outside the allowed roots ({roots_human}).\n"
                    f"  Path:        {raw}\n"
                    f"  Project cwd: {cwd}\n"
                    f"Ask the user for explicit permission before retrying. "
                    f"If the task doesn't need this access, work within the project directory instead."
                )
        sys.exit(0)

    if tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        matches = re.findall(r'(?:/Users/|/home/|~/)[^\s"\'`|>$&;()]+', command)
        risky = []
        for m in matches:
            resolved = resolve_safe(m)
            if resolved is None:
                continue
            if not path_under(resolved, roots):
                risky.append(m)
        if risky:
            preview = "\n".join(f"  {r}" for r in risky[:5])
            more = "" if len(risky) <= 5 else f"\n  (+ {len(risky) - 5} more)"
            block(
                f"Scope guard: Bash command references paths outside allowed roots ({roots_human}):\n"
                f"{preview}{more}\n"
                f"  Project cwd: {cwd}\n"
                f"Ask the user for explicit permission before retrying."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
