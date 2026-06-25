#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained git repo whose `main` is a clean
# baseline (green test) and whose feature branch `feat/reminders` carries a
# PR-in-progress diff with three planted defects (red test). A local bare
# `origin` (with `main`) makes the branch look like an open PR without a
# network. Re-runnable: wipes sandbox/ and rebuilds. The history lives only
# inside sandbox/ (git-ignored by the monorepo); the monorepo keeps just
# template/ + this script.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/template"
SB="$ROOT/sandbox"

rm -rf "$SB"
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

# ---------------------------------------------------------------------------
# main: clean baseline. Every file here is the SAFE version; `make test` green.
# ---------------------------------------------------------------------------
git branch -M main

# 1. scaffold package + repo etiquette + PR template
mkdir -p src/tasks src/tests
cp "$TEMPLATE/CLAUDE.md" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/.env.example" .
cp -R "$TEMPLATE/.claude" .
cp -R "$TEMPLATE/.github" .
cp "$TEMPLATE/src/tasks/__init__.py" src/tasks/__init__.py
cp "$TEMPLATE/src/tests/__init__.py" src/tests/__init__.py
seed_commit "chore: scaffold task-tracker package" \
  "Package skeleton, repo etiquette in CLAUDE.md, PR template, review commands."

# 2. persistence
cp "$TEMPLATE/src/tasks/store.py" src/tasks/store.py
seed_commit "feat(tasks): json file persistence"

# 3. model + formatting (single formatter, no duplication)
cp "$TEMPLATE/src/tasks/model.py" src/tasks/model.py
seed_commit "feat(tasks): task model and line formatting"

# 4. reminders window (inclusive boundary) + stdout notify
cp "$TEMPLATE/src/tasks/reminders.py" src/tasks/reminders.py
seed_commit "feat(tasks): due-within reminders window"

# 5. cli
cp "$TEMPLATE/src/tasks/cli.py" src/tasks/cli.py
seed_commit "feat(tasks): list and remind cli"

# 6. cover the reminders window with a test, green on this baseline
cp "$TEMPLATE/src/tests/test_reminders.py" src/tests/test_reminders.py
seed_commit "test(tasks): cover the reminders window"

git tag clean-baseline

# Local bare origin with main, so the feature branch reads as an open PR.
BARE="$ROOT/.sandbox-origin.git"
rm -rf "$BARE"
git init -q --bare "$BARE"
git remote add origin "$BARE"
git push -q origin main
git remote set-head origin main

# ---------------------------------------------------------------------------
# feat/reminders: the PR-in-progress. Overlays the DEFECTIVE versions on top
# of the baseline → three planted defects, `make test` red.
# ---------------------------------------------------------------------------
git checkout -q -b feat/reminders

# DEFECT 1 (off-by-one) + DEFECT 3 (command injection) live in reminders.py;
# DEFECT 2 (duplicated formatter) lives in model.py.
cp "$TEMPLATE/_defects/tasks/reminders.py" src/tasks/reminders.py
cp "$TEMPLATE/_defects/tasks/model.py" src/tasks/model.py
seed_commit "feat(tasks): desktop notifications for due reminders" \
  "Add notify_desktop and a short formatter for the notification body."

git push -q origin feat/reminders

# Back to the feature branch (it is the PR we review).
git checkout -q feat/reminders

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline main..feat/reminders   # the PR diff"
echo "   make test        # RED on feat/reminders (off-by-one), GREEN on clean-baseline"
echo "   git diff main...HEAD                                   # what review sees"
echo "   three planted defects: off-by-one (P1), command injection (P0), duplicated formatter (P2)"
