#!/usr/bin/env bash
# cleanup.sh — reset the remote demo state between takes: close any open PR
# whose head is one of THIS demo's branches and delete those remote branches.
# Touches ONLY the branches this demo owns (feat/token-refresh, feat/rate-limit);
# unrelated branches/PRs (e.g. claude/*) are left untouched. Safe to re-run.
set -e

GH_DEMO_REPO="${GH_DEMO_REPO-genkovich/course-project}"
DEMO_BRANCHES=("feat/token-refresh" "feat/rate-limit")

if [ -z "$GH_DEMO_REPO" ]; then
  echo "GH_DEMO_REPO is empty — local-only mode, nothing remote to clean."
  exit 0
fi

for br in "${DEMO_BRANCHES[@]}"; do
  # Close any open PR whose head is this demo branch (closing with
  # --delete-branch also removes the remote ref).
  for num in $(gh pr list -R "$GH_DEMO_REPO" --head "$br" --state open \
                 --json number --jq '.[].number' 2>/dev/null || true); do
    echo "closing PR #$num (head: $br)"
    gh pr close "$num" -R "$GH_DEMO_REPO" --delete-branch >/dev/null 2>&1 || true
  done
  # Delete the remote branch if it still exists (PR-less branch, or close didn't).
  if gh api "repos/$GH_DEMO_REPO/branches/$br" >/dev/null 2>&1; then
    echo "deleting remote branch $br"
    gh api -X DELETE "repos/$GH_DEMO_REPO/git/refs/heads/$br" >/dev/null 2>&1 || true
  fi
done

echo "✅ remote demo state cleaned on $GH_DEMO_REPO"
