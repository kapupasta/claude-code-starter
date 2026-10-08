#!/usr/bin/env python3
"""This file owns loading the workspace config every starter hook reads.

No hook hardcodes a user path. Workspace-specific values live in ONE JSON file,
written by install.sh and gitignored:

    ~/.claude/hooks/starter-config.json

(override the location with the STARTER_CONFIG environment variable, which is
also how the tests point a hook at a throwaway config). See
starter-config.example.json for the keys.

Missing or unreadable config never raises: load_config() returns None and each
hook decides how to degrade (guard-scope narrows to the session cwd, the rest
fail open).

Python 3.9 compatible: no `X | None`, no match/case.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Environment variable that overrides the config file location.
CONFIG_ENV_VAR = "STARTER_CONFIG"

# Where install.sh writes the config.
DEFAULT_CONFIG_PATH = "~/.claude/hooks/starter-config.json"

# Shown once on stderr when a hook needs the config and cannot find it.
MISSING_CONFIG_HINT = (
    "starter hooks: no starter-config.json found "
    "(~/.claude/hooks/starter-config.json) - run install.sh"
)

# Used when the config exists but omits a key.
DEFAULT_READONLY_ROOTS = ["~/.agents"]
DEFAULT_ROSTER_NAME = "PROJECTS.md"
DEFAULT_SCRATCH_NAME = "tmp"


def config_path() -> Path:
    """Return the path the config is read from (env override first).

    :return: expanded, absolute config path; the file may not exist.
    """
    raw = os.environ.get(CONFIG_ENV_VAR) or DEFAULT_CONFIG_PATH
    return Path(raw).expanduser()


def expand(raw: Any) -> Optional[Path]:
    """Expand `~` and resolve a configured path string.

    :param raw: a path string from the config (anything else yields None).
    :return: the resolved Path, or None if raw is empty, not a string, or unresolvable.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return Path(raw).expanduser().resolve()
    except (OSError, RuntimeError):
        return None


def expand_list(raw: Any) -> List[Path]:
    """Expand a list of configured path strings, dropping invalid entries.

    :param raw: a list from the config (anything else yields []).
    :return: resolved Paths, in config order.
    """
    if not isinstance(raw, list):
        return []
    out = []  # type: List[Path]
    for item in raw:
        p = expand(item)
        if p is not None:
            out.append(p)
    return out


def memory_slug(workspace: Path) -> str:
    """Return Claude Code's project slug for a directory (every `/` becomes `-`).

    :param workspace: absolute directory Claude Code was launched in.
    :return: the slug used under ~/.claude/projects/.
    """
    return str(workspace).replace("/", "-")


class StarterConfig(object):
    """Resolved, defaulted view of starter-config.json."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Build the view from the raw decoded JSON.

        :param data: decoded config object.
        """
        self.raw = data
        self.workspace_root = expand(data.get("workspace_root"))  # type: Optional[Path]
        self.extra_roots = expand_list(data.get("extra_roots"))
        readonly = data.get("readonly_roots")
        self.readonly_roots = expand_list(DEFAULT_READONLY_ROOTS if readonly is None else readonly)
        self.roster_file = expand(data.get("roster_file")) or self._under_workspace(DEFAULT_ROSTER_NAME)
        self.memory_dir = expand(data.get("memory_dir")) or self._default_memory_dir()
        self.scratch_dir = expand(data.get("scratch_dir")) or self._under_workspace(DEFAULT_SCRATCH_NAME)

    def _under_workspace(self, name: str) -> Optional[Path]:
        """Return workspace_root/name, or None without a workspace root.

        :param name: child file or directory name.
        :return: the joined path or None.
        """
        return self.workspace_root / name if self.workspace_root else None

    def _default_memory_dir(self) -> Optional[Path]:
        """Derive the memory dir from workspace_root the way Claude Code slugs it.

        :return: ~/.claude/projects/<slug>/memory, or None without a workspace root.
        """
        if not self.workspace_root:
            return None
        return Path.home() / ".claude" / "projects" / memory_slug(self.workspace_root) / "memory"


def load_config() -> Optional[StarterConfig]:
    """Read and parse the config file.

    :return: a StarterConfig, or None if the file is missing, unreadable or not a JSON object.
    """
    try:
        with open(str(config_path()), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return StarterConfig(data)
