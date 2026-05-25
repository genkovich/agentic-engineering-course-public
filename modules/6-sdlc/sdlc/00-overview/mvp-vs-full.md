# MVP vs Full set

Artefact size ∝ task size. For XS/S — minimal set. For M+ — full.

| Artefact | MVP (XS/S) | Full (M+) |
|---|---|---|
| idea-brief (15 sections, consolidated) | yes | yes |
| SPEC | yes | yes |
| sad.md (Arc42 12 sections + C4 L1/L2 inline) | yes — 12 sections walked, more `<!-- N/A -->` allowed | yes — all 12 sections filled |
| ADRs (in `adr/`) | 2-4 typical | 5-12 typical |
| sequence | 1 flow | all critical (3-5) |
| deployment | — | yes |
| data-model | if DB | yes |
| migration + rollback | if DB | yes |
| API contract | yes | yes |
| events | if async | yes |
| task-breakdown (`tasks/_epic.md` + `tasks/tracker.md`) | yes | yes |
| claude-context (`CONTEXT.md`) | yes | yes |
| test-plan | inline in SPEC | separate file |
| review-checklist | shared default | per-feature |
| security-review | if public/API/data-heavy | yes |
| feature-rollout-plan | if flag/canary present | yes |
| changelog | yes | yes |
| KB note | yes | yes |

## sad.md size behaviour

Even for XS/S, the skill walks all 12 Arc42 sections — consistency > completeness theatre. Sections that genuinely don't apply get `<!-- N/A: <one-line reason> -->`. Common XS/S N/A patterns:

- §7 Deployment — `<!-- N/A: feature reuses existing deployment unit, no infra change -->`
- §6 Runtime — collapses to one happy-path flow, no failure-mode flows.
- §11 Risks — one accepted-debt row, no medium/high risks.

Same skill, same template, smaller content footprint.

## How to classify size

- **XS**: 1 PR, up to 1 day, no migrations, no new API.
- **S**: 2-5 PRs, up to a week, possibly a small migration.
- **M**: separate epic, 1-2 sprints, new module / API / migration.
- **L**: cross-module, several teams, breaking changes possible.
- **XL**: new subsystem, requires a separate roadmap.

## One-sentence rule

> If you hesitate between MVP and Full — start with MVP. Filling the empty sections of sad.md later is cheaper than discarding pre-built artefacts.
