#!/bin/bash
# This file owns saving the /compact summary into memory/sessions/ (PostCompact hook).
#
# Why: compaction replaces the conversation with a summary that lives only in the
# session. Writing it to memory/sessions/<date>.md keeps it after /clear or a crash.
#
# Reads compact_summary from the PostCompact payload (older builds used summary).
# Target dir: memory_dir from starter-config.json, else the Claude Code project
# slug of $PWD. Never blocks: any failure exits 0. Needs jq.

CONFIG="${STARTER_CONFIG:-$HOME/.claude/hooks/starter-config.json}"
STDIN_TIMEOUT_SECONDS=5

# Bounded read: a payload that never reaches EOF must not freeze the session.
IFS= read -r -d '' -t "$STDIN_TIMEOUT_SECONDS" PAYLOAD
[ -z "$PAYLOAD" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0

SUMMARY=$(printf '%s' "$PAYLOAD" | jq -r '.compact_summary // .summary // empty' 2>/dev/null)
[ -z "$SUMMARY" ] && exit 0

DIR=""
if [ -f "$CONFIG" ]; then
  DIR=$(jq -r '.memory_dir // empty' "$CONFIG" 2>/dev/null)
  DIR="${DIR/#\~/$HOME}"
fi
if [ -z "$DIR" ]; then
  PROJ=$(printf '%s' "$PWD" | sed 's|/|-|g')
  DIR="$HOME/.claude/projects/${PROJ}/memory"
fi
DIR="$DIR/sessions"

mkdir -p "$DIR" 2>/dev/null || exit 0
DATE=$(date +%Y-%m-%d-%H%M)
printf "# Session Summary — %s\n\n%s\n" "$DATE" "$SUMMARY" > "$DIR/${DATE}.md" || exit 0
echo "Session summary saved: ${DIR}/${DATE}.md"
