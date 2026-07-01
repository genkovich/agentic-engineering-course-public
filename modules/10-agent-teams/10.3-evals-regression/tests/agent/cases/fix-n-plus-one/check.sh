#!/usr/bin/env bash
# check.sh — ДЕТЕРМІНОВАНИЙ чекер для fix-n-plus-one.
# Асерт на РЕЗУЛЬТАТ: інструментований лічильник запитів впав до ≤2 (N+1 усунено),
# а звіт лишився коректним. db.js і runner.js — довірені (перекопіюємо з кейса).
set -uo pipefail
. "$LIB_DIR/common.sh"

FAILED=0
SB="$SANDBOX"

if ! command -v node >/dev/null 2>&1; then
  _fail "node відсутній"
  exit 1
fi

# Перекопіюємо довірений раннер (щоб агент не міг його підмінити).
cp "$CASE_DIR/runner.js" "$SB/runner.js"

out="$(cd "$SB" && node runner.js 2>&1)"
rc=$?
printf "  ${C_DIM}runner: %s${C_RESET}\n" "$out"

queries="$(printf '%s' "$out" | sed -n 's/.*queries=\([0-9][0-9]*\).*/\1/p')"

assert_eq "$rc" "0" "runner exit 0 (звіт коректний і N+1 усунено)"
if [ -n "$queries" ] && [ "$queries" -le 2 ]; then
  _ok "SQL-викликів: $queries (≤2)"
else
  _fail "SQL-викликів: ${queries:-?} (>2 — N+1 лишився)"
fi

exit $FAILED
