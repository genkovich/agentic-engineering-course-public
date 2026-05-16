# 4.9 Legacy Refactoring Demo

Демо-проект для лекції **4.9 Legacy Refactoring без меж** з курсу «Agentic Engineering з Claude».

## Що це

Невеликий FastAPI-«моноліт» з users-модулем, який зроблено навмисно «спагетті»:

- глобальний `cache.recent_signups` для rate-limit без коментаря
- TTL 10 хвилин (`time.time() - 600`) захардкожений у коді
- синхронна `email.send()` блокує запит на 200-400ms
- baseline-тести з anti-patterns (`assert True`, без assertion, мовчазний мок)

Над цим кодом ти проганяєш **протокол з 4.9** — і через 1-2 дні маєш чисту реалізацію в `internal/account/` із зеленими characterization-тестами і атомарними комітами.

## Як ставити

```bash
cd ~/sources/claude-course-demos/4.9-legacy-refactor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q          # baseline зелений (саме тому що тести-привиди)
```

> Якщо треба — `pip install -e .[dev]` додасть `import-linter` і `hypothesis` для арх-тестів.

## Структура

```
.claude/
  rules/legacy-account.md          # path-rules: users/ read-only → account/ write
  skills/
    legacy-spike/SKILL.md          # /legacy-spike <module>
    legacy-extract/SKILL.md        # /legacy-extract <module>
    legacy-critic/SKILL.md         # /legacy-critic <module>
    legacy-plan/SKILL.md           # /legacy-plan <module> --phase=skeleton|finalize
    legacy-tests/SKILL.md          # /legacy-tests <module>
    legacy-cutover/SKILL.md        # /legacy-cutover <module> --usecase=<name>
    legacy-screencast/SKILL.md     # /legacy-screencast <step>
CLAUDE.md                          # Hard Rules (3 категорії) + Steps + Session rules
apps/
  auth/core/session.py             # Hard Rule: DO NOT modify (несуча стіна)
  common/models.py                 # Hard Rule: BaseModel захищений
  api/openapi.yaml                 # Hard Rule: публічний контракт
db/migrations/0001_initial.sql     # Hard Rule: незворотні зміни
internal/users/                    # ← legacy target (~5K LOC після розширення)
  registration.py                  # validate + insert + email
  verification.py                  # token check + activate (TTL 10хв захардкожено)
  password.py                      # reset_password (sync email)
  reset_password_sync.py           # глобальний cache.recent_signups
  _utils.py                        # хардкоди, magic numbers
tests/test_users.py                # baseline anti-patterns (assert True, no assertion)
server.py                          # entry: setup_app(db) → users.setup(db)
LEGACY/                            # порожня — заповнюється під час Step 2
pyproject.toml
```

## Як проходити протокол

```bash
claude                                    # старт
# Step 1 — scope
/legacy-spike account                     # → SPIKE.md
# Step 2 — archeology
/legacy-extract account                   # → LEGACY/account.md (6 секцій, ≤2k токенів)
/legacy-critic account                    # → CRITIC.md (підтверджені/спростовані)
# Step 3 — план з тестів
/legacy-plan account --phase=skeleton     # → PLAN.md (3 секції з 6)
/legacy-tests account                     # → tests/account/{contract,characterization,architecture}/
pytest -q tests/account                   # все зелене
/legacy-plan account --phase=finalize     # → PLAN.md повний
# Step 4 — cutover
/legacy-cutover account --usecase=register
pytest -q                                 # все зелене
# повторити для verify, reset
```

Після `cutover` дивись `REFACTOR_LOG.md` — Claude дописує його сам за правилом у `CLAUDE.md`.

## Цикл = 1-2 дні. Це ваш перший тренувальний прогін протоколу 4.9.
