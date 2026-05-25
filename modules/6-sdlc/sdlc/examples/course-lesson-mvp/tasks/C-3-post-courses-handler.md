---
id: C-3
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.75d
aggregate: courses
blocks: [E-1]
blocked_by: [C-2, F-3]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-01, AC-02, AC-09]
sad_refs: ["§6 US-01"]
openapi_paths: ["POST /courses"]
adr_refs: []
---

# C-3 · `POST /courses` handler (createCourse + rate-limit)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** C-2 (repo), F-3 (rate-limit helper).
- **Блокує:** E-1 (E2E lifecycle через цей endpoint).
- **Чому в цій хвилі:** один із 8 handler-ів, паралельний з іншими після C-2/L-2/F-*.

## Why (user story)

As a `methodist`, I want to create a course draft via `POST /courses`, so that I have an org-scoped workspace для контенту до публікації.

PRD US-01. AC-01 (happy 201), AC-02 (description ≤ 500 → 400), AC-09 (non-methodist → 403). Rate-limit 30/min/user (PRD §6.1 abuse-case 4).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-01-createcourse]]
- 🗄  Data delta:  none — schema у MIG-1.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /courses` (`createCourse`), `Course`, `CreateCourseRequest`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-01, AC-02, AC-09

## Data delta

```
INSERT-only. No new tables. Course writes to `courses` table.
```

## API contract

```
POST /courses
  AuthN: BearerAuth
  AuthZ: orgmw + OrgMemberChecker.IsMethodist(orgID, userID) == true
  Rate-limit: 30 req/min/user (F-3 ratelimit.Check namespace="courses-create")
  Body: CreateCourseRequest {title, description?, cover_image_url?}
  Response:
    201 Course  (success)
    400 validation.description_too_long  (AC-02)
    401 auth.unauthorized
    403 course.not_methodist            (AC-09)
    429 rate_limited                    (PRD §6.1.4)
```

## Acceptance criteria (GWT)

- [ ] **AC-c3-1 (happy create — AC-01):** Given valid body + methodist caller, when POST /courses, then 201 + body Course із status=draft, course_owner_id=caller, published_at=null; row у DB.
- [ ] **AC-c3-2 (description too long — AC-02):** Given description=501 chars, when POST, then 400 `validation.description_too_long`.
- [ ] **AC-c3-3 (non-methodist — AC-09):** Given caller з `is_methodist=false`, when POST, then 403 `course.not_methodist`.
- [ ] **AC-c3-4 (rate-limit):** Given 30 successful POSTs у вікні 60s, when 31-й POST, then 429 `rate_limited`.
- [ ] **AC-c3-5 (rate-limit isolation):** Given user A hits limit, when user B POSTs, then B success (separate counter).
- [ ] **AC-c3-6 (auth missing):** Given no Bearer header, when POST, then 401 `auth.unauthorized`.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/courses/app/create_course.go` — application service `CreateCourse(ctx, orgID, userID uuid.UUID, req CreateCourseRequest) (Course, error)`.
- [ ] Step 2 — App-service flow: validate (description ≤ 500 → ErrDescriptionTooLong, title required → ErrInvalidPayload) → call domain `NewDraftCourse` → `repo.Create`.
- [ ] Step 3 — Створити `beer-lms-api/internal/modules/courses/ports/http/handler.go` — HTTP handler `PostCourses(w, r)`. Реєструвати на `POST /courses`.
- [ ] Step 4 — Handler flow:
   1. Decode JSON → struct.
   2. `ratelimit.Check("courses-create", userID, 30, 1*time.Minute)` → 429 if not allowed.
   3. `checker.IsMethodist(orgID, userID)` → 403 `course.not_methodist` if false.
   4. `service.CreateCourse(...)` → on `ErrDescriptionTooLong` → 400; on success → 201 + Course JSON.
- [ ] Step 5 — Error mapping table у apperr-overlay: `course.not_methodist` 403, `validation.description_too_long` 400, `course.invalid_payload` 400.
- [ ] Step 6 — Handler tests `handler_test.go`: AC-c3-1..AC-c3-6 + golden response shape vs openapi `Course` example.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Body із trailing whitespace у `title` | Domain не trim-ає; зберігається as-is. Validator має trim() якщо UX-need (OQ). |
| `cover_image_url = "not-a-url"` | Handler не валідує — OQ-1 на allowlist URL-host. Зберігається as-is. |
| Rate-limit fail-open (Redis down — see F-3) | Request proceeds; warning лог. Acceptable risk. |
| Caller у двох orgs одночасно | OrgCtx видає поточну org з middleware; checker контекстуальний. Не наш case рішати. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler tests + service tests; coverage ≥ 80% у `app/` і `ports/http/`.
- [ ] OpenAPI Swagger UI показує endpoint що відповідає openapi.yaml.
- [ ] PR linked back to `tasks/C-3-post-courses-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
