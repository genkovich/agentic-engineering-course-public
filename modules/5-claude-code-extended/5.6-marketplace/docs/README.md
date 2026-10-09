# team-marketplace

A private Claude Code plugin marketplace for a 50-engineer team. Ships three
reference plugins that standardize how the team deploys services, reviews
pull requests, and scans branches for security issues before push:

- `deploy-checklist` — pre-deploy environment diff, migrations, smoke tests, rollback plan
- `pr-review-rules` — enforce changelog, tests, security checklist, no churn on every PR
- `security-scan` — pre-push audit for hardcoded secrets, dangerous `eval`/`shell=True` calls, vulnerable dependencies

The marketplace is the single source of truth for shared Claude Code automation.
Plugins are versioned independently with SemVer; the marketplace itself follows
SemVer too, recorded in `docs/CHANGELOG.md`.

## Release flow

1. Land changes on `main` via PR.
2. Tag the next version (`git tag v1.0.1 && git push origin v1.0.1`).
3. `.github/workflows/release-notes.yml` runs: validates every plugin, then
   asks Claude to draft `docs/CHANGELOG.md` updates and a draft GitHub Release
   from the conventional-commit history since the previous tag.
4. Maintainer reviews the PR + draft Release; publishes when ready.

## Subscribe

```
/plugin marketplace add github:your-org/team-marketplace
```

## Approval policy

Every plugin has a named maintainer-approver. Add the approver to the PR
description before requesting review:

- `deploy-checklist` → @platform-team
- `pr-review-rules` → @platform-team
- `security-scan` → @acme/security-team
