#!/usr/bin/env bash
# setup.sh — build sandbox/ : the SAME seed monorepo as 10.1 (five commits,
# billing / queue / auth / reports) plus a sixth "team prep" commit that makes
# the repo ready for an Agent Teams run:
#   - stable reports test (the intentionally flaky one from 10.1 would randomly
#     redden the TaskCompleted gate),
#   - team etiquette in CLAUDE.md,
#   - .claude/ with the agent-teams env flag, task-gate.sh (TaskCompleted
#     quality gate, verbatim from lecture 10.4 episode 4) and task-log.sh
#     (passive JSONL inspector of team hook payloads).
# Template packages come from ../10.1-subagents/template — the team run rides
# the same monorepo the subagent lecture used. Re-runnable: wipes sandbox/.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/../10.1-subagents/template"
OVERLAY="$ROOT/overlay"
SB="$ROOT/sandbox"

if [ ! -d "$TEMPLATE" ]; then
  echo "❌ $TEMPLATE не знайдено — демо 10.4 будується на template з 10.1-subagents." >&2
  exit 1
fi

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

# 1-5. the same five seed commits as 10.1 (scaffold + four package surfaces)

cp "$TEMPLATE/package.json" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/CLAUDE.md" .
cp -R "$TEMPLATE/.claude" .
seed_commit "chore: scaffold subagents demo monorepo" \
  "Node workspace (no deps), .gitignore, repo etiquette in CLAUDE.md, read-only ro-reviewer subagent."

mkdir -p packages/billing/__tests__
cp "$TEMPLATE/packages/billing/invoice.js" packages/billing/
cp "$TEMPLATE/packages/billing/discount.js" packages/billing/
cp "$TEMPLATE/packages/billing/__tests__/invoice.test.js" packages/billing/__tests__/
seed_commit "feat(billing): invoice builder with line items, discount and tax"

mkdir -p packages/queue/__tests__
cp "$TEMPLATE/packages/queue/consumer.js" packages/queue/
cp "$TEMPLATE/packages/queue/__tests__/consumer.test.js" packages/queue/__tests__/
seed_commit "feat(queue): retry-with-backoff consumer and dead-letter handling"

mkdir -p packages/auth/__tests__
cp "$TEMPLATE/packages/auth/middleware.js" packages/auth/
cp "$TEMPLATE/packages/auth/session.js" packages/auth/
cp "$TEMPLATE/packages/auth/__tests__/auth.test.js" packages/auth/__tests__/
seed_commit "feat(auth): bearer auth middleware over an in-memory session store"

mkdir -p packages/reports/__tests__
cp "$TEMPLATE/packages/reports/summary.js" packages/reports/
cp "$TEMPLATE/packages/reports/__tests__/summary.flaky.test.js" packages/reports/__tests__/
seed_commit "feat(reports): daily summary (with a known flaky test)" \
  "summary.flaky.test.js is intentionally non-deterministic — the 'find flaky tests' surface."

# 6. team prep: stable reports test + team etiquette + .claude (env flag, hooks)
rm packages/reports/__tests__/summary.flaky.test.js
cp "$OVERLAY/packages/reports/__tests__/summary.test.js" packages/reports/__tests__/
cp "$OVERLAY/CLAUDE.md" .
mkdir -p .claude/hooks
cp "$OVERLAY/.claude/settings.json" .claude/
cp "$OVERLAY/.claude/hooks/task-gate.sh" .claude/hooks/
cp "$OVERLAY/.claude/hooks/task-log.sh" .claude/hooks/
chmod +x .claude/hooks/task-gate.sh .claude/hooks/task-log.sh
seed_commit "chore(team): prep the monorepo for an agent-teams run" \
  "Deterministic reports test (the flaky one would randomly redden the TaskCompleted gate), team etiquette in CLAUDE.md, agent-teams env flag + task-gate.sh + task-log.sh in .claude/."

git branch -M main

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline      # 5 seed-комітів з 10.1 + 6-й team-prep"
echo "   cd sandbox && node --test            # ВСІ пакети зелені (flaky нейтралізовано)"
echo "   cd sandbox && claude                 # spawn-промпт зі screencast-prompts.md, епізод 1"
echo "   другий термінал:  ls -a ~/.claude/tasks/            # список задач команди на диску"
echo "                     cat sandbox/.claude/logs/team-events.jsonl   # payload-и team-хуків"
