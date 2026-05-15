#!/usr/bin/env bash
# Live subagent.jsonl — start/stop events підагентів.
set -euo pipefail
LOG="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/logs/subagent.jsonl"
mkdir -p "$(dirname "$LOG")"
touch "$LOG"

echo "tail -f $LOG"
echo

if command -v jq >/dev/null 2>&1; then
  tail -n 0 -f "$LOG" \
    | jq -r '"\(.ts)  \(.event)  type=\(.subagent_type // "?")  desc=\(.description // "")"'
else
  tail -n 0 -f "$LOG"
fi
