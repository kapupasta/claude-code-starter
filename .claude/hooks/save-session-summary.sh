#!/bin/bash
# PostCompact hook: saves the auto-compact summary to memory/sessions/ in the
# current project's memory dir. The dir is derived from $PWD (path with / → -),
# matching the Claude Code project slug convention.
SUMMARY=$(jq -r '.summary // empty' 2>/dev/null)
[ -z "$SUMMARY" ] && exit 0

PROJ=$(echo "$PWD" | sed 's|/|-|g')
DIR="$HOME/.claude/projects/${PROJ}/memory/sessions"
mkdir -p "$DIR"
DATE=$(date +%Y-%m-%d-%H%M)
printf "# Session Summary — %s\n\n%s\n" "$DATE" "$SUMMARY" > "$DIR/${DATE}.md"
echo "Session summary saved: ${DIR}/${DATE}.md"
