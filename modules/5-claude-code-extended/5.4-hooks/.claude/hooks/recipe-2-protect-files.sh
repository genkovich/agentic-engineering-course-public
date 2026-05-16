#!/usr/bin/env bash
# Slide 6.2 — File protection
# Event: PreToolUse, matcher: Edit|Write
# Дія: блокувати запис у sensitive файли (.env, .git/*, секрети, credentials).
# exit 2 → Claude Code показує stderr як reason і відмовляє у дії.
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("file_path", ""))
except Exception:
    print("")
')"

[ -z "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *.env|*.env.*|*/.env|*/.env.*)
    echo "BLOCKED: edits to .env files are not allowed (recipe-2-protect-files)." >&2
    echo "Reason: env files contain secrets. Use settings.local.json.example as template." >&2
    exit 2
    ;;
  *.git/*|*/.git/*)
    echo "BLOCKED: edits inside .git directory are not allowed." >&2
    exit 2
    ;;
  */id_rsa|*/id_ed25519|*/.ssh/*)
    echo "BLOCKED: SSH keys and ~/.ssh contents are protected." >&2
    exit 2
    ;;
  */credentials|*/credentials.json|*/service-account*.json)
    echo "BLOCKED: credentials files are protected." >&2
    exit 2
    ;;
esac

exit 0
