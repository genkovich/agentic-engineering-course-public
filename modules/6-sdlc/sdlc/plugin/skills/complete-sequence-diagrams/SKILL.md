---
name: complete-sequence-diagrams
description: >
  Use when the user wants to audit a SAD against PRD user stories and add
  sequence diagrams for every uncovered use case (not just the 3-5 critical
  ones). Triggers on "complete sequences for {slug}", "audit sequence coverage",
  "missing sequences", "sequence per US", "/sdlc-complete-sequences {slug}".
  Iterative: one use case at a time with user confirm. Output: Mermaid
  sequenceDiagram blocks appended/updated inline in
  docs/features/{slug}/sad.md §6 (Runtime view). Also handles single-flow ad-hoc
  draws (superset of legacy draw-sequence skill). Prerequisites:
  docs/features/{slug}/PRD.md (stage 03) + docs/features/{slug}/sad.md (stage 04) —
  hard refuse if missing.
---

# Skill: complete-sequence-diagrams

Auditor + completer for the Runtime view. Reads PRD user stories, cross-checks SAD §6, and adds Mermaid `sequenceDiagram` blocks for every US that does not yet have one. Iterative per use case (user confirms each diagram), validates Mermaid syntax with `mmdc`, flags ADR-worthy decisions, and adds async patterns (idempotency, retry, DLQ) where the flow is non-`localhost`.

Supersedes the legacy `draw-sequence` skill. For a single ad-hoc flow, invoke with `--flow <name>` (see "Single-flow mode" below).

## Owner

Tech Lead.

## When to use

- "complete sequences for <slug>", "audit sequence coverage for <slug>", "missing sequences for <slug>".
- After SAD has been written (stage 04) and at least the critical flows have been sketched. This skill closes the long tail of use cases — webhooks, scheduled jobs, third-party callbacks, cross-service flows.
- `/sdlc-complete-sequences <slug>` — explicit invocation.
- `/sdlc-complete-sequences <slug> --flow <name>` — single-flow ad-hoc draw (legacy `draw-sequence` use case).
- Skip if PRD has < 3 user stories or SAD §6 already references every US by name.

## Inputs

- `<slug>` — same as for PRD / SAD.
- **Gate (hard refuse if missing):**
  - `docs/features/<slug>/PRD.md` — user stories live in §4 as `US-N: <story>`.
  - `docs/features/<slug>/sad.md` — §6 Runtime view holds existing sequences (heading: `### US-N: <name>` per arc42 convention).
  - If either missing: STOP, suggest `sdlc:write-prd <slug>` or `sdlc:architecture-design <slug>`.

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md && test -f docs/features/<slug>/sad.md` → exit ≠ 0 = refuse with pointer to which prereq is missing.

2. **Inventory user stories from PRD §4.** Parse every `US-N:` heading. Build an internal list `[US-1, US-2, ...]` with title and primary actor.

3. **Cross-check SAD §6 coverage by heading match.** For each US-N: `grep -E "^### .*US-N\b" docs/features/<slug>/sad.md`. Build coverage table:
   - **Covered** — heading found, Mermaid block present.
   - **Missing** — no heading.
   - **Trivial** — auto-flagged (single hop UI → API → DB read, no business logic). Skipped by default; user can opt-in.

4. **Surface coverage report to user.** Markdown table with `US-N | Title | Status (Covered/Missing/Trivial) | Notes`. Ask user to confirm the list of "Missing" UCs to process. Trivial UCs are listed under a separate "Skipped — trivial" block; user can promote any back to "Missing".

5. **For each missing UC (iteratively, user confirms each):**

   a. **Classify sync vs async by PRD signals.** Look for keywords in PRD §4 acceptance criteria for this US: `webhook`, `cron`, `biweekly`, `scheduled`, `daily`, `external service`, `queue`, `event` → **async**. Otherwise → **sync**.

   b. **Identify actors from SAD §5 (Container view).** Parse Mermaid `C4Container` block. If async flow needs `Scheduler` / `Worker` / `External Service` and §5 has no such Container → **flag "new actor"** in the report; still draw the actor in sequence (don't block on §5 update).

   c. **Generate Mermaid `sequenceDiagram` block.** Template:
      ```mermaid
      sequenceDiagram
          autonumber
          participant U as User (Methodist)
          participant API as content-api
          participant DB as Postgres
          Note over U, API: Precondition: <state from PRD>
          U->>API: <action>
          API->>DB: <query>
          DB-->>API: <result>
          API-->>U: <response>
          Note over API, DB: writes <table.column> (see §6.4 ER)
          alt <error condition 1>
              API-->>U: 4xx <error code>
          else <error condition 2>
              DB-->>API: timeout
              API-->>U: 5xx <error code>
          end
          Note over U, API: Postcondition: <state from PRD>
      ```

   d. **Add async patterns to webhook + retry flows.** When async:
      - First step in handler: `check idempotency key`.
      - Retry budget in a `Note over Worker, External: retry up to N with exponential backoff`.
      - DLQ as an `alt` branch after N failed attempts.

   e. **Fold cache layer into a Note for performance-critical reads.** If PRD §5 lists a latency budget for this US (e.g., `p95 < 120ms`), do NOT draw a separate cache diagram. Add `Note over API, DB: dashboard hits Redis first; cache TTL 60s` inline.

   f. **Flag ADR potential.** If the flow involves a non-trivial architectural decision (`SAGA vs 2PC`, idempotency strategy choice, retry budget shape, polling vs push), do NOT auto-generate an ADR. Add to the final report under "ADR potential": `US-N: consider ADR for <topic>`.

   g. **Validate Mermaid syntax with `mmdc --parse-only`** (mandatory). Write the block to a temp file and run `mmdc -i <tmp> --parse-only` (or equivalent). If parse fails → fix one-shot or surface to user.

   h. **Show to user, ask confirm.** Render the diagram block (mention the `mmdc` validation passed). User responds `ok` / `redo` / `skip`. On `redo`, accept the user's note and regenerate.

6. **Append confirmed blocks to SAD §6.** Insert with heading `### US-N: <title from PRD>`. Preserve order by US-N. Do NOT touch existing sequences.

7. **Examples-as-corrigendum (learning loop, partial).** After the session, if the user has hand-edited any generated block, optionally copy the diff into `docs/features/<slug>/_audit/_examples/US-N.md` as a few-shot example for the next run. Opt-in: ask once at the end.

8. **Final summary report.** Append to `docs/features/<slug>/_audit/sequences-<timestamp>.md`:
   - **Added:** list of US-N + 1-line summary.
   - **Skipped (trivial):** list with reason.
   - **New actors flagged:** list (so §5 Container view can be updated).
   - **ADR potential:** list of decisions to capture as ADRs.

9. **Self-check against DoD.** Every PRD US is either Covered, explicitly Trivial, or has a fresh Mermaid block in §6. mmdc passed on all new blocks.

10. **Propose commit.** `06: complete sequence coverage for <slug>` + next owner (Backend Lead → stage 07 data-model / generate-data-model).

## Single-flow mode

`/sdlc-complete-sequences <slug> --flow <name>` — draws one sequence on demand (legacy `draw-sequence` use case). Skips inventory + coverage; goes straight to step 5 (classify → actors → generate → validate → confirm). Writes inline into SAD §6 under a `### Ad-hoc: <name>` (or `### Endpoint-level: <method path>` for HTTP-verb-aware flows) heading. No coverage report. No separate file is created — the new convention is inline-only.

## Inputs the skill does NOT touch

- **Deployment view (§7).** Out of scope. If a sequence requires a new node (e.g., `Scheduler pod`), flag in the report; the user updates §7 separately.
- **API contract method names.** If `define-api` already produced `openapi.yaml`, the skill reuses those operation names; otherwise leaves a TODO comment `<!-- TODO: align with openapi.yaml -->`.
- **C4 container/component diagrams.** Only reads them for actor list; does not modify.

## Questions for discussion

- Which UCs are genuinely trivial (single hop with no business logic) and which look trivial but need a sequence anyway (e.g., a list endpoint behind a cache)?
- Where does the flow cross a `non-localhost` boundary (webhook in, third-party out, queue between services)? Add async patterns there.
- Is there an idempotency key story for every mutating async flow?
- Which decisions in this flow deserve an ADR (SAGA, retry budget, polling vs push)?
- For performance-critical reads — fold into a Note or split into a separate cache-aware sequence?

## Definition of Done

- Every PRD US is Covered, explicitly Trivial, or has a fresh sequence in SAD §6.
- All new Mermaid blocks pass `mmdc --parse-only`.
- Audit report committed to `_audit/sequences-<timestamp>.md`.

## Anti-patterns

- **Draw-without-coverage.** Adding sequences for the same 3 happy paths over and over while webhook / cron / cross-service flows have nothing. The whole point of this skill is the long tail.
- **Auto-generated ADRs.** This skill only flags decisions; ADRs are written by a human (or `decide-adr` skill).
- **One mega-sequence for the whole feature.** Split per US. Cross-US flows get their own `### Cross-cutting: <name>` heading.
- **Drawing happy path only when PRD lists explicit error AC.** Each US gets happy + 2-3 errors from PRD acceptance criteria.
- **New actors silently added to sequences without flagging §5.** The Container view is the source of truth; the report MUST list new actors.
- **Modifying existing covered sequences.** Hard rule: this skill is additive only. If user wants to edit existing, that is a manual diff (or run with `--flow <name>` against that US specifically).

## Template

→ [./templates/seq-flow.md](./templates/seq-flow.md) — the single-flow shape, embedded inline in SAD §6.

## Example invocation

> **User:** "complete sequences for course-lesson-mvp"
>
> **Skill behavior:**
> 1. `test -f docs/features/course-lesson-mvp/PRD.md && test -f docs/features/course-lesson-mvp/sad.md` → OK.
> 2. Inventory: 5 user stories — US-1 createLesson, US-2 listLessons, US-3 biweeklyReminder, US-4 publishLesson, US-5 viewLearnerDashboard.
> 3. Coverage table:
>    - US-1 — Covered (heading `### US-1: createLesson` in §6).
>    - US-2 — Trivial (single GET, no business logic; user can promote).
>    - US-3 — Missing (async, biweekly cron).
>    - US-4 — Covered.
>    - US-5 — Missing (performance budget p95 < 120ms).
> 4. User confirms: process US-3 + US-5.
> 5. **US-3 (async):** classify async (keyword `biweekly`). Actors: Scheduler (NEW — flagged), Worker, content-api, notification-service, DB. Generates sequence with idempotency key check, retry budget Note, DLQ alt. mmdc OK. ADR potential: `consider ADR for retry budget shape`. User confirms.
> 6. **US-5 (sync, perf-critical):** classify sync. Actors from §5: web-app, content-api, DB. Generates sequence with `Note over API, DB: dashboard hits Redis first; cache TTL 60s` folded inline. mmdc OK. User confirms.
> 7. Appends both blocks to sad.md §6 under headings `### US-3: biweeklyReminder` and `### US-5: viewLearnerDashboard`.
> 8. Writes `_audit/sequences-2026-05-23.md`: added US-3, US-5; trivial US-2; new actor Scheduler; ADR potential for US-3 retry shape.
> 9. Self-check DoD → 5/5 US accounted for.
> 10. Commit suggestion: `06: complete sequence coverage for course-lesson-mvp`.
