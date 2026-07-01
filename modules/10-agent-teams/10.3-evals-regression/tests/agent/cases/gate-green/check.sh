#!/usr/bin/env bash
# check.sh — ДЕТЕРМІНОВАНИЙ чекер для gate-green.
# Асерт на РЕЗУЛЬТАТ: (1) гейт `node --test` зелений, (2) тести НЕ чіпали (не gaming),
# (3) стаб реально замінено реалізацією.
set -uo pipefail
. "$LIB_DIR/common.sh"

FAILED=0
SB="$SANDBOX"

if ! command -v node >/dev/null 2>&1; then
  _fail "node відсутній"
  exit 1
fi

# 1) Гейт зелений.
if ( cd "$SB" && node --test >/dev/null 2>&1 ); then
  _ok "гейт node --test зелений"
else
  _fail "гейт node --test ЧЕРВОНИЙ — total() не доведено до зеленого"
fi

# 2) Тести незаймані (не «підігнали тест під код»).
assert_clean_diff "$SB" "test" "test/ незаймано (тести не редагували)"

# 3) Стаб замінено реальною реалізацією.
assert_file_absent_value "$SB/src/total.js" "not implemented" "стаб 'not implemented' прибрано"

exit $FAILED
