# CLAUDE.md

Project etiquette for this monorepo. Claude reads this on startup.

## Layout
- `packages/queue` - RabbitMQ-style message consumer (retry with backoff, dead-letter). Contains a subtle duplicate-requeue bug for the model-comparison screencast.
- `packages/auth` - Bearer auth middleware over an in-memory session store.

## Tests
- Pure `node --test` (built-in runner). No npm dependencies, no `npm install`.
- Run the whole suite from the repo root: `node --test`.

## Git
- Conventional Commits: `type(scope): description`.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.