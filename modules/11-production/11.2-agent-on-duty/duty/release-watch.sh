#!/usr/bin/env bash
# Обов'язок № 2 чергового: реліз-нагляд.
# Збирає логи жертви-застосунку за вікно нагляду, віддає їх Claude
# на аналіз headless-запуском і, якщо агент бачить аномалію,
# створює GitHub issue. Публікацію робить скрипт, не модель.

set -euo pipefail

WINDOW="${WATCH_WINDOW:-5m}"
REPO="${COURSE_REPO:-genkovich/course-project}"
COMPOSE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DRY_RUN="${DRY_RUN:-0}"

# Модель викликаємо в контейнері агента: ANTHROPIC_API_KEY живе лише там.
# Для локального прогону без сервера: CLAUDE_BIN=claude make watch-dry
if [[ -n "${CLAUDE_BIN:-}" ]]; then
  CLAUDE_CMD=($CLAUDE_BIN)
else
  CLAUDE_CMD=(docker compose --project-directory "$COMPOSE_DIR" exec -T agent claude)
fi

logs_file="$(mktemp)"
verdict_file="$(mktemp)"
trap 'rm -f "$logs_file" "$verdict_file"' EXIT

docker compose --project-directory "$COMPOSE_DIR" logs --since "$WINDOW" --no-log-prefix victim > "$logs_file"

lines="$(wc -l < "$logs_file" | tr -d ' ')"
if [[ "$lines" -lt 10 ]]; then
  echo "Замало логів за вікно $WINDOW ($lines рядків). Нагляд пропущено."
  exit 0
fi

echo "Аналізую $lines рядків логів за останні $WINDOW..."

"${CLAUDE_CMD[@]}" -p "Ти черговий інженер після релізу. Нижче структуровані JSON-логи сервісу за вікно нагляду. Порівняй частку статусів 500 і латентність із нормальною поведінкою сервісу (базлайн: 0 помилок, латентність до 100 мс). Відповідай СТРОГО одним JSON-об'єктом без markdown: {\"anomaly\": true|false, \"title\": \"короткий заголовок issue\", \"body\": \"markdown-тіло issue: що зламалось, які докази з логів (цифри), яка ймовірна причина, що робити далі\"}. Якщо аномалії немає, title і body лиши порожніми рядками.

Логи:
$(cat "$logs_file")" \
  --setting-sources "" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --permission-mode dontAsk \
  --tools "" \
  --model sonnet \
  --max-budget-usd 1 > "$verdict_file"

anomaly="$(python3 -c '
import json, re, sys
raw = open(sys.argv[1]).read()
m = re.search(r"\{.*\}", raw, re.S)
verdict = json.loads(m.group(0))
print("true" if verdict.get("anomaly") else "false")
open(sys.argv[1] + ".title", "w").write(verdict.get("title", ""))
open(sys.argv[1] + ".body", "w").write(verdict.get("body", ""))
' "$verdict_file")"

if [[ "$anomaly" != "true" ]]; then
  echo "Аномалій не знайдено. Реліз виглядає здоровим."
  exit 0
fi

title="$(cat "$verdict_file.title")"
echo "АНОМАЛІЯ: $title"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "--- DRY RUN: issue не створюю ---"
  cat "$verdict_file.body"
  exit 0
fi

issue_url="$(gh issue create --repo "$REPO" \
  --title "duty: $title" \
  --label release-anomaly \
  --body-file "$verdict_file.body")"
echo "Створено issue: $issue_url"
