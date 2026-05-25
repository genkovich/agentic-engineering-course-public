---
status: Draft
owner: genkovich
reviewers: ["Tech Lead", "Security Lead", "Privacy Engineer"]
updated_at: "2026-05-23"
feature_size: M
stage: "04-05"
ticket: "beerlms-#1042"
---

# Software Architecture Document — course-lesson-mvp

<!-- Stages 04-05 → see sdlc/plugin/skills/architecture-design/SKILL.md -->
<!-- 12 Arc42 sections. Empty sections — <!-- N/A: <one-line reason> -->. -->
<!-- C4 Context (L1) lives inline in §3. C4 Container (L2) lives inline in §5. -->

## 1. Introduction and goals

**Intent.** Course-lesson-mvp розширює BeerLMS з інструмента для 1-on-1 mentorship у платформу для асинхронної доставки курсів.

Flow:

- `methodist` створює `course`;
- додає до нього `lesson` з блоків (текст / вбудоване відео / картинка / код);
- публікує;
- `member` тієї ж org читає урок, відмічає його як завершений (з тумблером приватності), бачить peer-completion signal (агрегований сигнал «скільки сусідів вже завершили цей урок» — з порогом проти fingerprinting, щоб не можна було ідентифікувати конкретну людину), і коментує урок (тільки текстом, без вкладених тредів у v1).

Це Approach C з idea-brief §13 (RICE = 81). Ключові деталі: блочна структура тіла уроку + сутність `lesson_completion` з налаштуванням приватності + плоска гілка коментарів. Це і є основний v1 differentiator — він мітигує «devil's-vector» з idea-brief: «methodist створив один курс і пропадає». Real-time engagement signal від member-ів дає автору відчуття, що його контент читають.

**Top-3 quality goals (1-liners; full scenarios у §10; визначення термінів у §12):**

1. **QG-1 Privacy/Confidentiality — peer-дані огороджені межами org + захист від fingerprinting + GDPR consent.** `peer_visibility` за замовчуванням `private` для нових member-ів. Лічильники прихані, якщо у org менше 3 completions на конкретний урок (порог проти ідентифікації). Усі зміни приватності логуються у `user_preference_audit` для GDPR recall (PRD §6.1; AC-13, AC-15).
2. **QG-2 Security — захист від кількох типів зловживань.** Cross-org існує-чи-ні приховується через 404 на чужий published course (PRD AC-07); leak чорновика виключений фільтром по `(org_id, status, course_owner_id)`; SSRF у `video_embed.url` блокується allowlist host-ів; XSS у коментарях — HTML-escape на сервері; rate-limit 30 req/min на POST /courses і 10/h на POST /comments (PRD §6.1 abuse cases #1-#5, #7, #8).
3. **QG-3 Availability — нові routes наслідують BeerLMS-API SLO 99.9% rolling 30-day window.** Нові routes (`*/courses`, `*/lessons`, `*/completion`, `*/comments`) включені у існуючий error budget. Якщо Redis-кеш peer-blob падає — урок все одно віддається (запасний шлях — пряме читання з БД, з вищою затримкою; це accepted higher-latency mode).

**Performance fallout.** PRD §6 NFR latency-targets (`POST /courses` ≤250 мс, `GET /lessons/{id}` з peer-blob ≤400 мс, `POST /completion` ≤200 мс, `POST /comments` ≤400 мс, throughput ≥30 req/s) свідомо виходять з §10 Top-3 і верифікуються через k6 load-test у CI pipeline (без окремих §10 сценаріїв). Stale peer-blob у 60-секундному Redis TTL — це §8 Crosscutting (конвенція кешу) + §11 Risk-row, accepted UX trade-off.

**Stakeholders.**

| Role | Interest | Sign-off owner? |
|---|---|---|
| `methodist` | Створює/публікує courses+lessons; отримує engagement-feedback через peer-completion signal | No |
| `course_owner` | Editor/publisher subset методиста для конкретного course (full rights only на own course) | No |
| `member` | Споживає published content, mark-complete, comment, manage privacy preference | No |
| `admin` | Org-scoped moderation (hide comments via PRD AC-18); не editor контенту | No |
| Tech Lead | Architecture sign-off; reviews ADRs | **Yes** |
| Security Lead | §6.1 abuse cases (cross-org leak, draft leak, SSRF, comment XSS, rate limits) — PRD §6.1 «Required + elevated» verdict | **Yes** |
| Privacy Engineer | GDPR consent flow + peer-visibility default + anti-fingerprinting threshold + `user_preference_audit` log | **Yes** |
| PM | §10 Quality Goals confirmation + §7 KPIs (peer-engagement, opt-in rate, comment engagement) | No |

## 2. Constraints

**Technical.** (verified by Step 3 Explore subagent against `internal/modules/mentorship/` as shipped reference)
- Go 1.25.0 (Alpine 3.23 runtime image).
- chi v5.2.5 (HTTP router; existing global rate-limit 60 req/min/IP at chi-middleware layer).
- pgx/v5 (Postgres async pool; raw SQL — **no** sqlc codegen у репо).
- Postgres ≥ 15 (assumed production version — confirm at Stage 08 data-model).
- golang-migrate/migrate v4 (embedded SQL `/migrations/*.sql` via `iofs`).
- UUID v7 (google/uuid) — ID strategy for **all** new entities (`courses.id`, `lessons.id`, `lesson_completions.id`, `comments.id`, `user_preferences.user_id` — composite or FK).
- golang-jwt/jwt v5 — JWT validation; Google OAuth via `golang.org/x/oauth2`.
- swaggo/http-swagger v2 — auto-docs at `/swagger`.
- **NEW shared infrastructure:** Redis ≥ 7.2 — required for (a) лічильник запитів на користувача для rate-limit (PRD §6.1 abuse cases #4, #8), і (b) кеш peer-blob з 60-секундним терміном життя (PRD §6 NFR ≤400 мс peer-enriched read). Rationale + alternatives → ADR-0002.

**Organisational.**
- Effort budget: 3-5 person-weeks (PRD frontmatter `feature_size: M`; idea-brief §11 RICE `E = 3`; §12 Time-feasibility ✓ для 4-6w window).
- Deadline: Q3 onboarding cycle **hard** — idea-brief §4 «Q3 onboarding cycle потребує асинхронної доставки знань як must-have».
- Team: BeerLMS backend + ~0.5 frontend (effective composition; PM-confirmed at sprint planning).
- DevOps capacity для введення Redis: required (ADR-0002 Negative consequence). §11 Risk-row tracks this dependency.

**Conventions.**
- **No root CLAUDE.md** (Explore §f). Effective convention reference = `internal/modules/mentorship/` shipped pattern (5 weeks production).
- DDD layering: `domain/` (entities + sentinel errors) → `app/` (use cases + authz via `OrgMemberChecker`) → `infra/` (Postgres repos з raw SQL via pgx; checker impl) → `ports/` (chi handler + DTO + `errors.go` для domain→HTTP map) → `module.go` (DI wiring factory).
- Error codes: `module.snake_case` — `course.not_found`, `lesson.sequence_conflict`, `lesson.not_found`, `comment.not_moderator`, `validation.description_too_long`, `validation.comment_too_long`, `validation.reorder_payload_too_large`, `rate_limited`. Mapping через `mapError()` у `ports/errors.go` → `apperr.Error{Code, Message, StatusCode}`.
- AuthZ: `OrgMemberChecker` interface — query `org_members WHERE org_id = $1 AND user_id = $2` для role/flag checks. Mentorship use `IsMentor`; новий feature додає `IsMethodist` (PRD AC-09) і `IsAdmin` (PRD AC-18). **Mandatory invariant:** всі repo SELECT-и фільтрують `org_id = $1` (mentorship parity; cross-org leak виключений архітектурно).
- HTTP routing: nested під `/api/v1/orgs/{orgId}/...` через `orgmw` middleware → `OrgContext{OrgID, OrgRole}` (Explore §f).
- Pagination: cursor-based composite `time.RFC3339Nano + "|" + UUID` (Explore §f).
- Side-effects pattern: domain-interface + composite-listener (mentorship `SessionLifecycleListener` + `NewCompositeSessionListener` fan-out). v1 course-lesson **no listeners** — email/push notification у PRD §3 Non-goals.

**Regulatory / external.**
- **GDPR** — privacy-by-default consent flow (PRD §6.1 GDPR consent block, AC-13); `user_preference_audit{user_id, old, new, changed_at}` для compliance recall; user-deletion semantics для `lesson_completions`, `user_preferences`, `comments` treated as user-generated PII-adjacent data. Privacy Engineer sign-off required.
- **Security review verdict:** «Required + elevated» per PRD §6.1 — SecEng + PrivacyEng review перед merge.
- No PCI / SOC2 applicable у v1 (no payment data; no compliance-classified data beyond GDPR).

## 3. Context and scope

<Business context in 2-3 sentences. What the system does for whom.>

**External systems (in / out):**

| Actor or system | Type | Interaction |
|---|---|---|
| <e.g. IC> | Person | Creates goals, adds checkpoints |
| <e.g. notification-service> | System (internal) | Receives cron registration |
| <e.g. Identity Provider> | System (external) | Provides JWT tokens |

**C4 Context (L1):**

```mermaid
C4Context
    title <system> — System Context

    Person(user, "<User>", "<role + intent>")
    System(system, "<Our System>", "<one-sentence description>")
    System_Ext(ext, "<External system>", "<one-sentence description>")

    Rel(user, system, "<interaction>", "<protocol>")
    Rel(system, ext, "<interaction>", "<protocol>")
```

## 4. Solution strategy

**Top-3 strategic choices (the seeds for ADRs):**

1. **<e.g. Module isolation through events>** — <2-3 sentences rationale referencing Quality Goals and constraints>.
2. **<e.g. Single-store persistence (Postgres)>** — <2-3 sentences>.
3. **<e.g. Server-rendered dashboard>** — <2-3 sentences>.

Each tactical decision in later sections should be traceable to one of these strategic seeds. Tactical decisions that *contradict* a strategic choice are red flags — surface them in §11 Risks.

## 5. Building block view

<One paragraph: layered / hexagonal / clean / event-driven. Why.>

**Internal decomposition:**

```
<e.g. internal/modules/goals/>
├── domain/       <entities + sentinel errors>
├── app/          <use cases / services>
├── infra/        <repository + outbox impl>
├── ports/        <HTTP handlers, DTOs, error mapping>
└── module.go     <self-wiring>
```

**C4 Container (L2):**

```mermaid
C4Container
    title <system> — Containers

    Person(user, "<User>")

    Container_Boundary(boundary, "<Our System>") {
        Container(web, "<Web/API container>", "<technology>", "<purpose>")
        Container(svc, "<Service container>", "<technology>", "<purpose>")
        ContainerDb(db, "<DB>", "<technology>", "<purpose>")
    }

    System_Ext(ext, "<External>", "<purpose>")

    Rel(user, web, "<interaction>", "<protocol>")
    Rel(web, svc, "<service calls>")
    Rel(svc, db, "<reads/writes>", "<driver>")
    Rel(svc, ext, "<emits>", "<protocol>")
```

## 6. Runtime view

<!-- Container-level sequences (US-NN; учасники = логічні модулі / спільна інфраструктура; без HTTP-verbs у параметрах). -->
<!-- Endpoint-level sequences inlined нижче під `### Endpoint-level: …` (HTTP verbs, status codes, alt-branches). -->
<!-- Sequence coverage audit: `_audit/sequences-2026-05-23.md`. -->

### US-01: createCourse (draft)

```mermaid
sequenceDiagram
    autonumber
    actor M as methodist
    participant API as content-api (handler)
    participant RL as Redis (rate-limit bucket)
    participant OMC as OrgMemberChecker
    participant DB as Postgres

    %% TODO: align with openapi.yaml — POST /courses not yet in contract
    M->>API: POST /courses {title, description?, cover_image_url?}
    API->>RL: INCR user:{user_id}:courses-per-min (TTL 60s)
    alt count > 30
        RL-->>API: limit exceeded
        API-->>M: 429 {code:"rate_limited"}
    else within limit
        RL-->>API: ok
        API->>API: validate description length ≤ 500
        alt description > 500 chars
            API-->>M: 400 {code:"validation.description_too_long"}
        else valid
            API->>OMC: IsMethodist(org_id, user_id)
            alt not methodist
                OMC-->>API: false
                API-->>M: 403 {code:"course.not_methodist"}
            else methodist
                OMC-->>API: true
                API->>DB: INSERT courses(id, org_id, course_owner_id, title, description, status='draft')
                DB-->>API: row created
                API-->>M: 201 {id, status:"draft", course_owner_id, org_id, created_at}
            end
        end
    end
```

### US-02: addLesson (block-based)

```mermaid
sequenceDiagram
    autonumber
    actor M as methodist
    participant API as content-api (handler)
    participant DB as Postgres
    participant OUT as outbox poller
    participant CON as search/analytics consumers

    M->>API: POST /courses/{course_id}/lessons {title, body[], sequence?}
    API->>DB: SELECT courses WHERE id=$1 AND org_id=$2
    alt course in different org
        DB-->>API: 0 rows
        API-->>M: 404 {code:"course.not_found"}
    else course found
        DB-->>API: course row
        API->>DB: BEGIN tx
        API->>DB: INSERT lessons(id, course_id, sequence, body, status='draft')
        API->>DB: INSERT outbox event_type='lesson.created'
        Note over API, DB: UNIQUE(course_id, sequence) constraint<br/>concurrent INSERT with same sequence → pq.unique_violation
        alt unique violation on (course_id, sequence)
            DB-->>API: 23505 unique_violation
            API->>DB: ROLLBACK
            API-->>M: 409 {code:"lesson.sequence_conflict"}
        else commit ok
            DB-->>API: lesson row + outbox row
            API->>DB: COMMIT
            API-->>M: 201 {id, status:"draft", sequence, body}
            Note over OUT, CON: poller picks lesson.created event<br/>idempotent via event_id (UUID v7)
            OUT->>CON: deliver lesson.created
        end
    end
```

### US-03: publishCourse

```mermaid
sequenceDiagram
    autonumber
    actor M as methodist
    participant API as content-api (handler)
    participant DB as Postgres
    participant OUT as outbox poller
    participant NS as notification-service

    %% TODO: align with openapi.yaml — POST /courses/{id}/publish not yet in contract (only POST /lessons/{id}/publish exists)
    M->>API: POST /courses/{id}/publish
    API->>DB: SELECT courses WHERE id=$1 AND org_id=$2 AND course_owner_id=$3
    alt not found / not owner
        DB-->>API: 0 rows
        API-->>M: 404 {code:"course.not_found"}
    else owner ok, already published
        DB-->>API: course row (status='published')
        API-->>M: 200 {status:"published", published_at} (idempotent, no DB write)
    else owner ok, draft
        DB-->>API: course row (status='draft')
        API->>DB: SELECT COUNT(*) FROM lessons WHERE course_id=$1 AND status='published'
        alt count = 0
            DB-->>API: 0
            API-->>M: 409 {code:"course.no_published_lessons"}
        else count ≥ 1
            DB-->>API: ≥1
            API->>DB: BEGIN tx
            API->>DB: UPDATE courses SET status='published', published_at=now() WHERE id=$1
            API->>DB: INSERT outbox event_type='course.published'
            API->>DB: COMMIT
            API-->>M: 200 {status:"published", published_at}
            Note over OUT, NS: poller picks course.published event<br/>retry budget per events.md (1s → 30min, DLQ after 5)
            OUT->>NS: deliver course.published
        end
    end
```

### US-04: viewCourse (cross-org 404)

```mermaid
sequenceDiagram
    autonumber
    actor U as member / methodist / admin
    participant API as content-api (handler)
    participant OMC as OrgMemberChecker
    participant DB as Postgres

    U->>API: GET /courses/{id}
    API->>DB: SELECT courses WHERE id=$1
    alt course not exists
        DB-->>API: 0 rows
        API-->>U: 404 {code:"course.not_found"}
    else course exists
        DB-->>API: course row {org_id, status, course_owner_id}
        API->>OMC: GetOrgRole(caller_user_id, course.org_id)
        alt published & same org
            OMC-->>API: member
            API-->>U: 200 {course details}
        else published & different org
            OMC-->>API: not_a_member
            Note over API: AC-07 deviation — existence-hiding<br/>NOT 403 org_mismatch (would leak cross-org membership)
            API-->>U: 404 {code:"course.not_found"}
        else draft & caller ≠ owner ∧ caller ≠ admin
            OMC-->>API: same-org member, but not owner / admin
            Note over API: AC-08 — drafts visible only to course_owner + admin
            API-->>U: 404 {code:"course.not_found"}
        else draft & caller = owner or admin
            OMC-->>API: owner or admin
            API-->>U: 200 {course details, status:"draft"}
        end
    end
```

### US-05: reorderLessons

```mermaid
sequenceDiagram
    autonumber
    actor M as methodist
    participant API as content-api (handler)
    participant DB as Postgres

    %% TODO: align with openapi.yaml — PATCH /courses/{id}/lessons/reorder not yet in contract
    M->>API: PATCH /courses/{id}/lessons/reorder {items:[{lesson_id, sequence}, ...]}
    alt len(items) > 50
        API-->>M: 400 {code:"validation.reorder_payload_too_large"}
    else len(items) ≤ 50
        API->>DB: SELECT courses WHERE id=$1 AND org_id=$2 AND course_owner_id=$3
        alt not owner / wrong org
            DB-->>API: 0 rows
            API-->>M: 404 {code:"course.not_found"}
        else owner ok, course already published
            DB-->>API: course row (status='published')
            Note over API: invariant — reorder allowed only on draft course
            API-->>M: 409 {code:"course.already_published"}
        else owner ok, draft
            DB-->>API: course row (status='draft')
            API->>DB: BEGIN tx
            API->>DB: UPDATE lessons SET sequence=$N WHERE id=$id AND course_id=$cid (batch)
            Note over API, DB: tx commit guards UNIQUE(course_id, sequence)<br/>any violation → ROLLBACK
            API->>DB: COMMIT
            API-->>M: 200 {items:[{lesson_id, sequence}, ...]}
        end
    end
```

### US-06: markLessonComplete (idempotent)

```mermaid
sequenceDiagram
    autonumber
    actor LRN as member (learner)
    participant API as content-api (handler)
    participant DB as Postgres

    %% TODO: align with openapi.yaml — POST /lessons/{id}/completion not yet in contract
    LRN->>API: POST /lessons/{id}/completion
    API->>DB: SELECT lessons l JOIN courses c ON c.id=l.course_id WHERE l.id=$1 AND l.status='published' AND c.org_id=$2
    alt draft lesson OR cross-org
        DB-->>API: 0 rows
        API-->>LRN: 404 {code:"lesson.not_found"}
    else published lesson, same org
        DB-->>API: lesson row
        API->>DB: INSERT lesson_completions(user_id, lesson_id, org_id, completed_at) -- UNIQUE(user_id, lesson_id)
        alt first completion
            DB-->>API: row inserted
            API-->>LRN: 201 {lesson_id, completed_at}
        else duplicate (unique_violation)
            DB-->>API: 23505 unique_violation
            Note over API, DB: idempotent — re-read existing row,<br/>do NOT overwrite completed_at
            API->>DB: SELECT completed_at FROM lesson_completions WHERE user_id=$1 AND lesson_id=$2
            DB-->>API: existing row
            API-->>LRN: 200 {lesson_id, completed_at} (idempotent)
        end
    end
```

### US-07: setPeerVisibilityPreference

```mermaid
sequenceDiagram
    autonumber
    actor U as member
    participant API as content-api (handler)
    participant DB as Postgres
    participant AUD as user_preference_audit (Postgres table)

    %% TODO: align with openapi.yaml — PATCH /me/preferences not yet in contract
    U->>API: PATCH /me/preferences {peer_visibility:"public"|"private"}
    Note over API: new user default = "private" (GDPR-friendly opt-in, AC-13)
    alt invalid value
        API-->>U: 400 {code:"validation.invalid_preference"}
    else valid value
        API->>DB: BEGIN tx
        API->>DB: SELECT current peer_visibility FROM user_preferences WHERE user_id=$1
        DB-->>API: previous value (or null if first set)
        API->>DB: UPSERT user_preferences SET peer_visibility=$new WHERE user_id=$1
        API->>AUD: INSERT user_preference_audit(user_id, field='peer_visibility', old, new, changed_at)
        Note over API, AUD: both writes in single tx —<br/>compliance trail for GDPR recall
        API->>DB: COMMIT
        API-->>U: 200 {peer_visibility:$new}
    end
```

### US-08: viewLessonWithPeerSignal

```mermaid
sequenceDiagram
    autonumber
    actor LRN as member (learner)
    participant API as content-api (handler)
    participant RDS as Redis (peer-blob cache)
    participant DB as Postgres

    LRN->>API: GET /lessons/{id}
    API->>DB: SELECT lessons l JOIN courses c ON c.id=l.course_id WHERE l.id=$1 AND c.org_id=$2
    alt lesson not found / cross-org / draft (caller ≠ owner)
        DB-->>API: 0 rows
        API-->>LRN: 404 {code:"lesson.not_found"}
    else lesson visible
        DB-->>API: lesson row + blocks
        API->>RDS: GET peer-blob:lesson:{lesson_id}:org:{org_id}
        Note over API, RDS: peer-blob cached with 60s TTL per (lesson_id, org_id) — ADR-0002
        alt cache hit
            RDS-->>API: cached blob {count, recent_completers[]}
        else cache miss
            RDS-->>API: nil
            API->>DB: SELECT COUNT(*), recent 5 FROM lesson_completions lc JOIN user_preferences up ON up.user_id=lc.user_id WHERE lc.lesson_id=$1 AND lc.org_id=$2 AND up.peer_visibility='public'
            DB-->>API: aggregated counts
            API->>RDS: SET peer-blob:... EX 60
        end
        API->>DB: SELECT 1 FROM lesson_completions WHERE user_id=$caller AND lesson_id=$1 -- my_completed flag
        DB-->>API: bool
        alt count < 3 (AC-15 anti-fingerprinting threshold)
            Note over API: small-org de-anonymization guard —<br/>hide count and completer list
            API-->>LRN: 200 {lesson, peer_completion:{count:null, recent_completers:[], my_completed}}
        else count ≥ 3
            API-->>LRN: 200 {lesson, peer_completion:{count, recent_completers[], my_completed}}
        end
    end
```

### US-09: createComment

```mermaid
sequenceDiagram
    autonumber
    actor LRN as member (learner)
    participant API as content-api (handler)
    participant RDS as Redis (rate-limit token-bucket)
    participant DB as Postgres

    %% TODO: align with openapi.yaml — POST /lessons/{id}/comments not yet in contract
    LRN->>API: POST /lessons/{id}/comments {content}
    alt content > 2000 chars
        API-->>LRN: 400 {code:"validation.comment_too_long"}
    else content length ok
        API->>RDS: token-bucket consume key=user:{user_id}:comments-per-hour (limit 10/h)
        Note over API, RDS: bucket key = user_id (per-user, not per-instance)<br/>AC-17 / abuse case #8
        alt bucket exhausted
            RDS-->>API: rate exceeded
            API-->>LRN: 429 {code:"rate_limited"}
        else token granted
            RDS-->>API: ok
            API->>DB: SELECT lessons l JOIN courses c ON c.id=l.course_id WHERE l.id=$1 AND l.status='published' AND c.org_id=$2
            alt lesson not visible (draft / cross-org)
                DB-->>API: 0 rows
                API-->>LRN: 404 {code:"lesson.not_found"}
            else lesson visible
                DB-->>API: lesson row
                Note over API: server-side HTML-escape content<br/>before persist — XSS mitigation (§6.1 #7)
                API->>DB: INSERT comments(id, lesson_id, author_id, content, status='visible', created_at)
                DB-->>API: row created
                API-->>LRN: 201 {id, author_id, lesson_id, content, status:"visible", created_at}
            end
        end
    end
```

### US-10: hideComment (moderation)

```mermaid
sequenceDiagram
    autonumber
    actor A as admin
    participant API as content-api (handler)
    participant OMC as OrgMemberChecker
    participant DB as Postgres
    participant AUD as comment_audit (Postgres table)

    %% TODO: align with openapi.yaml — POST /comments/{id}/hide not yet in contract
    A->>API: POST /comments/{id}/hide
    API->>DB: SELECT comments cm JOIN lessons l ON l.id=cm.lesson_id JOIN courses c ON c.id=l.course_id WHERE cm.id=$1 AND c.org_id=$2
    alt comment not found / cross-org
        DB-->>API: 0 rows
        API-->>A: 404 {code:"comment.not_found"}
    else comment found
        DB-->>API: comment row + org_id
        API->>OMC: IsAdmin(org_id, caller_user_id)
        alt not admin
            OMC-->>API: false
            API-->>A: 403 {code:"comment.not_moderator"}
        else admin
            OMC-->>API: true
            API->>DB: BEGIN tx
            API->>DB: UPDATE comments SET status='hidden', content='[hidden by moderator]' WHERE id=$1
            API->>AUD: INSERT comment_audit(comment_id, original_content, moderator_id, hidden_at)
            Note over API, AUD: original content preserved in audit table —<br/>compliance recall (AC-18)
            API->>DB: COMMIT
            API-->>A: 200 {id, status:"hidden", content:"[hidden by moderator]"}
        end
    end
```

### Endpoint-level: `POST /lessons/{id}/publish`

Двошарова дисципліна: контейнерний рівень (`US-NN` вище) лишається без HTTP verbs, а endpoint-level нижче розгортає той самий flow з конкретним контрактом — який код повертає сервер при cross-methodist publish, де закінчується транзакція, коли outbox poller підхоплює подію. Це той самий рівень деталі, що `openapi.yaml` для `publishLesson` operationId, тільки розгорнутий у часі.

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (web-app)
    participant API as content-api (handler)
    participant SVC as Lesson Service
    participant DB as Postgres
    participant W as media-worker
    participant CDN as CDN

    C->>API: POST /lessons/{id}/publish
    API->>SVC: PublishLesson(id, methodist_id)
    SVC->>DB: SELECT lesson WHERE id=? AND methodist_id=?
    alt lesson not found OR not owned
        DB-->>SVC: 0 rows
        SVC-->>API: lesson.not_found / lesson.forbidden
        API-->>C: 404 / 403 {code, message}
    else lesson found, draft status
        DB-->>SVC: lesson row
        SVC->>DB: SELECT blocks WHERE lesson_id=? ORDER BY sequence
        DB-->>SVC: ordered blocks
        SVC->>DB: BEGIN; UPDATE lessons SET status='published', published_at=now() WHERE id=?
        SVC->>DB: INSERT INTO lesson_events (event_type='lesson.published', payload=...)
        SVC->>DB: COMMIT
        SVC-->>API: published lesson
        API-->>C: 200 {lesson with status=published}
        Note over W: outbox poller picks event
        W->>CDN: invalidate cache for /courses/.../lessons/<slug>
    end
```

Drift check vs `openapi.yaml`:

- `POST /lessons/{id}/publish` — присутній у `paths`, operationId `publishLesson`.
- Response codes у diagram (200 / 403 / 404) — присутні у `responses` block of `publishLesson` operation.
- Error codes (`lesson.not_found`, `lesson.forbidden`) — використовуються у `ErrorResponse.code` per common convention `module.error_name`.
- Outbox INSERT у тій самій транзакції з UPDATE — відповідає `lesson.published` event з `contracts/events.md`.

## 7. Deployment view

<Topology in 2-3 sentences. Where it runs (k8s / VM / serverless), replicas, scaling thresholds.>

**Monitoring:**
- <Metrics — e.g. Prometheus `<metric_name>`>
- <Alerts — e.g. "outbox lag > 10 min → page on-call">
- <Tracing — e.g. OpenTelemetry HTTP spans>

**Scaling thresholds:**
- <e.g. 500 IC × 5 goals × 26 checkpoints/Q = 65k rows/year — comfortable in one table>
- <e.g. partitioning by quarter at >500k rows/year>

<!-- For XS/S that doesn't change deployment: <!-- N/A: feature reuses existing deployment unit -->. -->

## 8. Crosscutting concepts

| Concept | Convention | Where defined |
|---|---|---|
| Logging | <e.g. structured slog, fields `module=<name>`> | <CLAUDE.md §X or here> |
| Authentication | <e.g. JWT via session middleware> | <CLAUDE.md §X> |
| Error handling | <e.g. domain sentinel → ports/errors.go → apperr JSON> | <CLAUDE.md §X> |
| ID strategy | <e.g. UUID v7 in app layer> | <CLAUDE.md §X> |
| Internationalisation | <e.g. N/A, English only> | — |
| Observability | <e.g. OpenTelemetry on HTTP boundaries> | — |
| Outbox / events | <module-specific patterns, if any> | <here> |

## 9. Architecture decisions

| # | Title | Status | Section |
|---|---|---|---|
| 0001 | Зберігати урок як таблицю блоків різних типів | Accepted | §4 |
| 0002 | Додати Redis як спільну інфраструктуру для rate-limit + peer-blob кешу | Accepted | §2, §4, §8 |

ADR files live under `docs/features/<slug>/adr/NNNN-<title>.md`.

Дивись: [[adr/0001-content-storage-strategy]] · [[adr/0002-add-redis-as-shared-infrastructure]]

## 10. Quality requirements

Each top-3 goal from §1 expanded into a full scenario:

**QG-1. <quality attribute>**
- **When:** <trigger condition>
- **Then:** <expected behavior with numbers from PRD NFR>
- **How verify:** <test / chaos drill / load test / observability>

**QG-2. <quality attribute>**
- **When:** <trigger>
- **Then:** <expected>
- **How verify:** <how>

**QG-3. <quality attribute>**
- **When:** <trigger>
- **Then:** <expected>
- **How verify:** <how>

## 11. Risks and technical debt

<!-- Severity column literals: Low / Medium / High for regular risks; "Open question" for rows
     created by Step-7 `Save as Open Question` resolutions (see references/socratic-loop.md). -->

| Risk / debt | Severity | Mitigation | Owner |
|---|---|---|---|
| <e.g. Outbox lag may reach hours during downstream outage> | Medium | <Alert >10 min, on-call playbook, retry backoff> | <DevOps> |
| <e.g. No event schema versioning in v1> | Medium | <ADR-NNNN planned for v2, graceful handling of unknown fields> | <Backend> |
| Open architectural decision: <decision-headline> | Open question | Resolve before <stage trigger or YYYY-MM-DD>; <inline rationale from Step-7 Save-as-OQ> | <owner> |

**Accepted debt (acceptable in v1, plan to fix later):**
- <e.g. Goal entity is not versioned (immutable) — OK for v1, may need audit versioning in v2>

## 12. Glossary

| Term | Meaning |
|---|---|
| <e.g. Goal> | <quarterly intent in statement form> |
| <e.g. KR> | <Key Result — measurable target linked to a Goal> |
| <e.g. Checkpoint> | <bi-weekly progress update on a KR> |
