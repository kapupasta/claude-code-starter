"""This file owns the tests for guard-command-shape.py Rule B (name the repo a write-verb git hits).

Run: python3 test_rule_b.py   (builds a throwaway umbrella repo with a nested repo inside)
"""
import importlib.util
import os
import tempfile
from pathlib import Path

_HOOK = Path(__file__).with_name("guard-command-shape.py")
_spec = importlib.util.spec_from_file_location("guard_command_shape", _HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

BASE = os.path.realpath(tempfile.mkdtemp())
UMBRELLA = os.path.join(BASE, "workspace")
NESTED = os.path.join(UMBRELLA, "project")
NOT_A_REPO = os.path.join(BASE, "plain")
for repo in (UMBRELLA, NESTED):
    os.makedirs(os.path.join(repo, ".git"))
os.makedirs(NOT_A_REPO)

# (label, command, cwd, expected: None = silent, else a substring the note must contain)
CASES = [
    ("read-only status", "git status", NESTED, None),
    ("read-only log", "git log --oneline -5", UMBRELLA, None),
    ("read-only rev-parse", "git rev-parse --show-toplevel", UMBRELLA, None),
    ("not git", "ls -la", UMBRELLA, None),
    ("push from nested cwd", "git push", NESTED, "repo " + NESTED + "."),
    ("push from umbrella cwd", "git push", UMBRELLA, "repo " + UMBRELLA + "."),
    ("cd then commit", "cd " + NESTED + " && git commit -m x", UMBRELLA, "repo " + NESTED + "."),
    ("-C overrides cwd", "git -C " + NESTED + " push", UMBRELLA, "repo " + NESTED + "."),
    ("-c option skipped", "git -c user.name=x commit -m y", NESTED, "`git commit`"),
    ("relative cd", "cd project && git add .", UMBRELLA, "repo " + NESTED + "."),
    ("outside any repo", "git add .", NOT_A_REPO, "(not inside a git repo)"),
    ("write verb after read verb", "git status && git reset --hard", NESTED, "`git reset`"),
]


def main():
    """Run every case. @return None (exit 1 on any failure)"""
    failed = 0
    for label, command, cwd, expected in CASES:
        got = hook.check_git_scope(command, cwd)
        ok = got is None if expected is None else (got is not None and expected in got)
        failed += 0 if ok else 1
        print("{:5} {:28} -> {}".format("ok" if ok else "FAIL", label, (got or "silent")[:100]))
    print("\n{}/{} passed".format(len(CASES) - failed, len(CASES)))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
