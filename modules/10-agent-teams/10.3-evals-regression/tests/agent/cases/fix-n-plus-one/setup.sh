#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса fix-n-plus-one (generic-шаблон).
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture nplusone "$SB"
sandbox_git_init "$SB"

if [ -n "${BREAK:-}" ]; then
  echo "[BREAK] fix-n-plus-one — generic-кейс без guardrail-конфіга; BREAK тут no-op." >&2
fi
