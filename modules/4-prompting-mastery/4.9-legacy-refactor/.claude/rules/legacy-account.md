---
description: Path rules для рефакторингу users → account модуля у циклі 4.9 demo
paths:
  - "internal/users/**"
  - "internal/account/**"
  - "tests/account/**"
  - "LEGACY/**"
---

# Path-scoped rules для циклу users → account

Ці правила вмикаються коли Claude відкриває один з шляхів у списку вище. Поза цим — не діють.

## Read-only paths (main agent НЕ редагує)

- `internal/users/**` — legacy, мігруємо у `internal/account/`. Читання тільки через subagent з виходом у `LEGACY/account.md` ≤2k токенів.
- `LEGACY/*.md` — артефакти Step 2. Пишеш тільки через `/legacy-extract` або `/legacy-critic` skill.

## Write paths

- `internal/account/**` — новий код (домен → app → infra → ports)
- `tests/account/**` — нові тести: `contract/`, `characterization/`, `architecture/`
- `PLAN.md`, `REFACTOR_LOG.md`, `SPIKE.md`, `CRITIC.md` — артефакти процесу

## DI switching

Перемикання реалізації — через `apps/api/container.py` одним рядком:

```python
# from internal.users import setup as account_setup     # старе
from internal.account import setup as account_setup     # нове
```

Один рядок — одна зміна. **Без префіксів `usersv2`, без branch-flags, без feature-flag toggle на цьому етапі.** Feature-flag rollout — окрема тема (лекція 9.10), у демо не використовується.

## Чому нейтральне імʼя `account`, не `users-v2`

`-v2` — лабораторний прийом, який тягне за собою «коли ж буде v3», обовʼязок переіменування і код зі словом «users» по всьому стеку. Беремо нейтральну доменну назву (`account` — більш точно описує що там профіль + автентифікація + reset password) і одразу пишемо у фінальний нейм.

Якщо нейтральна назва не приходить за 5 хвилин — це сигнал що Bounded Context вибраний неправильно. Повертайся у Step 1.
