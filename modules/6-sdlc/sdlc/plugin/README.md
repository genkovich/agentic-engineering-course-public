# sdlc — Claude Code plugin

9 atomic stage skills + 2 cross-cutting skills for an ideation → ship pipeline with Claude. Each skill is a self-contained folder under `skills/<name>/` — `SKILL.md` (protocol + DoD + anti-patterns), optional `templates/` (skeletons the skill copies into `delivery/<slug>/`), optional `references/` (mini-guides the skill reads at specific protocol steps).

## Install

```bash
# Option A — symlink (recommended for hacking)
ln -s "$(pwd)/sdlc/plugin" ~/.claude/local-plugins/sdlc

# Option B — Claude Code installer
claude /plugin install ./sdlc/plugin
```

Verify: `claude /plugin list` shows `sdlc`; `/sdlc-interview` (or any other slash-trigger below) appears in the slash menu.

## Skill order — five phases

> Each phase reads the previous phase's artefacts. Cross-cutting skills (`fix-term`, `classify-size`) are called from inside the phase skills, not in sequence.

| Phase | Skill | When to run | Output |
|-------|-------|-------------|--------|
| **1. Ideation** | [`interview`](skills/interview/SKILL.md) | Raw idea exists, before PRD. Auto-invokes `fix-term` for new glossary terms. | `idea-brief.md` (15 sections) |
| **2. Product** | [`write-prd`](skills/write-prd/SKILL.md) 🚪 | `idea-brief.md` is `status: Confirmed`. | `PRD.md` |
| | [`classify-size`](skills/classify-size/SKILL.md) | Any time after `idea-brief.md` exists; downstream skills branch on size. | `.size` (XS/S/M/L/XL) |
| **3. Architecture** | [`architecture-design`](skills/architecture-design/SKILL.md) 🚪 | `PRD.md` exists. Spawns inline ADRs through the blast-radius gate. | `sad.md` + `adr/NNNN-*.md` |
| **4. Contracts + data** | [`complete-sequence-diagrams`](skills/complete-sequence-diagrams/SKILL.md) | `sad.md` exists; PRD §4 has US-N. | `sad.md §6` + per-flow Mermaid blocks |
| | [`generate-data-model`](skills/generate-data-model/SKILL.md) | `sad.md` + sequences exist. | `data-model.md` + paired `.up.sql`/`.down.sql` + audit |
| | [`api-forge`](skills/api-forge/SKILL.md) | `data-model.md` ready (Scenario A) or PRD + sequences only (Scenario B). | `openapi.yaml` (+ `events.md` if async) |
| **5. Breakdown + impl** | [`break-tasks`](skills/break-tasks/SKILL.md) | All design artefacts closed. | `tasks/_epic.md` + `tasks/tracker.md` + `tasks/<task>.md` |
| | [`plan-tests`](skills/plan-tests/SKILL.md) | `PRD.md` exists; ideally after API contracts too. | `test-plan.md` |
| | [`decide-adr`](skills/decide-adr/SKILL.md) 🚪 | Post-hoc decision documentation (a decision made earlier needs an ADR file). | `adr/NNNN-*.md` |

🚪 = hard refuse if prereq is missing.

## What's inside each skill

Every skill folder has the same anatomy:

- `SKILL.md` — frontmatter (`name`, `description`, `triggers`, `stage`) + the 7-step protocol the skill executes + Self-check + anti-patterns. Single source of truth.
- `templates/` *(if the skill copies a skeleton)* — the artefact starter that the skill writes into `delivery/<slug>/`. Owned by this skill: no other skill copies it.
- `references/` *(if the protocol is long)* — mini-guides loaded at specific protocol steps (e.g. `socratic-cadence.md`, `blast-radius-heuristic.md`, `draft-generation.md`).

Per-skill specifics (templates + key references):

| Skill | Key files |
|-------|-----------|
| `interview` | `templates/idea-brief.md` (15 sections) |
| `write-prd` | `templates/PRD-template.md`; `references/{draft-generation,socratic-loop,critic-phase,critic-prompt,ask-examples,checklist}.md` |
| `architecture-design` | `templates/{sad-template,adr-template,c4-context,c4-container,deployment}.md`; `references/{draft-generation,socratic-loop,blast-radius-heuristic,socratic-cadence,c4-mermaid-syntax,…}.md` |
| `complete-sequence-diagrams` | `templates/seq-flow.md` (single-flow shape, embedded inline in SAD §6) |
| `generate-data-model` | `templates/{data-model,rules-migrations-baseline}.md`; reads cross-feature `sdlc/document-templates/migration-plan.md` |
| `api-forge` | `templates/{openapi.yaml,events.md}` |
| `decide-adr` | no own templates — pulls canonical `../architecture-design/templates/adr-template.md` cross-skill |
| `break-tasks` | no own template — generates `_epic.md` + `tracker.md` + per-task files directly |
| `plan-tests` | `templates/test-plan.md` |
| `fix-term` | `templates/CONTEXT.md` (lazy bootstrap for the per-feature glossary) |
| `classify-size` | no template — writes a 1-line `.size` file |

## Shared templates

`sdlc/document-templates/` keeps templates that don't belong to any single skill:

- **Cross-feature / manual** — `CHANGELOG.md`, `CONTEXT-MAP.md` (multi-context glossary map), `claude-context.md` (coding-session bootstrap), `review-checklist.md`, `rollback-plan.md`, `migration-plan.md` (folded into `generate-data-model` audit on greenfield), `task-breakdown.md` (legacy alias for `break-tasks` outputs), `diagrams/c4-component.md` (L3, out of scope for SAD).
- **Legacy** — `SPEC.md`, `arc42.md`, `architecture-brief.md`, `adr/NNNN-title.md` — superseded artefacts kept for repos that haven't migrated.

Skills do **not** copy from this folder during their protocol. These are snippets a human pulls in by hand when the feature needs them.

## Conventions

- **Skill = source of truth.** Edit `skills/<name>/SKILL.md` to change skill behaviour; the protocol there is what gets executed.
- **Templates colocated with their owner skill** — single ownership; copying a skill folder gives you a working skill.
- **Mermaid only** for diagrams (C4, sequence, ER, deployment). No PlantUML, no draw.io.
- **One ADR = one decision.** Spawned inline through the blast-radius gate in `architecture-design`; standalone via `decide-adr` for post-hoc cases.
- **Texts in repo, not Confluence.**

## Customizing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to add a new skill.

## License

MIT. See [LICENSE](../LICENSE).
