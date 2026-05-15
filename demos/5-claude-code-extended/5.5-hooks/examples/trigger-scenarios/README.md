# trigger-scenarios

Готові копі-паст промпти для скринкасту. Кожен файл — один сценарій, який провокує конкретний hook у живій сесії Claude Code.

## Як використати

1. Запусти `claude` всередині `hooks-toolkit/`.
2. У другому терміналі — `make tail-trace` (щоб бачити events live).
3. Скопіюй вміст одного з `trigger-*.md` у вікно Claude.
4. Дивись на блок/notification/trace.

## Сценарії

| Файл | Демонструє | Slide |
|---|---|---|
| [trigger-auto-format.md](trigger-auto-format.md) | recipe-1: PostToolUse + matcher `Edit\|Write` → prettier формат після write | 6.1 |
| [trigger-protect.md](trigger-protect.md) | recipe-2: PreToolUse → блок Edit/Write у `.env` (exit 2 + stderr `BLOCKED:`) | 6.2 |
| [trigger-secret-scan.md](trigger-secret-scan.md) | recipe-3: Python regex → блок `eval()` (exit 2 + `SECURITY WARNING`) | 6.3 |
| [trigger-session-context.md](trigger-session-context.md) | recipe-4: SessionStart matcher=compact → re-inject reminders і recent commits | 6.4 |
| [trigger-if-field.md](trigger-if-field.md) | recipe-5 + matcher vs if: passes `ls -la`, blocks `git push --force origin main` | 4 |

## Якщо не хочеш живої сесії

- **`make test-hooks`** ([../test-isolation/](../test-isolation/)) — runner проганяє всі 5 хуків через 8 fixtures без Claude. Результат — кольорова PASS/FAIL матриця за 1 секунду
- **`make recipes-tour`** ([../recipes-tour/](../recipes-tour/)) — 4 рецепти за один прогін з headers `Recipe N/4`, payload, hook, stderr/stdout, exit code. Підсумкова таблиця 4/4

Live trigger-сценарії з цієї папки — це наступний крок після того, як isolation passes. Якщо isolation FAIL — спершу полагодь скрипт, не йди у Claude.

## Природні тригери (без файлу)

> **Notification (Telegram)** добре провокується природно — як тільки Claude натикається на permission prompt (наприклад, новий Bash command), spawnиться popup/Telegram message. Можна також штучно: вимкни `--dangerously-skip-permissions`, потім попроси рідкісну Bash команду

> **Subagent lifecycle** — попроси Claude `delegate this research to a subagent` або викликай `/agent` з підагентом — `subagent.jsonl` буде писатися live
