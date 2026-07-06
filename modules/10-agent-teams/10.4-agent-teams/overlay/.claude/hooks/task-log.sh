#!/usr/bin/env bash
# task-log.sh — пасивний інспектор командних подій. Нічого не блокує (завжди exit 0):
# складає сирий stdin-payload хука у .claude/logs/team-events.jsonl, щоб очима
# побачити, що саме несуть TaskCreated / TaskCompleted / TeammateIdle.
EVENT="${1:-unknown}"
INPUT="$(cat)"
mkdir -p .claude/logs
printf '{"hook_event":"%s","ts":"%s","payload":%s}\n' \
  "$EVENT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${INPUT:-null}" \
  >> .claude/logs/team-events.jsonl
exit 0
