#!/usr/bin/env bash
# Slide 8 — Subagent lifecycle.
# SubagentStart → debug-subagent-lifecycle.sh start
# SubagentStop  → debug-subagent-lifecycle.sh stop
# Async. Пише у logs/subagent.jsonl з sanitization.
set -euo pipefail

PHASE="${1:-start}"
LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
LOG_FILE="$LOG_DIR/subagent.jsonl"
mkdir -p "$LOG_DIR"

INPUT="$(cat)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
out = {
    'ts': '$TS',
    'event': 'subagent.$PHASE',
    'session_id': d.get('session_id', ''),
    'subagent_type': d.get('subagent_type') or d.get('agent_type', ''),
    'description': d.get('description', ''),
    'result_summary': (d.get('result') or '')[:300] if isinstance(d.get('result'), str) else None,
}
json.dump(out, sys.stdout, ensure_ascii=False)
" | python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/secrets-strip.py" \
  | tr -d '\n' >> "$LOG_FILE"
printf '\n' >> "$LOG_FILE"

exit 0
