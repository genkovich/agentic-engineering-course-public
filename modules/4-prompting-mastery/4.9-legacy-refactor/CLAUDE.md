# Project: 4.9 Legacy Refactoring Demo

Демо-проект для лекції 4.9 курсу «Agentic Engineering з Claude». Тут ти проганяєш **протокол з 4 кроками** на legacy users-модулі, переписуючи його у нейтральний `internal/account/` через DI-перемикання.

## Stack

- Python 3.12, FastAPI 0.110, SQLAlchemy 2.0, Pydantic 2
- pytest + hypothesis, import-linter (architectural fitness functions)
- pdm/poetry/pip — будь-який, з `pyproject.toml` працює `pip install -e .`

## Hard Rules — never touch without explicit approval

Це інваріанти проекту. Жорсткі формулювання `DO NOT` навмисно — м'які («уникай», «постарайся») модель легко переоцінює, коли «зараз треба швидко».

### Категорія 1 — Незворотні зміни

- **DO NOT change** `db/migrations/**`
  *Чому:* одна помилка ламає прод-схему, відкат вимагає окремої міграції-зворот. Помилку видно тільки після деплою.
- **DO NOT modify** `apps/common/models.py` (BaseModel)
  *Чому:* предок ВСІХ моделей ORM. Зміна одного поля = масовий ALTER TABLE на всіх таблицях, кілька годин downtime.

### Категорія 2 — Публічні контракти

- **DO NOT change** `apps/api/openapi.yaml`
  *Чому:* мобільні клієнти і CLI парсять цей файл. Зміна signature → клієнти падають у рантаймі, без можливості відкату на їхньому боці.
- **DO NOT bypass** payment idempotency middleware (приклад: `apps/api/middleware/idempotency.py`)
  *Чому:* подвійні платежі = фінансова катастрофа. Цей middleware має бути в ланцюгу для всіх платіжних роутів, без винятків.

### Категорія 3 — Несучі стіни

- **DO NOT modify** `apps/auth/core/**`
  *Чому:* якщо зломити, ніхто не входить у систему. Окремий цикл реалізації, окремий ревью, окремий чек-лист безпеки. Не змішувати з legacy-рефакторингом.

## Steps — один Bounded Context за цикл

1. **Step 1 — scope:** spike (2-4 год) + 4 критерії
   - Запуск: `/legacy-spike <module>`  → артефакт `SPIKE.md`
2. **Step 2 — archeology:** витяг через subagents per-file + помічник-критик
   - Запуск: `/legacy-extract <module>`  → `LEGACY/<module>.md` (6 секцій, ≤2k токенів)
   - Запуск: `/legacy-critic <module>`  → `CRITIC.md` (список тверджень + статус)
3. **Step 3 — план з тестів:** скелет → тести → допис
   - `/legacy-plan <module> --phase=skeleton` → `PLAN.md` з 3 заповненими секціями
   - `/legacy-tests <module>` → `tests/<module>/{contract,characterization,architecture}/`
   - `/legacy-plan <module> --phase=finalize` → `PLAN.md` повний (з зелених тестів)
4. **Step 4 — cutover:** новий код у `internal/<new>/` + DI swap + видалення
   - `/legacy-cutover <module> --usecase=<name>` за один атомарний коміт

Один Step = одна сесія. Між Steps — `/clear`. Контекст їде через файли (`LEGACY/`, `PLAN.md`, `REFACTOR_LOG.md`), не через chat history.

## Session rules

- **Чисті бар'єри замість token-чисел:** не привʼязуйся до «25-30k» або інших чисел. Перевіряй `/context`. Якщо chat history більший за `system + tools + files` — `/clear`.
- **Читай `/context` коли відчуваєш плутанину** (модель повторює, забуває, виходить за scope) — час `/clear`.
- **Plan mode (Shift+Tab двічі) обовʼязковий** для Step 1, Step 2, Step 3 (skeleton+finalize). Step 3 (tests) і Step 4 — Plan mode вимикаємо, бо саме там пишемо файли.

## Auto-rule: REFACTOR_LOG.md

Після кожного атомарного коміту в Step 4 (через `/legacy-cutover`) додай рядок у `REFACTOR_LOG.md` у форматі:

```
- <YYYY-MM-DD>: <action> · <result> · <next>
```

Приклад:

```
- 2026-04-16: register cutover · latency +40ms на staging · revert + diagnose UsersRepo
- 2026-04-17: повернули перемикання · timeout config поправлено · далі verify
```

Якщо `REFACTOR_LOG.md` не існує — створи з заголовком `# REFACTOR_LOG`. Це зобовʼязальне правило, не «постарайся».

## Auto-rule: PLAN.md checklist

Після кожного завершеного шматка міграції стисни рядок у секції `## Шматки міграції` файла `PLAN.md`:
- `- [ ] Register` → `- [x] Register · 2026-04-16 · register cutover green`

## NEVER

- edit legacy paths in-place (`internal/users/**` — read-only)
- read raw old code in main agent (тільки через subagent → `LEGACY/`)
- single big diff > 500 LOC
- skip critic-pass у Step 2 (`CRITIC.md` має існувати перед Step 3)
- v2-суфікси в іменах нових пакетів (`internal/account/`, не `internal/users-v2/`)
- copy-paste промптів — використовуй skills (`.claude/skills/legacy-*`)

## Cross-references

- Лекція 4.4 — формат CLAUDE.md
- Лекція 4.5 — `.claude/rules/` path-scoped правила
- Лекція 4.6 — Plan mode як read-only барʼєр
- Лекція 4.7 — `/context`, `/clear`, файли як носії контексту
- Лекція 4.8 — Bounded Contexts (модуль = BC)
