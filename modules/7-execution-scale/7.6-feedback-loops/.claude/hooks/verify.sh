#!/usr/bin/env bash
# Stop-hook для лекції 7.6 — детермінований гейт на завершенні ходу.
# Не дає Claude завершити хід, поки гейт (tsc + vitest) червоний.
#
# ВАЖЛИВО (чому гола `npm test` гейтом не є): на падінні тести повертають exit 1,
# а Stop-hook блокує завершення ТІЛЬКИ на exit 2 (stderr іде в Claude як причина).
# Тому цей скрипт конвертує fail у exit 2. І поважає stop_hook_active, щоб не зациклитись.
#
# Активувати (НЕ ввімкнено за замовчуванням, щоб не блокувати інші демо):
#   додай у .claude/settings.json:
#   { "hooks": { "Stop": [ { "hooks": [ { "type": "command",
#       "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/verify.sh" } ] } ] } }

set -uo pipefail

input=$(cat)   # Claude передає на stdin JSON про поточний хід

# stop_hook_active=true → це вже повторне коло від цього ж хука. Не блокуємо вдруге,
# інакше зациклимось (Claude і так примусово завершує після 8 поспіль блоків).
if command -v jq >/dev/null 2>&1; then
  active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
else
  active=$(printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && echo true || echo false)
fi
[ "$active" = "true" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Гейт: типи + тести. Захоплюємо вивід, щоб віддати причину в stderr.
if out=$(npx tsc --noEmit && npm test 2>&1); then
  exit 0   # зелено — дозволяємо завершити хід
fi

# Червоно — блокуємо завершення (exit 2) і віддаємо останні рядки як причину.
{
  echo "Гейт червоний — не завершуй хід, поки tsc/vitest не зелені. Виправ і спробуй знову:"
  printf '%s\n' "$out" | tail -n 25
} >&2
exit 2
