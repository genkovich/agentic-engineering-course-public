---
name: architecture-design
description: >
  Use when user wants to produce a Software Architecture Document (SAD) with
  Arc42 12 sections + ADRs for a feature, after PRD is closed. Triggers on
  "architecture for {slug}", "design architecture for {feature}", "SAD for
  {slug}", "arc42 for {slug}", "stage 04-05 for {slug}", "C4 context+container
  for {slug}", "/sdlc-architecture-design {slug}", "/sdlc-arc {slug}". One
  skill replaces draft-architecture + write-arc42 + draw-c4 + propose-adr.
  Drafts §1-§12 in-memory, then per-section batch validates via AskUserQuestion
  (4-state machine: Approve / Edit / Save as Open Question / Drop), spawns
  ADRs only on blast-radius gate (irreversible / multi-module / has legitimate
  alternatives), writes the section + commits atomically. Clean-context critic
  on the post-Socratic SAD before the finalization commit. C4 levels 1-2 inline
  (Context in §3, Container in §5); no L3/L4. Brownfield: dispatches Explore
  subagent to map the repo before drafting. Prerequisite: docs/features/{slug}/PRD.md
  — hard refuse if missing. GATE stage 🚪.
stage: "04-05"
---

# Skill: architecture-design (SDLC stages 04-05 🚪 GATE)

Generator of the Software Architecture Document (SAD) + supporting ADRs. Replaces the chain `draft-architecture → write-arc42 → draw-c4 → propose-adr`. Per-section batch validation through 12 Arc42 sections, asking the user via `AskUserQuestion` on every architectural decision, writing each resolved section to `docs/features/<slug>/sad.md` atomically, spawning ADRs only when a decision crosses the **blast-radius** threshold (*масштаб удару* — наскільки боляче буде передумати рішення). Detail per Protocol step lives in `references/`; this file is the backbone.

The output is a growing document — the document itself is the state, resuming after Ctrl-C is free. C4 Context (L1) and Container (L2) live inline in §3 and §5 as Mermaid blocks. L3 Component is out of scope of high-level design — request a separate diagramming pass for it.

## Як це читати (короткий вступ)

Це інструкція для агента, який запускає skill. У ній є **8-крокова процедура** (Protocol нижче) — крок за кроком, як з PRD дістатися до готового sad.md з 5-12 ADR.

Якщо вперше відкриваєш цей файл — почни з:

1. **`## When to use`** і **`## Inputs`** — щоб зрозуміти, коли цей skill застосовний.
2. **`## Protocol`** — 8 кроків, які skill робить послідовно.
3. **References** у списку нижче — детальні правила на кожен крок (як драфтити чорновики, як питати, як спавнити ADR).
4. **`## Self-check`** — список того, що має бути виконано до завершення.

**Словничок термінів** (англо-термін → що означає UA одним рядком):

- *blast radius* — масштаб удару: наскільки боляче буде передумати рішення.
- *Socratic loop* — режим діалогу з користувачем питаннями про рішення (одна `AskUserQuestion` за раз).
- *ADR-gate* — три питання, на яких рішення стає вартим окремого ADR-файлу (а не рядка inline).
- *MADR* — формат файлу ADR (markdown з заголовком, контекстом, опціями, наслідками).
- *4-state machine* — 4 можливі дії з рішенням: **Прийняти** / **Виправити** / **Винести у відкрите питання** / **Викинути**.
- *blast-radius gate* — перевірка з 3 критеріями: незворотнє (≥3 днів переробки), зачіпає ≥2 модулі, є чесна альтернатива.
- *Save-as-OQ* — Save as Open Question: рішення не приймається зараз, переноситься у §11 SAD як відкрите питання з власником і дедлайном.
- *clean-context critic* — окремий subagent, який бачить лише фінальний файл (а не діалог), і шукає внутрішні протиріччя.

## Owner

Architect / Tech Lead. PM stays consulted on Quality Goals (§10) and §11 Risk severities.

## When to use

- After `sdlc:write-prd` produced `docs/features/<slug>/PRD.md`.
- Brownfield repo (existing code the feature changes) OR greenfield with PRD only.
- `/sdlc-architecture-design <slug>` as explicit invocation.
- Replaces standalone calls to `draft-architecture`, `write-arc42`, `draw-c4`, `propose-adr` — those skills no longer exist.
- Skip if `docs/features/<slug>/sad.md` already exists with 12 sections filled (content or `<!-- N/A: reason -->`) AND `adr/` has ≥1 file — suggest review instead.

## Inputs (HARD REFUSE if missing)

- `<slug>` — feature slug used in previous stages.
- `docs/features/<slug>/PRD.md` — must exist, with §2 Goals + §6 NFR filled. If missing → refuse + suggest `sdlc:write-prd <slug>`.
- Git repo (so the Step 3 Explore subagent can read code on brownfield).

## Protocol

1. **Prereq check (hard refuse).** `test -f docs/features/<slug>/PRD.md` → exit ≠ 0 = refuse + suggest `sdlc:write-prd <slug>`. Also read `docs/features/<slug>/.size` if it exists (size class shapes ADR count + §6 flow count expectations — see [./references/checklist.md](./references/checklist.md)).
2. **Read required inputs.** `PRD.md` (§2 Goals, §3 Non-goals, §6 NFR with numeric targets + measurement sources, §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, §13 Recommendation, §1 ¶4 «Decision overrides» if any); `CONTEXT.md` `## Glossary` (canonical role names + domain terms — wins over anything that contradicts).
3. **Brownfield scan.** Dispatch one `Agent` (`subagent_type: "Explore"`) with this brief: «Map this repo for an architecture document. Report: (a) primary language + frameworks + versions, (b) top-level module layout, (c) ports/adapters or layering conventions, (d) data stores in use, (e) inter-module communication style (direct call / events / HTTP), (f) anything that constrains the feature `<slug>` (existing tables, existing endpoints, conventions in CLAUDE.md). Under 400 words.» Greenfield (no source files) → skip, note `<!-- brownfield: N/A — greenfield repo -->` in §3.
4. **Bootstrap.** Copy `./templates/sad-template.md` → `docs/features/<slug>/sad.md`. Patch frontmatter (`updated_at`, `ticket`, `feature_size` from `.size`). Initial commit `feat(<slug>): bootstrap sad.md from PRD + repo scan`. This is the **only** file write between Steps 4 and 7 — Step 6 drafts in-memory only.
5. **Read own templates.** `./templates/sad-template.md` (each section has `<!-- … -->` inline comments that are the per-section generation contract) + `./templates/adr-template.md` (MADR shape — Status / Context / Decision drivers / Considered options / Decision outcome / Consequences / Links).
6. **Per-section batch draft (in-memory only).** For each section §1 → §12: draft proposed content + identify the decisions the section contains + bundle trivial defaults (CLAUDE.md conventions per [./references/socratic-cadence.md](./references/socratic-cadence.md) Rule 1). Per-section sources, item-banks per §1-§12, pre-Socratic hygiene checks → see [./references/draft-generation.md](./references/draft-generation.md). Do NOT write to `sad.md` here — Step 7e writes per section.
7. **Socratic validation — batch-per-section + ADR-gate, per-section file write.** For each section §1 → §12: (a) render the full proposed section + numbered list of decisions in one message (big picture); (b) per-decision `AskUserQuestion` with 4-state machine `Approve` / `Edit` / `Save as Open Question` / `Drop`; (c) apply transitions in-memory; (d) for each Approved decision run the blast-radius gate (irreversible / multi-module / has legitimate alternatives — see [./references/blast-radius-heuristic.md](./references/blast-radius-heuristic.md)); spawn an ADR if ≥1 criterion fires; (e) write the resolved section to `sad.md` + ADR files spawned in 7d + commit `feat(<slug>): sad §N — <decisions summary>`; (f) move to next section. The skill never returns to a previously-written section (cross-section drift is the Step 8 critic's job). State transitions + edits-log schema + Save-as-OQ landing zone → see [./references/socratic-loop.md](./references/socratic-loop.md). Question shape + option `description` field → see [./references/ask-examples.md](./references/ask-examples.md). Cadence (mini-recap every 5, question budget per section) → see [./references/socratic-cadence.md](./references/socratic-cadence.md). C4 syntax for §3 + §5 Mermaid blocks → see [./references/c4-mermaid-syntax.md](./references/c4-mermaid-syntax.md).
8. **Critic stress-test + finalization commit.** Single `Agent` call (`subagent_type: "general-purpose"`, clean context) with the final `sad.md` + Step-7 edits-log + Step-7 ADR-spawns log + paths to `PRD.md` / `CONTEXT.md` / `docs/features/<slug>/adr/`. Resolve findings via `AskUserQuestion` with options `Accept revert/amendment` / `Accept amendment (different wording)` / `Override (rationale)` — `Override` emits a §1 ¶4 «Decision overrides» bullet. Then run the pre-write regex backup (Mermaid sanity + ADR title format + §9 orphan scan) as F5 backup; run Self-check below; on pass write any amendments to `sad.md` + commit `feat(<slug>): sad finalization (critic pass)`. Dispatch + resolution loop + pre-write regex scans → see [./references/critic-phase.md](./references/critic-phase.md); agent prompt body → see [./references/critic-prompt.md](./references/critic-prompt.md). Next owner: Architect signs → `sdlc:draw-sequence <slug>` (stage 06).

## Self-check

Full DoD + anti-patterns + N/A logic → [./references/checklist.md](./references/checklist.md). Inline non-negotiables:

- Step 3 Explore subagent ran on brownfield (or §3 has `<!-- brownfield: N/A — greenfield repo -->`).
- Step 7 edits-log maintained: each `Edit` / `Drop` / `Save as Open Question` has one entry with verbatim `before` / `after` / `user_reason` (action enum `edit|drop|save_as_oq`). `Approve` decisions absent (baseline).
- §11 Risks contains every `save_as_oq`-migrated decision from Step 7 with **both** owner AND due filled (no lone owner, no lone due — missing either downgraded the migration to `Drop` with a warning).
- Step 8 critic ran on post-Socratic `sad.md` + edits-log + ADR-spawns log; every finding resolved via `AskUserQuestion` or `Override` (with §1 ¶4 bullet).
- §3 has a `C4Context` Mermaid block AND §5 has a `C4Container` Mermaid block — both with real names from CONTEXT + Explore (no `<placeholder>` template stubs).
- §6 has ≥1 `sequenceDiagram` Mermaid block (3-5 for M+ size).
- §9 Architecture decisions table references every file in `docs/features/<slug>/adr/` (no orphans, no missing rows).
- Roles in §1 Stakeholders + §3 actors match CONTEXT glossary exactly (no inventing `user`/`admin` when glossary defines specific roles).
- Every ADR has Status = `Accepted` (this skill is synchronous); every ADR title is decision-form imperative kebab-case (`0003-sliding-window-with-redis.md` ✓ vs `0003-rate-limiting.md` ✗).

Any check fails → re-open the relevant `AskUserQuestion`, then re-check.

## References

- [./references/draft-generation.md](./references/draft-generation.md) — Step 6: per-section sources, item-banks per §1-§12, pre-Socratic hygiene.
- [./references/socratic-loop.md](./references/socratic-loop.md) — Step 7: batch-per-section flow, 4-state machine, edits-log + ADR-spawns log schemas, Save-as-OQ landing zone in §11.
- [./references/ask-examples.md](./references/ask-examples.md) — `AskUserQuestion` shape per decision-type (Strategic / Building-block / Crosscutting bundle / Quality scenario) + ADR-gate shape + critic-finding resolution shape.
- [./references/critic-phase.md](./references/critic-phase.md) — Step 8: critic dispatch, resolution loop, pre-write regex backup (Mermaid + ADR title + §9 orphan), failure modes.
- [./references/critic-prompt.md](./references/critic-prompt.md) — canonical agent prompt body for the Step 8 sub-agent. 6 failure classes adapted for SAD (F1 strategic-vector drift / F2 size-class creep / F3 defer vs PRD vector / F4 silent edits / F5 coverage regression / F6 constraint/quality leak).
- [./references/checklist.md](./references/checklist.md) — full Definition of Done + anti-patterns + N/A logic per section + ADR count expectations.
- [./references/blast-radius-heuristic.md](./references/blast-radius-heuristic.md) — when a decision becomes ADR-worthy (irreversible / multi-module / has alternatives), how to score borderline cases.
- [./references/socratic-cadence.md](./references/socratic-cadence.md) — how to avoid question fatigue (mini-recap every 5, 1-line WHY per option, bundle trivial defaults).
- [./references/c4-mermaid-syntax.md](./references/c4-mermaid-syntax.md) — Mermaid C4Context + C4Container quick reference with worked examples.

## Templates

- [./templates/sad-template.md](./templates/sad-template.md) — 12 Arc42 sections + Mermaid C4 L1/L2 placeholders + frontmatter + §11 row pattern for Open-Decisions.
- [./templates/adr-template.md](./templates/adr-template.md) — MADR format (status, context, drivers, options, decision, consequences, links). Also pulled by the `decide-adr` skill cross-skill.
- [./templates/c4-context.md](./templates/c4-context.md) — standalone L1 C4Context Mermaid snippet (embedded inline in SAD §3).
- [./templates/c4-container.md](./templates/c4-container.md) — standalone L2 C4Container Mermaid snippet (embedded inline in SAD §5).
- [./templates/deployment.md](./templates/deployment.md) — deployment diagram skeleton for §7 (Deployment View).
