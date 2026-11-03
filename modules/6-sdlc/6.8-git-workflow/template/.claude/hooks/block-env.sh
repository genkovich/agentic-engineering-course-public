#!/bin/bash
# .claude/hooks/block-env.sh - не даємо додати .env у коміт
command=$(jq -r '.tool_input.command')
if echo "$command" | grep -q '\.env'; then
  echo "Спроба додати .env заблокована" >&2
  exit 2          # exit 2 -> Claude Code блокує виклик інструмента
fi
