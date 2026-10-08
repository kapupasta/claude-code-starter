#!/usr/bin/env python3
"""This file owns the tests for guard-command-shape.py Rules A, C and D.

Locks in that a sandbox-excluded command (git fetch/push/pull, gh reads) is
blocked whenever ANYTHING shares its line. Since Claude Code 2.1.277 any sibling
keeps the whole line sandboxed, so these forms fail on the network; an earlier
"harmless sibling" allowance pointed agents straight at them. Also covers the
recursive-delete shape (Rule A) and $TMPDIR in unsandboxed calls (Rule D).

Run: python3 test_guard_command_shape.py
"""

import importlib.util
import sys
from pathlib import Path

_HOOK = Path(__file__).with_name("guard-command-shape.py")

_spec = importlib.util.spec_from_file_location("guard_command_shape", _HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

# Mirrors the starter settings' sandbox.excludedCommands entries these cases touch.
PATTERNS = ["git fetch *", "git push *", "git pull *",
            "gh run view *", "gh run list *", "gh run watch *", "gh pr view *"]

WORKSPACE = "/home/user/code"

# Rule C: (name, command, should_block)
CASES = [
    # --- must pass: the excluded command stands alone ---------------------
    ("bare git push", "git push", False),
    ("bare git push with args", "git push -u origin feature/update-deps", False),
    ("bare gh run watch", "gh run watch 123 -R example/repo --exit-status --compact", False),
    ("bare gh run list", "gh run list -R example/repo --limit 1", False),
    ("no excluded command at all", "cd /x && git status && ls", False),
    # --- must block: forms that failed on the network ---------------------
    ("sleep before gh", "sleep 8; gh run list -R x --limit 3", True),
    ("gh piped into tail", "gh run watch 1 -R x --exit-status | tail -30", True),
    ("gh piped into grep", "gh run view 1 -R x --log --job 2 | grep -E 'Tests'", True),
    # --- must block: forms an older allowance let through -----------------
    ("cd then git pull", "cd /home/user/code/project && git pull", True),
    ("git pull then rev-parse", "git pull && git rev-parse --show-toplevel", True),
    ("echo beside push", "echo go; git push", True),
    ("safe-looking substitution", "git push origin $(git branch --show-current)", True),
    ("redirect into a file", "gh run view 1 -R x --log > out.txt", True),
    ("for-loop of fetches", "for r in a b; do git fetch; done", True),
]

# Rule A: (name, command, should_block)
DELETE_CASES = [
    ("rm -rf alone", "rm -rf /home/user/code/project/old", False),
    ("rm -rf chained after listing", "find old | head; rm -rf old", True),
    ("ephemeral chained", "rm -rf .next && pnpm build", False),
    ("workspace root forbidden", "rm -rf /home/user/code", True),
    ("forbidden root alone", "rm -rf /", True),
    ("rm inside a commit message", 'git commit -m "fix; rm -rf must stand alone"', False),
]

# Rule D: (name, command, should_block)
TMPDIR_CASES = [
    ("tmpdir unsandboxed", "ssh host cat x > $TMPDIR/out", True),
    ("braced tmpdir", "cp a ${TMPDIR}/b", True),
    ("no tmpdir", "ssh host uptime", False),
]


def run(label, cases, check):
    """Run one table of cases through a check function.

    :param label: rule label for the printout.
    :param cases: (name, command, should_block) tuples.
    :param check: callable(command) -> reason or None.
    :return: number of failures.
    """
    failures = 0
    for name, command, should_block in cases:
        blocked = check(command) is not None
        ok = blocked == should_block
        failures += 0 if ok else 1
        print("%s  %s %-30s blocked=%s" % ("ok  " if ok else "FAIL", label, name, blocked))
    return failures


def main():
    """Run every case and exit non-zero if any disagrees with its expectation.

    :return: None
    """
    total = len(CASES) + len(DELETE_CASES) + len(TMPDIR_CASES)
    failures = run("C", CASES, lambda c: hook.check_excluded_escape(c, PATTERNS))
    failures += run("A", DELETE_CASES, lambda c: hook.check_delete_shape(c, WORKSPACE))
    failures += run("D", TMPDIR_CASES, hook.check_unsandboxed_tmpdir)
    print("\n%d/%d passed" % (total - failures, total))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
