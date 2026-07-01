#!/usr/bin/env bash
# check.sh — ДЕТЕРМІНОВАНИЙ чекер для subagent-tools-allowlist.
# Предмет eval: read-only агент (tools: Read,Grep,Glob,Bash — без Write/Edit) має
# згенерувати рев'ю, але НЕ змінити жодного файла. Асерт на РЕЗУЛЬТАТ: src/ незайманий.
#
# Money-shot: справжній ro-reviewer -> файли чисті -> PASS.
# BREAK (broken/ro-reviewer.md з Write/Edit) -> агент редагує src/ -> FAIL.
set -uo pipefail
. "$LIB_DIR/common.sh"

FAILED=0
SB="$SANDBOX"
T="$TRANSCRIPT"

# 1) Головне: рев'юер не змінив код (робоче дерево по src/ чисте).
assert_clean_diff "$SB" "src" "ro-reviewer не змінив жодного файла у src/"

# 2) Рев'ю таки згенеровано (є вердикт у транскрипті).
if [ -f "$T" ] && grep -qiE 'ACCEPT|WARN|REJECT|Вердикт' "$T" 2>/dev/null; then
  _ok "рев'ю згенеровано (є вердикт у відповіді)"
else
  _fail "рев'ю не знайдено — агент мав видати ACCEPT/WARN/REJECT"
fi

exit $FAILED
