---
name: classify-size
description: >
  Use to classify a feature into XS/S/M/L/XL and write docs/features/{slug}/.size
  so phase wrappers can skip arc42/c4-component/deployment/test-plan/
  security-review per MVP-vs-Full matrix. Triggers on "classify size",
  "feature size", "XS or M for {slug}?", "/sdlc-classify-size {slug}",
  "size {slug}". Asks 4 AskUserQuestion (PR count / time / new module-API-
  migration / breaking changes) → maps to XS/S/M/L/XL → writes a one-line file
  docs/features/{slug}/.size. Syncs with PRD.md frontmatter `feature_size:` if
  present (warns on conflict). Output: docs/features/{slug}/.size + (opt.) PRD
  frontmatter update.
---

# Skill: classify-size (Feature size classifier)

Atomic skill — classifies a feature into XS/S/M/L/XL and fixes it in `docs/features/<slug>/.size`. Single source for size-aware skip-logic across all phase wrappers (`sdlc:design`, `sdlc:detail`, `sdlc:impl-prep`, `sdlc:ship`).

Without `.size` — wrappers default to `M` (full set). With `.size=XS/S` — arc42, c4-component, deployment, separate test-plan, security-review are skipped (per `00-overview/mvp-vs-full.md`).

## Owner

PM or Tech Lead (driver of the intake phase). Architect can escalate from S → M if they see a new subsystem.

## When to use

- «classify size for <slug>», «feature size <slug>», «is this XS or M?».
- `/sdlc-classify-size <slug>` as explicit invocation.
- A wrapper (`sdlc:design`, etc.) asks for size if the `.size` file is missing.
- Soon after intake (idea-brief + brainstorm), before the design phase.
- Skip if `.size` already exists and the feature scope hasn't changed — suggest edit, not overwrite.

## Inputs

- `<slug>` — feature slug.
- (Optional) `docs/features/<slug>/idea-brief.md` — for context (rough size from stage 01).

## Protocol

1. **Read context.** `test -f docs/features/<slug>/idea-brief.md` — if it exists, read §Rough size (XS/S/M/L/XL) as a starting hint. Not required — the skill works without idea-brief.
2. **Check existing.** `test -f docs/features/<slug>/.size`. Exists → read the current value, ask user: «.size is currently `<X>`. Reclassify?» On «no» — STOP.
3. **AskUserQuestion #1 (PR count).** «How many PRs will this feature take?» Options: `1 PR (typo, config, micro-fix)` / `2-5 PR (small feature)` / `5-15 PR (new module / epic)` / `15+ PR (cross-module / new subsystem)`.
4. **AskUserQuestion #2 (time).** «How much time to merge the main part?» Options: `up to 1 day` / `1 week` / `1-2 sprints` / `>1 month`.
5. **AskUserQuestion #3 (new module/API/migration).** «Does it touch a new module / new API / DB migration?» Options: `None of these` / `Yes, one of three` / `Yes, two of three` / `Yes, all three`.
6. **AskUserQuestion #4 (breaking changes).** «Will there be breaking changes for consumers (API, DB schema, contract)?» Options: `No` / `Yes, internal only` / `Yes, public clients`.
7. **Classify.** Mapping:
   - **XS**: Q1=1 PR + Q2=up to 1 day + Q3=No + Q4=No. (Typo, copy fix, config tweak.)
   - **S**: Q1=2-5 PR + Q2=1 week + Q3∈{No, one} + Q4∈{No, internal}. (Small feature.)
   - **M**: Q1=5-15 PR + Q2=1-2 sprints + Q3∈{one, two} + Q4∈{internal, public}. (New module / API.)
   - **L**: Q1=15+ PR + Q2=>1 month + Q3∈{two, all three} + Q4=public. (Cross-module.)
   - **XL**: All maximums, new subsystem. Ask the user explicitly: «requires a separate roadmap?» Yes → XL.
   - On edge cases — explain: «this is M because new API + 2 sprints, even though PR count is 6 — on the edge of S».
8. **Confirm with user.** AskUserQuestion: «Classifying as `<size>` (<short rationale>). Lock it in?» Options: `Yes` / `No, I want <X>` / `Reclassify`.
9. **Write `.size`.** `echo "<size>" > docs/features/<slug>/.size`. One line — only `XS` / `S` / `M` / `L` / `XL`. No comments, no frontmatter — plain text. Wrappers read via `cat docs/features/<slug>/.size`.
10. **Sync with PRD frontmatter (if exists).** `test -f docs/features/<slug>/PRD.md` → grep `feature_size:` in frontmatter.
    - Field exists with the same value → OK.
    - Field exists with a conflict → WARN user: «PRD frontmatter says `feature_size: M`, we classified as `S`. Which is correct?» Resolve → update one of the two.
    - Field missing → suggest adding `feature_size: <size>` to PRD.md frontmatter.
11. **Propose commit.** `size: <slug> classified as <size>` or as part of intake commit (if called from a wrapper).

## Questions for discussion

- How many PRs?
- How much time to merge?
- Does it touch a new module / API / migration?
- Breaking changes — internal or public?
- Edge cases — discuss with Tech Lead before locking.

## Definition of Done

- `docs/features/<slug>/.size` created with one of: XS / S / M / L / XL.
- User confirmed the classification (not silent).
- (If PRD exists) sync with `feature_size:` frontmatter is verified.
- Single commit proposal.

## Anti-patterns

- **Self-classify without user confirm.** Skill proposes — user confirms.
- **Optimistic classification.** «I think it's S, let's write S» without checking the 4 questions — in a week the feature turns out to be M and the skipped arc42 hurts.
- **Skip Q3/Q4.** Most important for distinguishing S vs M.
- **Overwrite existing `.size` without warning.** If it exists — ask.
- **Conflict in frontmatter.** If PRD frontmatter says otherwise — resolve, don't leave drift.
- **.size with comments / multi-line.** A simple one-liner — wrappers grep it cheaply.

## Template

The `.size` file has no template — it's created inline as one-line text:
```
S
```

## Example invocation

> **User:** «classify size rate-limiting-per-user»
>
> **Skill behavior:**
> 1. Reads `idea-brief.md` §Rough size = `S` (hint).
> 2. `.size` doesn't exist → continue.
> 3. Q1: «How many PRs?» User: `2-5 PR`.
> 4. Q2: «How much time?» User: `1 week`.
> 5. Q3: «New module/API/migration?» User: `Yes, one (new API endpoint)`.
> 6. Q4: «Breaking changes?» User: `Yes, internal only (response headers)`.
> 7. Classify: answers match S. Rationale: 1 API endpoint + 1 week + internal breaking.
> 8. Confirm: «Classifying as `S`. Lock it in?» User: `Yes`.
> 9. Write `docs/features/rate-limiting-per-user/.size` → `S`.
> 10. `PRD.md` doesn't exist yet (intake just finished) → skip sync.
> 11. Commit: `size: rate-limiting-per-user classified as S`.
