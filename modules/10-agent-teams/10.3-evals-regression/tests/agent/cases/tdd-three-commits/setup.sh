#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса tdd-three-commits.
# Курс-специфічний кейс: регресить TDD-дисципліну (порт скіла 7.7 на node:test).
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture tdd-task "$SB"
cp -R "$CASE_DIR/config/.claude" "$SB/.claude"
sandbox_git_init "$SB"

if [ -n "${BREAK:-}" ]; then
  echo "[BREAK] tdd-three-commits — детермінований чекер однаково ловить порушення RGR; BREAK no-op." >&2
fi
