#!/usr/bin/env bash
# Live transcript.jsonl — UserPromptSubmit і Stop events.
set -euo pipefail
LOG="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/logs/transcript.jsonl"
mkdir -p "$(dirname "$LOG")"
touch "$LOG"

echo "tail -f $LOG"
echo

if command -v jq >/dev/null 2>&1; then
  tail -n 0 -f "$LOG" \
    | jq -r '"\(.ts)  \(.event)  prompt=\"\(.prompt_preview // "" | .[0:120])\"  stop=\(.stop_reason // "")"'
else
  tail -n 0 -f "$LOG"
fi
