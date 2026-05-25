---
id: F-1
epic: course-lesson-mvp
project: BeerLMS
wave: 1
priority: Must
estimate: 0.5d
aggregate: foundation
blocks: [C-1, C-2, L-1, L-2, P-1, CMT-4]
blocked_by: []
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-09, AC-18]
sad_refs: ["§6 US-01", "§6 US-10"]
openapi_paths: []
adr_refs: []
---

# F-1 · `OrgMemberChecker.IsMethodist` + `IsAdmin` Go funcs

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 1 (foundation)

## Місце в послідовності

- **Блокується:** нічим. Schema колонок (`org_members.is_methodist`) вже у DB (migration 000020 merged). Це чисто Go-side checker.
- **Блокує:** усі `POST/PATCH` handler-и, які роблять authz перед write (C-3, C-5, C-6, L-3, L-5, L-6 для methodist gate; CMT-4 для admin gate).
- **Чому в цій хвилі:** усі домени та handler-и викликають `IsMethodist` / `IsAdmin` для AuthZ → без них не можна писати tests on those layers.

## Why (user story)

As a backend developer, I want two reusable role-check funcs `IsMethodist(orgID, userID) → bool` and `IsAdmin(orgID, userID) → bool`, so that every write-handler can enforce role gates з одним патерном і код не дублює inline SQL.

Mirror of `mentorship.OrgMemberChecker.IsMentor` (5 weeks production) — same shape, same error semantics, same fail-closed read.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-01-createcourse]] (caller passes `is_methodist` gate), [[../sad.md#us-10-hidecomment]] (admin gate)
- 🗄  Data delta:  none — column `org_members.is_methodist` already exists (migration `000020_add_is_methodist_to_org_members.up.sql`, merged in `931deca`). `is_admin` already exists pre-feature (assumed; verify у Step 0).
- 🌐 API contract: [[../contracts/openapi.yaml]] — error response `CourseNotMethodist` (AC-09), `CommentNotModerator` (AC-18)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-09, AC-18
- 🧬 Parity ref:   `beer-lms-api/internal/modules/mentorship/infra/member_checker.go`

## Data delta

```
NO DB CHANGES.

Existing column referenced (migration 000020, already merged):
  org_members.is_methodist  BOOLEAN NOT NULL DEFAULT false

Existing column referenced (assumed pre-feature, verify у Step 0):
  org_members.is_admin      BOOLEAN NOT NULL DEFAULT false
```

## API contract

_API surface: none — internal Go funcs consumed by handlers._

## Acceptance criteria (GWT)

- [ ] **AC-chk-1 (IsMethodist true):** Given `org_members` row з `org_id=X, user_id=Y, is_methodist=true`, when `IsMethodist(X, Y)` is called, then returns `(true, nil)`.
- [ ] **AC-chk-2 (IsMethodist false on flag):** Given `org_members` row з `is_methodist=false`, when called, then returns `(false, nil)`.
- [ ] **AC-chk-3 (IsMethodist false on missing row):** Given no `org_members` row for `(X, Y)`, when called, then returns `(false, nil)` (fail-closed — `pgx.ErrNoRows` → `false`, not error).
- [ ] **AC-chk-4 (IsAdmin analogues):** Three analogous cases as AC-chk-1..3 for `IsAdmin`.
- [ ] **AC-chk-5 (DB error propagates):** Given DB returns connection error, when called, then returns `(false, err)` із non-nil error wrapping pgx error.

## Checklist (atomic steps for impl-agent)

- [ ] Step 0 — `grep -n "is_admin" beer-lms-api/migrations/` щоб підтвердити, що колонка існує. Якщо нема — додати окрему 1-line story `F-1a-migration-is-admin.md` і поставити її blocker-ом цієї story. Якщо є — продовжити.
- [ ] Step 1 — Знайти або створити `beer-lms-api/internal/modules/org/` модуль. Mirror layout mentorship-а: `domain/` (interfaces) + `infra/` (Postgres impl).
- [ ] Step 2 — У `internal/modules/org/domain/checker.go` оголосити інтерфейс `OrgMemberChecker` з методами `IsMethodist(ctx, orgID, userID) (bool, error)` + `IsAdmin(ctx, orgID, userID) (bool, error)`.
- [ ] Step 3 — У `internal/modules/org/infra/member_checker.go` створити `PostgresOrgMemberChecker` — копія структури `mentorship/infra/member_checker.go`, але два методи замість одного. Обидва селекти однакові за формою (`SELECT <flag> FROM org_members WHERE org_id=$1 AND user_id=$2`).
- [ ] Step 4 — Юніт-тести у `infra/member_checker_test.go` — використати `pgxmock` (mirror mentorship test style) або testcontainers. Покрити AC-chk-1..AC-chk-5.
- [ ] Step 5 — Wire constructor у `cmd/api/main.go` (або analogous wiring entrypoint) — отримати один `*PostgresOrgMemberChecker` і передати у handler-и через DI.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `(orgID, userID)` валідні UUID, але user не у org → `org_members` row відсутній | `(false, nil)` — fail-closed (mentorship parity). |
| User у org, але обидва flag-и false | `(false, nil)`. |
| User у двох org-ах із різними flag-ами | `WHERE org_id = $1` обмежує scope — checker завжди контекстуальний до конкретної org. |
| `userID = uuid.Nil` | `(false, nil)` — нема такого row у DB. Не валідуємо input у checker — це responsibility caller-а. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] `go vet` + `golangci-lint run` clean у `internal/modules/org/`.
- [ ] Coverage ≥ 90% у `infra/member_checker.go`.
- [ ] DI wiring додано — handler-и наступних story-сей можуть приймати `org.OrgMemberChecker` як constructor param.
- [ ] PR linked back to `tasks/F-1-checkers-is-methodist-is-admin.md`.
- [ ] `tracker.md` оновлено: status `done`.
