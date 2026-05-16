# SPIKE — account

> Step 1 feasibility spike. Legacy `internal/users/` → новий нейтральний `internal/account/`.
> Дата: 2026-05-05.

## 1. Churn (3 місяці)

| File | commits | last touched |
| --- | --- | --- |
| internal/users/registration.py | 1 | 2026-05-05 (init) |
| internal/users/verification.py | 1 | 2026-05-05 (init) |
| internal/users/password.py | 1 | 2026-05-05 (init) |
| internal/users/reset_password_sync.py | 1 | 2026-05-05 (init) |
| internal/users/_utils.py | 1 | 2026-05-05 (init) |
| internal/users/__init__.py | 1 | 2026-05-05 (init) |

Реальної історії немає — це seed-коміт демо-проекту. У реальному репо тут була б матриця «топ-5 файлів за commits» — для нашого циклу це нейтральний сигнал, не блокер.

## 2. Debt indicators

- **LOC у legacy:** 202 (6 файлів)
- **# public functions:** 7 доменних + 1 DI `setup`
  - `register(email, password, db=None)`
  - `verify_email(token, db=None)`
  - `reset_password(email, db=None)`
  - `send_email(to, body)` *(внутрішня, але видима з модуля)*
  - `is_valid_email(email)`, `is_strong_password(pw)`, `now_seconds()`
- **Тестове покриття:** 1 файл `tests/test_users.py` — 33 LOC, 3 test-функції, `from internal.users import *` (антипатерн — приховує реальну поверхню API)
- **TODO/FIXME у коді:** 0 — але `__init__.py` docstring сам визнає три проблеми (глобальний кеш, hardcoded TTL, sync email)

## 3. Isolation

- **Імпортується ззовні:**
  - `server.py:17` — `from internal.users import setup as account_setup` (єдина DI-точка)
  - `tests/test_users.py:18` — `from internal.users import *`
  - `apps/**` — **нічого** (auth/api/common чисті)
- **Глобальні змінні / singletons (за docstring `__init__.py`):**
  - `cache.recent_signups` у `reset_password_sync` *(гіпотеза для критика — підтвердити у Step 2)*
- **Прихована логіка:**
  - `TOKEN_TTL_SECONDS = 600` у `_utils.py` **і** окремо `time.time() - 600` у `verification.py` — два джерела істини
  - `MIN_PASSWORD_LEN = 8`, `SIGNUP_RATE_LIMIT_PER_MIN = 5` — хардкоди констант, не у конфізі
  - sha256+salt для паролів (не bcrypt/argon2) — слабке хешування
  - sync `send_email` у `reset_password` — блокує запит

## 4. Feasibility verdict

**Climbs in 1-2 weeks?** **YES**

Чому YES:
- модуль маленький (202 LOC)
- зовнішня поверхня = одна DI-точка у `server.py` + `from … import *` у тестах
- 3 use case-и, доменна логіка локалізована
- немає cross-module coupling з `apps/auth/core/**` чи `apps/api/**`
- основний ризик — `import *` приховує контракт; characterization-тести у Step 3 закриють це

Rough Bounded Context (public interface):

```
register(email: str, password: str) -> {user_id: str, verify_token: str}
verify_email(token: str) -> bool                         # success / expired
reset_password(email: str) -> {reset_token: str}         # async send
```

Все інше (`is_valid_email`, `is_strong_password`, `now_seconds`, `send_email`) → internal у `internal/account/_utils` чи `infra/email`, **не у public surface**.

## Rough plan

1. **Step 2** — extract 6 файлів через subagents per-file → `LEGACY/account.md` (6 секцій, ≤2k токенів) → `/legacy-critic account` для перевірки гіпотез нижче.
2. **Step 3** — 3 use cases для test plan:
   - contract: register / verify_email / reset_password
   - characterization: edge cases (TTL boundary, weak password, double-signup, email format)
   - architecture: import-linter rule «`internal.account` не імпортує `internal.users`»
3. **Step 4** — 3 chunks (1 use case = 1 атомарний коміт):
   - `register` cutover
   - `verify_email` cutover
   - `reset_password` cutover (з винесенням sync `send_email` у `infra/email` port)

## Гіпотези для Step 2 critic

- [ ] Глобальний `cache.recent_signups` живе у `reset_password_sync.py` (docstring `__init__` стверджує — перевірити)
- [ ] TTL 600s продубльовано: `_utils.TOKEN_TTL_SECONDS` + literal `600` у `verification.py`
- [ ] `password.reset_password` синхронно викликає `send_email` (блокуючий I/O)
- [ ] `from internal.users import *` ховає реальну поверхню — порівняти `__all__` з фактично використаним у тестах
- [ ] Хешування паролів = sha256+salt (не bcrypt/argon2 — слабкість, але **не блокер cutover** — мігруємо as-is, безпеку — окремим циклом)
- [ ] `MIN_PASSWORD_LEN`, `SIGNUP_RATE_LIMIT_PER_MIN` — у `_utils.py` як module-level constants, не з config
