#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained monorepo git repo with a small
# seed history, ready for the subagent screencasts. The repo seeds FOUR
# independent search surfaces (billing / queue / auth / reports-flaky) so a
# fan-out of Explore subagents or orchestrator workers has real, separable
# targets. Re-runnable: wipes sandbox/ and rebuilds. The repo lives only inside
# sandbox/ (git-ignored by the monorepo); the monorepo keeps just template/ +
# this script.
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

# 1. scaffold: workspace marker, ignore rules, repo etiquette, read-only reviewer
cp "$TEMPLATE/package.json" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/CLAUDE.md" .
cp -R "$TEMPLATE/.claude" .
seed_commit "chore: scaffold subagents demo monorepo" \
  "Node workspace (no deps), .gitignore, repo etiquette in CLAUDE.md, read-only ro-reviewer subagent."

# 2. billing surface: invoice + discount (rounding / negative-total risk)
mkdir -p packages/billing/__tests__
cp "$TEMPLATE/packages/billing/invoice.js" packages/billing/
cp "$TEMPLATE/packages/billing/discount.js" packages/billing/
cp "$TEMPLATE/packages/billing/__tests__/invoice.test.js" packages/billing/__tests__/
seed_commit "feat(billing): invoice builder with line items, discount and tax"

# 3. queue surface: RabbitMQ-style retry + dead-letter (subtle re-queue bug)
mkdir -p packages/queue/__tests__
cp "$TEMPLATE/packages/queue/consumer.js" packages/queue/
cp "$TEMPLATE/packages/queue/__tests__/consumer.test.js" packages/queue/__tests__/
seed_commit "feat(queue): retry-with-backoff consumer and dead-letter handling"

# 4. auth surface: Bearer middleware + session store (3 files = fan-out targets)
mkdir -p packages/auth/__tests__
cp "$TEMPLATE/packages/auth/middleware.js" packages/auth/
cp "$TEMPLATE/packages/auth/session.js" packages/auth/
cp "$TEMPLATE/packages/auth/__tests__/auth.test.js" packages/auth/__tests__/
seed_commit "feat(auth): bearer auth middleware over an in-memory session store"

# 5. reports surface: summary + an intentionally flaky test
mkdir -p packages/reports/__tests__
cp "$TEMPLATE/packages/reports/summary.js" packages/reports/
cp "$TEMPLATE/packages/reports/__tests__/summary.flaky.test.js" packages/reports/__tests__/
seed_commit "feat(reports): daily summary (with a known flaky test)" \
  "summary.flaky.test.js is intentionally non-deterministic — the 'find flaky tests' surface."

git branch -M main

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline      # seed history with Co-Authored-By: Claude"
echo "   cd sandbox && node --test            # billing/queue/auth pass, reports flaky fails intermittently"
echo "   cd sandbox && claude                 # start a session; copy a prompt from screencast-prompts.md"
