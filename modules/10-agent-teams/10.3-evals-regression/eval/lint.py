#!/usr/bin/env python3
"""lint.py - статичний лінт конфігурації агентів. Нуль токенів, секунди.

Агент не запускається. Лінт читає ТЕКСТ .claude/agents/*.md і звіряє
allowlist tools із контрактом: диф "+Write, +Edit" червоніє ще до прогону.
"""
import sys
from pathlib import Path

# Контракт: очікуваний allowlist кожного агента. Новий агент без запису
# тут - теж помилка: контракт мусить бути свідомим.
EXPECTED_TOOLS = {
    "ro-reviewer": {"Read", "Grep", "Glob", "Bash"},
}

failed = False
for agent_md in sorted(Path(".claude/agents").glob("*.md")):
    # Frontmatter - пари "key: value" між двома лініями "---".
    fm = {}
    for line in agent_md.read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip() == "---":
            break
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()

    name = fm.get("name", agent_md.stem)
    tools = {t.strip() for t in fm.get("tools", "").split(",") if t.strip()}
    expected = EXPECTED_TOOLS.get(name)
    if expected is None:
        print(f"✗ {name}: агента нема в EXPECTED_TOOLS - додай контракт")
        failed = True
    elif tools != expected:
        print(f"✗ {name}: tools {sorted(tools)} != контракт {sorted(expected)}")
        failed = True
    else:
        print(f"✓ {name}: tools збігаються з контрактом")

sys.exit(1 if failed else 0)
