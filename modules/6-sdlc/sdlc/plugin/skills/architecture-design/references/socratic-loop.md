# Socratic loop — batch-per-section + ADR-gate flow for architecture-design Protocol step 7

## TL;DR (короткий вступ українською)

Це крок 7 у Protocol — діалог з користувачем по кожній секції SAD. Логіка:

1. Skill **малює всю секцію відразу** + нумерує рішення всередині.
2. Питає **по одному рішенню** через `AskUserQuestion`.
3. Користувач обирає одну з **4 дій з рішенням** (англ. *4-state machine*): **Прийняти** / **Виправити** / **Винести у відкрите питання** (`Save as OQ`) / **Викинути** (`Drop`).
4. Для кожного **Прийнятого** рішення skill прогоняє **3 питання масштабу удару** (англ. *blast-radius gate*). Якщо хоч 2 з 3 спрацьовують — створюється файл ADR з форматом **MADR** (markdown з заголовком, контекстом, опціями, наслідками).
5. Skill **пише секцію + ADR-файли + комітить** одним комітом. Більше до цієї секції не повертається — внутрішні протиріччя ловить окремий критик на кроці 8.

---

Goes between the in-memory draft (Step 6) and the Phase-8 critic (Step 8). Per-section batch validation via `AskUserQuestion` over the in-memory draft; per Approved decision a blast-radius gate; per ADR-gated decision an ADR spawn; **then** the section is written to `sad.md` + incremental commit. Section file-writes are atomic — the skill never returns to a previous section after writing it (cross-section drift caught by Phase-8 critic).

For concrete question wording + option `description` fields, see [ask-examples.md](./ask-examples.md). Cadence (mini-recap every 5, question budget per section) → [socratic-cadence.md](./socratic-cadence.md). ADR-gate scoring → [blast-radius-heuristic.md](./blast-radius-heuristic.md).

## Contract

**Per-section batch, not per-decision-across-sections.** For each of §1 → §12 in order, the skill:

1. **7a. Renders the full proposed section** in one message — proposed body text + numbered list of decisions the section contains. This gives the user the big picture before any resolution is requested (they spot duplicates / gaps / drop-the-whole-section problems before per-decision commitment).
2. **7b. Walks per-decision resolutions** — one `AskUserQuestion` per decision, using the 4-state machine below.
3. **7c. Applies transitions** to the in-memory section as each resolution arrives.
4. **7d. Runs the blast-radius gate** on every Approved decision (NOT on Edit/Drop/Save-as-OQ — those don't become ADRs). If ≥1 criterion fires, spawn an ADR (Phase-1b logic preserved — see SKILL.md Step 7 (d-e) and [blast-radius-heuristic.md](./blast-radius-heuristic.md)).
5. **7e. Writes the resolved section to `sad.md`** (with all in-memory transitions applied) + writes any ADR files spawned in 7d + commits `feat(<slug>): sad §N — <decisions summary>`. Single commit per section that bundles sad.md + adr/.
6. **7f. Moves to the next section** — repeats 7a-7e. The skill **never returns** to a previously-written section. Cross-section drift (e.g. §4 strategy contradicts §6 happy-path flow) is the Phase-8 critic's job.

## Decision-types catalog

Each section may contain a mix of decision-types. The same 4-state machine applies to all of them — the `description` field of each option (see [ask-examples.md](./ask-examples.md)) names the next mechanical step the skill takes.

- **Strategic decision** — predominantly §4 Solution strategy, occasionally §7 Deployment. Option-set of 2-4 with «Recommended first + 1-line WHY». **ADR-gate kicks in almost always** (irreversible + multi-module).
- **Building-block decision** — predominantly §5 Building blocks. Module boundary (extend vs new), layered-vs-hexagonal-vs-clean (only ask if PRD signals divergence from CLAUDE.md default), internal sub-package layout. ADR-gate often fires (multi-module).
- **Crosscutting bundle** — §8 Crosscutting. Option-set of 2: «Keep CLAUDE.md defaults» / «Custom for §X». ADR-gate rarely fires (decisions are convention-level, not blast-radius).
- **Quality scenario** — §10 Quality requirements. Option-set is rarely useful (numbers come from PRD NFR). Typical resolution = `Approve` / `Edit` (refine verification method) / `Save as Open Question` (defer scenario till after Phase-8 critic — usually because verification method is TBD by SRE).
- **Risk entry** — §11 Risks. Auto-generated from edits-log + PRD §8 Open Questions + Step 4 brownfield gotchas. User Approves verbatim or `Edit`-s severity/mitigation/owner.
- **Open-architectural-decision row** (special case of Risk entry) — created automatically from any `Save as Open Question` resolution in earlier sections. Skill writes the §11 row at the moment of the OQ resolution; user does NOT see a separate question for it (already approved when they picked `Save as Open Question`).

## 4 дії з рішенням — 4-state machine (uniform across all decision-types)

> **UA-перифраза.** «4-state machine» — це 4 можливі дії з кожним рішенням: **Прийняти** (Approve) / **Виправити** (Edit) / **Винести у відкрите питання** (Save as OQ) / **Викинути** (Drop). `Cancel` і `Reject` — синоніми Drop. Кожна дія має чітку механіку нижче.


- **`Approve`** → keep decision verbatim. No edits-log entry. **Run blast-radius gate** (Step 7d). If gated, spawn ADR (Phase-1b logic — see SKILL.md and [blast-radius-heuristic.md](./blast-radius-heuristic.md)). Move to next decision.

- **`Edit`** → user types new option / new wording / new severity etc. in one go; skill regenerates the decision with the new constraint and asks **once more** on the new version (single-iteration cap — the second answer is final). Log entry with `action: "edit"`.

- **`Save as Open Question`** → decision is removed from its native section AND a row is appended to §11 Risks/Open-Decisions table in this exact shape:

  ```
  | Open architectural decision: <headline> | Open question | Resolve before <stage trigger or YYYY-MM-DD>; <inline rationale from user> | <owner> |
  ```

  Owner + due (date OR stage trigger like «before sdlc:break-tasks») are **mandatory** — skill issues a follow-up `AskUserQuestion` immediately after the user picks this option to capture both. If the user leaves owner OR due blank, the resolution is **downgraded to `Drop`** with an explicit warning surfaced.

  Severity column accepts literal `Open question` value (not Low/Medium/High) — that's the marker that distinguishes OQ rows from regular risks (used by Phase-8 critic F3 + checklist).

  Log entry with `action: "save_as_oq"`. **No ADR spawn** — `Save as OQ` is a defer, not a decision; ADRs are for accepted decisions only.

- **`Drop`** → decision is removed from the section. Two sub-paths:
  - **If decision was mandatory** (e.g. §5 module boundary — every feature has one) → skill re-asks with a **reframed** option set (e.g. if user dropped «extend existing» and «new module», skill asks «extend existing with new sub-package» / «move to shared package»). Single re-ask only; if user drops again → escalate to `Save as Open Question` with skill-suggested owner = Architect + due = «before next pass» and a warning.
  - **If decision was optional** (e.g. §6 extra failure-mode flow beyond happy-path) → leave it out, no replacement.
  - Log entry with `action: "drop"`.

Each option label must be paired with a `description` explaining the next mechanical step the skill will take after that choice — see [ask-examples.md](./ask-examples.md) for canonical wording.

`Cancel` and `Reject` are synonyms for `Drop` — same transition, same edits-log action.

Persist edits into the in-memory section after each resolution. The on-disk `sad.md` is **not** touched until step 7e (after all decisions in the current section resolved + blast-radius gate run + ADRs spawned).

## ADR spawn within Step 7d

When the blast-radius gate fires on an Approved decision:

1. Compute NNNN: `ls docs/features/<slug>/adr/*.md 2>/dev/null | wc -l` + 1, zero-padded to 4 digits.
2. Compute kebab-case title from the **decision** (not the problem): `0003-sliding-window-with-redis.md` ✓ vs `0003-rate-limiting.md` ✗.
3. Copy `./templates/adr-template.md` → `docs/features/<slug>/adr/NNNN-<title>.md`. Fill: Status = `Accepted`; Context (2-4 sentences from the section); Decision drivers (relevant Quality Goals + Constraints); Considered options (from the AskUserQuestion options including rejected ones); Decision outcome (chosen option + 1-2 sentences rationale); Consequences (Positive / Negative / Neutral); Links (PRD path, sad.md §N, related ADRs).
4. Add a row to §9 ADR table in-memory: `| NNNN | <imperative title> | Accepted | §N |`.
5. **No separate commit** — the ADR file goes into the section commit in Step 7e together with sad.md edits.
6. Append to ADR-spawns log (in-memory only, not persisted):
   ```
   {adr_id: "NNNN", title: "<imperative kebab>", section: "§N", triggered_by: "DEC-§N-<decision-id>"}
   ```
   The Phase-8 critic reads `docs/features/<slug>/adr/` directly — the spawns log is for in-memory traceability, NOT a persisted artifact.

## Edits-log (mandatory)

Maintain an edits-log throughout step 7. After each `Edit` / `Drop` / `Save as Open Question` resolution (NOT for `Approve`), append one entry:

```
{decision_id: "DEC-§N-<short-id>"  (e.g. "DEC-§4-modulesIntegration", "DEC-§5-moduleBoundary",
                                    "DEC-§10-QG1-verification"),
 action:      "edit" | "drop" | "save_as_oq",
 before:      "<verbatim option / wording / severity before user action>",
 after:       "<verbatim option / wording / severity after — for save_as_oq this is the §11 row text
                incl. owner+due; for drop this is null>",
 user_reason: "<the rationale the user provided, verbatim>"}
```

`Approve` decisions do **not** go into the log — they are the baseline. The log is the **sole** signal the Phase-8 critic uses to detect upstream-coherence drift caused by user edits during Socratic. Without it, the critic has no input for F1/F2/F3/F4.

If the user provides no reason on `Drop` or `Save as Open Question` — re-prompt once for it. Verbatim user wording matters: the critic uses it to judge whether a defer silently re-introduces a vector that PRD §6 NFR / §7 KPI / §13 Recommendation named as load-bearing.

The ADR-spawns log lives **adjacent** to the edits-log (not folded in) because they're different signals: edits-log = upstream-coherence (what user changed); ADR-spawns log = downstream artifact (what new file was created). Critic reads `adr/` directly; spawns log is in-memory only.

## Exit condition

Step 7 completes when:

- All 12 sections have been batch-rendered (7a) + walked (7b) with one resolution per decision.
- Each section's resolved content + any ADR files spawned in 7d are **already written to disk** in 7e (incremental commits per section).
- The §9 ADR table is closed (no orphans — every file in `adr/` has a §9 row, every §9 row has a file).
- §11 Risks contains every `save_as_oq`-migrated row from Step 7 with owner+due filled (no lone owner, no lone due).
- The edits-log is closed (no pending entries).

Then proceed to Step 8 (see [critic-phase.md](./critic-phase.md)).
