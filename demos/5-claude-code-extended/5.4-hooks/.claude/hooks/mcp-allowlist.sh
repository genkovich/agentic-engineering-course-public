#!/usr/bin/env bash
# Slide 11 — MCP security policies через regex matchers.
# Event: PreToolUse, matcher: mcp__.* (всі MCP tool calls — будь-якого сервера).
# Логіка: дістати server name з tool_name (формат mcp__<server>__<tool>),
# перевірити проти $MCP_ALLOWLIST (CSV). Якщо не у списку → exit 0 + JSON deny (slide 5 — structured output).
#
# Чому matcher mcp__.* а не mcp__.*__write.* — лекція 5.4 slide 11:
# create_pr / editJiraIssue / store_note — це теж writes, але в назві немає літерально "write".
# Allowlist по server name працює на всі writes без винятків. Tool naming convention — ненадійна основа.
set -euo pipefail

INPUT="$(cat)"
ALLOWLIST="${MCP_ALLOWLIST:-mcp__filesystem,mcp__memory}"

TOOL_NAME="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_name", ""))
except Exception:
    print("")
')"

# Skip non-MCP calls (matcher вже мав би відфільтрувати, але про всяк випадок)
case "$TOOL_NAME" in
  mcp__*__*) ;;
  *) exit 0 ;;
esac

# Витягуємо server name з будь-якого формату mcp__<server>__<tool>
# (раніше код припускав __write.* — тепер працює для create_, edit_, store_, transition_, ...)
SERVER="$(printf '%s' "$TOOL_NAME" | awk -F'__' '{print "mcp__"$2}')"

# Перевірка проти allowlist (CSV)
if printf ',%s,' "$ALLOWLIST" | grep -qF ",$SERVER,"; then
  exit 0
fi

# structured JSON deny — Claude Code побачить permissionDecision=deny і покаже reason
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "MCP server '$SERVER' not in MCP_ALLOWLIST. Current allowlist: $ALLOWLIST. Tool: $TOOL_NAME"
  }
}
EOF
exit 0
