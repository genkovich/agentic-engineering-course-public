#!/usr/bin/env bash
# Deterministic stand-in for what the skill-improver subagent writes on a real
# `make outer` run. Appends ONE new rule to the end of the triage skill and ONE
# lesson to lessons.md, both idempotently. This lets `make judge` show 19/20
# without spending tokens on a live `claude` run. In the screencast the same
# edit is produced live by the subagent; here it is scripted so the numbers are
# reproducible in CI.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$ROOT/.claude/skills/triage/SKILL.md"
LESSONS="$ROOT/lessons.md"
RULE='- question | how do i, how to'
LESSON='- issue, сформульований як питання ("how do I", "how to"), це question, а не bug: наївний скіл плутав їх, бо реагував на слово error.'

if grep -qF "$RULE" "$SKILL"; then
  echo "rule already present in SKILL.md - nothing to do"
else
  printf '\n%s\n' "$RULE" >> "$SKILL"
  echo "appended rule to SKILL.md: $RULE"
fi

if grep -qF "$LESSON" "$LESSONS" 2>/dev/null; then
  echo "lesson already present in lessons.md - nothing to do"
else
  printf '\n%s\n' "$LESSON" >> "$LESSONS"
  echo "appended lesson to lessons.md"
fi
