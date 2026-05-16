#!/usr/bin/env bash
# Slide 6.1 — Auto-format після Edit/Write
# Event: PostToolUse, matcher: Edit|Write
# Дія: знайти редагований файл у вхідному JSON, прогнати через форматер за extension.
# Не блокуючий — це side-effect, не gate.
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
[ ! -f "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md|*.css|*.html)
    command -v prettier >/dev/null 2>&1 && prettier --write "$FILE_PATH" >&2 || true
    ;;
  *.py)
    command -v black >/dev/null 2>&1 && black --quiet "$FILE_PATH" >&2 || true
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && gofmt -w "$FILE_PATH" >&2 || true
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt --quiet "$FILE_PATH" >&2 || true
    ;;
esac

exit 0
