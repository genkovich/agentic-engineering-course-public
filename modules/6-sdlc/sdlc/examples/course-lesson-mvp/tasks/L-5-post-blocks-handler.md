---
id: L-5
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.5d
aggregate: lessons
blocks: [E-1]
blocked_by: [L-2]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-03]
sad_refs: ["§6 US-02 block sub-flow"]
openapi_paths: ["POST /lessons/{id}/blocks"]
adr_refs: [ADR-0001]
---

# L-5 · `POST /lessons/{id}/blocks` handler (addBlock — polymorphic payload validation)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** L-2 (`AddBlock` repo method).
- **Блокує:** E-1.
- **Чому в цій хвилі:** smallest handler — quick parallel pickup.

## Why (user story)

As a `methodist`, I want to add content blocks (`text` / `video_embed` / `image` / `code`) to my lesson with polymorphic payload per type, so that lesson body є multi-format.

PRD US-02 (block-based body). ADR-0001 (polymorphic payload).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-02-addlesson-block-based]] (sub-flow)
- 🗄  Data delta:  INSERT into `lesson_blocks`.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/blocks` (`addBlock`), `AddBlockRequest`, `LessonBlock`
- 📜 Relevant ADR: [[../adr/0001-content-storage-strategy|ADR-0001]] (polymorphic payload per block_type)
- 📋 PRD ACs:      AC-03 (block у body), derived from openapi + ADR-0001

## Data delta

```
INSERT-only. UNIQUE(lesson_id, sequence) enforced у DB (MIG-1).
```

## API contract

```
POST /lessons/{id}/blocks
  AuthN: BearerAuth
  AuthZ: orgmw + IsMethodist + caller == course_owner of parent lesson's course
  Body: AddBlockRequest {block_type, sequence?, payload}
  Response:
    201 LessonBlock
    400 lesson.invalid_payload          (payload shape mismatch per block_type)
    401 auth.unauthorized
    403 course.not_methodist
    404 lesson.not_found
    409 lesson.block_sequence_conflict
```

## Acceptance criteria (GWT)

- [ ] **AC-l5-1 (happy — text):** Given valid `{block_type:"text", payload:{content:"hi"}}`, methodist owner, when POST, then 201 + LessonBlock (sequence assigned).
- [ ] **AC-l5-2 (happy — video_embed):** Given `{block_type:"video_embed", payload:{url:"https://youtube.com/...", provider:"youtube"}}`, when POST, then 201.
- [ ] **AC-l5-3 (happy — image):** `{block_type:"image", payload:{url:"...", alt:"..."}}` → 201.
- [ ] **AC-l5-4 (happy — code):** `{block_type:"code", payload:{language:"go", content:"package main"}}` → 201.
- [ ] **AC-l5-5 (invalid block_type):** Given block_type=`bogus`, when POST, then 400 `lesson.invalid_payload`.
- [ ] **AC-l5-6 (missing required payload key per type):** Given `{block_type:"text", payload:{}}` (без content), when POST, then 400 `lesson.invalid_payload`. Same для video_embed без url, image без url, code без language/content.
- [ ] **AC-l5-7 (block sequence conflict):** Given block із sequence=2 existing, when POST з explicit sequence=2, then 409 `lesson.block_sequence_conflict`.
- [ ] **AC-l5-8 (non-methodist or non-owner):** Same as L-3 collapse — 404 or 403 пер matrix.
- [ ] **AC-l5-9 (cross-org lesson):** 404 `lesson.not_found`.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `AddBlock(ctx, orgID, userID, lessonID, req AddBlockRequest) (LessonBlock, error)`.
- [ ] Step 2 — Validation layer для polymorphic payload — `validateBlockPayload(blockType, payload) error`. Кожен block_type → перевірка обов'язкових ключів (із ADR-0001 shape):
   - `text` → `content` (string, non-empty)
   - `video_embed` → `url` (string), `provider` (string)
   - `image` → `url` (string), `alt` (string, can be empty for decorative — TODO confirm)
   - `code` → `language` (string non-empty), `content` (string non-empty)
- [ ] Step 3 — Service flow: IsMethodist → fetch lesson (cross-aggregate get parent course → check owner) → validate payload → domain `NewBlock` → `lessonsRepo.AddBlock`.
- [ ] Step 4 — Handler `PostLessonBlocks(w, r)` — реєструвати path.
- [ ] Step 5 — Тести: AC-l5-1..AC-l5-9.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Lesson вже published | Допускаємо чи блокуємо? PRD §3 "Edit-after-publish out of scope". Обираємо: 409 `lesson.already_published` (handler-side check). |
| Payload із extra ключами понад required | Дозволяємо (`additionalProperties: true` per openapi); зберігаємо. |
| Payload — масив замість object | 400 `lesson.invalid_payload`. |
| Block_type у різних регістрах ("TEXT") | 400 — enum case-sensitive. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] Per-block_type validation table — окремий unit test file.
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/L-5-post-blocks-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
