#!/usr/bin/env bash
# This file owns installing the starter: it links .claude/ into your home and writes the workspace config.
#
# Non-interactive use (CI, testing against a throwaway $HOME):
#   STARTER_WS=~/code STARTER_YES=1 ./install.sh

set -euo pipefail

LINKED_ITEMS="settings.json hooks skills rules"

echo "Claude Code starter installer"
echo "============================="
echo

# 0. Requirements: hooks are Python 3, the session-summary hook uses jq.
for tool in python3 git; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool"; exit 1; }
done
command -v jq >/dev/null || echo "Note: jq not found. save-session-summary.sh needs it; install jq to keep compaction summaries."

# 1. Workspace path
DEFAULT_WS="$HOME/code"
if [[ -n "${STARTER_WS:-}" ]]; then
  WS="$STARTER_WS"
else
  read -r -p "Workspace root [$DEFAULT_WS]: " WS
  WS="${WS:-$DEFAULT_WS}"
fi
WS="${WS/#\~/$HOME}"
if [[ ! -d "$WS" ]]; then
  if [[ "${STARTER_YES:-}" == "1" ]]; then mk=y; else read -r -p "Directory $WS doesn't exist. Create it? [y/N] " mk; fi
  if [[ "$mk" == "y" ]]; then mkdir -p "$WS"; else echo "Aborted."; exit 1; fi
fi
WS="$(cd "$WS" && pwd)"

# 2. Project slug = absolute path with / → - (how Claude Code names ~/.claude/projects/<slug>)
SLUG="${WS//\//-}"
REPO="$(cd "$(dirname "$0")" && pwd)"

echo
echo "Workspace:    $WS"
echo "Project slug: $SLUG"
echo "Repo:         $REPO"
echo

# 3. Refuse to replace real (non-symlink) config. Back it up yourself first.
for item in $LINKED_ITEMS; do
  dest="$HOME/.claude/$item"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    echo "STOP: ~/.claude/$item exists and is not a symlink."
    echo "Back it up (mv ~/.claude/$item ~/.claude/$item.bak), then re-run."
    exit 1
  fi
done

if [[ "${STARTER_YES:-}" != "1" ]]; then
  read -r -p "Proceed? [y/N] " confirm
  [[ "$confirm" == "y" ]] || exit 0
fi

# 4. Rename the placeholder memory dir to this workspace's slug
PLACEHOLDER="$REPO/.claude/projects/PLACEHOLDER_WORKSPACE"
TARGET="$REPO/.claude/projects/$SLUG"
if [[ -d "$PLACEHOLDER" && ! -d "$TARGET" ]]; then
  mv "$PLACEHOLDER" "$TARGET"
  echo "Renamed PLACEHOLDER_WORKSPACE → $SLUG"
elif [[ -d "$TARGET" ]]; then
  echo "Memory dir already exists at $TARGET (re-run?). Skipping rename."
fi

# 5. Symlink config into ~/.claude (only replaces existing symlinks; step 3 guarded real files)
mkdir -p "$HOME/.claude/projects"
for item in $LINKED_ITEMS; do
  ln -sfn "$REPO/.claude/$item" "$HOME/.claude/$item"
  echo "Linked ~/.claude/$item"
done
ln -sfn "$TARGET" "$HOME/.claude/projects/$SLUG"
echo "Linked ~/.claude/projects/$SLUG"

# 6. Write the workspace config every hook and script reads (gitignored; never committed)
CONFIG="$REPO/.claude/hooks/starter-config.json"
if [[ ! -e "$CONFIG" ]]; then
  python3 - "$CONFIG" "$WS" "$TARGET/memory" <<'PY'
import json, sys
config_path, ws, memory_dir = sys.argv[1], sys.argv[2], sys.argv[3]
config = {
    "workspace_root": ws,
    "extra_roots": [],
    "readonly_roots": ["~/.agents"],
    "roster_file": ws + "/PROJECTS.md",
    "memory_dir": memory_dir,
    "scratch_dir": ws + "/tmp",
}
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")
PY
  echo "Wrote hooks/starter-config.json (add extra_roots there for folders outside $WS)"
else
  echo "hooks/starter-config.json already exists, leaving alone."
fi

# 7. Seed the workspace (never overwrites)
copy_if_absent() {
  # $1 = source in repo, $2 = destination in workspace
  if [[ ! -e "$2" ]]; then cp -R "$1" "$2"; echo "Copied $(basename "$2") → $WS/"; else echo "$(basename "$2") exists in workspace, leaving alone."; fi
}
copy_if_absent "$REPO/CLAUDE.md" "$WS/CLAUDE.md"
copy_if_absent "$REPO/templates/PROJECTS.md" "$WS/PROJECTS.md"
mkdir -p "$WS/tmp"

# 8. Make hooks and scripts executable
chmod +x "$REPO/.claude/hooks/"*.py "$REPO/.claude/hooks/"*.sh "$REPO/scripts/"*.sh

echo
echo "Done. Next:"
echo "  1. Open Claude Code in $WS and run /sandbox to confirm the sandbox started"
echo "  2. Edit $WS/CLAUDE.md: replace the (example) sections with your own"
echo "  3. Edit memory/MEMORY.md: profile, preferences, and which example gates you keep"
echo "  4. Add your projects to $WS/PROJECTS.md"
echo "  5. Read WHY.md before removing anything"
