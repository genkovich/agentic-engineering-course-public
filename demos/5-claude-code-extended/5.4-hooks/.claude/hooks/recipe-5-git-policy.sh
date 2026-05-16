#!/usr/bin/env bash
# Slide 4 — приклад `if` field у hook конфігурації.
# Event: PreToolUse, matcher: "Bash" + if: "Bash(git push --force *)".
# matcher активує групу для всіх Bash викликів — але hook process спавниться
# ТІЛЬКИ коли if-permission rule матчить (handler-level фільтр).
# Дія: блокувати force-push у protected branches (main/master/production).
set -euo pipefail

INPUT="$(cat)"
CMD="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("command", ""))
except Exception:
    print("")
')"

[ -z "$CMD" ] && exit 0

PROTECTED_BRANCHES=("main" "master" "production")
for branch in "${PROTECTED_BRANCHES[@]}"; do
  if [[ "$CMD" =~ git[[:space:]]+push[[:space:]]+(-f|--force|--force-with-lease).*${branch}([[:space:]]|$) ]]; then
    echo "BLOCKED: force-push to protected branch '${branch}' is not allowed (recipe-5-git-policy)." >&2
    echo "Reason: protected branches require regular pushes only. Use a feature branch + PR." >&2
    exit 2
  fi
done

exit 0
