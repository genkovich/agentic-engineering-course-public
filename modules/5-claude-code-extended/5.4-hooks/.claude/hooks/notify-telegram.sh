#!/usr/bin/env bash
# Slide 6 (other recipes) — Notification → Telegram.
# Event: Notification, matcher: permission_prompt|idle_prompt
# Якщо TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID не задані — fallback на macOS osascript.
set -euo pipefail

INPUT="$(cat)"

read -r KIND MESSAGE <<<"$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
kind = d.get("notification_type") or d.get("type") or "notification"
msg  = d.get("message") or d.get("title") or "Claude Code is waiting for input"
print(kind, msg)
')"

KIND="${KIND:-notification}"
MESSAGE="${MESSAGE:-Claude Code event}"

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  TEXT="🤖 Claude · ${KIND}: ${MESSAGE}"
  curl -fsS -m 2 \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${TEXT}" \
    >/dev/null 2>&1 || true
elif [ "$(uname -s)" = "Darwin" ]; then
  osascript -e "display notification \"${MESSAGE}\" with title \"Claude · ${KIND}\"" >/dev/null 2>&1 || true
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "Claude · ${KIND}" "${MESSAGE}" >/dev/null 2>&1 || true
fi

exit 0
