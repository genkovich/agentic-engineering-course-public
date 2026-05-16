#!/usr/bin/env bash
# Slide 8 — Analytics POST на mock receiver.
# Event: PostToolUse (async) — не блокує, не валить workflow.
# Pipeline: stdin JSON → secrets-strip → curl POST $ANALYTICS_URL.
# Якщо ANALYTICS_URL не заданий або сервер недоступний — silent fail.
set -euo pipefail

URL="${ANALYTICS_URL:-http://localhost:8090/events}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

INPUT="$(cat)"

CLEAN="$(printf '%s' "$INPUT" | python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/secrets-strip.py")"

ENRICHED="$(printf '%s' "$CLEAN" | python3 -c "
import json, sys, os
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
d['_ts'] = '$TS'
d['_source'] = 'hooks-toolkit'
json.dump(d, sys.stdout, ensure_ascii=False)
")"

curl -fsS -m 2 -X POST "$URL" \
  -H 'Content-Type: application/json' \
  --data "$ENRICHED" \
  >/dev/null 2>&1 || true

exit 0
