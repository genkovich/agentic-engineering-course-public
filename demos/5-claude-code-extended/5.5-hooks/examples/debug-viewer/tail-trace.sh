#!/usr/bin/env bash
# Live-перегляд tool-trace.jsonl — кожен tool call як одна охайна лінія.
set -euo pipefail
LOG="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/logs/tool-trace.jsonl"
mkdir -p "$(dirname "$LOG")"
touch "$LOG"

echo "tail -f $LOG"
echo "(Ctrl-C для виходу. Запусти Claude у другому терміналі і виконуй задачі.)"
echo

if command -v jq >/dev/null 2>&1; then
  tail -n 0 -f "$LOG" \
    | jq -r '"\(.ts)  \(.event | ascii_upcase | .[0:4])  \(.tool)  \(.tool_input.file_path // .tool_input.command // "")"'
else
  tail -n 0 -f "$LOG"
fi
