#!/bin/bash
# .claude/hooks/block-main-push.sh - не даємо запушити напряму в main
command=$(jq -r '.tool_input.command')
if echo "$command" | grep -qE 'git push.*\bmain\b'; then
  echo "Прямий push у main заблоковано. Пушити треба в named worktree-гілку." >&2
  exit 2          # exit 2 -> Claude Code блокує виклик і показує підказку
fi
