# CRITIC — account

> Незалежна перевірка `LEGACY/account.md` claim-by-claim проти випадково взятих файлів.

**Перевірено файлів:** 3 з 6 — `registration.py`, `verification.py`, `reset_password_sync.py`
**Дата:** 2026-05-05
**Метод:** critic-subagent читає raw код **до** summary, потім кожне твердження → `confirmed` / `contradicted` / `undetermined`. Секція 6 LEGACY («Що треба для тестів») не перевіряється — це наміри, не факти про код.

## Підтверджені (25)

- `register(email, password, db=None) → {status, user_id, verify_token}` або `{status, error}` · `registration.py:22` + return shapes 31/33/40/46/63
- Error codes `register`: `invalid_email`, `weak_password`, `rate_limited`, `email_taken` · `registration.py:31,33,40,46`
- `verify_email(token, db=None)` з `token_expired`/`token_invalid` · `verification.py:14,22,26`
- `recent_signups: list[float]` як module-level mutable · `reset_password_sync.py:21` — `recent_signups: list[float] = []`
- `send_email(to, body) -> None` живе у `reset_password_sync.py` · `reset_password_sync.py:24`
- `registration.py` імпортує `_utils` — `is_valid_email`, `is_strong_password`, `now_seconds` · `registration.py:14`
- `registration.py` імпортує `reset_password_sync as cache_module` для `recent_signups` і `send_email` · `registration.py:13,36,61`
- `verification.py` імпортує **тільки** stdlib `time`, не імпортує `_utils.TOKEN_TTL_SECONDS` · `verification.py:11`
- TTL `600` як літерал у `verification.py` · `verification.py:21` — `if time.time() - issued > 600`
- TTL дублювання підтверджено коментарем: «Друге місце де ця ж 600 живе — `_utils.TOKEN_TTL_SECONDS`» · `verification.py:6`
- `recent_signups` використовується у `register` для rate-limit · `registration.py:36-41`
- Rate-limit «5 signups/min» з вікном 60с · `registration.py:38-39`
- Rate-limit append+check non-atomic (filter→len→append без локу) · `registration.py:38-41`
- `db = db or {}` default-arg trap · `registration.py:44`, `verification.py:16`
- Mutating `db` in-place у `register` · `registration.py:51-58`
- Mutating `db` in-place у `verify_email` · `verification.py:23-24` — `user["status"]="active"; user["verify_token"]=None`
- Sync `send_email` блокує hot path (sleep, без async/threadpool) · `reset_password_sync.py:27` — `time.sleep(0.001)` з коментарем «у проді 200-400ms»
- `_hash_password = sha256(salt+pw):salt` · `registration.py:17-19` — слабке хешування підтверджено
- `verify_token` повертається у response `register` (security leak) · `registration.py:63`
- Empty-token match: `verify_email("", {"a@x":{"verify_token":""}})` → success · `verification.py:18` — `if user.get("verify_token") == token`
- TTL boundary: `> 600` → 601 expired, 600 ще валідний · `verification.py:21`
- `register` викликає `send_email` синхронно через alias · `registration.py:61` — `cache_module.send_email(email, f"Verify: {verify_token}")`
- Анахронічна назва `reset_password_sync.py` (god-module) · `reset_password_sync.py:1-15` docstring
- Case-sensitive email collision miss · `registration.py:45` — `if email in db:` без `.lower()`
- SMTP exception пропускається наверх (немає try/except навколо `send_email`) · `registration.py:61`, `reset_password_sync.py:24-27`

## Спростовані (0)

(порожньо)

## Невизначені (14)

- `reset_password` signature, «завжди success», user-enumeration захист · причина: `password.py` поза вибіркою
- Re-export через `__init__.py` (`register`, `verify_email`, `reset_password`, `setup`) · причина: `__init__.py` поза вибіркою
- `setup(db) -> dict` з 3 lambda-handlers і closures над `db` · причина: `__init__.py` поза вибіркою
- `password.py` імпортує `reset_password_sync as email_module` · причина: `password.py` поза вибіркою
- Module-level константи у `_utils.py` (`MIN_PASSWORD_LEN=8`, `EMAIL_RE`, `TOKEN_TTL_SECONDS=600`, `SIGNUP_RATE_LIMIT_PER_MIN=5`) · причина: `_utils.py` поза вибіркою (хоча `_utils` імпортується у `registration.py:14`, реалізація — у `_utils.py`)
- Helpers `is_valid_email`, `is_strong_password`, `now_seconds` як приватні `_utils` · причина: `_utils.py` поза вибіркою
- `server.py:17 from internal.users import setup`, `tests/test_users.py:18 from internal.users import *` · причина: файли поза вибіркою
- Token overwrite без інвалідації у `reset_password` · причина: `password.py` поза вибіркою
- Unknown email у `reset_password` НЕ викликає `send_email` (timing leak) · причина: `password.py` поза вибіркою
- `reset_token` записується у локальний `{}` при `db=None` · причина: `password.py` поза вибіркою
- Lambda-closures у `setup` замість `functools.partial` · причина: `__init__.py` поза вибіркою
- Кейс «6-й валідний `register` за 60с → `rate_limited`» · причина: динамічна поведінка, не статичний факт; код узгоджений з твердженням, але не «доказ цитатою»
- `from internal.users import *` як антипатерн у тестах · причина: `tests/test_users.py` поза вибіркою
- LOC counts для `_utils.py` (30) / `password.py` (30) / `__init__.py` (25) · причина: `_utils.py`/`password.py`/`__init__.py` поза вибіркою. (Для `registration.py`/`verification.py`/`reset_password_sync.py` LOC підтверджено — 63/26/28.)

## Verdict

**M = 0 → переходимо до Step 3 ✅**

Жодне твердження `LEGACY/account.md` не спростовано. Невизначені 14 пунктів — обмеження вибірки (3 з 6 файлів), не сигнал недостовірності summary. Якщо у Step 3 (skeleton план) виникне сумнів у конкретному пункті — точково перечитати відповідний файл через subagent.

**Виявлено інваріант для Step 3 contract-тесту:**
- `verification.py` НЕ імпортує `_utils.TOKEN_TTL_SECONDS` → дублювання TTL **гарантоване**, не гіпотеза. У новому модулі `internal/account/` TTL мусить йти з єдиного джерела (`config` чи константа `_utils`), і architecture-тест має це enforce-ити.
