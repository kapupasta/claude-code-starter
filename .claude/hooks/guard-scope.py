#!/usr/bin/env python3
"""This file owns the scope guard: blocking tool calls that reach outside the workspace.

Reads a PreToolUse payload on stdin (Read/Write/Edit/MultiEdit/NotebookEdit/Glob/
Grep/Bash). Exits 2 with a stderr message when the tool targets a path outside the
allow-list, which blocks the call and shows Claude the reason so it can ask the
user for permission.

Allowed roots:
  - the session cwd (the project Claude was launched in)
  - workspace_root + extra_roots from starter-config.json
  - ~/.claude, ~/.config            (Claude's own state; editor/terminal config)
  - /tmp, /private/tmp, /private/var (system and macOS scratch)

Read-only roots (readonly_roots in the config, default ~/.agents) are reachable by
Read/Glob/Grep and Bash, never by Write/Edit. Skill installers put skill bodies
there and symlink them into ~/.claude/skills, so resolving those links would
otherwise block every read of an installed skill.

Without starter-config.json the guard still runs: it allows only the session cwd
tree plus the system roots above, and prints a one-line "run install.sh" hint.

Bash commands are tokenised with shlex and every home-dir path token is checked.
System paths (/etc, /usr) are intentionally not guarded here.
"""

import os
import re
import shlex
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_io import read_event  # noqa: E402
from starter_config import MISSING_CONFIG_HINT, StarterConfig, load_config  # noqa: E402

PATH_PARAM_BY_TOOL = {
    "Read":         ["file_path"],
    "Write":        ["file_path"],
    "Edit":         ["file_path"],
    "MultiEdit":    ["file_path"],
    "NotebookEdit": ["notebook_path"],
    "Glob":         ["path"],
    "Grep":         ["path"],
}

# Tools that cannot modify anything. A read-only root is reachable by these and by
# Bash (whose writes the sandbox already confines), never by the editing tools.
READ_ONLY_TOOLS = {"Read", "Glob", "Grep"}

# Always allowed, config or not.
SYSTEM_ROOTS = ["~/.claude", "~/.config", "/tmp", "/private/tmp", "/private/var"]

# Only path tokens with these prefixes (after ~ / $VAR expansion) are checked in Bash.
HOME_PREFIXES = ("/Users/", "/home/")

# shlex keeps shell punctuation glued to a word: `ls /root;` yields "/root;" and
# `(cd /root)` yields "(cd" + "/root)". Stripped before the path check so an
# allowed root followed by `;`, `&`, `|`, `)` or `,` is not mistaken for a sibling.
TRAILING_PUNCT = ";&|),"
LEADING_PUNCT = "("

# Fallback for commands shlex cannot lex (unbalanced quotes): a plain regex scan.
FALLBACK_PATH_RE = re.compile(r'(?:/Users/|/home/|~/)[^\s"\'`|>$&;()]+')


def resolve_safe(raw: str) -> Optional[Path]:
    """Expand `~` and resolve a path without raising.

    :param raw: path text from a tool input or a Bash token.
    :return: the resolved Path, or None if it cannot be resolved.
    """
    try:
        return Path(raw).expanduser().resolve()
    except (OSError, RuntimeError, ValueError):
        return None


def resolve_all(raw_roots: List[str]) -> List[Path]:
    """Resolve a list of root strings, skipping any that fail.

    :param raw_roots: path strings (may start with ~).
    :return: resolved Paths.
    """
    out = []  # type: List[Path]
    for r in raw_roots:
        p = resolve_safe(r)
        if p is not None:
            out.append(p)
    return out


def allowed_roots(project_root: Path, config: Optional[StarterConfig]) -> List[Path]:
    """Return every root the guard allows for read AND write.

    :param project_root: the session cwd.
    :param config: the loaded starter config, or None when it is missing.
    :return: resolved roots.
    """
    roots = resolve_all(SYSTEM_ROOTS)
    roots.append(project_root.resolve())
    if config is not None:
        if config.workspace_root is not None:
            roots.append(config.workspace_root)
        roots.extend(config.extra_roots)
    return roots


def read_only_roots(config: Optional[StarterConfig]) -> List[Path]:
    """Return roots that may be read but never written.

    :param config: the loaded starter config, or None.
    :return: resolved read-only roots (empty without a config).
    """
    return list(config.readonly_roots) if config is not None else []


def path_under(p: Path, roots: List[Path]) -> bool:
    """True when p is one of the roots or sits beneath one.

    :param p: resolved path to test.
    :param roots: resolved roots.
    :return: whether p is inside the allow-list.
    """
    for root in roots:
        try:
            p.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def strip_shell_punct(token: str) -> str:
    """Remove shell punctuation shlex left glued to a word.

    :param token: one shlex token, e.g. "/root;" or "(cd".
    :return: the token without leading `(` or trailing `;&|),`.
    """
    return token.lstrip(LEADING_PUNCT).rstrip(TRAILING_PUNCT)


def extract_bash_path_tokens(command: str) -> List[Tuple[str, str]]:
    """Return (raw_token, candidate_path) pairs for home-dir paths in a Bash command.

    shlex keeps quoted or escaped paths with spaces intact (a naive regex would cut
    them at the space). Falls back to a regex scan if the command cannot be lexed.

    :param command: the Bash command text.
    :return: pairs of the original token and its expanded path.
    """
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return [(m, m) for m in FALLBACK_PATH_RE.findall(command)]

    out = []  # type: List[Tuple[str, str]]
    for tok in tokens:
        cand = strip_shell_punct(tok)
        # Strip leading --flag= / VAR= prefixes so "--config=/home/x" is checked.
        if "=" in cand and not cand.startswith(("/", "~")):
            cand = cand.split("=", 1)[1]
        expanded = os.path.expanduser(os.path.expandvars(cand))
        if expanded.startswith(HOME_PREFIXES):
            out.append((tok, expanded))
    return out


def out_of_scope_bash_tokens(command: str, roots: List[Path]) -> List[str]:
    """Return the Bash path tokens that fall outside every root.

    :param command: the Bash command text.
    :param roots: resolved allowed roots (read-only roots included).
    :return: offending raw tokens, in command order.
    """
    risky = []  # type: List[str]
    for raw_tok, candidate in extract_bash_path_tokens(command):
        resolved = resolve_safe(candidate)
        if resolved is not None and not path_under(resolved, roots):
            risky.append(raw_tok)
    return risky


def describe_roots(roots: List[Path], ro_roots: List[Path]) -> str:
    """Human-readable allow-list for block messages.

    :param roots: read/write roots.
    :param ro_roots: read-only roots.
    :return: one-line summary.
    """
    text = ", ".join(str(r) for r in roots)
    if ro_roots:
        text += "; read-only: " + ", ".join(str(r) for r in ro_roots)
    return text


def block(reason: str) -> None:
    """Refuse the tool call: stderr goes to Claude, exit 2 blocks it.

    :param reason: block message.
    :return: never returns.
    """
    print(reason, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    """Hook entry point: check the tool's path inputs against the allow-list.

    :return: None (exits 0 to allow, 2 to block).
    """
    payload = read_event()
    if payload is None:
        sys.exit(0)

    config = load_config()
    hint = ""
    if config is None:
        print(MISSING_CONFIG_HINT, file=sys.stderr)
        hint = "\n(" + MISSING_CONFIG_HINT + "; only the session cwd is allowed until then.)"

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    roots = allowed_roots(Path(cwd), config)
    ro_roots = read_only_roots(config)

    if tool_name in PATH_PARAM_BY_TOOL:
        tool_roots = roots + (ro_roots if tool_name in READ_ONLY_TOOLS else [])
        for param in PATH_PARAM_BY_TOOL[tool_name]:
            raw = tool_input.get(param)
            if not raw:
                continue
            resolved = resolve_safe(raw)
            if resolved is None:
                continue
            if not path_under(resolved, tool_roots):
                block(
                    "Scope guard: {} targets a path outside the allowed roots.\n"
                    "  Path:        {}\n"
                    "  Project cwd: {}\n"
                    "  Allowed:     {}\n"
                    "Ask the user for explicit permission before retrying. If the task "
                    "doesn't need this access, work within the project directory instead.{}".format(
                        tool_name, raw, cwd, describe_roots(roots, ro_roots), hint)
                )
        sys.exit(0)

    if tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        risky = out_of_scope_bash_tokens(command, roots + ro_roots)
        if risky:
            preview = "\n".join("  {}".format(r) for r in risky[:5])
            more = "" if len(risky) <= 5 else "\n  (+ {} more)".format(len(risky) - 5)
            block(
                "Scope guard: Bash command references paths outside the allowed roots:\n"
                "{}{}\n"
                "  Project cwd: {}\n"
                "  Allowed:     {}\n"
                "Ask the user for explicit permission before retrying.{}".format(
                    preview, more, cwd, describe_roots(roots, ro_roots), hint)
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
