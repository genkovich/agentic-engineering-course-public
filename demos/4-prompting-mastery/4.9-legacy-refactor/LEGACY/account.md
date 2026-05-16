# LEGACY/account.md

> Архелогічний витяг legacy `internal/users/` (6 файлів, 202 LOC) для cutover у `internal/account/`.
> Дата: 2026-05-05.
> **Стратегія розподілу:** per-file (6 паралельних subagents). Main agent агрегує без читання сирого коду.

## 1. Що модуль робить назовні

**3 доменних use cases + 1 DI entry-point.** Фасад — `internal/users/__init__.py`, який re-export-ує:

| Public callable | Signature | Return shape |
| --- | --- | --- |
| `register` | `(email: str, password: str, db=None)` | `{"status":"success","user_id":hex32,"verify_token":hex32}` або `{"status":"error","error":<code>}` |
| `verify_email` | `(token: str, db=None)` | `{"status":"success"}` або `{"status":"error","error":"token_expired"\|"token_invalid"}` |
| `reset_password` | `(email: str, db=None)` | **завжди** `{"status":"success"}` (навмисний user-enumeration захист) |
| `setup` | `(db) -> dict` | DI: dict з 3 lambda-handlers, у яких `db` захоплений у замиканні |

Error codes для `register`: `invalid_email`, `weak_password`, `rate_limited`, `email_taken`.

**Помічники, які формально приватні (`_utils`), але доступні через імпорт:** `is_valid_email`, `is_strong_password`, `now_seconds`, плюс module-level константи `MIN_PASSWORD_LEN=8`, `EMAIL_RE`, `TOKEN_TTL_SECONDS=600`, `SIGNUP_RATE_LIMIT_PER_MIN=5`.

**Ще одна публічна поверхня — без `__all__`:** `send_email(to, body) -> None` у `reset_password_sync.py` і module-level `recent_signups: list[float]` (mutable!) у тому ж файлі. Імпортується ззовні модуля для rate-limit.

**Зовнішня поверхня для проекту:** `apps/` → нічого; `server.py:17` → `from internal.users import setup`; `tests/test_users.py:18` → `from internal.users import *` (антипатерн — ховає реальний контракт).

## 2. Залежності

**Зовнішні (stdlib only):**
- `hashlib` (sha256 для паролю), `secrets` (`token_hex` для солі/user_id/verify_token/reset_token)
- `time` (`time.time()`, `time.sleep` як заглушка SMTP)
- `re` (compiled `EMAIL_RE`)

**Зовнішні сервіси:**
- SMTP/email-провайдер — згадано у docstring `reset_password_sync.send_email`, але реальний клієнт у коді **не використовується** (зараз `time.sleep(0.001)` як placeholder; у проді — 200-400ms блокуючий sync виклик). Це I/O-port, який ще не виокремлено.

**Внутрішні (cross-file у межах модуля):**
- `registration.py` → `_utils` (`is_valid_email`, `is_strong_password`, `now_seconds`)
- `registration.py` → `reset_password_sync` як `cache_module` (для `recent_signups` і `send_email`)
- `password.py` → `reset_password_sync` як `email_module` (для `send_email`)
- `verification.py` → **тільки** stdlib `time` (не імпортує `_utils.TOKEN_TTL_SECONDS`, хоча docstring на нього посилається — джерело розсинхрону)
- `__init__.py` → `registration`, `verification`, `password` (re-export)

**БД:** немає ORM. `db` параметр — звичайний `dict[email, dict]`, in-memory. Дефолт `db = db or {}` у всіх трьох use cases — викликає silent-loss state при виклику без `db`.

## 3. Сховані звʼязки

- **Глобальний mutable список `recent_signups`** живе у `reset_password_sync.py` на module level. `registration.py` пише туди timestamps для rate-limit (5 signup/min). Process-wide singleton без локу. Memory leak — нічого не очищає; per-process state — не масштабується горизонтально; race на читання+filter (через GIL `append` атомарний, але fenced filter — ні).
- **TTL дублювання:** `_utils.TOKEN_TTL_SECONDS = 600` **і** літерал `600` всередині `verification.py:20` (`time.time() - issued > 600`). Два джерела істини. Зміна тут без зміни там → silent divergence.
- **Sync `send_email` у hot path:** `password.reset_password` синхронно блокує запит на 200-400ms. Те саме у `registration.register` (через alias `cache_module.send_email`). Без retry, без черги, без логів. Exception зі SMTP пропускається наверх — токен у БД є, лист не дійшов.
- **Mutating `db` in-place:** усі три use cases мутують переданий dict на місці без явного return нового стану. Race при shared dict між тредами.
- **Default-arg trap:** `db = db or {}` створює новий dict при кожному виклику без аргументу — `email_taken` перевірка ніколи не спрацює, `reset_token` записується у локальний `{}` що зникає після return, `verify_email("tok")` без db завжди повертає `token_invalid`.
- **Rate-limit append + check non-atomic:** під concurrency 6+ паралельних `register` можуть всі пройти rate-check.
- **Case-sensitive email:** `register("A@B.COM", db={"a@b.com": {...}})` → `success` замість `email_taken`.
- **Token leak у response:** `register` повертає `verify_token` у response (не тільки на email). Out-of-band channel зломаний.
- **Empty-token match:** `verify_email("", db={"a@x": {"verify_token": ""}})` → `success`. Будь-який юзер з порожнім токеном у БД активується першим викликом.
- **Token overwrite без інвалідації:** повторний `reset_password` перезаписує `reset_token` мовчки. Старі токени з листів стають мертвими.
- **`_utils._password = sha256(salt+pw):salt`** — слабке хешування, не bcrypt/argon2. Без `verify_password` функції — як перевіряти при логіні? (логіка живе десь поза модулем).
- **Lambda-closures у `setup`:** захоплюють `db` за reference. Якщо контейнер замінить session — handlers побачать новий стан або зламаються.
- **Анахронічна назва файлу `reset_password_sync.py`:** містить email-хелпер + global cache + (раніше?) reset-логіку. Класичний god-module за назвою.

## 4. Приклади вхід → вихід (10 кейсів через 3 use cases)

**register:**
1. `register("a@b.com", "Strong1!", db={})` → `{"status":"success","user_id":hex32,"verify_token":hex32}` + `db["a@b.com"]` створено + лист (sync) + `recent_signups.append(now)`
2. `register("not-email", "Strong1!")` → `{"status":"error","error":"invalid_email"}` (rate-limit не зачіпається)
3. `register("a@b.com", "123")` → `{"status":"error","error":"weak_password"}`
4. 6-й валідний виклик за 60с → `{"status":"error","error":"rate_limited"}`
5. `register("A@B.COM", db={"a@b.com": {...}})` → `success` (case-sensitive collision miss — баг)

**verify_email:**
6. `verify_email("tok", {"a@x": {"verify_token":"tok","verify_token_issued_at": now}})` → `{"status":"success"}` + `user["status"]="active"`, `verify_token=None`
7. issued_at = now-601 → `{"status":"error","error":"token_expired"}` (рівно 601s)
8. `verify_email("tok")` без `db` → `token_invalid` (default `{}`)
9. `verify_email("", {"a@x": {"verify_token":""}})` → `success` (empty-token trap)

**reset_password:**
10. `reset_password("ghost@x.com", {})` → `{"status":"success"}` (unknown email — навмисно success, але send_email НЕ викликано → timing leak: 200ms vs <1ms)
11. Повторний `reset_password("a@b", db)` → `success` × N, токен перезаписаний, попередній лист мертвий

## 5. Підозріле (гіпотези — для Step 2 critic-pass)

1. **Глобальний `recent_signups` у `reset_password_sync` для rate-limit `register`** — перехресна відповідальність. Гіпотеза: «там вже був список — заіюзаємо», копіпаст без рефакторингу. Critic має підтвердити, що `registration.py` дійсно імпортує `cache_module.recent_signups` для rate-limit.
2. **TTL `600` дубльовано** у `_utils.TOKEN_TTL_SECONDS` і літерал `600` у `verification.py:20`. Гіпотеза: prod-incident hot-fix — захардкодили локально, не імпортували `_utils`. Critic має перевірити, чи дійсно у `verification.py` не імпортується `_utils.TOKEN_TTL_SECONDS`.
3. **Sync `send_email` у hot path** — гіпотеза: ранній продукт без черги; SMTP клієнт ще не був async. Платіжний борг: 200-400ms блокування воркера. Критик підтверджує, що у `reset_password_sync` НЕ робиться async/await і НЕ запускається у threadpool.
4. **`db: dict` замість ORM/Repository** — гіпотеза: in-memory MVP, який ніколи не мігрував. Або тестовий стаб, що засвітився у проді через DI. Critic перевіряє, чи `apps/` десь обгортає dict у адаптер з SQLAlchemy session (мала імовірність — apps зараз порожні від `users`).
5. **`_hash_password = sha256(salt+pw):salt`** — слабке хешування. Гіпотеза: legacy-епохи без passlib/bcrypt. Critic не lifts safety, але фіксує: цей факт **не блокер cutover**, security-upgrade — окремий цикл (лекція 9.X).
6. **`verify_token` у response register** — гіпотеза: тести/QA читали з API, забули прибрати після debug. Або CLI-deeplink. Security-leak.
7. **«Завжди success» у `reset_password` для unknown email** — навмисний user-enumeration захист, але без fake-затримки → timing-attack. Захист напівреалізований.
8. **`from internal.users import *` у тестах** ховає реальну поверхню API. Гіпотеза: автор тестів не хотів думати про що саме потрібно, або тести виросли як smoke до того, як зʼявився `__all__`.
9. **Lambda-closures у `setup` замість `functools.partial`** — гіпотеза: страх, що `partial` ламає introspection FastAPI/Pydantic. Або просто звичка. Lambdas не пікл-яться (важливо для celery/multiprocessing).

## 6. Що треба для тестів

**Fake clock (обовʼязково):**
- `freezegun.freeze_time` або `monkeypatch.setattr("internal.users._utils.time.time", lambda: 1_700_000_000.0)` + те саме на `internal.users.verification.time.time`, `internal.users.password.time.time`. У новому модулі — інʼєктувати `Clock` як port.

**Fake email transport (обовʼязково):**
- `MagicMock` для `internal.users.reset_password_sync.send_email`. Assert called/not_called, capture `(to, body)`, body містить токен.
- Network isolation: `pytest-socket disable_socket` або monkeypatch на `smtplib.SMTP`.

**Cache reset (autouse fixture):**
- `recent_signups[:] = []` перед кожним тестом, інакше state тече між кейсами.

**Random control:**
- `monkeypatch.setattr("secrets.token_hex", lambda n: "a"*n*2)` для детермінованих `user_id`/`verify_token`/`reset_token`/`salt` у contract-тестах.

**Fixtures:**
- `db_empty` — `{}`
- `db_with_user(email, **kwargs)` — фабрика
- `frozen_time(t)` — обертка над `freeze_time`

**Contract tests** (Step 3.2 — `tests/account/contract/`):
- Точні return shapes для всіх 3 use cases × happy + error paths
- `send_email` called/not_called під відповідні гілки
- `__all__` стабільний, re-export identity (`internal.users.register is internal.users.registration.register`)

**Characterization tests** (Step 3.2 — `tests/account/characterization/` — фіксують поточну поведінку as-is):
- TTL boundary: 599s/600s/601s
- Empty-token match (зафіксувати як known-defect перед cutover)
- Case-sensitive email collision miss
- `db=None` → silent state loss
- Concurrent register × 10 → race на rate-limit (skip у unit, integration-only)
- SMTP exception у `reset_password` пропускається наверх
- Unknown email у `reset_password` НЕ викликає `send_email`

**Architecture tests** (Step 3.2 — `tests/account/architecture/`, import-linter):
- `internal.account` НЕ імпортує `internal.users` після cutover
- `internal.account.domain` НЕ імпортує `infra` (порти+адаптери)
- `apps.api.container` — єдиний legitimate caller `setup`

**Property-based (hypothesis):**
- Будь-який `token: str` без матчу у `db` → завжди `token_invalid`
- Будь-який `issued_at < now - 600` → завжди `token_expired`

**Env:** жодних env vars не читається у legacy. SMTP/DB URL — не потрібні для unit. Для integration — fake SMTP (`aiosmtpd` або `MailHog`).

---

**Source files (для критика):**
- `internal/users/__init__.py` (25 LOC)
- `internal/users/_utils.py` (30 LOC)
- `internal/users/registration.py` (63 LOC)
- `internal/users/verification.py` (26 LOC)
- `internal/users/password.py` (30 LOC)
- `internal/users/reset_password_sync.py` (28 LOC)
