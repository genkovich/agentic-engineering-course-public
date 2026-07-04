#!/usr/bin/env bash
# verify.sh — Stop-hook: детермінований гейт на завершенні ходу (порт 7.6 verify.sh
# на стек node --test). Не дає агенту завершити хід, поки `node --test` червоний.
#
# Чому це гейт, а не гола `node --test`: Stop-hook блокує завершення лише на exit 2
# (stderr іде в Claude як причина). Цей скрипт конвертує fail у exit 2 і поважає
# stop_hook_active, щоб не зациклитись.
set -uo pipefail

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
else
  active=$(printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && echo true || echo false)
fi
[ "$active" = "true" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if out=$(node --test 2>&1); then
  exit 0
fi

{
  echo "Гейт червоний — не завершуй хід, поки node --test не зелений. Виправ і спробуй знову:"
  printf '%s\n' "$out" | tail -n 20
} >&2
exit 2
