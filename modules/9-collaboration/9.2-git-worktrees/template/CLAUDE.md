# CLAUDE.md

Project etiquette for this repo. Claude reads this on startup.

## Worktrees
- Name each worktree after the feature it works on; the `w` helper prefixes it
  with the project name so `ls` groups them all together.
- Each worktree gets its own port and DB. Base `.env` arrives via
  `.worktreeinclude`; override PORT/DB_NAME per worktree on top of it.
- A fresh worktree is a fresh checkout: install dependencies inside it before
  running anything.

## Git
- Commits in Conventional Commits format: `type(scope): description`.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.
- Never commit `.env`. Only `.env.example` with placeholder values stays in the repo.
