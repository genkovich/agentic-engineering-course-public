# team-marketplace

A private Claude Code plugin marketplace for a 50-engineer team. Ships three reference plugins (`deploy-checklist`, `pr-review-rules`, `security-scan`) that standardize how the team deploys services, reviews pull requests, and scans branches for security issues before push. Use this repo as the single source of truth for shared Claude Code automation.

## Subscribe

Add this marketplace to your Claude Code instance:

```
/plugin marketplace add github:your-org/team-marketplace
```

To pin the marketplace at the project level (so every contributor in this repo gets it automatically), commit `.claude/settings.json` with:

```json
{
  "extraKnownMarketplaces": {
    "team-marketplace": {
      "type": "github",
      "repo": "your-org/team-marketplace"
    }
  }
}
```

## Install a plugin

```
/plugin install deploy-checklist@team-marketplace
/plugin install pr-review-rules@team-marketplace
/plugin install security-scan@team-marketplace
```

## Update flow

- Maintainers cut a release with `claude plugin release` after merging to `main`.
- Consumers pull the latest with:

```
/plugin marketplace update team-marketplace
```

## Contribute

1. Read [SECURITY.md](./SECURITY.md) before opening a PR — every plugin runs with full user privileges, review accordingly.
2. Add an entry to [CHANGELOG.md](./CHANGELOG.md) under the next version.
3. CI validates every plugin on every PR via `.github/workflows/validate-plugins.yml`.
4. Get the named maintainer-approver of the affected plugin to review.
