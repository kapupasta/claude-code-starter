#!/usr/bin/env python3
"""This file owns stdin/stdout plumbing shared by the starter's Python hooks.

Two jobs:

1. read_event() - read the hook payload with a timeout. A hook blocks the session
   while it runs, so a stdin read that never sees EOF freezes the whole turn
   (symptom: 0% CPU, the session just "feels slow"). SIGALRM bounds the read; a
   timeout takes the same fail-open path as a malformed payload.

2. PreToolUse output helpers. The old top-level {"decision": "approve"} is
   deprecated for PreToolUse and maps to permissionDecision "allow", which SKIPS
   the user's permission prompt. A guard that "approves" every call it has no
   opinion on therefore silently auto-approves everything. These helpers either
   print nothing (no opinion), deny, or add context without deciding.

Python 3.9 compatible.
"""

import json
import signal
import sys
from typing import Optional

STDIN_TIMEOUT_SECONDS = 5

PRE_TOOL_USE = "PreToolUse"


class _StdinTimeout(Exception):
    """Raised when the hook payload does not arrive within the timeout."""


def read_event() -> Optional[dict]:
    """Read the hook payload from stdin, bounded by STDIN_TIMEOUT_SECONDS.

    :return: the decoded payload, or None if it was malformed, not an object, or never arrived.
    """
    def _on_alarm(signum, frame):
        raise _StdinTimeout()

    signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(STDIN_TIMEOUT_SECONDS)
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError, _StdinTimeout):
        return None
    finally:
        signal.alarm(0)
    return data if isinstance(data, dict) else None


def pretool_deny(reason: str) -> None:
    """Print a PreToolUse deny decision; Claude sees the reason.

    :param reason: why the call was refused and what to do instead.
    :return: None
    """
    json.dump({"hookSpecificOutput": {
        "hookEventName": PRE_TOOL_USE,
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, sys.stdout)
    sys.stdout.write("\n")


def pretool_context(text: str) -> None:
    """Print context for Claude WITHOUT making a permission decision.

    The normal permission flow still runs; the text lands next to the tool result.

    :param text: the warning or note for Claude.
    :return: None
    """
    json.dump({"hookSpecificOutput": {
        "hookEventName": PRE_TOOL_USE,
        "additionalContext": text,
    }}, sys.stdout)
    sys.stdout.write("\n")
