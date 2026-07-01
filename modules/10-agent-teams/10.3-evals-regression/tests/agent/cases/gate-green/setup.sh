#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса gate-green.
# Курс-специфічний кейс: регресить verify-gate (порт скіла 7.6 + Stop-hook).
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture gate "$SB"

# Стейджимо .claude/ зі скілом verify-gate + Stop-hook (гейт = node --test).
cp -R "$CASE_DIR/config/.claude" "$SB/.claude"
[ -f "$SB/.claude/hooks/verify.sh" ] && chmod +x "$SB/.claude/hooks/verify.sh"

sandbox_git_init "$SB"

if [ -n "${BREAK:-}" ]; then
  echo "[BREAK] gate-green: детермінований чекер однаково ловить gaming тестів; BREAK — no-op." >&2
fi
