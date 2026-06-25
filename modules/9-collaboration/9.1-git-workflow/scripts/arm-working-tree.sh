#!/usr/bin/env bash
# arm-working-tree.sh — drop a mixed set of uncommitted edits onto the
# sandbox, so the commit / chunking / diff screencasts have real work to
# show. Run after `make sandbox`.
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$HERE/sandbox"
CHANGES="$HERE/changes"

if [ ! -d "$SB/.git" ]; then
  echo "no sandbox yet — run 'make sandbox' first" >&2
  exit 1
fi

# 1. fix(api): users listing now handles the empty cursor   -> modified
cp "$CHANGES/users.py" "$SB/src/api/users.py"
# 2. feat(api): new list-orders endpoint                    -> modified
cp "$CHANGES/orders.py" "$SB/src/api/orders.py"
# 3. test(api): cover the new endpoint                      -> new file
cp "$CHANGES/test_orders.py" "$SB/src/tests/test_orders.py"
# 4. multi-hunk edit in auth.py                             -> for git add -p
cp "$CHANGES/auth.py" "$SB/src/api/auth.py"

echo ""
echo "✅ working tree armed in $SB"
echo "   cd sandbox && git status            # users/orders/auth modified, test_orders new"
echo "   git add -p src/api/auth.py          # two hunks: expiry skew + log line"
