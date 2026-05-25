---
status: Draft
owner: "<Backend Lead name>"
reviewers: ["<SRE name>"]
updated_at: "<YYYY-MM-DD>"
feature_size: M
stage: "09"
ticket: "<ticket-id>"
---

# Rollback plan — <feature>

<!-- Stage 09 → see SDLC/plugin/skills/plan-migration/SKILL.md -->

## Triggers
Roll back if:
- <Error rate > X%>
- <Latency p95 > Yms>
- <Specific incident: <...>>

## Rollback steps

| # | Step | Action | Time-to-execute |
|---|---|---|---|
| 1 | Revert code | `kubectl rollout undo` | <s> |
| 2 | Revert migration | <if expand+contract done — restore from snapshot OR write inverse migration> | <m> |
| 3 | Verify | <metrics return to baseline> | <m> |

## Data safety
- Which data may be lost? <...>
- Backup point before migration: <snapshot id / time>.

## Tested on staging?
- [ ] Yes, date: <YYYY-MM-DD>, executed by: <name>.

<!-- Why: a rollback "in theory" = a rollback that does not work during an incident. -->
