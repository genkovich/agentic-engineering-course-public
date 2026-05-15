# test-isolation

Slide 5.5 з лекції 5.4: «Test your hook in isolation». Кожен hook читає JSON зі stdin і повертає exit code. Найдешевший спосіб ловити баги (chmod забув / jq не стоїть / шлях не парситься) — прогнати fixtures **без** живої сесії Claude.

## Як запустити

```bash
# з hooks-toolkit/
make test-hooks

# або напряму
bash examples/test-isolation/run-isolation-tests.sh
```

Очікуваний вивід — кольорова матриця 8 тест-кейсів, всі `PASS`.

## Структура

```
test-isolation/
├── README.md                    — цей файл
├── run-isolation-tests.sh       — runner: 8 fixtures × 5 хуків, друкує PASS/FAIL
└── payloads/
    ├── protect-env.json         → recipe-2 має блок (exit 2 + stderr "BLOCKED")
    ├── protect-clean.json       → recipe-2 пропускає (exit 0)
    ├── secrets-eval.json        → recipe-3 має блок (exit 2 + stderr "Security")
    ├── secrets-clean.json       → recipe-3 пропускає (exit 0)
    ├── git-force-main.json      → recipe-5 має блок (exit 2 + stderr "BLOCKED")
    ├── git-ls.json              → recipe-5 пропускає (exit 0)
    ├── mcp-allowed.json         → mcp-allowlist пропускає (exit 0; filesystem allowed)
    └── mcp-denied.json          → mcp-allowlist денаїть (exit 0 + structured JSON deny у stdout)
```

## Що читати у fixtures

Payload — це JSON event, який Claude Code надсилає у stdin hook-у. Поля, які потрібні для роботи hook'ів цього демо:

- **`tool_name`** — напр. `Edit`, `Write`, `Bash`, `mcp__github__create_pull_request`. Використовується matcher'ом і скриптами (`mcp-allowlist.sh` парсить server name)
- **`tool_input.file_path`** — для recipe-2 (file-protection)
- **`tool_input.new_string`** / **`content`** — для recipe-3 (secrets-scan), там скрипт шукає eval/innerHTML/etc.
- **`tool_input.command`** — для recipe-5 (git-policy), там парситься на force-push pattern

## Як читати exit codes

| Exit code | Сенс |
|-----------|------|
| 0 + порожній stdout | дозволено, hook нічого не робить |
| 0 + JSON у stdout (`hookSpecificOutput.permissionDecision: "deny"`) | дозволено system, але Claude Code блокує дію по structured output |
| 2 + повідомлення у stderr | заблоковано; stderr → Claude як reason |
| інший exit code | non-blocking error (логується, але не показується Claude) |

## Як додати свій тест

1. Створи `payloads/<my-case>.json` з реальним shape'ом event'а (підглянь у `.claude/logs/tool-trace.jsonl` що Claude Code насправді надсилає на твій сценарій)
2. Додай рядок у `run-isolation-tests.sh`:
   ```bash
   run_case "my-hook: blocks foo"  "$HOOKS/my-hook.sh"  "$PAYLOADS/my-case.json"  2  "BLOCKED"
   ```
   Аргументи: label, hook script, payload, очікуваний exit, substring у stderr (або `-` щоб не перевіряти).
3. Запусти `make test-hooks`. Поки PASS — твій hook витримує isolation; live-сесія додасть тільки моделі-специфічні баги (typos у промпті, race conditions тощо)

## Edge case: malformed payload

Усі hooks цього демо безпечно обробляють відсутність полів (повертають `0` без падіння). Це навмисно — Claude Code на різних event'ах надсилає різні shape'и, і hook не має падати з `jq: parse error` коли `tool_input` відсутній. Якщо у твоєму hook'у є `set -e` і `jq -r '.tool_input.file_path'` — додай `// empty` у jq filter, інакше edge case впаде в проді

## Обмеження isolation-тестів

- Не тестують matcher/if dispatch (це робить Claude Code сам — runner просто прокидає payload в hook напряму)
- Не тестують async behavior — runner синхронний
- Не тестують side-effects на файлову систему (recipe-1 auto-format, telemetry POST'и) — для цього потрібна жива сесія або docker sandbox

Це знімає 80% «hook не спрацьовує» — решту 20% ловить live-сесія.
