---
id: P-1
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: preferences
blocks: [P-2, CMP-3]
blocked_by: [F-1]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-13]
sad_refs: ["§6 US-07"]
openapi_paths: []
adr_refs: []
---

# P-1 · `UserPreference` + `UserPreferenceAudit` domain + repo + tests

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** F-1 (chain).
- **Блокує:** P-2 (handler), CMP-3 (peer-blob reads `peer_visibility` через JOIN — потрібен domain shape тут).
- **Чому в цій хвилі:** singleton-per-user store + audit pattern — невелика story.

## Why (user story)

As a `member`, I want my preferences (currently just `peer_visibility`) persisted із GDPR-friendly default 'private' + audit log on every change, so that org compliance може отримати recall з історії моїх consent-actions.

PRD US-07. AC-13.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-07-updatepreferences]]
- 🗄  Data delta:  inherits MIG-1 (`user_preferences` + `user_preference_audit` у migration 000021)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `UserPreferences`, `UpdateUserPreferencesRequest`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-13
- 🧬 Parity ref:   mirror `mentorship/infra/session_repo.go` (tx-aware UPSERT із audit insert)

## Data delta

```
NO DB CHANGES. Domain types:

UserPreference:
  user_id (UUID, PK), peer_visibility (enum: public|private),
  created_at, updated_at

UserPreferenceAudit:
  id (UUID v7), user_id (UUID), field (string), old_value, new_value, changed_at

Default constant:
  DefaultPeerVisibility = "private"  -- GDPR-friendly default.
```

## API contract

_No HTTP. Internal Go interface consumed by P-2 + CMP-3 readers._

```go
type Repository interface {
  Get(ctx, userID uuid.UUID) (UserPreference, error)  // returns ErrPreferenceNotFound if no row
  // Upsert+audit у single tx: if row exists і peer_visibility different → INSERT audit + UPDATE row.
  // If no row → INSERT row + INSERT audit (old=null).
  UpsertWithAudit(ctx, userID uuid.UUID, newVisibility string) (UserPreference, error)
}
```

## Acceptance criteria (GWT)

- [ ] **AC-p1-1 (factory + default):** `NewUserPreference(userID)` returns struct із peer_visibility='private'.
- [ ] **AC-p1-2 (Get not exists):** First call для user without row → `ErrPreferenceNotFound`.
- [ ] **AC-p1-3 (Upsert insert new):** First Upsert(userID, 'public') → INSERT pref row + INSERT audit row (old_value=null, new_value='public'). Returns pref.
- [ ] **AC-p1-4 (Upsert update existing — AC-13):** Existing row із 'private', Upsert(userID, 'public') → UPDATE row + INSERT audit (old='private', new='public'). updated_at оновлено.
- [ ] **AC-p1-5 (Upsert idempotent no-change):** Existing 'public', Upsert('public') → no UPDATE, no audit row (idempotent).
- [ ] **AC-p1-6 (transactional consistency):** Audit + pref оновлення в одній transaction — failure відкатує обидва.
- [ ] **AC-p1-7 (sentinels):** `ErrPreferenceNotFound`, `ErrInvalidPreference` — exported.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/preferences/domain/preference.go` + `audit.go` + `errors.go`.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/preferences/ports/repository.go`.
- [ ] Step 3 — Створити `beer-lms-api/internal/modules/preferences/infra/postgres_preference_repo.go`. Constructor: `NewPostgresPreferenceRepository(db *database.DB)`.
- [ ] Step 4 — Реалізувати `Get` (SELECT) + `UpsertWithAudit` (BEGIN; SELECT current; if different → INSERT audit + UPSERT pref; COMMIT).
- [ ] Step 5 — Юніт-тести domain + integration tests (testcontainers): AC-p1-1..AC-p1-7.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Concurrent Upsert із different values for same user | Row-lock на SELECT-for-update; перший win, другий бачить оновлений current — створить ще одну audit row якщо знов інше. Acceptable. |
| Upsert із 'invalid' value | Repo throws `ErrInvalidPreference` (handler-side validation primary; repo — defense-in-depth). |
| User_id deleted (FK) | ON DELETE CASCADE з users — auto-cleanup pref + audit. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests; coverage ≥ 85%.
- [ ] `go vet` + `golangci-lint run` clean.
- [ ] PR linked back to `tasks/P-1-domain-and-repo-preferences.md`.
- [ ] `tracker.md` оновлено: status `done`.
