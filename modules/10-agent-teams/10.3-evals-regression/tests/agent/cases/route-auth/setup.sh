#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса route-auth.
# Generic-кейс (портовний шаблон, як у Simon): сервіс із відкритим приватним роутом.
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture route "$SB"
sandbox_git_init "$SB"

# BREAK: для generic-кейса немає guardrail-у в .claude/, але лишаємо гачок —
# у BREAK-режимі підкладаємо «зіпсований» сервіс, де /private завжди 200.
if [ -n "${BREAK:-}" ]; then
  echo "[BREAK] route-auth не має guardrail-конфіга; BREAK тут — no-op (див. forbid-env-read)." >&2
fi
