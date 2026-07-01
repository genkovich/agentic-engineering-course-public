#!/usr/bin/env bash
# protect-env.sh — PreToolUse guardrail: блокує читання .env.
# Лінія від 5.4 recipe-2 protect-files (там блок на Write у .env) — тут розширено
# на Read і на shell-обхід (cat/head/grep/source .env тощо).
# exit 2 → Claude Code показує stderr як reason і ВІДМОВЛЯЄ у дії.
#
# Це і є предмет eval forbid-env-read: цей файл — частина версіонованої .claude/.
# Прибери його (BREAK) — і секрет тече у вивід агента; кейс червоніє.
set -uo pipefail

INPUT="$(cat)"

# JSON іде у stdin python3; програма — в -c (інакше heredoc/stdin конфліктують).
verdict="$(printf '%s' "$INPUT" | python3 -c '
import json, sys, re
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
tool = d.get("tool_name", "")
ti = d.get("tool_input", {}) or {}
fp = str(ti.get("file_path", "") or "")
cmd = str(ti.get("command", "") or "")

def is_env_path(p):
    return bool(re.search(r"(^|/)\.env(\.|$)", p))

if tool in ("Read", "Write", "Edit") and is_env_path(fp):
    print("BLOCKED: file .env access denied (protect-env guardrail).")
    sys.exit(0)

if tool == "Bash" and re.search(r"\.env(\b|$)", cmd):
    readers = r"\b(cat|less|more|head|tail|grep|egrep|fgrep|strings|od|xxd|nl|tac|source|printenv|env|awk|sed|cp|mv|read)\b"
    if re.search(readers, cmd) or re.search(r"(^|\s)\.\s", cmd):
        print("BLOCKED: shell read of .env denied (protect-env guardrail).")
        sys.exit(0)
')"

if [ -n "$verdict" ]; then
  echo "$verdict" >&2
  echo "Reason: .env містить секрети. Користуйся назвами змінних, не значеннями." >&2
  exit 2
fi

exit 0
