#!/usr/bin/env bash
# Smoke test для stage-2-feature-first: 6 endpoints, all 2xx.
# Usage: ./scripts/smoke.sh [BASE_URL]
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
EMAIL="smoke-$(date +%s)@example.com"
PASSWORD="hunter2hunter2"

fail() {
    echo "✗ $1"
    exit 1
}
ok() {
    echo "✓ $1"
}

# 1. POST /auth/register
REGISTER=$(curl -sS -o /tmp/smoke-register.json -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
    "${BASE_URL}/auth/register")
[ "$REGISTER" = "201" ] || fail "register expected 201 got $REGISTER ($(cat /tmp/smoke-register.json))"
USER_ID=$(grep -oE '"user_id":"[^"]+"' /tmp/smoke-register.json | cut -d'"' -f4)
[ -n "$USER_ID" ] || fail "user_id missing in register response"
ok "register → 201"

# 2. POST /auth/login
LOGIN=$(curl -sS -o /tmp/smoke-login.json -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
    "${BASE_URL}/auth/login")
[ "$LOGIN" = "200" ] || fail "login expected 200 got $LOGIN"
ok "login → 200"

# 3. GET /products
PRODUCTS=$(curl -sS -o /tmp/smoke-products.json -w "%{http_code}" "${BASE_URL}/products")
[ "$PRODUCTS" = "200" ] || fail "products expected 200 got $PRODUCTS"
ok "products → 200"

# 4. POST /orders
ORDER=$(curl -sS -o /tmp/smoke-order.json -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d "{\"user_id\":\"${USER_ID}\",\"total_cents\":4500}" \
    "${BASE_URL}/orders")
[ "$ORDER" = "201" ] || fail "order expected 201 got $ORDER"
ok "order → 201"

# 5. POST /subscriptions
SUB=$(curl -sS -o /tmp/smoke-sub.json -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d "{\"user_id\":\"${USER_ID}\",\"plan\":\"pro\"}" \
    "${BASE_URL}/subscriptions")
[ "$SUB" = "201" ] || fail "subscription expected 201 got $SUB"
ok "subscription → 201"

# 6. POST /notifications/test
NOTIF=$(curl -sS -o /tmp/smoke-notif.json -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d "{\"user_id\":\"${USER_ID}\",\"channel\":\"email\",\"payload\":\"welcome\"}" \
    "${BASE_URL}/notifications/test")
[ "$NOTIF" = "200" ] || fail "notification expected 200 got $NOTIF"
ok "notification → 200"

echo
echo "All 6 endpoints passed."
