# Trigger: file-protection (recipe-2)

## Промпт для Claude (копі-паст)

> Створи у поточній директорії файл `.env` з такими змінними:
> `DATABASE_URL=postgres://user:pass@localhost:5432/db` і
> `OPENAI_API_KEY=sk-fake-xxxx`.
> Потім додай у нього коментар на першому рядку.

## Що має статись

1. Claude викличе `Write` (або `Edit`) на `.env`.
2. PreToolUse hook `recipe-2-protect-files.sh` спрацює, бо matcher = `Edit|Write`.
3. Скрипт побачить case `*.env`, виведе у stderr:
   ```
   BLOCKED: edits to .env files are not allowed (recipe-2-protect-files).
   Reason: env files contain secrets. Use settings.local.json.example as template.
   ```
4. Exit 2 → Claude Code не виконає Write і поверне Claude цей stderr як reason.
5. Claude скаже у відповіді: «не можу записати у .env, тому що hook заблокував».

## На чому акцентувати у скринкасті

- **PreToolUse — найважливіший hook** (slide 6.2): дозволяє блокувати ДО виконання.
- Stderr stack — точне джерело правди для Claude (slide 5).
- Exit code 2 — простіший за structured JSON, але обмежений: тільки `block + stderr-as-reason`.

## Очищення

Жодного — `.env` не створиться, бо hook заблокував саме `Write`.
