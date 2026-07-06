#!/usr/bin/env bash
# Build a throwaway sandbox/ for the 10.6 self-improvement-loop demo.
#
# Two things live here:
#   - the INNER loop: a naive triage skill (.claude/skills/triage/SKILL.md) that
#     labels issues by keyword and mislabels questions as bugs. Held-out score 14/20.
#   - the OUTER loop: a skill-improver subagent that reads the held-out failures
#     and the human relabels, appends one rule to the skill, and opens a draft PR.
#     After its fix the held-out score is 19/20.
#
# The seeded git history includes a few HUMAN RELABEL commits (issue moved
# bug -> question in the tracker). That is the signal the outer loop reads.
# Pure python + git + gh. No npm, no ANTHROPIC_API_KEY for the deterministic
# scoring. Idempotent: wipes and rebuilds sandbox/ every run.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/template"
SB="$ROOT/sandbox"

echo "building sandbox at $SB"
rm -rf "$SB"
mkdir -p "$SB"
cp -r "$TEMPLATE"/. "$SB"/

cd "$SB"
git init -q
git config commit.gpgsign false
git config user.email "demo-author@example.com"
git config user.name "Demo Author"

seed_commit() {
  git add -A
  GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" \
    git commit -q -m "$2" -m "Co-Authored-By: Claude <noreply@noreply.anthropic.com>"
}

# 1. the skill + eval harness go in first
seed_commit "2026-06-01T09:00:00" "init: triage skill v1 + held-out eval (14/20)"

# 2. a batch of incoming issues arrives and gets auto-labelled by the skill
echo "# Relabel log — human corrections in the tracker" > relabels.log
echo "(each line = a human moved an issue the skill got wrong)" >> relabels.log
seed_commit "2026-06-02T10:00:00" "seed: incoming issues auto-labelled by triage"

# 3-5. humans notice the skill calls questions 'bug' and relabel them by hand.
#      These are the deltas the outer loop learns from.
echo "how-do-i-rotate-keys: bug -> question (this is a how-to, not a defect)" >> relabels.log
seed_commit "2026-06-03T11:00:00" "relabel: how-do-i-rotate-keys bug -> question"
echo "how-to-enable-debug: bug -> question (asking how, not reporting a break)" >> relabels.log
seed_commit "2026-06-03T14:00:00" "relabel: how-to-enable-debug bug -> question"
echo "how-do-i-configure-proxy: bug -> question (setup question)" >> relabels.log
seed_commit "2026-06-04T09:00:00" "relabel: how-do-i-configure-proxy bug -> question"

# generate the working gold copy (the mutable ground-truth the loop must not rewrite)
python3 eval/run.py >/dev/null

echo ""
echo "✅ sandbox ready at $SB"
echo ""
echo "next:"
echo "  cd $SB"
echo "  python3 eval/run.py           # held-out score of the naive skill: 14/20"
echo "  git log --oneline             # see the human relabels the outer loop reads"
echo "  cat .claude/skills/triage/SKILL.md   # the artifact under optimization"
