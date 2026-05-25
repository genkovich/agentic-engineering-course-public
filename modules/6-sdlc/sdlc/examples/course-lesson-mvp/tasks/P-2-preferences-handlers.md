---
id: P-2
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.75d
aggregate: preferences
blocks: [E-2]
blocked_by: [P-1]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-13]
sad_refs: ["§6 US-07"]
openapi_paths: ["GET /me/preferences", "PATCH /me/preferences"]
adr_refs: []
---

# P-2 · `GET /me/preferences` + `PATCH /me/preferences` handlers

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 4

## Місце в послідовності

- **Блокується:** P-1 (repo).
- **Блокує:** E-2 (E2E peer-signal flow змінює visibility і assert через GET).
- **Чому в цій хвилі:** simple read+write handlers після domain ready.

## Why (user story)

As a `member`, I want to read and update my preferences (currently `peer_visibility`) with GDPR-default 'private' for new users, so that I control peer-visibility у lesson pages.

PRD US-07. AC-13.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-07-updatepreferences]]
- 🗄  Data delta:  uses MIG-1 tables `user_preferences` + `user_preference_audit`.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `GET /me/preferences` (`getMyPreferences`), `PATCH /me/preferences` (`updateMyPreferences`)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-13

## Data delta

```
GET → SELECT (returns default 'private' if no row, NOT inserting yet — lazy create on PATCH).
PATCH → UpsertWithAudit (single tx).
```

## API contract

```
GET /me/preferences
  AuthN: BearerAuth (userID from JWT)
  Response: 200 UserPreferences

PATCH /me/preferences
  AuthN: BearerAuth
  Body: UpdateUserPreferencesRequest {peer_visibility: 'public'|'private'}
  Response:
    200 UserPreferences
    400 validation.invalid_preference   (enum mismatch)
    401 auth.unauthorized
```

## Acceptance criteria (GWT)

- [ ] **AC-p2-1 (GET first call — default):** Given user без row у `user_preferences`, when GET, then 200 + `{peer_visibility: 'private', updated_at: <now>}` (default returned без INSERT).
- [ ] **AC-p2-2 (GET after PATCH):** Given PATCH set 'public', when GET, then 200 + `peer_visibility: 'public'`.
- [ ] **AC-p2-3 (PATCH valid):** Given body `{peer_visibility: 'public'}`, when PATCH, then 200 + UserPreferences; DB has pref row + 1 audit row (old=null, new='public') if first time.
- [ ] **AC-p2-4 (PATCH invalid enum):** Given body `{peer_visibility: 'foo'}`, when PATCH, then 400 `validation.invalid_preference`.
- [ ] **AC-p2-5 (PATCH idempotent same value):** Given existing 'private', PATCH 'private' → 200 (no audit row added, no UPDATE — quietly idempotent).
- [ ] **AC-p2-6 (PATCH triggers audit row — AC-13):** Given 'private' existing, PATCH 'public', then audit row created із `{field:'peer_visibility', old_value:'private', new_value:'public', changed_at: now}`.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `GetMyPreferences(userID)` та `UpdateMyPreferences(userID, newVisibility)`.
- [ ] Step 2 — Get flow: `repo.Get(userID)` → on `ErrPreferenceNotFound` → synthesize `UserPreference{userID, 'private', now, now}` (NOT persisted — lazy).
- [ ] Step 3 — Update flow: validate enum → call `repo.UpsertWithAudit(userID, value)` → return updated pref.
- [ ] Step 4 — HTTP handlers `GetMyPreferences(w,r)`, `PatchMyPreferences(w,r)`. UserID — з JWT context, не з path.
- [ ] Step 5 — Тести: AC-p2-1..AC-p2-6.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Body порожній на PATCH | 400 `validation.invalid_payload`. |
| Body має extra fields (наприклад future preference) | Ignore unknown fields (forward-compat). |
| Concurrent PATCH | Один audit row per actual change (idempotent same-value caller does not insert). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує обидва endpoints.
- [ ] PR linked back to `tasks/P-2-preferences-handlers.md`.
- [ ] `tracker.md` оновлено: status `done`.
