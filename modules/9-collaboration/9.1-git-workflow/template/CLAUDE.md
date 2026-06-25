# CLAUDE.md

Project etiquette for this repo. Claude reads this on startup.

## Git
- Commits in Conventional Commits format: `type(scope): description`
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
- Branch names: `feat/<short-name>` or `fix/<short-name>`.
- Open a pull request right after the first clean commit.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.
- Never commit `.env`. Only `.env.example` with placeholder values stays in the repo.
