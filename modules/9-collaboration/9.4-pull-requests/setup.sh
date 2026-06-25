#!/usr/bin/env bash
# setup.sh [sandbox|rules|perms] — build sandbox/ for the 9.4 Pull Requests
# screencasts. Unlike 9.1-9.3, `gh pr create` talks to the real GitHub API, so
# a fully-local fixture is impossible. The fixture here is a deterministic local
# SEED (history, branches, code, configs) PLUS a real `origin` on GitHub.
#
# Modes — one start state per screencast (each wipes sandbox/ and rebuilds):
#   sandbox  base repo + pushed feat/token-refresh + demo issue; CLAUDE.md has
#            NO PR section, no PR template, default permissions  -> SC#1
#   rules    base + .github/pull_request_template.md + `## Pull requests` in
#            CLAUDE.md + fix-issue skill + a 2nd branch feat/rate-limit -> SC#2
#   perms    base + .claude/settings.json (allow gh pr create / ask gh pr merge) -> SC#3
#
# Remote: GH_DEMO_REPO defaults to genkovich/course-project. Set it empty
# (GH_DEMO_REPO= make sandbox) for a network-free local build — handy for
# verifying the seed without touching GitHub. Re-runnable: cleans the remote
# demo branches/PRs first, then force-pushes a fresh seed.
set -e

MODE="${1:-sandbox}"
case "$MODE" in
  sandbox|rules|perms) ;;
  *) echo "usage: setup.sh [sandbox|rules|perms]"; exit 2 ;;
esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$ROOT/template"
SB="$ROOT/sandbox"
GH_DEMO_REPO="${GH_DEMO_REPO-genkovich/course-project}"

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

# ── 1. base seed history on main ───────────────────────────────────────────
mkdir -p src/api src/tests
cp "$TEMPLATE/CLAUDE.md" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/.env.example" .
cp "$TEMPLATE/src/api/__init__.py" src/api/__init__.py
cp "$TEMPLATE/src/tests/__init__.py" src/tests/__init__.py
seed_commit "chore: scaffold api package" \
  "Package skeleton: api/ and tests/, plus repo etiquette in CLAUDE.md."

cp "$TEMPLATE/src/api/users.py" src/api/users.py
seed_commit "feat(api): add users listing"

cp "$TEMPLATE/src/api/token.py" src/api/token.py
cp "$TEMPLATE/src/api/auth.py" src/api/auth.py
seed_commit "feat(auth): issue access tokens on login" \
  "Tokens carry an expiry; an expired token is rejected (no refresh yet)."

cp "$TEMPLATE/src/tests/test_token.py" src/tests/test_token.py
seed_commit "test(auth): cover token issuance"

git branch -M main

# ── 2. mode extras land on main BEFORE feature branches fork off ───────────
#    Feature branches must fork from the FINAL main of this mode, so that
#    `git diff main..feat/*` shows only the feature change (and not a phantom
#    reverse-diff of the rules/perms commit).
if [ "$MODE" = "rules" ]; then
  mkdir -p .github .claude/skills/fix-issue
  cp "$TEMPLATE/_rules/pull_request_template.md" .github/pull_request_template.md
  cat "$TEMPLATE/_rules/claude-pr-section.md" >> CLAUDE.md
  cp "$TEMPLATE/_rules/fix-issue-SKILL.md" .claude/skills/fix-issue/SKILL.md
  seed_commit "chore: add PR template, PR rules in CLAUDE.md, fix-issue skill" \
    "Structure (.github/pull_request_template.md) + how to fill it (## Pull requests in CLAUDE.md) + the issue->fix->PR skill."
fi

if [ "$MODE" = "perms" ]; then
  mkdir -p .claude
  cp "$TEMPLATE/_perms/settings.json" .claude/settings.json
  seed_commit "chore(claude): allow gh pr create, ask before merge" \
    "Create is reversible -> allow; merge is irreversible -> ask."
fi

# ── 3. feature branch feat/token-refresh (every mode) ──────────────────────
#    Real logic change off main: an expired token is now refreshed instead of
#    rejected. This branch-vs-main diff is what the agent summarises in SC#1/#2.
git checkout -q -b feat/token-refresh
cat > src/api/token.py <<'PY'
"""Access-token issuance and refresh."""

import time

TTL_SECONDS = 3600


def now():
    """Current timestamp in seconds."""
    return int(time.time())


def issue(user_id):
    """Issue a fresh access token for the user, valid for one hour."""
    return {
        "user_id": user_id,
        "token": "tok-%s" % user_id,
        "expires_at": now() + TTL_SECONDS,
    }


def is_valid(token):
    """True while the token has not reached its expiry."""
    return token.get("expires_at", 0) > now()


def refresh(token):
    """Return a still-valid token, re-issuing it when it has expired."""
    if is_valid(token):
        return token
    return issue(token["user_id"])
PY
cat > src/api/auth.py <<'PY'
"""Authentication: log a user in, hand back a token, refresh it on expiry."""

from api import token


def login(user_id):
    """Authenticate the user and issue an access token."""
    return token.issue(user_id)


def authorize(tok):
    """Refresh the token when it has expired, then allow the request.

    The request no longer fails on an expired token: we transparently
    re-issue it and carry on. Returns the (possibly refreshed) token.
    """
    return token.refresh(tok)
PY
seed_commit "feat(auth): refresh access token on expiry" \
  "Check the token before each request and re-issue it when it has expired, instead of rejecting the call."

cat > src/tests/test_refresh.py <<'PY'
import unittest

from api import token


class RefreshTest(unittest.TestCase):
    def test_valid_token_is_returned_unchanged(self):
        tok = token.issue(7)
        self.assertEqual(token.refresh(tok), tok)

    def test_expired_token_is_reissued(self):
        stale = {"user_id": 7, "token": "tok-7", "expires_at": token.now() - 1}
        fresh = token.refresh(stale)
        self.assertTrue(token.is_valid(fresh))
        self.assertEqual(fresh["user_id"], 7)


if __name__ == "__main__":
    unittest.main()
PY
seed_commit "test(auth): cover token refresh"
git checkout -q main

# ── 4. rules mode: a 2nd, contrasting branch for the "second PR" beat ──────
if [ "$MODE" = "rules" ]; then
  git checkout -q -b feat/rate-limit
  cat > src/api/rate_limit.py <<'PY'
"""Simple fixed-window request rate limiting."""

import time

WINDOW_SECONDS = 60
MAX_REQUESTS = 100

_hits = {}


def allow(client_id):
    """True while the client stays under its per-window request budget."""
    window = int(time.time()) // WINDOW_SECONDS
    key = (client_id, window)
    _hits[key] = _hits.get(key, 0) + 1
    return _hits[key] <= MAX_REQUESTS
PY
  seed_commit "feat(api): add request rate limiting" \
    "Fixed-window limiter: at most MAX_REQUESTS per client per WINDOW_SECONDS."
  cat > src/tests/test_rate_limit.py <<'PY'
import unittest

from api import rate_limit


class RateLimitTest(unittest.TestCase):
    def test_allows_up_to_the_budget(self):
        rate_limit._hits.clear()
        allowed = [rate_limit.allow("c1") for _ in range(rate_limit.MAX_REQUESTS)]
        self.assertTrue(all(allowed))

    def test_blocks_past_the_budget(self):
        rate_limit._hits.clear()
        for _ in range(rate_limit.MAX_REQUESTS):
            rate_limit.allow("c1")
        self.assertFalse(rate_limit.allow("c1"))


if __name__ == "__main__":
    unittest.main()
PY
  seed_commit "test(api): cover rate limiting"
  git checkout -q main
fi

# Working-tree-only secret (git-ignored), parallel to 9.1's secret-guard prop.
printf 'API_KEY=sk-demo-not-a-real-key\n' > .env

# ── 5. remote wiring on GitHub (skipped when GH_DEMO_REPO is empty) ─────────
if [ -n "$GH_DEMO_REPO" ]; then
  echo ""
  echo "→ wiring origin to git@github.com:$GH_DEMO_REPO and pushing seed…"
  GH_DEMO_REPO="$GH_DEMO_REPO" bash "$ROOT/cleanup.sh" || true
  git remote remove origin 2>/dev/null || true
  git remote add origin "git@github.com:$GH_DEMO_REPO"
  git push -q --force origin main
  git push -q --force origin feat/token-refresh
  [ "$MODE" = "rules" ] && git push -q --force origin feat/rate-limit
  git remote set-head origin main >/dev/null 2>&1 || true

  # Ensure a demo issue exists (theme: token refresh). Re-used across takes.
  ISSUE="$(gh issue list -R "$GH_DEMO_REPO" --state open --json number,title \
            --jq 'map(select(.title | test("token";"i"))) | .[0].number // empty' 2>/dev/null || true)"
  if [ -z "$ISSUE" ]; then
    URL="$(gh issue create -R "$GH_DEMO_REPO" \
            --title "Refresh access token on expiry" \
            --body "Authorising with an expired token currently fails — the caller has to log in again. Refresh the token transparently instead." \
            2>/dev/null || true)"
    ISSUE="${URL##*/}"
  fi
  echo "   demo issue: #${ISSUE:-?}  (slides/voice use #214 illustratively — substitute the real number on camera)"
else
  echo ""
  echo "GH_DEMO_REPO empty — local-only build, no remote wiring (no push, no issue)."
fi

echo ""
echo "✅ sandbox ready at $SB  (mode: $MODE)"
echo "   cd sandbox && git log --oneline --all   # seed history + feature branch(es)"
echo "   git diff main..feat/token-refresh        # the change the agent summarises into a PR"
[ "$MODE" = "rules" ] && echo "   cat .github/pull_request_template.md     # structure the platform injects into every PR"
[ "$MODE" = "perms" ] && echo "   cat .claude/settings.json                # allow gh pr create / ask gh pr merge"
