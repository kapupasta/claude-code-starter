#!/usr/bin/env python3
"""This file owns the tests for md-link-check.py's bare-.md-path detection.

Locks in which forms of .md reference the Stop hook flags, so the
fenced-block rules can be tightened without silently re-introducing noise.

Run: python3 test_md_link_check.py
"""

import importlib.util
import sys
from pathlib import Path

_HOOK = Path(__file__).with_name("md-link-check.py")

_spec = importlib.util.spec_from_file_location("md_link_check", _HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

PATH = "~/code/project/notes/incident-report-2026-08-06.md"
ABS = "/home/user/code/project/notes/incident-report-2026-08-06.md"

# (name, text, should_flag)
CASES = [
    # --- must be caught: the user is being pointed at a file -------------
    ("bare path in prose", f"The report is at {PATH} now.", True),
    ("inline backticks", f"result: written -> `{PATH}` (ok)", True),
    ("lone path in fence", f"Here it is:\n\n```\n{PATH}\n```\n\nOpen it.", True),
    ("lone path in fence + lang", f"```text\n{PATH}\n```", True),
    ("lone path in tilde fence", f"~~~\n{PATH}\n~~~", True),
    ("lone abs path in fence", f"```\n{ABS}\n```", True),
    ("lone path, padded fence", f"```\n\n  {PATH}  \n\n```", True),

    # --- must NOT be caught: incidental, or already linked ---------------
    ("proper md link", f"[report.md]({'file://' + ABS})", False),
    ("md link with tilde label", f"[{PATH}](file://{ABS})", False),
    ("bare filename, no slash", "See MEMORY.md for the index.", False),
    (
        "multi-line shell output in fence",
        f"```\n$ git status\n modified: {PATH}\n modified: other.md\n```",
        False,
    ),
    (
        "multi-line code in fence",
        f'```python\npath = "{PATH}"\nprint(path)\n```',
        False,
    ),
    ("command in fence", f"```\ncat {PATH}\n```", False),
    ("empty fence", "```\n\n```", False),
    ("fence with prose line", f"```\nthe file {PATH} is here\n```", False),
    ("no md at all", "```\nls -la\n```\nNothing to see.", False),
    ("inline code, no path", "Run `git status` first.", False),
]


def main() -> int:
    """Run every case, print a table, return a POSIX exit code."""
    failures = 0
    for name, text, should_flag in CASES:
        hits = hook.find_bare_paths(text)
        flagged = bool(hits)
        ok = flagged == should_flag
        if not ok:
            failures += 1
        print(
            f"{'PASS' if ok else 'FAIL':4} | "
            f"{'flags' if flagged else 'quiet':5} "
            f"(want {'flags' if should_flag else 'quiet':5}) | {name}"
        )
    total = len(CASES)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
