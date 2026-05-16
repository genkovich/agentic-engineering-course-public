#!/usr/bin/env bash
# Slide 8 — Observability: tool call trace.
# Single hook script для двох events:
#   PreToolUse   → invoked as: debug-tool-trace.sh pre   → пише {event:"pre",  tool, input}
#   PostToolUse  → invoked as: debug-tool-trace.sh post  → пише {event:"post", tool, output_summary, duration?}
# Async — не блокує. Перед записом — pipe через secrets-strip.py.
set -euo pipefail

PHASE="${1:-pre}"
LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
LOG_FILE="$LOG_DIR/tool-trace.jsonl"
mkdir -p "$LOG_DIR"

INPUT="$(cat)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Збагачуємо payload tags-ами, потім стрипимо секрети, потім append.
printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {'raw': sys.stdin.read()}
out = {
    'ts': '$TS',
    'event': '$PHASE',
    'tool': d.get('tool_name') or d.get('tool') or '?',
    'session_id': d.get('session_id', ''),
    'tool_input': d.get('tool_input', {}),
    'tool_response': d.get('tool_response', None),
}
json.dump(out, sys.stdout, ensure_ascii=False)
" | python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/secrets-strip.py" \
  | tr -d '\n' >> "$LOG_FILE"
printf '\n' >> "$LOG_FILE"

exit 0
