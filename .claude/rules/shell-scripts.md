---
paths:
  - "**/*.sh"
  - "**/*.bash"
  - "**/*.zsh"
---

# Shell script cardinal constraints (example — auto-loaded when a shell script is opened)

This file owns the must-not-violate rules for writing shell scripts that run on macOS and Linux. Claude Code injects it for files matching `paths:` above. Each rule is a trap that fails *silently*: the script runs, exits 0 and reports something wrong. Replace or extend with your own.

- **Target bash 3.2 + BSD tools** unless the script says otherwise (macOS ships bash 3.2): no associative arrays, no `mapfile`, no `${var,,}`, no GNU-only flags (`sed -i` without a suffix argument, `date -d`, `grep -P`).
- **BSD `sed` has no `\|` alternation in basic regex** — it matches nothing and exits 0. Use `sed -E 's/(a|b)//'`.
- **`sed -i` exits 0 when it changed nothing.** Read the file back or `diff` it against a backup before reporting the edit done.
- **Never end a check with `|| echo "ok"`.** `grep -c` exits 1 on zero matches, short-circuits the `&&`, and the fallback prints the all-clear.
- **A missing binary inside a loop falls through to the "clean" branch.** Check `command -v <tool>` once before the loop, or exit non-zero on the first `command not found`.
- **Quote every expansion** (`"$var"`, `"$@"`) and every glob passed as an argument (`--include='*.md'`).
- **Exit code = findings.** A check script exits non-zero when it found something, so a wrapper can branch on it; printing "warning" and exiting 0 is an alarm that can't report.
- **System Python on macOS may be 3.9** — no `X | None` type hints, no `match`. Keep embedded `python3` helpers 3.9-safe.
- **One-line `This file owns …` header** at the top of every script.
