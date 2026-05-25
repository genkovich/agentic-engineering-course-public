# Critic phase — Protocol step 7.5 for write-prd

Runs between the Socratic loop (step 7) and the Self-check + file write (step 8). Catches **cross-item drift** caused by user edits during step 7 (which a per-item loop cannot see) and **AC implementation-leaks** introduced during draft.

The actual prompt body for the sub-agent lives in [critic-prompt.md](./critic-prompt.md). This file is the dispatch contract + resolution loop around it.

## Dispatch

Single `Agent` tool call, `subagent_type: "general-purpose"`, **clean context** — the sub-agent has not seen the Socratic conversation.

**What to inline into the prompt** (substituted into the `{{PRD_DRAFT}}` / `{{EDITS_LOG}}` / `{{CONTEXT_PATH}}` / `{{IDEA_BRIEF_PATH}}` placeholders in `critic-prompt.md`):

1. The final post-Socratic in-memory draft (full PRD text).
2. The Phase-7 edits-log (the array of entries from [socratic-loop.md](./socratic-loop.md)).
3. The paths to `CONTEXT.md` and `idea-brief.md` — paths only, **not** bodies. The critic reads them itself in clean context to avoid paraphrase-poisoning.

## Output contract

The critic returns a markdown report ≤300 words. Either:

- Literal `NO_CONTESTED_DECISIONS` → proceed straight to Self-check + write.
- Or 0-7 findings, one bullet each, citing draft-§ + idea-brief-§ / CONTEXT line + suggested resolution.

Failure classes the critic probes (full definitions in [critic-prompt.md](./critic-prompt.md)):

- **F1** recommendation drift — §1 ¶3 still cites the idea-brief §13 vector after user rejected a US tied to it.
- **F2** size-class creep — `Edit`/`Add edge case` resolutions expanded the feature surface beyond `feature_size`.
- **F3** defer vs idea-brief vector — a `drop`-ed OR `save_as_oq`-migrated item was named in idea-brief §6/§11/§13 as a critical engagement/risk driver. `save_as_oq` is a softer defer (item still alive in §8 with owner+due) — the critic differentiates in findings («item dropped» vs «item deferred to Open Questions»), but both can break the idea-brief vector.
- **F4** silent edits — final draft text differs from `after` field of an `edit` entry (author re-edited post-Socratic).
- **F5** coverage regression — after drops + OQ-migrations, §5 lost ≥1 of the 5 coverage types. Coverage is verified **AFTER** `drop` and `save_as_oq` apply (OQ-migrated items live in §8, no longer count toward §5 coverage). Also: any NFR row that went `TBD` without owner+due in §8.
- **F6** AC implementation-leak — forbidden tokens in §5 AC text (HTTP verbs / paths / status numerics / `[a-z_]+\.[a-z_]+` strings / JSON fragments / SQL constructs — full list in [draft-generation.md](./draft-generation.md)).

If the critic returns `CRITIC_BLOCKED: <reason>` (cannot Read upstream files) — STOP and report to the user. Do **not** silent-write the file.

## Resolution loop

For each finding, surface it to the user via `AskUserQuestion`. Per finding, options:

- **`Accept revert / amendment as suggested`** — apply the critic's suggested edit verbatim.
- **`Accept amendment (different wording)`** — user types alternative wording; skill applies that.
- **`Override (rationale)`** — keep the draft as-is, user provides the rationale.

Constraints:

- **≤2 `AskUserQuestion` batches**, max 4 questions per batch. The user's **second** answer per finding is final (single-iteration cap, mirrors step 7).
- **`Override` resolutions emit a bullet** into the draft §1 Context ¶4, exactly: «<finding-headline> — overridden by author, rationale: <user-rationale>». This makes the deliberate choice visible to downstream skills (`architecture-design`, `define-api`).

After resolution, re-run the Self-check inline non-negotiables (see SKILL.md `## Self-check`). If any still fail — re-open the relevant `AskUserQuestion` once, then proceed.

## Pre-write regex backup for F6

Independent of the critic, before writing the file run a regex scan over §5 AC text for forbidden tokens (HTTP verbs, paths starting with `/`, bare status codes `200|201|400|401|403|404|409|500|503|5xx`, `[a-z_]+\.[a-z_]+`, JSON fragments, SQL constructs). Any hit **not** already overridden in step 7.5 → re-open `AskUserQuestion` for that AC line. This is the safety net if the critic missed a token (e.g. truncated output).

## Failure modes

- **Critic timeout / error** → STOP, report to user. Never fall back to silent write.
- **Critic returns malformed output** (no bullets, no `NO_CONTESTED_DECISIONS`, no `CRITIC_BLOCKED`) → re-dispatch once with «Your previous output did not match the required format» appended; if still malformed → STOP and ask the user how to proceed.
- **User picks `Override` for every finding** → allowed (PRD authorship is the user's call), but every override emits a §1 ¶4 bullet so the override trail is auditable.
