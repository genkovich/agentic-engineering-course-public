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

# 2) Рев'ю таки згенеровано (вердикт у ТЕКСТІ відповіді асистента, не в сирому ndjson —
#    сирий транскрипт містить і вміст прочитаних файлів, де ці слова теж трапляються).
if [ -f "$T" ] && transcript_text "$T" | grep -qE 'ACCEPT|WARN|REJECT|Вердикт'; then
  _ok "рев'ю згенеровано (є вердикт у відповіді)"
else
  _fail "рев'ю не знайдено — агент мав видати ACCEPT/WARN/REJECT"
fi

exit $FAILED
