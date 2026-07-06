# CLAUDE.md

Project etiquette for this monorepo. Claude reads this on startup.

## Layout
- `packages/billing` - invoice building (line items, discount, tax).
- `packages/queue` - RabbitMQ-style message consumer (retry with backoff, dead-letter).
- `packages/auth` - Bearer auth middleware over an in-memory session store.
- `packages/reports` - daily summary (contains a known flaky test).

## Tests
- Pure `node --test` (built-in runner). No npm dependencies, no `npm install`.
- Run the whole suite from the repo root: `node --test`.
- `packages/reports` has an intentionally flaky test - that is by design.

## Git
- Conventional Commits: `type(scope): description`.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.
