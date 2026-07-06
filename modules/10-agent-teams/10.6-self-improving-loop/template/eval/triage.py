#!/usr/bin/env python3
"""Deterministic reference implementation of the triage skill.

It reads the SAME `SKILL.md` the live skill uses, parses its rule list, and
applies the rules exactly as the skill body describes (top to bottom, the LAST
matching rule wins, default `question`). This lets the whole demo score without
an ANTHROPIC_API_KEY, and makes the `skill_md[:1500]` truncation bug real: a
rule appended past char 1500 genuinely disappears from what the classifier sees.
"""
import re
from pathlib import Path

RULE_RE = re.compile(r"^- (\w+) \| (.+)$")
DEFAULT_SKILL = Path(__file__).resolve().parent.parent / ".claude/skills/triage/SKILL.md"


def load_skill(path=None, truncate=None):
    text = Path(path or DEFAULT_SKILL).read_text(encoding="utf-8")
    if truncate is not None:
        text = text[:truncate]  # the intentional bug: skill_md[:1500]
    return text


def parse_rules(skill_text):
    rules = []
    for line in skill_text.splitlines():
        m = RULE_RE.match(line.strip())
        if m:
            label = m.group(1).strip()
            keywords = [k.strip().lower() for k in m.group(2).split(",") if k.strip()]
            rules.append((label, keywords))
    return rules


def classify(issue_text, skill_text):
    text = issue_text.lower()
    rules = parse_rules(skill_text)
    label = "question"  # default: an open request with no clear signal
    for rule_label, keywords in rules:
        if any(kw in text for kw in keywords):
            label = rule_label  # last matching rule wins
    return label


if __name__ == "__main__":
    import sys
    skill = load_skill()
    print(classify(" ".join(sys.argv[1:]), skill))
