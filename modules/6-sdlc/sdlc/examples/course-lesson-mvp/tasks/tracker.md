---
type: tracker
feature: course-lesson-mvp
iteration: 2
updated_at: 2026-05-25
---

# Tracker — course-lesson-mvp (iter 2)

Flat status for impl-agent polling. Pick the lowest-ID story у Wave order with `status: todo` and `blocked_by` clear of any non-`done` story.

| Story | Wave | Status | Blocked by | Estimate |
|---|---|---|---|---|
| **MIG-1** (migrations 000020-000022, commit `931deca`) | 0 | **done** | — | — |
| [[F-1-checkers-is-methodist-is-admin\|F-1]] | 1 | todo | — | 0.5d |
| [[F-2-outbox-infrastructure\|F-2]] | 1 | todo | — | 1d |
| [[F-3-redis-rate-limit-helper\|F-3]] | 1 | todo | — | 0.5d |
| [[F-4-redis-idempotency-helper\|F-4]] | 1 | todo | — | 0.5d |
| [[C-1-domain-course\|C-1]] | 2 | todo | F-1 | 0.5d |
| [[C-2-postgres-course-repo\|C-2]] | 2 | todo | F-1, C-1 | 1d |
| [[L-1-domain-lesson-block\|L-1]] | 2 | todo | F-1 | 1d |
| [[L-2-postgres-lesson-repo\|L-2]] | 2 | todo | F-1, L-1 | 1.5d |
| [[C-3-post-courses-handler\|C-3]] | 3 | todo | C-2, F-3 | 0.75d |
| [[C-4-get-courses-handlers\|C-4]] | 3 | todo | C-2 | 0.75d |
| [[C-5-post-courses-publish-handler\|C-5]] | 3 | todo | C-2, L-2, F-2, F-4 | 1d |
| [[C-6-patch-courses-reorder-handler\|C-6]] | 3 | todo | C-2, L-2 | 0.5d |
| [[L-3-post-course-lessons-handler\|L-3]] | 3 | todo | L-2, C-2 | 0.75d |
| [[L-4-get-lessons-handlers\|L-4]] | 3 | todo | L-2 | 0.75d |
| [[L-5-post-blocks-handler\|L-5]] | 3 | todo | L-2 | 0.5d |
| [[L-6-post-lessons-publish-handler\|L-6]] | 3 | todo | L-2, F-2, F-4 | 1d |
| [[CMP-1-domain-and-repo-completions\|CMP-1]] | 4 | todo | L-2 | 0.5d |
| [[CMP-2-post-completion-handler\|CMP-2]] | 4 | todo | CMP-1 | 0.5d |
| [[CMP-3-peer-blob-aggregation-cache\|CMP-3]] | 4 | todo | CMP-1, P-1 | 1d |
| [[CMP-4-extend-get-lesson-with-peer-signal\|CMP-4]] | 4 | todo | CMP-3, L-4 | 0.5d |
| [[P-1-domain-and-repo-preferences\|P-1]] | 4 | todo | F-1 | 0.5d |
| [[P-2-preferences-handlers\|P-2]] | 4 | todo | P-1 | 0.75d |
| [[CMT-1-domain-and-repo-comments\|CMT-1]] | 4 | todo | L-2 | 0.5d |
| [[CMT-2-post-comment-handler\|CMT-2]] | 4 | todo | CMT-1, F-3 | 0.75d |
| [[CMT-3-list-comments-handler\|CMT-3]] | 4 | todo | CMT-1 | 0.5d |
| [[CMT-4-hide-comment-handler\|CMT-4]] | 4 | todo | CMT-1, F-1 | 0.5d |
| [[E-1-e2e-course-lesson-lifecycle\|E-1]] | 5 | todo | C-3, C-4, C-5, L-3, L-4, L-5, L-6 | 0.5d |
| [[E-2-e2e-peer-signal-and-preferences\|E-2]] | 5 | todo | CMP-4, P-2 | 0.75d |
| [[E-3-e2e-comments-moderation\|E-3]] | 5 | todo | CMT-2, CMT-3, CMT-4 | 0.5d |

## Status legend

- `todo` — ready to claim once `blocked_by` clears.
- `wip` — claimed by impl-agent or human; do not pick.
- `done` — merged. Unblocks anything that listed this story у `blocked_by`.
- `blocked` — impl-agent or human reported issue. See story file footer для note.

## Progress

- Total: 1/30 stories done (MIG-1 — historic, already merged)
- Wave 0 (historic): 1/1 done (MIG-1)
- Wave 1: 0/4 done (F-1, F-2, F-3, F-4)
- Wave 2: 0/4 done (C-1, C-2, L-1, L-2)
- Wave 3: 0/8 done (C-3, C-4, C-5, C-6, L-3, L-4, L-5, L-6)
- Wave 4: 0/10 done (CMP-1..4, P-1, P-2, CMT-1..4)
- Wave 5: 0/3 done (E-1, E-2, E-3)

## Next runnable

Pick **F-1**, **F-2**, **F-3**, або **F-4** (Wave 1 foundation, no blockers; all parallel).

Sequential humans recommended order:
1. **F-3** + **F-4** (Redis helpers — fastest, no migration touch).
2. **F-1** (checkers; depends on `is_admin` column verification).
3. **F-2** (outbox; includes new migration 000023, longest of Wave 1).

Parallel fan-out (2-4 impl-agents): start всі чотири foundation stories simultaneously.

## Notes

- **MIG-1** — not a TODO. Schema migrations 000020-000022 уже у репо (commit `931deca`, 2026-05-24). Listed для traceability у coverage matrix; no PR expected.
- **Migration 000023** (outbox_events) — NEW, owned by F-2.
- **Stale skill warning:** `sdlc:break-tasks` skill (як of 2026-05-25) refuses без `implementation-pack.md`, який було видалено у commit `ebe0bbd`. Цей tracker регенеровано вручну поза скилом; меta-задача оновити skill — окрема (out of scope).
