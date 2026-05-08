#!/usr/bin/env bash
# Claude Code starter installer.
# Symlinks .claude/ into your home and customizes it for your workspace.

set -euo pipefail

echo "Claude Code starter installer"
echo "============================="
echo

# 1. Workspace path
DEFAULT_WS="$HOME/code"
read -r -p "Workspace root [$DEFAULT_WS]: " WS
WS="${WS:-$DEFAULT_WS}"
WS="${WS/#\~/$HOME}"
if [[ ! -d "$WS" ]]; then
  read -r -p "Directory $WS doesn't exist. Create it? [y/N] " mk
  if [[ "$mk" == "y" ]]; then mkdir -p "$WS"; else echo "Aborted."; exit 1; fi
fi
WS="$(cd "$WS" && pwd)"

# 2. Project slug = absolute path with / → -
SLUG="${WS//\//-}"

echo
echo "Workspace:    $WS"
echo "Project slug: $SLUG"
echo

# 3. Existing-setup safety
if [[ -e "$HOME/.claude/settings.json" && ! -L "$HOME/.claude/settings.json" ]]; then
  echo "WARNING: ~/.claude/settings.json exists and is not a symlink."
  echo "Back it up (mv ~/.claude/settings.json ~/.claude/settings.json.bak), then re-run."
  exit 1
fi

read -r -p "Proceed? [y/N] " confirm
[[ "$confirm" == "y" ]] || exit 0

# 4. Repo root (where this script lives)
REPO="$(cd "$(dirname "$0")" && pwd)"

# 5. Rename placeholder project dir
PLACEHOLDER="$REPO/.claude/projects/PLACEHOLDER_WORKSPACE"
TARGET="$REPO/.claude/projects/$SLUG"
if [[ -d "$PLACEHOLDER" && ! -d "$TARGET" ]]; then
  mv "$PLACEHOLDER" "$TARGET"
  echo "Renamed PLACEHOLDER_WORKSPACE → $SLUG"
elif [[ -d "$TARGET" ]]; then
  echo "Project dir already exists at $TARGET (re-running installer?). Skipping rename."
fi

# 6. Symlink into ~/.claude
mkdir -p "$HOME/.claude" "$HOME/.claude/projects"
for item in settings.json hooks skills; do
  src="$REPO/.claude/$item"
  dest="$HOME/.claude/$item"
  [[ -e "$dest" || -L "$dest" ]] && rm -rf "$dest"
  ln -s "$src" "$dest"
  echo "Symlinked ~/.claude/$item"
done

# 7. Symlink memory dir
ln -sfn "$REPO/.claude/projects/$SLUG" "$HOME/.claude/projects/$SLUG"
echo "Symlinked ~/.claude/projects/$SLUG"

# 8. Drop CLAUDE.md into the workspace root (don't overwrite)
if [[ ! -e "$WS/CLAUDE.md" ]]; then
  cp "$REPO/CLAUDE.md" "$WS/CLAUDE.md"
  echo "Copied CLAUDE.md → $WS/"
else
  echo "CLAUDE.md already exists in workspace, leaving alone."
fi

# 9. Make hooks executable
chmod +x "$REPO/.claude/hooks/"*.py "$REPO/.claude/hooks/"*.sh

echo
echo "Done."
echo
echo "Next:"
echo "  1. Open Claude Code in $WS"
echo "  2. Edit CLAUDE.md (TODO sections)"
echo "  3. Edit memory/MEMORY.md (User Profile, Standing Preferences)"
echo "  4. Edit memory/CONVENTIONS.md (tech-stack tags)"
