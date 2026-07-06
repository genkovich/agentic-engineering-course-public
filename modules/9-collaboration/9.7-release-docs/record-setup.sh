#!/usr/bin/env bash
#
# record-setup.sh — one command to make the 9.7 demo recordable.
#
# It copies this folder out, seeds a real commit history, creates a private
# GitHub repo, sets the API-key secret, lets Actions open PRs, and pushes the
# v0.1.0 baseline — leaving the repo ready with NO release tag. During the
# recording you open a PR (firing docs-drift + version comments) and push v0.2.0
# live (firing changelog + release-notes). The same secret and Actions-PR
# permission serve all four workflows.
#
# Prerequisites (check these first):
#     gh auth status                        # logged in to GitHub
#     export ANTHROPIC_API_KEY=sk-ant-...   # becomes the repo Actions secret
#
# Usage:
#     ./record-setup.sh [repo-name] [target-dir]
#       repo-name   default: release-demo-9-7
#       target-dir  default: $HOME/<repo-name>
#
set -euo pipefail

REPO_NAME="${1:-release-demo-9-7}"
TARGET="${2:-$HOME/$REPO_NAME}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 0. Preconditions -------------------------------------------------------
command -v gh >/dev/null 2>&1 || { echo "need the gh CLI (https://cli.github.com)" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "not logged in — run: gh auth login" >&2; exit 1; }
: "${ANTHROPIC_API_KEY:?export ANTHROPIC_API_KEY=sk-ant-... before running}"
if [[ -e "$TARGET" ]]; then
  echo "$TARGET already exists — remove it or pass another target dir." >&2
  exit 1
fi

# --- 1. Fresh copy + seeded history (git init + commits + v0.1.0 tag) --------
echo "› copying demo to $TARGET"
cp -R "$SRC_DIR" "$TARGET"
cd "$TARGET"
rm -rf .git                # ensure seed-history.sh starts from a clean repo
./seed-history.sh

# --- 2. Create the private repo (adds 'origin'), push main only — no tags ----
echo "› creating private GitHub repo '$REPO_NAME'"
gh repo create "$REPO_NAME" --private --source=. --remote=origin --push
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

# --- 3. Repo secret for the headless `claude -p` step -----------------------
echo "› setting ANTHROPIC_API_KEY secret on $REPO"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY" --repo "$REPO"

# --- 4. Let Actions open the Release-PR -------------------------------------
echo "› allowing Actions to create pull requests"
gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -F default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true >/dev/null

# --- 5. Push the v0.1.0 baseline tag ----------------------------------------
# CI needs it on the remote so `git log v0.1.0..HEAD` resolves during the live
# v0.2.0 run. Pushing it fires one harmless no-op run (nothing to release at
# the baseline itself — the workflow exits cleanly on an empty diff).
echo "› pushing v0.1.0 baseline tag"
git push origin v0.1.0

cat <<EOF

Ready: $REPO is private, seeded, secret set, Actions can open PRs.
No release tag yet. Two live moments to record (full runbook in RECORD.md):

  1. Open a PR (e.g. a branch that documents nothing new):
       git checkout -b show-drift && git commit --allow-empty -m "chore: open PR" \\
         && git push -u origin show-drift && gh pr create --fill
     -> the 'version' workflow comments the proposed v0.2.0, and 'docs-drift'
        comments that filter_by_tag is undocumented in docs/api.md.

  2. Push the release tag:
       git tag v0.2.0 && git push origin v0.2.0
     -> 'changelog' opens a Release-PR; 'release-notes' drafts a GitHub Release
        (~1–2 min in the Actions tab).
EOF
