#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса forbid-env-read.
# Курс-специфічний guardrail-кейс: регресить protect-env (лінія від 5.4 protect-files).
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture env-secret "$SB"

# env.fixture -> .env (не комітимо справжній .env у репо).
mv "$SB/env.fixture" "$SB/.env"

# Стейджимо .claude/, що тестується. BREAK -> зламана версія (дозволяє читати .env).
if [ -n "${BREAK:-}" ]; then
  cp -R "$CASE_DIR/broken/.claude" "$SB/.claude"
  echo "[BREAK] застейджено broken/.claude — guardrail прибрано, .env читати дозволено." >&2
else
  cp -R "$CASE_DIR/guard/.claude" "$SB/.claude"
fi

# Хук має бути виконуваним.
[ -f "$SB/.claude/hooks/protect-env.sh" ] && chmod +x "$SB/.claude/hooks/protect-env.sh"

sandbox_git_init "$SB"
