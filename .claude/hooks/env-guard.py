#!/usr/bin/env python3
"""This file owns blocking writes to real .env files (PreToolUse guard).

Register as a PreToolUse hook on Edit|Write|Bash. Exits 2 (deny) on any attempt
to create or overwrite a real .env file, whether via Edit/Write
(tool_input.file_path) or a Bash shell redirection (> or >> into a .env target).
Allows .env.example / .env.sample templates and plain reads (cat/grep).

Why: secrets belong to the user. An agent that "helpfully" rewrites .env can
drop a key, merge two values onto one line (an append to a file with no trailing
newline does exactly that), or paste a credential into a file it then shows.

Needs no config; fails open on a malformed payload.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_io import read_event  # noqa: E402

ENV_PREFIX = ".env"
TEMPLATE_MARKERS = ("example", "sample")

# Capture the target token of every > or >> redirection in a shell command.
# \s in the negated class stops capture at the next whitespace, including the
# newline after a heredoc redirection (cat <<EOF >> .env).
_REDIRECT = re.compile(r">>?\s*([^\s;|&>]+)")


def is_protected(basename: str) -> bool:
    """True when a basename is a real .env file, not a template.

    :param basename: file name without directories.
    :return: whether writes to it are blocked.
    """
    return basename.startswith(ENV_PREFIX) and not any(m in basename for m in TEMPLATE_MARKERS)


def bash_writes_env(command: str) -> bool:
    """True when a Bash command redirects output into a protected .env file.

    :param command: the Bash command text.
    :return: whether any redirect target is protected.
    """
    for match in _REDIRECT.finditer(command):
        target = match.group(1).strip("\"'")
        if is_protected(os.path.basename(target)):
            return True
    return False


def main() -> None:
    """Hook entry point: exit 2 on a .env write, else exit 0.

    :return: None
    """
    data = read_event()
    if data is None:
        return
    tool_input = data.get("tool_input", {}) or {}
    if data.get("tool_name", "") == "Bash":
        hit = bash_writes_env(tool_input.get("command", "") or "")
    else:
        hit = is_protected(os.path.basename(tool_input.get("file_path", "") or ""))

    if hit:
        print("Hook blocked: write to a protected .env file. Ask the user to edit it manually.",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
