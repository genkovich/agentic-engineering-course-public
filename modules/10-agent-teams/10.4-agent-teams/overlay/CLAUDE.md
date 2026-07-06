# CLAUDE.md

Project etiquette for this monorepo. Claude reads this on startup.

## Layout
- `packages/billing` - invoice building (line items, discount, tax).
- `packages/queue` - RabbitMQ-style message consumer (retry with backoff, dead-letter).
- `packages/auth` - Bearer auth middleware over an in-memory session store.
- `packages/reports` - daily summary.

## Tests
- Pure `node --test` (built-in runner). No npm dependencies, no `npm install`.
- Run the whole suite from the repo root: `node --test`.
- A single package: `node --test packages/<name>/`.

## Git
- Conventional Commits: `type(scope): description`.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.

## Team etiquette (Agent Teams)
- The task plan is file-disjoint: every task owns its file set, the sets never overlap.
- Each package has exactly one owner; commit only the files of your own package.
- Agree on cross-package contracts (e.g. event formats) directly via SendMessage - never guess.
- Run `node --test` before closing a task; the TaskCompleted hook re-checks and keeps
  the task open while any test is red.
