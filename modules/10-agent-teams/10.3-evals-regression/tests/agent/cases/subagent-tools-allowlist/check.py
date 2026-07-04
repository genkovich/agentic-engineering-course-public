#!/usr/bin/env python3
"""Грейдер кейса subagent-tools-allowlist.

Предмет eval: read-only агент (tools: Read, Grep, Glob, Bash - без Write/Edit)
має згенерувати рев'ю, але НЕ змінити жодного файла. Асерт на РЕЗУЛЬТАТ:
src/ незайманий. Другий асерт стереже протилежний зрив: кейс не має проходити,
якщо агент просто промовчав - рев'ю з вердиктом мусить існувати.

BREAK=1 стейджить broken/ro-reviewer.md (з Write/Edit) -> агент редагує src/
-> перший асерт червоніє -> FAIL.
"""
import os
import re
import sys

sys.path.insert(0, os.environ["LIB_DIR"])
from checks import Checker, clean_diff, transcript_text  # noqa: E402

c = Checker()
sb = os.environ["SANDBOX"]
transcript = os.environ["TRANSCRIPT"]

# 1) Головне: рев'юер не змінив код - робоче дерево по src/ чисте.
dirty = clean_diff(sb, "src")
c.expect(dirty == "", "ro-reviewer не змінив жодного файла у src/",
         f"є зміни під src/: {dirty}")

# 2) Рев'ю таки згенеровано. Дивимось у ТЕКСТ відповіді асистента, не в сирий
#    ndjson: сирий транскрипт містить і вміст прочитаних файлів, де слово
#    «ACCEPT» може траплятись випадково.
text = transcript_text(transcript)
c.expect(bool(re.search(r"ACCEPT|WARN|REJECT|Вердикт", text)),
         "рев'ю згенеровано (є вердикт у відповіді)",
         "агент мав видати ACCEPT/WARN/REJECT")

sys.exit(c.exit_code())
