---
id: CMP-4
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: completions
blocks: [E-2]
blocked_by: [CMP-3, L-4]
status: todo
context_budget: ~2000 tokens
created: 2026-05-25
prd_refs: [AC-14, AC-15]
sad_refs: ["§6 US-08"]
openapi_paths: ["GET /lessons/{id}"]
adr_refs: []
---

# CMP-4 · Extend `GET /lessons/{id}` response with `peer_completion` field

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMP-3 (peer-blob service), L-4 (existing handler для extend).
- **Блокує:** E-2 (E2E peer-signal flow assert).
- **Чому в цій хвилі:** маленький extension до L-4. Split з L-4 щоб уникнути cross-aggregate dep у Wave 3.

## Why (user story)

As a `member`, I want `peer_completion` field на `GET /lessons/{id}` response with count, recent_completers, my_completed, so that lesson page показує social proof + my-progress indicator.

PRD US-08. AC-14 / AC-15.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-08-peer-completion-signal]]
- 🗄  Data delta:  none — read-only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `LessonWithBlocks` із `peer_completion`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-14, AC-15

## Data delta

```
NO writes.
```

## API contract

```
GET /lessons/{id}
  + injects: peer_completion: PeerCompletionSignal (per AC-14 shape)
  Conditions:
    - Returned ONLY якщо lesson.status == 'published'.
    - draft lesson — поле omit (мала причина показувати peer-signal на draft, який мало хто бачить).
```

## Acceptance criteria (GWT)

- [ ] **AC-cmp4-1 (peer_completion present on published):** Given GET /lessons/{published_id}, when call, then response містить поле `peer_completion: {count, recent_completers, my_completed}`.
- [ ] **AC-cmp4-2 (peer_completion absent on draft):** Given draft lesson visible to caller (owner), when GET, then response — без `peer_completion` поля.
- [ ] **AC-cmp4-3 (threshold passed through — AC-15):** Given count=2, when GET, then `peer_completion.count=null, recent_completers=[]`.
- [ ] **AC-cmp4-4 (my_completed reflects caller):** Caller A has completion, B has not. GET as A → my_completed=true; GET as B → false (CMP-3 service handles correctness).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — У L-4 handler/service `GetLessonWithBlocks` додати inject of `PeerBlobService` (DI).
- [ ] Step 2 — Flow:
   1. Existing logic для fetch lesson + blocks + visibility check.
   2. Якщо lesson.status == 'published' → `peerBlob, err := peerSvc.GetForLesson(orgID, userID, lessonID)` → on err — log warning + omit field (no fail).
   3. Compose response: вкладений `peer_completion` field тільки якщо отримано signal.
- [ ] Step 3 — Тести: AC-cmp4-1..AC-cmp4-4 + golden response shape.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `peerSvc` returns err (Redis down + DB issue) | Log warning, omit `peer_completion` field; lesson read still returns 200. |
| Lesson is draft + caller is owner | Field omitted (AC-cmp4-2). |
| Caller is admin viewing draft | Field omitted (consistent with AC-cmp4-2). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler test updated to cover new field + golden response with/without peer_completion.
- [ ] OpenAPI Swagger UI відображає `LessonWithBlocks` шапу.
- [ ] PR linked back to `tasks/CMP-4-extend-get-lesson-with-peer-signal.md`.
- [ ] `tracker.md` оновлено: status `done`.
