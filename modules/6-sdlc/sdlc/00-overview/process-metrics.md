# Process metrics

Metrics are needed to see SDLC health without manually polling the team. They are not an SLA for people; they are signals where the process is creating extra work or where artefacts are growing stale.

## Core metrics

| Metric | Definition | Source | Target signal |
|---|---|---|---|
| Lead time idea -> implementation-ready | Days from `idea-brief.md` date to approved `tasks/_epic.md` | frontmatter `updated_at`, status | M+ tasks don't stall between SPEC and the task-breakdown gate |
| Review cycle time | Days from ready-for-review PR to merge | GitHub PR timestamps | Checklist shortens repeat review rounds |
| % M+ with complete DoR | Share of M+ feature folders with all required artefacts before code starts | `scripts/sdlc_lint.py --metrics` | >=80% after 2 months of rollout |
| Escaped defects | Bugs/incidents after release, linked to the feature | incident tracker / postmortem links | Decreasing or has a clear root cause |
| Rollback frequency | Share of releases with a rollback or kill switch | rollout plan / release notes | Does not grow after adoption |
| Stale artefacts | Artefacts with status Draft/Review, not updated >30 days | frontmatter `status`, `updated_at` | Old drafts are removed or driven to a gate |

## Static report

```bash
make sdlc-metrics
```

The report reads `delivery/` and `examples/`, determines feature size, status/date frontmatter, required artefact coverage and stale artefacts. For full metrics (review cycle time / escaped defects) you need to hook up GitHub and the incident tracker separately.
