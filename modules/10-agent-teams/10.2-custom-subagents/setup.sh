#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained monorepo git repo with a small
# seed history, ready for the 10.2 custom-subagents authoring screencasts. Two
# surfaces: packages/queue (a subtle duplicate-requeue bug — the reasoning
# target for the haiku-vs-opus model comparison) and packages/auth (a second
# file to "fix" so the least-privilege demo has somewhere to write). The full
# authored .claude/ (six subagents + settings.json) is copied in too, so every
# screencast runs against a real repo with real agent definitions on disk.
# Re-runnable: wipes sandbox/ and rebuilds. sandbox/ is git-ignored by the
# monorepo; the monorepo keeps just template/ + fixtures/ + this script.
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

# 1. scaffold: workspace marker, ignore rules, repo etiquette, the authored .claude/
cp "$TEMPLATE/package.json" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/CLAUDE.md" .
cp -R "$TEMPLATE/.claude" .
seed_commit "chore: scaffold custom-subagents demo monorepo" \
  "Node workspace (no deps), .gitignore, repo etiquette in CLAUDE.md, six authored subagents + settings.json in .claude/."

# 2. queue surface: RabbitMQ-style retry + dead-letter (subtle duplicate-requeue bug)
mkdir -p packages/queue/__tests__
cp "$TEMPLATE/packages/queue/consumer.js" packages/queue/
cp "$TEMPLATE/packages/queue/__tests__/consumer.test.js" packages/queue/__tests__/
seed_commit "feat(queue): retry-with-backoff consumer and dead-letter handling"

# 3. auth surface: Bearer middleware + session store (a place for file-writer to fix)
mkdir -p packages/auth
cp "$TEMPLATE/packages/auth/middleware.js" packages/auth/
cp "$TEMPLATE/packages/auth/session.js" packages/auth/
seed_commit "feat(auth): bearer auth middleware over an in-memory session store"

git branch -M main

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline      # seed history with Co-Authored-By: Claude"
echo "   cd sandbox && node --test            # queue tests green (bug is on an untested edge)"
echo "   cd sandbox && ls .claude/agents      # six authored subagents"
echo "   cd sandbox && claude                 # start a session; copy a prompt from screencast-prompts.md"
