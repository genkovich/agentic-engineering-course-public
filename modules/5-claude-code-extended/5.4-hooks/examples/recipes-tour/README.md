# recipes-tour

End-to-end walkthrough всіх 4 рецептів з лекції 5.4 у один прогін. Кожен крок: команда → expected output → посилання на live trigger у `examples/trigger-scenarios/`.

## Як запустити

```bash
# з hooks-toolkit/
make recipes-tour

# або напряму
bash examples/recipes-tour/run-tour.sh
```

Скрипт пройдеться по 4 рецептах послідовно — для кожного: заголовок `Recipe N/4`, payload, hook, stderr, exit code, PASS/FAIL. У кінці — підсумкова таблиця 4/4.

## Що показує

| Крок | Рецепт | Slide | Поведінка | Live trigger |
|------|--------|-------|-----------|--------------|
| 1/4 | Auto-format | 6.1 | PostToolUse + matcher `Edit\|Write` — формат за розширенням, exit 0 | [trigger-auto-format.md](../trigger-scenarios/trigger-auto-format.md) |
| 2/4 | File protection | 6.2 | PreToolUse + exit 2 — блокує `.env` зі stderr `BLOCKED:` | [trigger-protect.md](../trigger-scenarios/trigger-protect.md) |
| 3/4 | Secrets-scan | 6.3 | PreToolUse + Python — блокує `eval()` зі stderr `SECURITY WARNING` | [trigger-secret-scan.md](../trigger-scenarios/trigger-secret-scan.md) |
| 4/4 | Session re-inject | 6.4 | SessionStart matcher=compact — друкує reminders у stdout (=context Claude) | [trigger-session-context.md](../trigger-scenarios/trigger-session-context.md) |

## Чому ця папка існує

Раніше у демо-репо був тільки сам код hooks і trigger-сценарії для двох рецептів (recipe-2, recipe-3). Інші два — recipe-1 і recipe-4 — лежали як файли без шляху від теорії до «спробуй сам». `recipes-tour` закриває цю прогалину:

- **`run-tour.sh`** — автоматичний прогін без живої сесії, бачимо exit codes і stderr/stdout кожного hook'а одразу
- **`README.md`** (цей файл) — індекс trigger-сценаріїв для кожного рецепта; від «прочитав» до «спробував» — один клік
- **зчеплення з isolation runner**: `run-tour.sh` використовує fixtures з `../test-isolation/payloads/` — не дублюємо payload-и

## Як інтерпретувати exit codes (нагадування)

- **exit 0** + порожній stdout → рецепт працює без вторгнення (recipe-1, recipe-2 на чистому файлі, recipe-4 пише у stdout = injects context)
- **exit 2** + stderr → блокування (recipe-2 на `.env`, recipe-3 на eval, recipe-5 на force-push)
- **exit 0** + structured JSON у stdout (`hookSpecificOutput.permissionDecision: "deny"`) → теж блокування, але через JSON (recipe-mcp-allowlist на github)

## Наступний крок після туру

1. **Live live demo** — відкрий `claude` всередині `hooks-toolkit/`, копіпасть промпти з `trigger-*.md` і подивись як той самий рецепт спрацьовує у живій сесії
2. **Адаптуй під свій SaaS** — slide 12 (ADAPT-вправа) має 4 варіанти; найшвидший — Variant A (auto-format із case по розширенню) або Variant D (pre-commit gate на CRUD-комітах)
3. **Розшир `run-tour.sh`** — додай свій recipe-N (custom скрипт) + fixture у `payloads/` і нову `section` функцію виклик; за 5 хвилин маєш живу demo для команди
