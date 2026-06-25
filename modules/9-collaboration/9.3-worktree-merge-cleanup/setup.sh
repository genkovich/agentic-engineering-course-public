#!/usr/bin/env bash
# setup.sh — build the deterministic start state for the 9.3 merge/cleanup
# screencasts. On top of the 9.2 worktree baseline (git + seed history + local
# bare origin) this script adds what 9.3 needs: two real worktree siblings whose
# branches both touch the SAME line of app.py (so merging the second back gives a
# real conflict), plus one "forgotten" worktree for the cleanup demo. The repo
# lives only inside sandbox/ and its siblings (all git-ignored by the monorepo);
# the monorepo keeps just template/ + this script. Re-runnable: wipes the
# previous run and rebuilds identically.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/template"
SB="$ROOT/sandbox"

# Wipe the previous run, including the worktree siblings and the bare origin.
rm -rf "$SB"
rm -rf "$ROOT"/sandbox-*
rm -rf "$ROOT/.sandbox-origin.git"

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

# set_greeting <dir> <line> — rewrite the single GREETING line in <dir>/app.py.
# awk keeps it portable (no sed -i differences between macOS and Linux) and only
# the one line changes, so the merge conflict stays clean and on-topic.
set_greeting() {
  local dir="$1" line="$2"
  awk -v repl="$line" '/^GREETING = / {print repl; next} {print}' \
    "$dir/app.py" > "$dir/app.py.tmp" && mv "$dir/app.py.tmp" "$dir/app.py"
}

# 1. scaffold the project: env config, ignore rules, worktree-include, etiquette.
cp "$TEMPLATE/CLAUDE.md" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/.env.example" .
cp "$TEMPLATE/.worktreeinclude" .
seed_commit "chore: scaffold worktree merge/cleanup demo" \
  "Env config (.env.example), .worktreeinclude, .gitignore worktree hygiene, merge/cleanup etiquette in CLAUDE.md."

# 2. the push safety-hook + settings (Slide 5: catch an accidental push to main).
cp -R "$TEMPLATE/.claude" .
chmod +x .claude/hooks/block-main-push.sh
seed_commit "chore(claude): add push safety-hook + settings" \
  "PreToolUse Bash hook blocks 'git push ... main'; permissions deny force-push."

# 3. env-driven http service with the GREETING line both branches will edit.
cp "$TEMPLATE/app.py" app.py
seed_commit "feat: env-driven http service" \
  "app.py reads PORT and DB_NAME from .env; GREETING is the shared line the worktree branches edit, so the second merge conflicts."

# Make sure the default branch is 'main', then add a local bare 'origin' so the
# merge/push demos work without a network. No server-side protection here on
# purpose: the offline direct-merge flow stays coherent, and branch protection is
# described as a server layer in the README and the lecture.
git branch -M main
BARE="$ROOT/.sandbox-origin.git"
git init -q --bare "$BARE"
git remote add origin "$BARE"
git push -q origin main
git remote set-head origin main

# 4. two parallel worktree siblings whose branches both edit the SAME GREETING
#    line — feature-a one way, bugfix-b the other. Both branch off the seed main
#    BEFORE anything is merged, so merging the second back conflicts with the
#    first. (Real `git worktree add`, so `git worktree list` shows them live.)
git worktree add -q "$ROOT/sandbox-feature-a" -b worktree-feature-a
set_greeting "$ROOT/sandbox-feature-a" 'GREETING = "service up, feature A вітається"'
git -C "$ROOT/sandbox-feature-a" commit -q --no-verify -am \
  "feat: feature A greeting" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

git worktree add -q "$ROOT/sandbox-bugfix-b" -b worktree-bugfix-b
set_greeting "$ROOT/sandbox-bugfix-b" 'GREETING = "service up, bugfix B вітається"'
git -C "$ROOT/sandbox-bugfix-b" commit -q --no-verify -am \
  "fix: bugfix B greeting" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. one "forgotten" worktree for the cleanup demo (git worktree list/remove/prune).
git worktree add -q "$ROOT/sandbox-old-experiment" -b worktree-old-experiment

# Working-tree-only .env (git-ignored, copied into worktrees via .worktreeinclude).
printf 'PORT=8000\nDB_NAME=app_dev\nAPI_KEY=sk-demo-not-a-real-key\n' > "$SB/.env"

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git worktree list   # main + feature-a + bugfix-b + old-experiment"
echo "   git diff main..worktree-feature-a # review a branch before merging it"
echo "   git merge worktree-feature-a      # land the first branch cleanly"
echo "   (cd ../sandbox-bugfix-b && git merge main)  # second branch -> CONFLICT on app.py"
echo "   git worktree remove ../sandbox-old-experiment  # cleanup demo"
