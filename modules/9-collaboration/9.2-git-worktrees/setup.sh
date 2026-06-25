#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained git repo with a small seed
# history, ready for the worktree screencasts. The worktree feature needs git
# initialized + at least one commit, so the seed history below satisfies that
# precondition. Re-runnable: wipes sandbox/ (and any w-helper worktree
# siblings) and rebuilds. The repo lives only inside sandbox/ (git-ignored by
# the monorepo); the monorepo keeps just template/ + this script.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/template"
SB="$ROOT/sandbox"

# Wipe the previous run, including any sibling worktrees the `w` helper made.
rm -rf "$SB"
rm -rf "$ROOT"/sandbox-*

mkdir -p "$SB"
cd "$SB"

git init -q
git config user.email "demo-author@example.com"
git config user.name "Demo Author"
git config commit.gpgsign false

# seed_commit <subject> [body] — stage everything and commit with a
# Co-Authored-By trailer (so git log mirrors agent-made history).
seed_commit() {
  local subject="$1" body="$2"
  git add -A
  if [ -n "$body" ]; then
    git commit -q --no-verify \
      -m "$subject" -m "$body" \
      -m "Co-Authored-By: Claude <noreply@anthropic.com>"
  else
    git commit -q --no-verify \
      -m "$subject" \
      -m "Co-Authored-By: Claude <noreply@anthropic.com>"
  fi
}

# 1. scaffold the project: env config, ignore rules, repo etiquette
cp "$TEMPLATE/CLAUDE.md" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/.env.example" .
cp "$TEMPLATE/.worktreeinclude" .
cp -R "$TEMPLATE/.claude" .
seed_commit "chore: scaffold worktree demo project" \
  "Env config (.env.example), .worktreeinclude, .gitignore worktree hygiene, repo etiquette in CLAUDE.md."

# 2. env-driven http service (reads PORT/DB_NAME — basis of the isolation demo)
cp "$TEMPLATE/app.py" app.py
seed_commit "feat: env-driven http service" \
  "app.py reads PORT and DB_NAME from .env, so each worktree binds its own port and db."

# 3. the agent-vs-agent task (multiple valid solutions)
cp "$TEMPLATE/component.py" component.py
seed_commit "feat: render_card task for agent-vs-agent comparison"

# 4. the `w` worktree helper (committed, so the screencast sources it)
mkdir -p scripts
cp "$TEMPLATE/scripts/w.sh" scripts/w.sh
seed_commit "chore(scripts): add w worktree helper"

# Make sure the default branch is 'main' regardless of the host git config,
# then add a local bare 'origin' so the worktree demos work without a network:
#   - claude --worktree bases new worktrees on origin/HEAD
#   - git worktree add ... origin/main needs origin/main to exist
#   - the base-retarget demo (git remote set-head origin develop) needs develop
git branch -M main
# Hidden name (leading dot) so it never shows up in the `ls ../sandbox-*`
# naming-convention demo alongside the real worktrees.
BARE="$ROOT/.sandbox-origin.git"
rm -rf "$BARE"
git init -q --bare "$BARE"
git remote add origin "$BARE"
git branch develop
git push -q origin main develop
git remote set-head origin main

# Working-tree-only .env (git-ignored, copied into worktrees via .worktreeinclude).
printf 'PORT=8000\nDB_NAME=app_dev\nAPI_KEY=sk-demo-not-a-real-key\n' > .env

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline   # clean Conventional commits with Co-Authored-By"
echo "   claude --worktree feature-a       # precondition (git + >=1 commit) satisfied"
echo "   source scripts/w.sh && w feature-a  # one-call isolated worktree with a free port"
echo "   python3 app.py                    # service on PORT from .env (make serve)"
