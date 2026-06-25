# CLAUDE.md

Project etiquette for this repo. Claude reads this on startup.

## Merging worktree branches back
- Merge one branch at a time, never all at once. Land the first, confirm `main`
  is intact, then take the next. That way you always know which merge broke
  something if anything does.
- Review every branch before merging it: read the diff with `git diff main..<branch>`
  (or `/diff` inside a session). No worktree branch enters `main` unreviewed.
- Run `git pull` before you push, so other people's merges into `main` arrive
  first and conflicts get resolved locally. Conflicts on shared files are the
  normal cost of parallel work, not a surprise: plan for the resolution step.

## Pushing
- Always push to a named branch with an explicit name, for example
  `git push origin worktree-feature-a`. Never push straight to `main`.
- A push hook (`.claude/hooks/block-main-push.sh`) catches an accidental push to
  `main` and stops it. The real protection is server-side branch protection; the
  hook only backs you up against the obvious cases.

## Cleanup
- Push first, then remove. `git worktree remove` (or removing on session exit)
  discards uncommitted work and even commits, so an unpushed branch is lost work.
- Make `git worktree remove` and `git worktree prune` a habit: clean up a
  worktree as soon as you finish with its branch, so the repo never fills up with
  abandoned worktrees.
- A manual `git worktree remove` only removes the directory. The branch stays, so
  delete it separately with `git branch -d <branch>` once it is merged.

## Git
- Commits in Conventional Commits format: `type(scope): description`.
- Add a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer to commits you make.
- Never commit `.env`. Only `.env.example` with placeholder values stays in the repo.
