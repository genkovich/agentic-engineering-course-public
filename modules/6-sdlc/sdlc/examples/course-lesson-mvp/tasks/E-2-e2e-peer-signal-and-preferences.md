---
id: E-2
epic: course-lesson-mvp
project: BeerLMS
wave: 5
priority: Must
estimate: 0.75d
aggregate: e2e
blocks: []
blocked_by: [CMP-4, P-2]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-11, AC-12, AC-13, AC-14, AC-15]
sad_refs: ["§6 US-06", "§6 US-07", "§6 US-08"]
openapi_paths: []
adr_refs: []
---

# E-2 · E2E peer-signal + preferences + completion

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 5

## Місце в послідовності

- **Блокується:** CMP-4 (peer-signal in GET response), P-2 (preferences handlers).
- **Блокує:** нічим.
- **Чому в цій хвилі:** end-to-end privacy assertion з threshold логікою.

## Why (user story)

As a release engineer, I want a black-box test що демонструє: member marks complete → peer-signal на GET /lessons/{id} відображає completion → public-opt-in member з'являється у recent_completers → privacy threshold (`count<3`) фіксує `count=null` при <3 completions, so that privacy invariants assert-ються end-to-end.

PRD ACs: AC-11 (completion happy), AC-12 (draft 404), AC-13 (preferences PATCH + audit), AC-14 (peer-blob shape), AC-15 (anti-fingerprinting threshold).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-06-completelesson]], [[../sad.md#us-07-updatepreferences]], [[../sad.md#us-08-peer-completion-signal]]
- 🗄  Data delta:  none.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/completion`, `GET /me/preferences`, `PATCH /me/preferences`, `GET /lessons/{id}` (with peer_completion)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-11, AC-12, AC-13, AC-14, AC-15

## Data delta

```
NO new tables. Seeds: 1 org з 4 members + 1 methodist + 1 published lesson із 1 block.
```

## Acceptance criteria (GWT)

- [ ] **AC-e2-1 (completion happy + my_completed):** Given member A, published lesson, when POST /lessons/{l}/completion + GET /lessons/{l}, then peer_completion.my_completed=true.
- [ ] **AC-e2-2 (threshold fires при count<3 — AC-15):** Given 2 completions (A, B), when GET /lessons/{l} as third member C (no completion), then peer_completion.count=null, recent_completers=[]. my_completed=false.
- [ ] **AC-e2-3 (threshold released при count=3):** Given 3 completions, when GET as fourth member, then count=3 returned. recent_completers — empty (всі private — default), або contains opt-in users.
- [ ] **AC-e2-4 (PATCH preferences toggles visibility — AC-13):** Given member D updates `peer_visibility:public`, completes lesson, when other member GETs /lessons/{l}, then D з'являється у recent_completers. Audit row created.
- [ ] **AC-e2-5 (draft lesson completion forbidden — AC-12):** Given draft lesson, when POST /lessons/{draft_l}/completion, then 404.
- [ ] **AC-e2-6 (idempotent completion — AC-11):** First POST → 201; repeat POST → 200 із same completed_at.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/test/e2e/peer_signal_test.go`.
- [ ] Step 2 — Seed: 1 org + 4 members + 1 methodist + 1 published lesson + 1 block.
- [ ] Step 3 — Scenarios per AC.
- [ ] Step 4 — Verify Redis cache hit: in AC-e2-1, second GET should not re-hit DB (use spy / metrics).

## Edge cases

| Кейс | Поведінка |
|---|---|
| Redis cache може показувати stale 60s | Test wait > 60s або direct cache invalidation у test helper. Обираємо direct invalidation для speed. |
| Audit row check | SQL query `SELECT count(*) FROM user_preference_audit WHERE user_id=...` після AC-e2-4 → ≥1. |
| Test flake on TZ | Use UTC у assertions. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] CI green на pre-merge.
- [ ] PR linked back to `tasks/E-2-e2e-peer-signal-and-preferences.md`.
- [ ] `tracker.md` оновлено: status `done`.
