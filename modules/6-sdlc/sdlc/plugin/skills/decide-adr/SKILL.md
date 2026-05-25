---
name: decide-adr
description: >
  Use for standalone / post-hoc ADR documentation outside the synchronous
  architecture-design pass. Triggers on "ADR for {decision}", "adr for
  {slug}", "decide on ADR", "lock in decision", "MADR for {topic}", "stage
  10 for {slug}", "/sdlc-decide-adr {slug} {title}". Use this when a decision
  was made earlier (in code, in a chat, on a whiteboard) and only needs to
  be recorded — for synchronous design-time decisions use
  sdlc:architecture-design (which spawns ADRs inline). Output:
  docs/features/{slug}/adr/NNNN-{title}.md with context / options / decision /
  consequences / status. Prerequisite: docs/features/{slug}/PRD.md +
  sad.md (stages 03 + 04-05) — hard refuse if missing. GATE
  stage 🚪 — ADR merged with status Accepted before downstream stages
  (break-tasks / prep-context / ship).
---

# Skill: decide-adr (SDLC stage 10 🚪 GATE — standalone / post-hoc ADR)

Standalone Architecture Decision Record generator (MADR / Nygard format) for decisions that need recording **outside** the synchronous `architecture-design` pass — code that already shipped, a chat-room agreement, or a whiteboard discussion that didn't go through the Socratic walk. One file = one decision. Produces `docs/features/<slug>/adr/NNNN-<title>.md` from template with context, 2-3 serious options, explicit decision, honest consequences (cons included), status.

For synchronous design-time decisions made *with* the user during `sdlc:architecture-design`, ADRs are spawned inline by that skill — don't call `decide-adr` for those.

This is the **stage 10 runner**: records "why this way" for archeology 6 months from now. ADR without options = declaration, not a decision.

## Owner

Decision author (usually Tech Lead or Backend Lead).

## When to use

- "ADR for <decision>", "adr for <slug>", "lock in decision <topic>", "MADR for <X>", "run stage 10".
- User has PRD + sad.md and needs to record a decision made outside the Socratic pass (post-hoc / async).
- `/sdlc-decide-adr <slug> <title>` as explicit invocation.
- Skip if the decision is being made *now* with the user — use `sdlc:architecture-design` which spawns ADRs inline.
- Skip if an ADR on the same topic already exists with status Accepted — propose edit or new ADR with `Superseded by`.

## Inputs

- `<slug>` — same as for PRD.
- `<title>` — kebab-case, describes the **decision**, not the problem (`sliding-window-rate-limit`, not `rate-limiting`).
- Trade-offs from `sad.md` §4 Solution strategy / §11 Risks / `idea-brief.md §14 Parked & rejected approaches`.
- **Gate (hard refuse):** `docs/features/<slug>/PRD.md` + `docs/features/<slug>/sad.md`. If anything is missing — STOP, suggest the appropriate skill.

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md && test -f docs/features/<slug>/sad.md` → exit ≠ 0 = refuse with indication of which prereq is missing.
2. **Dedup check.** `ls docs/features/<slug>/adr/*.md 2>/dev/null` — search for prior ADRs on the same topic. If found — propose a Superseded formula, not a duplicate.
3. **Pick number.** `NNNN` = next 4-digit (0001, 0002, ...) in `docs/features/<slug>/adr/`. Do not repeat.
4. **Read prereqs.** PRD (constraints, NFR), sad.md (§4 strategy, §9 existing ADR index, §11 risks), idea-brief.md §14 Parked & rejected approaches (rejected options — give balance).
5. **Copy template.** Copy `../architecture-design/templates/adr-template.md` → `docs/features/<slug>/adr/NNNN-<title>.md`. This is the canonical ADR shape — owned by `architecture-design`, referenced cross-skill.
6. **Context.** 2-4 sentences: why is this decision being discussed at all? What forced it (NFR, incident, constraint)?
7. **Options (2-3).** Each — name + 1 paragraph essence + pros + cons + cost (S/M/L) + risk (low/med/high). No alternatives — that's not a decision, it's a declaration.
8. **Decision.** One phrase: "We choose X." 1-2 sentences of justification referencing options / PRD NFR.
9. **Consequences.** Positive, negative, neutral. Cons too — otherwise it's rationalisation. What changes in codebase, ops, monitoring, training.
10. **Status.** `Proposed` (under discussion), `Accepted` (final), `Deprecated`, `Superseded by NNNN`. Without status — any reader won't understand if it's a plan or a fact.
11. **Fill draft.** Fill ADR; `<!-- TBD -->` where honestly missing (e.g., cost estimate without a deep spike).
12. **Self-check against DoD.** One file = one decision, options >= 2, consequences honest, status explicit, title describes decision not problem.
13. **Propose commit.** `10: ADR ${NNNN} ${title} for <slug>` + next owner (Tech Lead → stage 13 task-breakdown).

## Questions for discussion

- Context: why is this decision being discussed at all?
- Options: which 2-3 serious variants?
- Decision: which one was chosen? One phrase.
- Consequences: positive, negative, neutral.
- Status: Proposed / Accepted / Deprecated / Superseded by NNNN.

## Definition of Done

- ADR merged with status `Accepted`.
- Linked from sad.md §9 Architecture decisions index (and from `tasks/_epic.md` if the ADR scopes a specific task).
- One file = one decision. Not "module architecture" — that's sad.md.
- Format MADR or Nygard ADR.
- Consequences honest — cons included.
- Title describes decision, not problem: `0007-sliding-window-rate-limit.md`, not `0007-rate-limiting.md`.

## Anti-patterns

- ADR without options. "We chose X" without alternatives — that's a declaration, not a decision.
- ADR as news-feed: "tried it, didn't work". That's a changelog, not an ADR.
- Duplicate decisions: ADR on the same topic as last quarter. Always dedup-check before writing.
- ADR as PRD: AC, NFR — no. ADR is trade-off and reasoning.
- No status. Reader 6 months later thinks this is the current plan, not an old decision.
- Title describes the problem ("rate-limiting"), not the decision ("sliding-window-rate-limit"). In the ADR-index it's unclear which decisions exist.
- Consequences are all pros. An honest ADR has negative consequences too.

## Template

→ [sdlc/plugin/skills/architecture-design/templates/adr-template.md](../architecture-design/templates/adr-template.md) — canonical MADR for both this skill and `architecture-design`.

## Example invocation

> **User:** "ADR on sliding-window vs token-bucket for rate-limiting-per-user"
>
> **Skill behavior:**
> 1. `test -f` PRD + sad.md → OK.
> 2. `ls docs/features/rate-limiting-per-user/adr/` → empty. NNNN=0001.
> 3. Title: `0001-token-bucket-with-redis.md` (describes the decision).
> 4. Copies template → `docs/features/rate-limiting-per-user/adr/0001-token-bucket-with-redis.md`.
> 5. Context: "brainstorm recommendation — token bucket; sad.md §5 says Redis exists. This is an ADR on the algorithm (token bucket vs sliding window log vs fixed window)".
> 6. Options: (a) Token bucket — simple, INCR+EXPIRE; (b) Sliding window log — more precise, but O(N) memory per tenant; (c) Fixed window — simplest, but edge bursts on boundary.
> 7. Decision: "Token bucket with Redis INCR+EXPIRE per tenant_id." Justification: PRD NFR p95 ≤ 5ms excludes sliding log (O(N) Redis ZRANGE); fixed window doesn't cover AC "sustained 50k/s without edge bursts".
> 8. Consequences: + simple code; − accuracy ±1 sec in burst window; neutral: observe bucket exhaustion via `rate_limit.exceeded` event.
> 9. Status: Accepted (after review).
> 10. Self-check DoD → options ✅, consequences honest ✅, status ✅.
> 11. Commit: `10: ADR 0001 token-bucket-with-redis for rate-limiting-per-user`.
