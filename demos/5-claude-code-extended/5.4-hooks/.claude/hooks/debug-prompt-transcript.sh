#!/usr/bin/env bash
# Slide 8 — Prompt/response transcript.
# UserPromptSubmit → debug-prompt-transcript.sh        (no arg, default phase = "user")
# Stop             → debug-prompt-transcript.sh stop   (assistant turn end)
# Async. Пише у logs/transcript.jsonl з sanitization.
set -euo pipefail

PHASE="${1:-user}"
LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
LOG_FILE="$LOG_DIR/transcript.jsonl"
mkdir -p "$LOG_DIR"

INPUT="$(cat)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
prompt = d.get('prompt') or d.get('user_prompt') or ''
stop_reason = d.get('stop_reason', '')
out = {
    'ts': '$TS',
    'event': 'transcript.$PHASE',
    'session_id': d.get('session_id', ''),
    'prompt_preview': prompt[:400] if isinstance(prompt, str) else '',
    'stop_reason': stop_reason,
}
json.dump(out, sys.stdout, ensure_ascii=False)
" | python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/secrets-strip.py" \
  | tr -d '\n' >> "$LOG_FILE"
printf '\n' >> "$LOG_FILE"

exit 0
