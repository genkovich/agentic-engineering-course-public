# PLAN — account

> Step 3 finalized. Секції 1-3 — з `SPIKE.md` + `LEGACY/account.md` + `CRITIC.md`.
> Секції 4-6 — з зелених тестів `tests/account/` (43 passed, 5 skipped).
> Дата skeleton: 2026-05-05 · Дата finalize: 2026-05-06.

## 1. Чому цей модуль ✅ (з SPIKE.md)

- **module:** `account` (нейтральна доменна назва замість `users-v2`)
- **критерії:**
  - **churn** = 1 коміт init (seed демо-проекту, реальної історії немає → нейтральний сигнал)
  - **debt** = 4 фактичні борги, підтверджені критиком: TTL дубльовано (`_utils.TOKEN_TTL_SECONDS` + літерал `600` у [verification.py:21](internal/users/verification.py#L21)), глобальний mutable `recent_signups` у [reset_password_sync.py:21](internal/users/reset_password_sync.py#L21), sync `send_email` у hot path ([reset_password_sync.py:27](internal/users/reset_password_sync.py#L27)), `_hash_password = sha256(salt+pw):salt` ([registration.py:17-19](internal/users/registration.py#L17-L19))
  - **isolation** = одна DI-точка ([server.py:17](server.py#L17)) + `from internal.users import *` у [tests/test_users.py:18](tests/test_users.py#L18); `apps/auth/core/**`, `apps/api/**`, `apps/common/**` не імпортують legacy → cross-module coupling нульовий
  - **spike verdict** = **YES** (climbs in 1-2 weeks)
- **скільки часу:** 1-2 тижні людського часу (3 use cases × 1 атомарний коміт + characterization-тести як fix point)

## 2. Що будуємо ✅

```
internal/account/
├── domain/
│   ├── user.py              # User entity (frozen dataclass): email, password_hash, status, verify_token, verify_token_issued_at, reset_token, reset_token_issued_at
│   └── errors.py            # sentinel errors: InvalidEmail, WeakPassword, RateLimited, EmailTaken, TokenExpired, TokenInvalid
├── app/
│   ├── register.py          # RegisterUseCase: orchestrate validation → hash → repo.insert → email.send_verify → rate_limit.append
│   ├── verify_email.py      # VerifyEmailUseCase: repo.find_by_token → check TTL з єдиного джерела → repo.activate
│   └── reset_password.py    # ResetPasswordUseCase: repo.find_by_email → (if found) generate token → repo.set_reset → email.send_reset; завжди return success
├── infra/
│   ├── users_repo.py        # UsersRepo port + InMemoryUsersRepo adapter (дзеркалить dict-shape legacy для backward-compat)
│   ├── password_hasher.py   # PasswordHasher port + Sha256SaltHasher adapter (формат "<sha256_hex>:<salt>" — як у legacy, security-upgrade окремим циклом)
│   ├── rate_limit.py        # RateLimitStore port + InMemoryRateLimitStore (замінює global recent_signups)
│   ├── email_sender.py      # EmailSender port + SyncEmailAdapter (sync as-is — async/queue окремий цикл)
│   └── clock.py             # Clock port + SystemClock adapter (заміна неявного time.time())
└── ports/
    ├── handler.py           # setup(db) → dict[str, Callable] — DI entry, контракт legacy збережено байт-у-байт
    ├── dto.py               # response shapes: SuccessRegister, SuccessVerify, SuccessReset, ErrorResponse — TypedDict для документації
    └── errors.py            # mapping domain → API codes (InvalidEmail → "invalid_email", тощо)
```

**Public interface (без змін, контракт з [LEGACY/account.md](LEGACY/account.md) §1):**

| Public callable | Signature | Return shape (зберігається байт-у-байт) |
| --- | --- | --- |
| `register` | `(email: str, password: str, db=None) -> dict` | `{"status":"success","user_id":hex32,"verify_token":hex32}` або `{"status":"error","error": "invalid_email"\|"weak_password"\|"rate_limited"\|"email_taken"}` |
| `verify_email` | `(token: str, db=None) -> dict` | `{"status":"success"}` або `{"status":"error","error":"token_expired"\|"token_invalid"}` |
| `reset_password` | `(email: str, db=None) -> dict` | завжди `{"status":"success"}` (навмисний user-enumeration захист) |
| `setup` | `(db) -> dict[str, Callable]` | DI entry: 3 handlers, як у legacy `__init__.setup` |

**DI swap point:** [server.py:17](server.py#L17) — рівно один рядок зміни:

```python
# from internal.users import setup as account_setup    # старе
from internal.account import setup as account_setup    # нове
```

(Path-rule згадує `apps/api/container.py` як цільову конвенцію; у поточному демо-репо роль контейнера виконує `server.py` — туди й ставимо swap. Виокремлення у `container.py` — поза скоупом цього циклу.)

## 3. Що НЕ чіпаємо у цьому циклі ✅

(з `CRITIC.md` "невизначені" + LEGACY §5 + path-rule «без префіксів v2, без feature-flag»)

- **Слабке хешування паролів** (`sha256(salt+pw):salt`) — причина: legacy-епохи без passlib/bcrypt, контракт hash-формату експортовано у persistent storage; зміна формату ламає логін. **Окремий цикл (security-upgrade, лекція 9.X)**: bcrypt/argon2 + міграційна стратегія (re-hash on next login).
- **`verify_token` у response `register`** — security leak (мав би бути out-of-band only). Причина: гіпотеза «тести/QA читали з API, забули прибрати після debug». Зберігаємо байт-у-байт у response, інакше зламаються зовнішні клієнти. **Окремий цикл (API contract change з deprecation window).**
- **User-enumeration timing leak у `reset_password`** — unknown email повертає миттєво, known — 200-400ms (sync `send_email`). Причина: захист напівреалізований. **Окремий цикл (constant-time response: fake delay або async-only).**
- **SMTP exception пропускається наверх** (немає try/except навколо `send_email`) — токен у БД є, лист не дійшов. Причина: ранній продукт без черги/retry. **Окремий цикл (queue + retry + observability, лекція 9.Y).**
- **Empty-token match** у `verify_email` (`""` матчить `""`) — known defect. Зафіксуємо у characterization-test як «поведінка as-is». **Окремий цикл (`if not token: return token_invalid` як guard).**
- **Case-sensitive email collision miss** (`A@B.COM` не матчить `a@b.com` у `email_taken`) — known defect. Зафіксуємо у characterization-test. **Окремий цикл (email normalization у домені).**
- **Rate-limit non-atomic** (filter→len→append без локу — race на 6+ паралельних `register`) — known defect. Зафіксуємо у characterization (skip у unit, integration-only). **Окремий цикл (Redis INCR або DB-lock з TTL).**
- **Token overwrite без інвалідації у `reset_password`** — повторний reset перезаписує `reset_token` мовчки, попередній лист мертвий. Зафіксуємо у characterization. **Окремий цикл (token versioning або revocation list).**
- **Sync `send_email` у hot path** — 200-400ms блокування. Інкапсулюємо за портом `EmailSender` у `infra/email_sender.py`, але реалізація лишається sync-as-is. **Окремий цикл (async + черга — Celery/RQ/SQS).**
- **`db: dict` контракт замість ORM** — legacy використовує `dict[email, dict]` як «базу». Зберігаємо контракт через `InMemoryUsersRepo`, який дзеркалить shape. **Окремий цикл (SQLAlchemy + alembic міграція + repository pattern на ORM).**
- **Lambda-closures у `setup`** замість `functools.partial` — не блокер cutover, дзеркалимо як є для контракту. **Окремий цикл (якщо буде потреба у pickle/celery).**
- **`from internal.users import *` у [tests/test_users.py:18](tests/test_users.py#L18)** — антипатерн ховає реальну поверхню. Замість того, щоб правити legacy-тести, **переписуємо їх у `tests/account/`** з явним імпортом. Старий `tests/test_users.py` видаляється на Step 4 разом із `internal/users/`.

**Що ЧІПАЄМО у цьому циклі (не плутати з «не чіпаємо»):**
- TTL `600` дублювання — у `internal/account/` ОДНЕ джерело (`domain/config.py` чи константа `_utils`), плюс architecture-test enforce-ить, що `app/verify_email` НЕ містить літерала `600` і бере значення з єдиного джерела.

## 4. Поведінка яку зберігаємо ✅ (з зелених тестів)

> Джерело: `pytest tests/account/` — 43 passed, 5 skipped (architecture, активуються після cutover). Кожен пункт нижче = 1 тест-кейс. Знак ⚠️ = known defect, навмисно зберігається до окремого cleanup-циклу.

### Public surface — contract (12)

- `account.setup(db)` повертає dict з рівно 3 callable: `register`, `verify_email`, `reset_password`
- Модуль re-export-ує імена `register`, `verify_email`, `reset_password`, `setup`
- `register` success shape: `{"status":"success","user_id":hex32,"verify_token":hex32}` — рівно ці 3 ключі
- `register` error `invalid_email`: `{"status":"error","error":"invalid_email"}`
- `register` error `weak_password`: `{"status":"error","error":"weak_password"}`
- `register` error `email_taken`: при повторному реєстрі того ж email
- `verify_email` success shape: `{"status":"success"}` (без зайвих ключів)
- `verify_email` `token_invalid` shape для невідомого токена
- `verify_email` `token_expired` shape після 601с
- `reset_password` для known email → `{"status":"success"}`
- `reset_password` для unknown email → `{"status":"success"}` (user-enumeration захист)
- `register` error-коди — closed set: `{invalid_email, weak_password, rate_limited, email_taken}`

### Register — characterization (15)

- `register` happy path → user dict у db має ключі `{id, email, password, status, verify_token, verify_token_issued_at}`, `password = "<sha256_hex>:<salt_hex>"`, `status = "pending"`
- `register` happy path → `send_email(to, body)` викликаний 1×, `body` містить `verify_token`, `to` = email
- Validation order (9 parametrize-кейсів):
  - `("not-email","weak")` → `invalid_email` *(invalid email перевіряється раніше за weak password)*
  - `("not-email","Strong1A")` → `invalid_email`
  - `("","Strong1A")` → `invalid_email`
  - `("a @b.com","Strong1A")` → `invalid_email` (пробіл заборонений)
  - `("a@b.com","weak")` → `weak_password`
  - `("a@b.com","abcdefgh")` → `weak_password` (без цифри)
  - `("a@b.com","12345678")` → `weak_password` (без літери)
  - `("a@b.com","a1")` → `weak_password` (закоротко, < 8)
  - `("a@b.com","")` → `weak_password`
- `email_taken` для exact-match повторного email (case-sensitive)
- ⚠️ `email_taken` НЕ спрацьовує для `A@B.COM` vs `a@b.com` (case-sensitive collision miss)
- Rate-limit: 6-й валідний `register` за 60с → `rate_limited`
- Rate-limit window resets після 60с
- Rate-limit НЕ рахує невалідні (invalid_email/weak_password не їдять бюджет)
- `register` happy path → `recent_signups` (global) збільшується на 1
- ⚠️ `register("...", db={})` (порожній dict — falsy) → return success, але caller's `db` лишається `{}` (silent state loss через `db = db or {}`)

### VerifyEmail — characterization (8)

- Happy path → `db[email]["status"] = "active"`, `db[email]["verify_token"] = None`
- Reused token after first success → `token_invalid` (бо verify_token обнулено)
- TTL boundary (5 parametrize-кейсів):
  - `0s` offset → `success`
  - `599s` → `success`
  - `600s` (рівно межа) → `success` (умова `> 600`, не `>= 600`)
  - `601s` → `token_expired`
  - `3600s` → `token_expired`
- Unknown token → `token_invalid`
- ⚠️ Empty token `""` матчить юзера з `verify_token == ""` → `success` + status стає `active` (empty-token trap)

### ResetPassword — characterization (4)

- Known email → `db[email]` отримує `reset_token` (32 hex chars) + `reset_token_issued_at` (float)
- Known email → `send_email` викликаний рівно 1× з `to = email`
- ⚠️ Unknown email → success, але `send_email` НЕ викликаний → timing leak (200-400ms vs миттєво)
- ⚠️ Повторний `reset_password` перезаписує `reset_token` — попередній лист стає мертвим (token overwrite)

### Architecture — invariants для нового модуля (5, skip до cutover)

- `internal.account` пакет існує після cutover
- `internal.account` НЕ імпортує `internal.users` (інакше cutover не cutover)
- `internal.account.domain` НЕ імпортує `internal.account.{infra,app,ports}`
- `internal.account.app` НЕ імпортує `internal.account.infra` (тільки через ports)
- Літерал `600` ЗАБОРОНЕНО у `internal.account.app.*` — TTL мусить йти з єдиного джерела (config/domain)

## 5. Шматки міграції ✅

Стратегія: 3 use cases + 1 cleanup = 4 атомарні коміти. Кожен use-case-коміт:
1. Пише новий код у `internal/account/` (`domain` → `infra` → `app` → `ports`)
2. Свопає ОДНУ lambda у `setup_app` ([server.py:17](server.py#L17)) — інші use cases поки що legacy (hybrid `setup_app`)
3. `pytest tests/account/` — має лишатися зеленим (architecture-тести до cleanup-коміту лишаються `skip`-нутими, бо `internal.account` тільки частково готовий)
4. Запис у `REFACTOR_LOG.md` після `git commit`

- [x] **Register** · 2026-05-06 · `domain.{user, errors, ports, config}` + `infra.{InMemoryUsersRepo, Sha256SaltHasher, LegacyBackedRateLimitStore, LegacyBackedEmailSender, LegacyBackedClock}` + `app.RegisterUseCase` + `ports.handler.setup_register` + hybrid `setup_app` у `server.py`. **Note:** infra-адаптери зараз `LegacyBacked*` — транзитивно делегують до `internal.users.{reset_password_sync, _utils}` для збереження сумісності з фікстурами (`recent_signups`, `send_email`, `frozen_time`). Cleanup-коміт замінить на приватні реалізації. Acceptance: 50 passed + 1 skip (hybrid-skip `test_account_does_not_import_legacy_users` — by design до cleanup).
- [ ] **VerifyEmail** · 1 атомарний коміт · `domain.errors.{TokenExpired, TokenInvalid}` + `app.VerifyEmailUseCase` + `infra.UsersRepo.{find_by_token, activate}` (розширення з Register-коміту) + swap `verify_email` lambda. Acceptance: 8 verify characterization + TTL живе у domain config (architecture-тест `no_literal_600` готовий зеленіти, але ще skip бо `internal.account.app` неповний).
- [ ] **ResetPassword** · 1 атомарний коміт · `app.ResetPasswordUseCase` + `infra.UsersRepo.{find_by_email, set_reset_token}` + `infra.EmailSender.send_reset` + swap `reset_password` lambda. Acceptance: 4 reset characterization. Після цього коміту `setup_app` повністю на новому модулі.
- [ ] **Cleanup** · 1 атомарний коміт · видалити `internal/users/` + `tests/test_users.py` (legacy ghost-baseline) + видалити `from internal.users import setup as legacy_setup` з `server.py` + оновити `tests/account/conftest.py` (`ACCOUNT_MODULE = "internal.account"`, `_PATCH_PATHS` → нові шляхи). Acceptance: 5 architecture-тестів стають PASSED (не skip), pytest = 48 passed, 0 skipped.

**Якщо use-case-коміт > 500 LOC** (CLAUDE.md ліміт) — розбити на pre-commit (infra-адаптери + домен) + use-case-коміт (app + swap). Кожна частина — окремий атомарний коміт.

## 6. Відкат ✅

Кожен коміт — атомарний, відкат = повернення стану до попереднього коміту. Жодних feature-flag, branch-by-abstraction вистачає (hybrid `setup_app` природно підтримує обидві реалізації одночасно під час циклу).

| Чанк зламається | Дія | Час до відкату |
| --- | --- | --- |
| **Register** | `git revert <register-cutover-hash>` — повертає `register` lambda на legacy у `setup_app`; новий код у `internal/account/` лишається мертвим, але не заважає (DI до нього не йде). Альтернатива: вручну повернути одну lambda у `setup_app` без revert (зберігає `internal/account/` як WIP для допилу). | < 5 хв |
| **VerifyEmail** | Те саме, що Register. `git revert <verify-cutover-hash>`. | < 5 хв |
| **ResetPassword** | Те саме. `git revert <reset-cutover-hash>`. | < 5 хв |
| **Cleanup** | Найризикованіший — повертає `internal/users/` із git history. `git revert <cleanup-hash>` + перевірити, що conftest swap-точки знов вказують на `internal.users.*`. **Не робити Cleanup поки 3 use-case-коміти не «обкатані» ≥1 день у staging.** | 10-15 хв (через conftest revert) |

**REFACTOR_LOG.md** після кожного коміту (формат з CLAUDE.md):

```
- 2026-05-08: register cutover · 43 passed на staging · далі verify_email
- 2026-05-09: verify_email cutover · 43 passed · далі reset_password
- 2026-05-10: reset_password cutover · 43 passed · далі cleanup після обкатки
- 2026-05-12: cleanup · 48 passed (architecture green) · цикл завершено
```

При відкаті — додатковий рядок з `revert + diagnose`:

```
- 2026-05-08: register cutover · latency +40ms на staging · revert + diagnose UsersRepo
- 2026-05-09: повернули перемикання · timeout config поправлено · далі verify
```
