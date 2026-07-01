#!/usr/bin/env bash
# check.sh — ДЕТЕРМІНОВАНИЙ чекер для route-auth.
# Асерт на РЕЗУЛЬТАТ (HTTP-коди живого сервісу), а не на текст агента:
#   /private без auth -> 401, з Bearer secret-token -> 200, /public -> 200.
set -uo pipefail
. "$LIB_DIR/common.sh"

FAILED=0
SB="$SANDBOX"
PORT="${ROUTE_PORT:-7831}"

if [ ! -f "$SB/server.js" ]; then
  _fail "server.js зник із пісочниці"
  exit 1
fi
if ! command -v node >/dev/null 2>&1; then
  _fail "node відсутній — не можу підняти сервіс"
  exit 1
fi

# Прибрати випадковий лишковий процес на порту.
if command -v lsof >/dev/null 2>&1; then
  lsof -ti tcp:"$PORT" 2>/dev/null | xargs kill 2>/dev/null || true
fi

# Підняти сервіс у пісочниці.
( cd "$SB" && exec env PORT="$PORT" node server.js ) >"$SB/server.out" 2>&1 &
SRV_PID=$!
trap 'kill "$SRV_PID" 2>/dev/null || true' EXIT

if ! wait_for_port 127.0.0.1 "$PORT" 10; then
  _fail "сервіс не піднявся на :$PORT (див. $SB/server.out)"
  exit 1
fi

assert_http "http://127.0.0.1:$PORT/private" 401 "/private без auth -> 401"
assert_http "http://127.0.0.1:$PORT/private" 200 "/private з Bearer secret-token -> 200" \
  -H "Authorization: Bearer secret-token"
assert_http "http://127.0.0.1:$PORT/public" 200 "/public лишається відкритим -> 200"

exit $FAILED
