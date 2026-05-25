---
status: Draft
owner: "<Tech Lead name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "14"
ticket: "<ticket-id>"
---

# Claude execution context — <feature>

<!-- Stage 14 → see SDLC/plugin/skills/prep-context/SKILL.md -->
<!-- Prefix for the Claude session for this feature / task. -->

## Goal
<1 sentence: what Claude should do in this session.>

## Scope
- <specifically, which tasks from task-breakdown>

## Files to read (in order)
1. [SPEC.md](SPEC.md) — sections <N>
2. [architecture-brief.md](architecture-brief.md) — module boundaries / runtime / ADR index (or `sad.md` in v3.3+ projects)
3. [adr/](adr/) — relevant Accepted ADRs
4. [task-breakdown.md](task-breakdown.md) — task scope (or `tasks/_epic.md` in tasks/-layout projects)
5. <code path 1>
6. <code path 2>

## Hard Rules
1. <rule 1 — specific>
2. <rule 2>
3. <rule 3>

## Commands
- Test: `<make test>` (have to be green before commit)
- Lint: `<make lint>`
- Format: `<make fmt>`
- Run locally: `<docker compose up -d && make run>`

## Out of scope
- <Do NOT touch `<module/Y>`>
- <Do NOT change API contract without an ADR>
- <Do NOT add new dependencies without discussion>

## Acceptance
PR is considered ready when:
- [ ] All AC from [SPEC](SPEC.md) §5 covered by tests (and the corresponding `tasks/<task>.md` row in `tasks/tracker.md` is marked done).
- [ ] CI green.
- [ ] Lint pass.
- [ ] CHANGELOG entry added.
- [ ] No new dependencies without an ADR.
