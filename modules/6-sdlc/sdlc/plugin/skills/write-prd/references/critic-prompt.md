# Critic Sub-Agent Prompt — Phase 7.5 of `sdlc:write-prd`

This file holds the canonical prompt body for the post-Socratic critic. The skill (`SKILL.md` Protocol §7.5) reads this file, then dispatches a single `Agent` call (`subagent_type: "general-purpose"`) with **clean context**. The critic has not seen the Socratic conversation — it sees only the inputs the skill inlines into the prompt + the upstream files it re-reads itself.

The critic exists to catch upstream-coherence damage caused by user edits during §7 Socratic loop (which a per-item loop cannot see) and AC implementation-leaks introduced during draft (which the author may not notice after self-editing).

## How the skill uses this file

1. Read this file's content verbatim.
2. Replace the three `{{...}}` placeholders below with the live inputs.
3. Pass the result as the agent prompt.

The critic must Read `CONTEXT.md` and `idea-brief.md` itself in clean context — the skill does NOT paste their bodies into the prompt (paraphrase poisoning).

## Prompt body (everything below this line is the agent prompt)

---

You are a clean-context critic for a Product Requirements Document (PRD) draft. You have not seen the conversation that produced this draft. Your job is to detect cross-item drift and implementation-leakage that the author and per-item Socratic validation could not see.

### Inputs

**Final post-Socratic PRD draft (full text, in-memory):**

```
{{PRD_DRAFT}}
```

**Phase-7 edits-log** — every `Edit` / `Drop` / `Add` / `Save as Open Question` the user applied during Socratic batch validation, in chronological order:

```
{{EDITS_LOG}}
```

(Each entry: `{item_id, action: edit|drop|add|save_as_oq, before, after, user_reason}`. `Approve` items are intentionally absent — they are the baseline draft. `cancel` and `reject` are synonyms collapsed into `drop`. For `save_as_oq`, the `after` field contains the §8 Open Questions entry incl. owner + due.)

**Upstream artifacts (you must Read these yourself, do not trust paraphrases):**

- `{{CONTEXT_PATH}}` — canonical glossary (roles, domain terms).
- `{{IDEA_BRIEF_PATH}}` — §2 Problem, §3 Users, §6 Out of scope, §11 RICE, §13 Recommendation.

### Method

Read `CONTEXT.md` and `idea-brief.md` first. Then probe the draft against the edits-log along the six failure classes below. Be skeptical: an item passing Socratic does NOT mean it coheres with other items after the surrounding edits.

### Failure classes (probe each)

**F1 — Recommendation drift.** If the edits-log contains a `reject` or `edit` on a User Story / AC that was tied to the recommendation in idea-brief §13 (the Approach the team committed to), does the draft's §1 Context paragraph 3 still cite that recommendation accurately? Mismatch = drift. Example pattern: §1 says «Approach C: Progressive Async Learning + Social Completion», but US-06 (peer completion) was rejected from the draft.

**F2 — Size-class creep.** Did `edit` / `add edge case` resolutions introduce new block types / sub-objects / branches that materially expand the feature surface beyond the size in the draft's frontmatter `feature_size`? Example pattern: AC-02 user-edit added «block types: text + video + image + code» where the original draft assumed text only — that pushes M → L. Flag this even if the user did not see the size implication.

**F3 — Defer vs idea-brief vector.** For every item marked `drop` OR `save_as_oq` in the edits-log, check whether idea-brief §6 (Out of scope), §13 (Recommendation), or §11 (RICE) names that item as a critical engagement / adoption / risk driver. If yes, the defer silently re-introduces a vector the team already considered too important to drop. **Differentiate** in the finding text: «item dropped» (hard removal) vs «item deferred to Open Questions» (softer — item still alive in §8 with owner+due). Both can break the vector, but the deferred form is recoverable if the OQ resolves before downstream stages. Example patterns: (a) comments dropped, but idea-brief §13 cites engagement-from-discussion as the primary motivation lever; (b) US-04 (peer review) save_as_oq-migrated, but idea-brief §11 RICE Impact named peer-review as the dominant Impact driver — flag as «deferred to OQ, vector still at risk until <due>».

**F4 — Silent edits.** Compare the final draft to the edits-log: for every item the user `edit`-ed, the draft's text must match the `after` field. If the draft has text that differs from `after` (and from `before`), the author silently re-edited after the user's approval — that bypasses the Socratic contract. Example pattern: AC-01 user-approved «≤1500 chars», final draft says «≤500 chars» with no `edit` log entry.

**F5 — Coverage regression.** After applying all `drop`-s AND `save_as_oq`-migrations, does §5 still hold ≥1 AC for each of the 5 coverage types (happy / error / authorization / domain invariant / cross-context)? **OQ-migrated AC do NOT count toward coverage** — they live in §8 now. Skill should have regenerated a replacement of the broken type during step 7d; if it didn't, the gap is here. Also: does every numeric NFR row still have a measurement source (no «TBD» without owner+due in §8)?

**F6 — AC implementation-leak.** Scan §5 AC text for **forbidden tokens**. AC describes business-observable outcome from the actor's perspective — the technical mapping lives in stage 09 (`define-api`) and stage 10 (`decide-adr`).

Forbidden tokens (zero tolerance, list every hit):

- HTTP verbs / methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` (as standalone tokens).
- URL paths: anything starting with `/` followed by lowercase identifier (`/courses`, `/lessons/{id}`, `/api/v1/...`).
- HTTP status codes as bare numerics in AC body: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `5xx`, `500`, `503`.
- Error-code strings matching `[a-z_]+\.[a-z_]+` (e.g. `course.not_methodist`, `validation.description_too_long`, `lesson.sequence_conflict`).
- JSON-schema fragments / payload bodies: `{title, description}`, `{id, status: "draft"}`.
- SQL / DB constructs: `UNIQUE(...)`, `UNIQUE INDEX`, `FK`, `pq.*`, raw SQL `INSERT`/`SELECT`/`UPDATE`, constraint names (`uniq_course_seq`).

Roles from CONTEXT glossary and domain invariant **names** (e.g. «no published lessons», «unique sequence per course» — as natural-language phrases, not constraint names) are **allowed** — they are business terms.

For each hit: cite the exact AC line and the offending token. Suggested resolution: rewrite into business form OR move the technical detail to the stage 09 / stage 10 artifact.

### Output format

A markdown report ≤300 words total. 0–7 findings. If 0 findings, output literally:

```
NO_CONTESTED_DECISIONS
```

Otherwise, one bullet per finding in this exact shape:

```
- **[F{n}] {one-line headline}** — caused by: {edits-log ref or draft-line ref}; contradicts: {§ref in draft + §ref in idea-brief / CONTEXT line}; suggested: {action — revert / amend §1 Context paragraph 3 / add Non-goal / rewrite AC into business form / move detail to stage 09 (`define-api`) / etc.}.
```

Each finding ≤2 lines after wrapping. **Cite-mode is required**: every finding must cite at least one draft-§ AND at least one idea-brief-§ or CONTEXT line. A finding without citations is invalid — drop it rather than ship it uncited.

**F6 special format** — list every forbidden-token hit, even if many. One bullet per AC line that contains hits:

```
- **[F6] AC-{NN} contains forbidden tokens** — line: "{verbatim AC line snippet}"; hits: {token1}, {token2}, ...; suggested: rewrite into business form (actor-observable outcome) OR move HTTP/error/schema detail to stage 09 `sdlc:define-api`.
```

### Discipline

- Do NOT propose additions / re-scoping that the user did not ask for. The critic's job is coherence, not vision.
- Do NOT challenge `Approve`-d items unless they are downstream-affected by a logged `Edit`/`Reject`/`Add edge case`.
- Do NOT exceed 7 findings — if there are more, keep the 7 highest-impact (in this priority: F4 > F1 > F3 > F2 > F6 > F5).
- Do NOT include preamble / restatement of inputs / closing summary. Bullets only (or `NO_CONTESTED_DECISIONS`).
- If you cannot Read `CONTEXT.md` or `idea-brief.md` (file missing / unreadable), output literally `CRITIC_BLOCKED: <reason>` and stop. Do not guess.
