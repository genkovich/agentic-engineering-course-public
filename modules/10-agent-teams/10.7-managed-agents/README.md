# Demo 10.7 — Managed Agents: агентний harness як API

Той harness, який у 10.6 ми збирали руками (loop із ролями, sandbox, суддя,
пам'ять), Anthropic продає як hosted API-продукт - **Claude Managed Agents**.
Це демо будує один **hosted code-reviewer** і показує його на чотирьох
сценаріях, усі на одному course-репо `review-target/` із посіяним багом.

## Що всередині

```
10.7-managed-agents/
├── common.py            # клієнт + .env + збірка рев'ю-запиту з review-target/
├── setup.py             # крок 0: create agent + environment -> .env (ПЛАТНО, раз)
├── run.py               # #1 session + SSE-стрім: рев'ю course-репо
├── interrupt.py         # #2 user.interrupt + redirect посеред рев'ю
├── outcome.py           # #3 user.define_outcome + grader за rubric.md (КЛІМАКС #1)
├── multiagent.py        # #4 coordinator + треди bug/test/docs (КЛІМАКС #2)
├── rubric.md            # вимірювані критерії для grader-а
├── review-target/       # course-репо з багом подвійного округлення (58.42 vs 58.43)
├── fallback/*.txt       # детерміновані транскрипти під кожен скринкаст
├── screencast-prompts.md
├── Makefile             # install/setup/run/.../parse/fallback; demo-* лише друк
└── requirements.txt     # anthropic (SDK ставить beta-header сам)
```

## Швидкий старт

```bash
cp .env.example .env      # встав ANTHROPIC_API_KEY
make install
make parse                # безкоштовний гейт: усі скрипти парсяться
make setup                # ПЛАТНО, раз: агент + оточення -> .env
make run                  # ПЛАТНО: рев'ю course-репо
```

## Чесні нотатки

- Кожен `python *.py` (окрім `parse`/`fallback`) б'є в hosted Managed Agents API
  і **коштує токенів**. `make setup` створює реальний агент і оточення на боці
  Anthropic. Не ганяй у циклі.
- Вихід агента **недетермінований** - запис може взяти кілька дублів. Страховка -
  `fallback/*.txt`: детермінований транскрипт того самого сценарію.
- `demo-*` цілі Makefile **лише друкують runbook**, вони не запускають скрипти.
- Beta-статус: усе під header `managed-agents-2026-04-01` (SDK ставить сам).
  MCP tunnels і Dreams усередині бети - вужчий research preview (request access).
- Managed Agents stateful за дизайном - не ZDR/HIPAA. Після запису видали тестові
  сесії й завантажені файли через API.
