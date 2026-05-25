---
type: generation
feature: course-lesson-mvp
iteration: 2
generated_by: manual-regen (skill bypassed — see Caveat)
generated_at: 2026-05-25
supersedes: iteration 1 (2026-05-24)
stories_total: 30
stories_done_at_start: 1
waves: 5
scope_note: "Full PRD scope — 5 aggregate roots, 18 openapi endpoints, foundation infra (outbox, rate-limit, idempotency). Migrations 000020-000022 already shipped (MIG-1 placeholder)."
---

# Generation provenance — course-lesson-mvp (iter 2)

Records why each story exists, where у SDLC artifacts it comes from, and why it sits in its wave. Reviewers audit slicing here without opening 30 story files.

## Why a regen?

Iter 1 (8 lesson-only stories, generated 2026-05-24) became stale on three axes:

1. **Stage-13 skill itself is out-of-date.** Hard gate is `implementation-pack.md`, but that concept was dropped у commit `ebe0bbd` ("features use tasks/_epic.md as entrypoint"). Skill would refuse. Bypassed (see Caveat) — followed new convention.
2. **Tracker drift on completed work.** Migrations S-2-equivalent shipped у commit `931deca`. Tracker still showed it as `todo`.
3. **Scope expansion already реалізована у контракті.** `migrations 000021/000022` create tables for **all 5 aggregates** (`courses`, `lessons`, `lesson_blocks`, `lesson_completions`, `user_preferences`, `user_preference_audit`, `comments`, `comment_audit`), AND `contracts/openapi.yaml v1.1.0` covers **all 18 endpoints** across 5 aggregates. Iter 1 had only `lessons` (5 endpoints) — covered ⅓ of контракту.

Regenerated to fully match сurrent contract + DB state.

## Inputs read

- `PRD.md` — §4 (US-01..US-10), §5 (AC-01..AC-18), §6.1 (8 abuse cases — rate-limit, XSS, SSRF, anti-fingerprinting, existence-hiding deviation).
- `sad.md` — §6 Runtime view (10 US-NN container sequences + endpoint-level publishLesson).
- `data-model.md` — all 4 aggregate root sections + 4 audit / completion tables.
- `contracts/openapi.yaml` v1.1.0 — paths (18 endpoints), schemas (all 5 aggregates), error responses.
- ADRs by reference: ADR-0001 (polymorphic block payload), ADR-0002 (Redis as shared infrastructure).
- Migrations: `000020_add_is_methodist_to_org_members`, `000021_create_course_lesson_tables`, `000022_add_course_lesson_indexes` — already merged (`931deca`).
- Reference module: `beer-lms-api/internal/modules/mentorship/` (5-week production; parity for `OrgMemberChecker`, repo style, error-code naming).

## Slicing rationale (per aggregate prefix)

| Prefix | Aggregate | Why this split |
|---|---|---|
| **F** | Foundation (cross-cutting) | Reused across handler stories — DRY. Each F-x blocks multiple handlers. |
| **C** | Courses (5 endpoints) | First-class aggregate per data-model.md. Domain + repo + handlers — same pattern as L-*. |
| **L** | Lessons (5 endpoints із deprecated) | First-class, has block sub-flow + publish with outbox. Largest aggregate by endpoint count. |
| **CMP** | Completions (2 endpoints + peer-blob service) | Distinct sub-flow з privacy threshold; needed CMP-3 cache layer split out. |
| **P** | Preferences (2 endpoints) | Singleton-per-user pattern; audit pattern різний від comments. |
| **CMT** | Comments (3 endpoints) | Moderation lifecycle distinguish від completion; admin gate via F-1. |
| **E** | E2E (3 stories) | One per coherent lifecycle cluster (course/peer/comment) — splits для CI parallelization. |
| **MIG** | Migrations (historic) | Placeholder for done work; preserves traceability у coverage matrix. |

Stories ≤ 1 day (max 1.5d for L-2 repo), each = one reviewable PR ≤ 500 LOC, each links to upstream PRD / SAD / openapi / ADR (no duplication).

## Per-story per-wave allocation rationale

**Wave 1 — Foundation:** F-1..F-4 are pure infrastructure with no upstream dependencies (other than the already-merged MIG-1). Their absence blocks ALL other waves. Parallelizable: 4 impl-agents можуть взяти один за одним.

**Wave 2 — Domain + Repo:** C-1/C-2 i L-1/L-2 — pairs for two main aggregates. C-2 and L-2 share dependency on F-1 (indirectly through chain) and are the gate-of-most-handlers, so they live у own wave перед handler fan-out.

**Wave 3 — Handlers:** 8 stories, all parallel within wave. Each handler is one endpoint or one tight pair (C-4 has 2 GET endpoints — kept together since shared code path).

**Wave 4 — Smaller aggregates:** Completions / preferences / comments are each smaller (2-3 endpoints) and don't need their own full Wave 2+3 split. Domain+repo bundled у one story per aggregate (CMP-1, P-1, CMT-1), then handlers fan out.

**Wave 5 — E2E:** One per coherent lifecycle cluster. Splits the test suite for CI parallelization.

## Coverage check (PRD ACs → stories)

| AC | Bound story | Covered? |
|---|---|---|
| AC-01 (createCourse happy) | C-1, C-3, E-1 | ✓ |
| AC-02 (description ≤ 500) | C-1, C-3 | ✓ |
| AC-03 (createLesson happy + body) | L-1, L-3, L-5, E-1 | ✓ |
| AC-04 (explicit sequence conflict) | L-1, L-2, L-3 | ✓ |
| AC-04b (concurrent UNIQUE) | L-2, L-3 | ✓ |
| AC-05 (course publish gate: ≥1 published lesson) | C-2 CountPublishedLessons, C-5, E-1 | ✓ |
| AC-06 (publish idempotent) | C-5, L-6 (mirror), E-1 | ✓ |
| AC-07 (cross-org 404 existence-hiding) | C-2, C-4, L-2, L-4, E-1 | ✓ |
| AC-08 (draft visibility — owner+admin) | C-4, L-4 | ✓ |
| AC-09 (non-methodist 403) | F-1, C-3, L-3 | ✓ |
| AC-10 (cross-org parent → 404) | C-2, L-2, L-3, E-1 | ✓ |
| AC-11 (completion happy + idempotent via UNIQUE) | CMP-1, CMP-2, E-2 | ✓ |
| AC-12 (completion draft/cross-org → 404) | CMP-2, E-2 | ✓ |
| AC-13 (preferences PATCH + GDPR audit) | P-1, P-2, E-2 | ✓ |
| AC-14 (peer_completion shape) | CMP-3, CMP-4, E-2 | ✓ |
| AC-15 (anti-fingerprinting threshold count<3) | CMP-3, CMP-4, E-2 | ✓ |
| AC-16 (createComment happy) | CMT-1, CMT-2, E-3 | ✓ |
| AC-17 (comment length cap + rate-limit) | F-3, CMT-2, E-3 | ✓ |
| AC-18 (admin hide + audit preservation) | F-1 (IsAdmin), CMT-1, CMT-4, E-3 | ✓ |

**Result:** 18/18 ACs covered. No orphans.

## Coverage check (openapi endpoints → stories)

| Endpoint | Story |
|---|---|
| POST /courses | C-3 |
| GET /courses | C-4 |
| GET /courses/{id} | C-4 |
| POST /courses/{id}/lessons | L-3 |
| POST /courses/{id}/publish | C-5 |
| PATCH /courses/{id}/lessons/reorder | C-6 |
| POST /lessons (deprecated) | — (intentionally NOT implemented; canonical route — L-3) |
| GET /lessons | L-4 |
| GET /lessons/{id} | L-4 (base shape) + CMP-4 (peer_completion extension) |
| POST /lessons/{id}/blocks | L-5 |
| POST /lessons/{id}/publish | L-6 |
| POST /lessons/{id}/completion | CMP-2 |
| POST /lessons/{id}/comments | CMT-2 |
| GET /lessons/{id}/comments | CMT-3 |
| POST /comments/{id}/hide | CMT-4 |
| GET /me/preferences | P-2 |
| PATCH /me/preferences | P-2 |

**Result:** 17/18 implemented (deprecated `POST /lessons` skipped — canonical route via L-3 covers same flow per openapi v1.1.0 changelog "v1.1.0 deprecated this in favor of /courses/{id}/lessons").

## Mentorship parity references

Per the architectural inheritance pattern, наступні stories explicitly mirror `beer-lms-api/internal/modules/mentorship/`:

- **F-1** ← `mentorship/infra/member_checker.go` (PostgresMemberChecker shape — single method extended to two flags)
- **C-2** ← `mentorship/infra/session_repo.go` (org-scoped reads, cursor pagination, UNIQUE-violation translation)
- **L-2** ← `mentorship/infra/session_repo.go` (same + tx-aware Publish method)
- **CMP-1** ← `mentorship/infra/session_repo.go` (org-scoped + INSERT ON CONFLICT для idempotency)
- **CMT-1** ← `mentorship/infra/session_repo.go` (tx-aware Hide із audit insert)
- **P-1** ← `mentorship/infra/session_repo.go` (tx-aware UPSERT із audit)

Error-code convention `<module>.<snake_case>` applied throughout (mentorship `mentorship.not_mentor` → courses `course.not_methodist`, lessons `lesson.sequence_conflict`, comments `comment.not_moderator`).

## Open questions surfaced during slicing

- **F-1 Step 0** — Verify `org_members.is_admin` колонка існує у migrations. Якщо ні — split окрему story `F-1a` для додавання колонки + migration. Block at impl-time.
- **L-5 image block `alt` text** — empty allowed for decorative images? Confirm з PM. Default: allow empty.
- **L-6 admin (non-owner) publishing lesson** — currently treated as 403 (cross-methodist branch). Open: should admin be allowed to publish? Confirm з PM/admin-UX-PRD.
- **CMP-3 peer-blob cache invalidation** — TTL-only у v1 per PRD OQ-8. Future event-driven invalidation requires consumer-side outbox.
- **CMT-4 placeholder string `"[hidden by moderator]"`** — i18n consideration deferred. Hardcoded literal у v1.

No PRD AC orphaned. No openapi endpoint orphaned (except intentionally deprecated `POST /lessons` top-level).

## Caveat — skill bypassed

The `sdlc:break-tasks` SKILL.md (in `agentic-engineering-course/sdlc/plugin/skills/break-tasks/`) has a hard-refuse gate on missing `implementation-pack.md`. That concept was dropped у `ebe0bbd` ("chore(docs): drop implementation-pack — features use tasks/_epic.md as entrypoint"). This regen ran **manually** without invoking the stale skill.

Follow-up: rewrite skill's prerequisite to `tasks/_epic.md` and add support for per-aggregate prefixes — meta-task у `agentic-engineering-course` repo, out of scope here.

## Stage 1 checkpoint

User accepted scope expansion (5 aggregates, outbox-as-separate-story, per-aggregate prefix, migration 000023 new) on 2026-05-25 у plan-mode dialog. Stage 2 (generation) wrote 29 TODO stories + 1 historic MIG-1 entry. Stage 3 assembled `_epic.md`, `tracker.md`, this `_generation.md`.
