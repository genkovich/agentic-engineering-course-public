#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained git repo with a seed history
# of ~8 Conventional Commits, a good-baseline tag, and one planted bug.
# Re-runnable: wipes sandbox/ and rebuilds. The history lives only inside
# sandbox/ (git-ignored by the monorepo); the monorepo keeps just template/
# plus this script.
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

# 1. scaffold api package — skeleton + repo etiquette
mkdir -p src/api src/tests
cp "$TEMPLATE/CLAUDE.md" .
cp "$TEMPLATE/.gitignore" .
cp "$TEMPLATE/.env.example" .
cp -R "$TEMPLATE/.claude" .
cp "$TEMPLATE/src/api/__init__.py" src/api/__init__.py
cp "$TEMPLATE/src/tests/__init__.py" src/tests/__init__.py
cp "$TEMPLATE/src/api/orders.py" src/api/orders.py
seed_commit "chore: scaffold api package" \
  "Package skeleton: api/ and tests/, plus repo etiquette in CLAUDE.md."

# 2. add cursor pagination — SAFE version (handles the empty cursor)
cat > src/api/pagination.py <<'PY'
"""Cursor-based pagination for list endpoints."""

LIMIT = 20

# In-memory dataset standing in for a database table.
_ROWS = [{"id": i, "name": "item-%d" % i} for i in range(1, 101)]


def query_first():
    """First page of rows, used when no cursor is given."""
    return list(_ROWS)


def query(cursor):
    """Rows whose id is past the given cursor."""
    return [row for row in _ROWS if row["id"] > cursor]


def page(cursor=None):
    """Return one page of rows, starting from cursor (None = first page)."""
    items = query(cursor) if cursor else query_first()
    return items[:LIMIT]
PY
seed_commit "feat(api): add cursor pagination"

# 3. cover pagination with a test, then tag the known-good baseline
cp "$TEMPLATE/src/tests/test_pagination.py" src/tests/test_pagination.py
seed_commit "test(api): cover pagination"
git tag good-baseline

# 4. add users listing
cp "$TEMPLATE/src/api/users.py" src/api/users.py
seed_commit "feat(api): add users listing"

# 5. add token refresh on expiry — v1 logging
cat > src/api/auth.py <<'PY'
"""Authentication helpers: token refresh."""

import logging
import time

log = logging.getLogger("auth")


def now():
    """Current timestamp in seconds."""
    return int(time.time())


def is_expired(token):
    """True if the token has passed its expiry."""
    return token.get("expires_at", 0) <= now()


def issue_new(user):
    """Issue a fresh token for the user, valid for one hour."""
    return {
        "user": user,
        "token": "tok-" + str(user),
        "expires_at": now() + 3600,
    }


def refresh_token(user, token):
    """Return a valid token, refreshing it if the old one expired."""
    if is_expired(token):
        token = issue_new(user)
        log.info("token refreshed")
    return token
PY
seed_commit "feat(auth): add token refresh on expiry" \
  "Check the token before each request and issue a new one when it expired."

# 6. refactor pagination — PLANTED BUG: drops the empty-cursor branch.
#    From here on, test_pagination is red (page() with no cursor crashes).
cp "$TEMPLATE/src/api/pagination.py" src/api/pagination.py
seed_commit "refactor(api): simplify pagination cursor handling" \
  "Collapse the two query paths into one. Empty cursor now falls through to query()."

# 7. usage notes
mkdir -p docs
cp "$TEMPLATE/docs/usage.md" docs/usage.md
seed_commit "docs: usage notes"

# 8. tidy refresh logging
cp "$TEMPLATE/src/api/auth.py" src/api/auth.py
seed_commit "chore(auth): tidy refresh logging"

# Working-tree-only secret for the secret-guard screencast. Git-ignored,
# so it never lands in a commit unless someone forces it (git add -f).
printf 'API_KEY=sk-demo-not-a-real-key\n' > .env

echo ""
echo "✅ sandbox ready at $SB"
echo "   cd sandbox && git log --oneline   # ~8 Conventional commits with Co-Authored-By"
echo "   git tag                           # good-baseline on the last working commit"
echo "   make test                         # red at HEAD (planted bug), green at good-baseline"
echo "   make arm                          # throw mixed edits for the commit/chunk/diff demos"
