#!/usr/bin/env bash
#
# reset-demo.sh — put the working tree back so a demo can be re-recorded.
#
# Run inside the demo repo between takes. It reverts every working-tree edit the
# pipeline makes — the bumped version (pyproject.toml), the curated changelog,
# the doc-drift fix (docs/api.md), and any codified rules — returns to main, and
# clears throwaway release branches and tags (keeping the v0.1.0 baseline). It
# touches local state only — a Release-PR or draft Release left on GitHub from a
# live take you close by hand (`gh pr close ...` / `gh release delete ...`).
#
set -euo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo — run inside the demo copy" >&2; exit 1; }

# 1. Drop uncommitted demo edits: version bump, curated [Unreleased], doc-drift
#    fix, and codified rules.
git checkout -- pyproject.toml docs/CHANGELOG.md docs/api.md .claude/rules/ 2>/dev/null || true
git clean -fdq .claude/rules/ 2>/dev/null || true   # remove any new rule file

# 2. Back to main, remove throwaway pipeline branches from earlier takes.
git checkout -q main 2>/dev/null || true
while IFS= read -r b; do
  [[ -n "$b" ]] && git branch -D "$b" >/dev/null 2>&1 || true
done < <(git branch --format='%(refname:short)' | grep -E '^(changelog|release-notes|docs-drift)/' || true)

# 3. Remove local v0.2.0+ tags, keep the v0.1.0 baseline.
while IFS= read -r t; do
  [[ -n "$t" ]] && git tag -d "$t" >/dev/null 2>&1 || true
done < <(git tag | grep -vx 'v0.1.0' || true)

echo "Reset: working tree clean, on main, only v0.1.0 remains."
echo "Re-run the demo from the top. (Remote PR/draft from a live take: close by hand.)"
