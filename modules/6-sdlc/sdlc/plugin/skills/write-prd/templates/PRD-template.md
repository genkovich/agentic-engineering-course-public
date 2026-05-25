---
status: Draft
owner: "<заповни з idea-brief frontmatter owner>"
reviewers: ["Tech Lead", "Security Lead"]
updated_at: "<сьогодні YYYY-MM-DD>"
feature_size: <з classify-size output: XS/S/M/L/XL>
stage: "03"
ticket: "<TBD>"
---

# PRD — <slug>

<!-- Skill instruction: посилання на required inputs + перелік selected additional channels через відносні шляхи або джерела. Format:

> **Inputs (required):** [idea-brief](./idea-brief.md) · [CONTEXT](./CONTEXT.md)
> **Reference module:** `internal/modules/<name>` — code patterns used (error codes, authz, status transitions). Якщо --reference не передано або user declined — пиши «N/A — green-field mode».
> **External context channels used:** перелічи selected channels з step-3 AskUserQuestion: «MCP-Atlassian: Confluence page "X", Jira ticket Y-123», «Project docs: docs/architecture/auth.md», «Projects knowledge: business-rules.md», або «None — only CONTEXT + idea-brief».

Не згадуй brainstorm або initiatives artifacts — це не inputs PRD. -->

## 1. Context

<!-- Skill instruction: 3-4 параграфи.
Параграф 1: Що вирішуємо. Витягни з idea-brief §2 Problem — конкретно, без abstraction. Цитуй segment з §3 Users.
Параграф 2: Чому зараз. Витягни з idea-brief §2 «Why now» / triggers (incident, contract, deadline).
Параграф 3: Прийнятий вектор — recommendation з idea-brief §13. 1-2 речення.
Параграф 4 (якщо було використано additional channels у step 3-4): Reference module patterns АБО quoted external sources як **traceability context для §1**, не для §5 AC. Конкретно: «existing similar module uses authz pattern X» / «business rule from Confluence page Y» / «historical decision: cross-org hides existence». Ці reference-patterns **не пробігають** у §5 AC — §5 описує business-observable outcome без HTTP/error-code/schema (див. §5 instruction нижче).
Параграф 4 також — місце для «Decision overrides» bullets, які emit-ить Phase 7.5 critic: коли критик знаходить contested decision, а user обрав `Override`, додай bullet формату «<finding-headline> — overridden by author, rationale: <reason>» для traceability downstream.
Wikilinks: [idea-brief](./idea-brief.md), [CONTEXT](./CONTEXT.md).
Без архітектурних рішень — це WHAT+WHY, не HOW. Не згадуй Redis/Postgres/JWT тут.
Не згадуй brainstorm або initiatives artifacts — це outside scope. -->

## 2. Goals

<!-- Skill instruction: 2-3 виміряні outcomes у форматі bullet list.
Кожна goal — це прояв recommendation з idea-brief §13. Cite §13 directly. Без brainstorm/initiatives reference.
Формат: «<strategic outcome>, <quantifier if obvious — e.g. "одним кліком", "без ручного пошуку">».
Без чисел тут ОК — числа у §7 KPIs. Тут — strategic outcome.

Приклад:
- Editor публікує article одним кліком, без ручної перевірки чи sections непорожні (валідація на бекенді).
- Editor бачить усі drafts своєї команди у єдиному списку. -->

## 3. Non-goals

<!-- Skill instruction: 3-4 явні non-goals у bullet list.
Кожен non-goal: одне речення + причина (з idea-brief §6 Out of scope). Без посилань на parked initiatives — джерело тільки idea-brief §6.
Формат: «- <non-goal>, <причина з idea-brief §6 або власне обґрунтування PM/Tech Lead на review».»

Приклад:
- Видалення published article — у v2 через архівацію, бо неможливо безпечно видалити з активними downstream-посиланнями.
- Кросс-team портативність — out of scope, кожна team має ізольовані articles. -->

## 4. User stories

<!-- Skill instruction: ≥5 user stories, без верхнього cap. Skill пропонує стільки, скільки треба, щоб усі ролі з CONTEXT glossary + усі goals з §2 покриті. Формат:

### US-NN: <короткий title>
**As a** <role з CONTEXT glossary>
**I want** <action>
**So that** <observable benefit>

Roles тільки ті що у CONTEXT (наприклад `<role-A>`, `<role-B>`, `<role-C>` — не "user", не "admin" якщо не у glossary).
Кожна US — від recommendation з idea-brief §13 + role patterns з reference code (якщо reference channel selected — хто має CRUD permissions у reference module).
Title 3-6 слів, описує дію не сутність («Publish a course version», не «Course publishing»).
Кожна US покривається ≥1 AC у §5. -->

### US-01: <title>

**As a** <role>
**I want** <action>
**So that** <benefit>

### US-02: <title>

**As a** <role>
**I want** <action>
**So that** <benefit>

## 5. Acceptance criteria

<!-- Skill instruction: ≥1 AC кожного з 5 coverage types (happy / error / authz / domain invariant / cross-context), без верхнього cap. Skill пропонує стільки, щоб усі US покриті ≥1 AC + усі 5 типів представлені. Формат:

### AC-NN (US-XX) — короткий title типу покриття
**Given** <business preconditions: actor-у роль, стан його domain-об'єктів, попередні події>
**When** <business action від actor-perspective: "<role> attempts to <verb> <domain-object>" або "<role> opens <UI-context>">
**Then** <observable business outcome: actor sees X / system blocks Y and explains Z / system records W>

AC описує **business-observable outcome від actor's perspective**. Не HOW системa це робить.

**ЗАБОРОНЕНО у §5 AC text** (zero tolerance — перевіряє Phase 7.5 critic F6 + pre-write regex scan):
- HTTP verbs/methods (`GET`/`POST`/`PUT`/`PATCH`/`DELETE`).
- URL paths (`/courses`, `/lessons/{id}`, `/api/v1/...`).
- Status codes як bare numerics у тілі AC (`200`/`201`/`400`/`403`/`404`/`409`/`5xx`).
- Error-code strings формату `[a-z_]+\.[a-z_]+` (наприклад `course.not_methodist`, `validation.description_too_long`).
- JSON-schema fragments / payload bodies (`{key: "value"}`).
- SQL / DB constructs (`UNIQUE`, `FK`, `pq.*`, raw SQL, constraint names).

Технічний mapping (HTTP method+endpoint+payload, status codes, error-code strings, schemas, DB constraints) живе у stage 09 (`sdlc:define-api`) + stage 10 (`sdlc:decide-adr`). Тут — тільки WHAT actor спостерігає.

Дозволено у AC text: roles з CONTEXT glossary, domain invariant **names** (наприклад «no published lessons», «unique sequence per course»), domain-objects з glossary.

5 типів покриття обов'язкові (хоча б по 1 кожного):
1. **happy** — actor виконує main flow → system records the outcome and confirms (без status code, без endpoint).
2. **error** — actor подає невалідний input → system blocks the action and explains the reason to the actor (без HTTP-коду, без error-code-string; формулюй як «system shows actor that <field> must be <constraint>»).
3. **authorization** — actor lacks permission (cross-org / cross-role / not-owner) → system denies access OR hides existence. Rationale у business terms: «system hides existence to avoid leaking that the object belongs to another team» — без слів «404»/«403».
4. **domain invariant** — actor attempts an action that violates a named invariant (наприклад «course cannot be published with zero lessons», «sequence must be unique per course») → system blocks the action and names the invariant in plain language (без error-code-string, без `409`).
5. **cross-context** — actor's action depends on state in another bounded context (membership, parent-child relation) → system enforces the cross-context rule (наприклад «system requires the lesson to belong to a draft course owned by the actor»).

Кожен AC tagged з US-NN. Якщо у когось є race condition / concurrent edge — додай як AC-NNb (subletter), все ще у business-language. -->

### AC-01 (US-01) — happy path

**Given** an authorized <role> owns a draft <domain-object>
**When** the <role> attempts to publish the <domain-object>
**Then** the system records the <domain-object> as published and confirms to the <role>

### AC-02 (US-01) — domain invariant violation

**Given** an authorized <role> owns a draft <domain-object> with no child <sub-objects>
**When** the <role> attempts to publish the <domain-object>
**Then** the system blocks the publication and tells the <role> that at least one <sub-object> must be published first

## 6. Non-functional requirements

<!-- Skill instruction: таблиця, recommended list, без верхнього cap.
Колонки: Aspect | Target | Measurement.
Targets — ЧИСЛОВІ (≤250ms, ≥30 req/s, 99.9%). Без прикметників ("fast", "high").
Measurement — конкретна метрика з прода (наприклад API-метрика endpoint name, як у reference module).
Якщо число невідоме → TBD з owner+due у §8 Open Questions, а не «fast».

Рядки які майже завжди потрібні (recommended floor, не cap):
- Latency p95 для головного write endpoint
- Latency p95 для головного read endpoint (list)
- Throughput на 1 інстанс (k6 smoke у CI)
- Availability (наслідує API SLO)
- Concurrency safety або точність (якщо feature має race conditions або вимірюваність — наприклад seek drift) -->

| Aspect | Target | Measurement |
|---|---|---|
| Latency p95 <operation> | ≤ <N ms> | <endpoint metric name> |
| Latency p95 <list operation> | ≤ <N ms> | <endpoint metric name> |
| Throughput | ≥ <N req/s> на 1 інстанс | k6 smoke у CI |
| Availability | 99.X% | місячне SLO-вікно |
| <Concurrency / Accuracy> | <safety guarantee> | <how enforced> |

## 6.1 Security / privacy

<!-- Skill instruction:
- **Data classification:** public / internal / confidential / regulated (одне слово + 1 речення rationale).
- **Personal data touched:** жодного нового поля АБО список нових полів з типом + sensitivity.
- **AuthZ/AuthN impact:** які endpoint-групи додаються, які check-и виконує repo / middleware (наприклад «repo завжди фільтрує org_id = current_user.org_id», «middleware вимагає JWT»).
- **Abuse cases (3-5):**
  1. **Cross-org доступ** — який response (403 чи 404), посилання на rationale якщо обираємо неконвенційний (404 для hide-existence).
  2. **Draft-leak** — як ховаємо чернетки від не-власників (filter at repo, not at handler).
  3. **SSRF / injection через URL/text поля** — який allowlist / escape (тільки якщо feature приймає URL).
  4. **Spam create** — rate limit на скільки req/min/user (наприклад 60/min на POST).
  5. **(опціонально) Token misuse** — JWT rotation / scoping якщо feature додає нові scopes.
- **Security review verdict:** Required (M+ або нові authz boundaries або нові PII поля) / N/A з конкретним reason (S-size, internal, без нових PII).
Якщо обираємо response code не як у reference module — додай 1-2 речення trade-off (наприклад чому 404 а не 403). -->

- **Data classification:** <...>
- **Personal data touched:** <...>
- **AuthZ/AuthN impact:** <...>
- **Abuse cases:**
  - <cross-org>: <response>
  - <draft-leak>: <how hidden>
  - <spam>: rate limit <N req/min/user>
- **Security review:** <Required / N/A with reason>

## 7. Metrics / KPIs

<!-- Skill instruction: ≥3 KPI у bullet list, без верхнього cap. Skill пропонує стільки, скільки RICE drivers з idea-brief §11 + Recommendation §13.
Формат: «- **<metric name>** — baseline: <X>, target: <Y за <таймфрейм>>».
baseline=0 ОК для нової фічі. baseline=TBD → обов'язково baseline measurement plan: як виміряти до релізу (наприклад «перед релізом — 2 тижні track як користувачі виконують target action вручну (у Notion/Docs/spreadsheets)»).
KPIs з idea-brief §13 Recommendation + idea-brief §11 RICE Impact.

Що зазвичай беремо:
- **Adoption rate** — частка active users, що зробили target action за 30 днів.
- **Engagement uplift / retention** — return-to-feature rate у когорті з ≥N use.
- **Quality / accuracy** — error rate, drift, retry count (feature-specific).
- **Latency p95** — як у NFR (повторюємо тут як KPI для post-release tracking). -->

- **<metric 1>** — baseline: <...>, target: <... за ... днів>.
- **<metric 2>** — baseline: <...>, target: <...>.
- **<metric 3>** — baseline: <...>, target: <...>.

## 8. Open questions

<!-- Skill instruction: 2-4 open Q checkboxes.
Формат: `- [ ] <питання>? — owner: <role/name>, due: <YYYY-MM-DD or stage trigger like "перед 6.9">`
Питання що skill не зміг впевнено запропонувати з inputs/code.
Default відповідь у тексті питання якщо вона є («Default зараз: <X>»).
«TBD» без owner — anti-pattern. Кожне питання має owner. -->

- [ ] <питання>? Default зараз: <...>. — owner: <name/role>, due: <date or stage>
- [ ] <питання>? — owner: <name/role>, due: <date or stage>
- [ ] <питання>? — owner: <name/role>, due: <date or stage>
