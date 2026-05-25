---
status: Draft
owner: "<Backend Lead name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: M
stage: "09"
ticket: "<ticket-id>"
---

# Migration plan — <feature>

<!-- Stage 09 → see SDLC/plugin/skills/plan-migration/SKILL.md -->

## Strategy
Expand → deploy code → contract.

## Steps

| # | Step | SQL / Action | Backward-compatible? | ETA |
|---|---|---|---|---|
| 1 | <Add nullable column> | `ALTER TABLE x ADD COLUMN y ...` | yes | <s> |
| 2 | <Deploy new code reading old + writing both> | deploy | yes | <s> |
| 3 | <Backfill> | `UPDATE ... WHERE y IS NULL` (batched) | yes | <m> |
| 4 | <Make NOT NULL> | `ALTER TABLE x ALTER COLUMN y SET NOT NULL` | yes (data is ready) | <s> |
| 5 | <Deploy code using only new column> | deploy | yes | <s> |
| 6 | <Drop old column> | `ALTER TABLE x DROP COLUMN old` | contract | <s> |

## Backfill
- Strategy: <batched / streaming>.
- Batch size: <N rows>.
- Resumability: <key / checkpoint>.
- ETA: <total>.

## Verification
- [ ] Row counts match (`SELECT COUNT(*) ...`).
- [ ] Spot-check 100 random rows.
- [ ] Application metrics: no errors related to new schema.

## Locks
- Steps 1, 4, 6: <ACCESS EXCLUSIVE — short>; check `pg_locks`.
- Step 3: <no exclusive lock>.

## Online migration tool
- <pg-osc / pt-osc / native — and why>.
