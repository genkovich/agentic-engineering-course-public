---
name: legacy-cutover
description: Use when running Step 4 of legacy refactoring protocol — writes one use case worth of new code in internal/<module>/, switches DI, ensures pytest stays green, and appends to REFACTOR_LOG.md. Triggers on '/legacy-cutover <module> --usecase=<name>' or when user asks to 'переписати register', 'cutover register', 'переписування у нову папку'.
argument-hint: <module-name> --usecase=<name>
allowed-tools: Read, Write, Edit, Bash, Glob
disable-model-invocation: false
---

# legacy-cutover — Step 4 один атомарний use case за виклик

Пише один use case у `internal/<module>/`, перемикає DI у `apps/api/container.py` (або `server.py`), запускає тести, дописує `REFACTOR_LOG.md`. Один виклик skill = один атомарний коміт.

## Аргументи

- `<module-name>` — імʼя нового модуля (наприклад `account`)
- `--usecase=<name>` — імʼя use case (наприклад `register`, `verify_email`, `reset_password`)

## Стратегії chunking (3 варіанти, обери у PLAN.md)

1. **1 use case = 1 коміт** (default)
   Напр. Register: domain.User + RegisterUseCase + UsersRepo.Insert + EmailSender.SendWelcome — все в одному комміті. Підходить для простих use cases (<200 LOC).
2. **Дрібніше — 4 коміти на use case**
   - Commit 1: `domain/user.py` (entity + sentinel errors)
   - Commit 2: `infra/users_repo.py` (тільки Insert)
   - Commit 3: `app/register_usecase.py`
   - Commit 4: `ports/handler.py` + DI swap
   Підходить коли use case > 200 LOC або коли хочеш дрібніший git bisect.
3. **За HTTP endpoint**
   1 коміт = 1 endpoint (`POST /register` повністю). Підходить коли є contract tests і працюємо contract-driven.

Стратегія для конкретного циклу зафіксована у `PLAN.md` секція 5.

## Inputs

- `PLAN.md` (з `/legacy-plan --phase=finalize`)
- `LEGACY/<module>.md` (як reference)
- `tests/<module>/` (мають бути зелені)

## Output

- Нові файли у `internal/<module>/`
- Зміна одного рядка у `apps/api/container.py` (або `server.py` у демо)
- `REFACTOR_LOG.md` дописаний один рядок
- `PLAN.md` секція «Шматки міграції» — `- [ ]` стає `- [x]`

## Шаблон зміни DI

```python
# server.py або apps/api/container.py
# from internal.users import setup as account_setup       # ← коментуємо
from internal.account import setup as account_setup       # ← новий імпорт
```

Один рядок. Без феверфлагів, без branch-toggle.

## Acceptance criteria

- diff ≤ 500 LOC (інакше skill попереджає «розбий на дрібніше chunking»)
- pytest зелений ДО і ПІСЛЯ
- `REFACTOR_LOG.md` дописаний рядок у форматі `- <date>: <usecase> cutover · <result> · <next>`
- `PLAN.md` секція "Шматки міграції" оновлена: `- [x] <usecase>`
- Жоден файл у `internal/users/**` не змінений (path-rules guard)

## REFACTOR_LOG.md auto-append

Після успішного коміту skill дописує рядок:

```
- 2026-04-16: register cutover · pytest green, latency unchanged · далі verify_email
```

Якщо тест червоний:

```
- 2026-04-16: register cutover · pytest RED — UsersRepo.Insert повертає None · revert
```

## Examples

```
/legacy-cutover account --usecase=register
git log --oneline       # має зʼявитися 1 коміт у internal/account/
pytest                  # все зелене
/legacy-cutover account --usecase=verify_email
/legacy-cutover account --usecase=reset_password
# після останнього use case — окремий коміт на видалення старого
```

## Anti-patterns

- **Не змішуй use cases в одному виклику** — `--usecase=register,verify_email` — погана ідея. Один skill call = один атомарний коміт = один git revert у разі регресії.
- **Не редагуй `internal/users/**` всередині cutover** — path rules заборонять. Якщо потребуєш — це окремий skill (поки не існує).
- **Не закінчуй cutover без оновлення REFACTOR_LOG** — це auto-rule з CLAUDE.md, не «постарайся».
