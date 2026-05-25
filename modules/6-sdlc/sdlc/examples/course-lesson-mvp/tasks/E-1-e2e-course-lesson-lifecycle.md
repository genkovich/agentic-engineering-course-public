---
id: E-1
epic: course-lesson-mvp
project: BeerLMS
wave: 5
priority: Must
estimate: 0.5d
aggregate: e2e
blocks: []
blocked_by: [C-3, C-4, C-5, L-3, L-4, L-5, L-6]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-01, AC-03, AC-05, AC-06, AC-07, AC-10]
sad_refs: ["§6 US-01", "§6 US-02", "§6 US-03", "§6 US-04"]
openapi_paths: []
adr_refs: []
---

# E-1 · E2E course→lesson lifecycle (create → publish → cross-org 404)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 5 (E2E)

## Місце в послідовності

- **Блокується:** усі C-* і L-* handler-и (потрібні щоб HTTP path працював end-to-end).
- **Блокує:** нічим.
- **Чому в цій хвилі:** integration assertion після всіх handler-ів готові.

## Why (user story)

As a release engineer, I want a black-box HTTP test що демонструє повний lifecycle: methodist створює course → додає lesson → додає blocks → publish-ить lesson → publish-ить course → member з іншого org отримує 404, so that lifecycle invariants assert-ються end-to-end.

PRD ACs cross-validated: AC-01, AC-03, AC-05 (publish gate), AC-06 (idempotent publish), AC-07 (cross-org 404), AC-10 (cross-org parent guard на lesson create).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-01-createcourse]] → [[../sad.md#us-02-addlesson-block-based]] → [[../sad.md#us-03-publishcourse]] → [[../sad.md#us-04-getcourse]]
- 🗄  Data delta:  жодних — використовує існуючі таблиці.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /courses`, `POST /courses/{id}/lessons`, `POST /lessons/{id}/blocks`, `POST /lessons/{id}/publish`, `POST /courses/{id}/publish`, `GET /courses/{id}`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-01, AC-03, AC-05, AC-06, AC-07, AC-10

## Data delta

```
NO new tables. Test seeds через handler-и (no direct SQL):
  - 2 orgs (X, Y), each з 1 methodist + 1 random member.
```

## API contract

_No new HTTP — composes existing endpoints у scenario._

## Acceptance criteria (GWT)

- [ ] **AC-e1-1 (lifecycle happy):** Given methodist X у org A із fresh state, when test executes scenario {POST /courses → POST /courses/{c}/lessons → POST /lessons/{l}/blocks (text) → POST /lessons/{l}/publish → POST /courses/{c}/publish}, then усі responses 200/201; final GET /courses/{c} → 200 + Course status='published'; GET /lessons/{l} → 200 + LessonWithBlocks містить published lesson + 1 block.
- [ ] **AC-e1-2 (cross-org 404 — AC-07):** Given lifecycle із AC-e1-1 завершений, when member із org B робить GET /courses/{c}, then 404 `course.not_found`.
- [ ] **AC-e1-3 (cross-org lesson create — AC-10):** Given methodist Y у org B, when POST /courses/{course_X.id}/lessons, then 404 `course.not_found`.
- [ ] **AC-e1-4 (publish gate enforced — AC-05):** Given course із 0 published lessons, when POST /courses/{c}/publish, then 409 `course.no_published_lessons`.
- [ ] **AC-e1-5 (publish idempotent — AC-06):** Given course published, when same Idempotency-Key replay, then 200 + same body; second fresh-key call → 200 без зміни published_at.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/test/e2e/course_lesson_lifecycle_test.go`. Використати existing test harness pattern із mentorship (`mentorship_lifecycle_test.go` як reference).
- [ ] Step 2 — Setup helper: spin Postgres + Redis testcontainer; run migrations; seed 2 orgs + methodists + members; mint JWT tokens for each.
- [ ] Step 3 — Сценарій AC-e1-1 — sequential HTTP calls + JSON parsing per response shape.
- [ ] Step 4 — Сценарії AC-e1-2, AC-e1-3, AC-e1-4, AC-e1-5 — окремі suite tests (each може reuse seed).
- [ ] Step 5 — Add to CI: run E2E suite на pre-merge гilters.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Test flake через Redis | Use stable miniredis або testcontainer Redis із health check. |
| Migration order | Test runs migrations 000001..000023 sequentially. F-2 додає 000023; усе має apply без помилок. |
| Parallel test runs | Кожна test suite — fresh DB schema (testcontainer separate); no shared state. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] CI green на pre-merge.
- [ ] Test run < 30s на dev machine.
- [ ] PR linked back to `tasks/E-1-e2e-course-lesson-lifecycle.md`.
- [ ] `tracker.md` оновлено: status `done`.
