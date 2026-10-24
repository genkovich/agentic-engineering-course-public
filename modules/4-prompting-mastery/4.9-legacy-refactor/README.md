# 4.9 Legacy Refactoring: чистий старт

Демо-проєкт до уроку **Legacy Refactoring без меж** з курсу «Agentic Engineering».

Це стартовий стан: legacy-модуль `internal/users/` і протокол у `.claude/skills/legacy-*`. Нового модуля `internal/account/` тут ще немає, артефактів процесу (`SPIKE.md`, `LEGACY/account.md`, `CRITIC.md`, `PLAN.md`, `REFACTOR_LOG.md`) теж. Усе це ти створюєш сам, проходячи цикл.

Пройдений цикл лежить поруч, у [`../4.9-legacy-refactor-solution`](../4.9-legacy-refactor-solution). Відкривай його після свого циклу, щоб звірити рішення. Не копіюй звідти файли: тоді тести будуть зелені, а протокол ти так і не пройдеш.

## Що це

Невеликий Python-«моноліт» з users-модулем, зробленим навмисно «спагетті». Код на стандартній бібліотеці: «БД» = `dict` у пам'яті, HTTP-шару немає, DI-точка = `server.py`. Запахи в коді:

- глобальний `cache.recent_signups` для rate-limit без коментаря
- TTL 10 хвилин (`time.time() - 600`) захардкожений у коді
- синхронна `email.send()` блокує запит на 200-400ms
- baseline-тести з anti-patterns (`assert True`, без assertion, мовчазний мок)

`internal/users/` займає близько 200 рядків. У реальному проєкті такий модуль буває на тисячі рядків, але протокол той самий, а цикл на маленькому коді проходиться за вечір-два.

## Як стартувати

Потрібні Python 3.12 або новіший (перевірено на 3.12 і 3.14) і Claude Code.

```bash
git clone https://github.com/genkovich/agentic-engineering-course-public   # якщо репозиторію курсу ще немає
cd agentic-engineering-course-public/modules/4-prompting-mastery/4.9-legacy-refactor
git switch -c legacy-refactor        # працюй на своїй гілці, щоб diff проти main щось показував

python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'              # ставить лише pytest, інших залежностей у коду немає

pytest -q                            # 3 passed: baseline зелений саме тому, що тести-привиди
python server.py                     # App ready. account handlers: ['register', 'verify_email', 'reset_password']
```

З uv те саме одним рядком: `uv run --extra dev pytest -q`.

## Структура

```
.claude/
  rules/legacy-account.md          # path-rules для internal/users, internal/account, tests/account, LEGACY
  skills/
    legacy-spike/SKILL.md          # /legacy-spike <module>
    legacy-extract/SKILL.md        # /legacy-extract <module>
    legacy-critic/SKILL.md         # /legacy-critic <module>
    legacy-plan/SKILL.md           # /legacy-plan <module> --phase=skeleton|finalize
    legacy-tests/SKILL.md          # /legacy-tests <module>
    legacy-cutover/SKILL.md        # /legacy-cutover <module> --usecase=<name>
    legacy-screencast/SKILL.md     # /legacy-screencast <step>, для запису скринкасту, у циклі не потрібен
CLAUDE.md                          # Hard Rules (3 категорії) + Steps + Session rules
apps/
  auth/core/session.py             # Hard Rule: DO NOT modify (несуча стіна)
  common/models.py                 # Hard Rule: BaseModel захищений
  api/openapi.yaml                 # Hard Rule: публічний контракт
db/migrations/0001_initial.sql     # Hard Rule: незворотні зміни
internal/users/                    # legacy target, ~200 рядків
  registration.py                  # validate + insert + email
  verification.py                  # token check + activate (TTL 10хв захардкожено)
  password.py                      # reset_password (sync email)
  reset_password_sync.py           # глобальний cache.recent_signups
  _utils.py                        # хардкоди, magic numbers
tests/test_users.py                # baseline anti-patterns (assert True, no assertion)
server.py                          # DI-точка: setup_app(db) → internal.users.setup(db)
LEGACY/                            # порожня, заповнюється на Step 2
pyproject.toml
```

## Як проходити протокол

Step 1, Step 2 і Step 3 (skeleton, finalize) ідуть у plan mode. Вмикай його через `claude --permission-mode plan` або Shift+Tab, доки у footer не з'явиться `⏸ plan mode on`. У plan mode skill лише досліджує. Файл артефакту з'являється, коли ти схвалюєш план пунктом «Yes, manually approve edits». Схвалення виводить сесію з plan mode, тому на наступному кроці вмикай його знову.

```bash
claude --permission-mode plan
# Step 1: scope
/legacy-spike account                     # → SPIKE.md
# Step 2: archeology (між кроками /clear)
/legacy-extract account                   # → LEGACY/account.md (6 секцій, ≤2k токенів)
/legacy-critic account                    # → CRITIC.md (підтверджені/спростовані)
# Step 3: план з тестів
/legacy-plan account --phase=skeleton     # → PLAN.md (3 секції з 6)
/legacy-tests account                     # → tests/account/{contract,characterization,architecture}/, без plan mode
pytest -q tests/account                   # усе зелене
/legacy-plan account --phase=finalize     # → PLAN.md повний
# Step 4: cutover, без plan mode
/legacy-cutover account --usecase=register
pytest -q                                 # усе зелене
# повторити для verify, reset
```

Після cutover дивись `REFACTOR_LOG.md`: Claude дописує його сам за правилом у `CLAUDE.md`.

## Межі

`.claude/rules/legacy-account.md` вантажиться в контекст, коли Claude читає чи редагує файли з його `paths:`. Це лише текст для моделі, і заборону редагувати `internal/users/` він не забезпечує. Тому після кожного кроку дивись `git status`.
