---
description: "Run pre-deploy checklist for service $ARGUMENTS"
---

Run the team's pre-deploy checklist for the service named in `$ARGUMENTS`. Walk the user through each item and stop on the first hard blocker.

- Env diff: compare staging vs prod environment variables and flag missing or changed keys
- Migrations dry-run: list pending migrations and confirm they ran clean on staging
- Smoke endpoints: hit `/health`, `/ready`, and one critical business endpoint
- Rollback plan: confirm previous image tag is pinned and a one-line rollback command is ready
- Oncall heads-up: post a short message to the oncall channel with deploy window and risk level

If any item is missing, refuse to mark deploy as ready and tell the user what to fix.
