# Demo 10.6 — Self-Improvement Loop (skill self-editor).
#
# Builds a throwaway sandbox/ with a naive triage skill (held-out 14/20), a
# held-out eval, a binary judge, and a skill-improver subagent. The `outer`/`pr`
# targets only PRINT the recording runbook — they never launch `claude`. The
# scoring targets (judge / apply-fix / seed-bad / fix-seed) run pure Python and
# need no ANTHROPIC_API_KEY, so every number in the lecture is reproducible.

.PHONY: setup judge inner outer pr apply-fix seed-bad fix-seed clean help

# Rebuild a clean sandbox/ with the seeded issue + relabel history.
setup:
	bash setup.sh

# Score the current triage skill against the held-out set (binary judge).
judge:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && python3 eval/run.py

# Screencast #1 — inner loop: the task in prod. Prints the runbook, then the score.
inner:
	@test -d sandbox || bash setup.sh >/dev/null
	@echo "SCREENCAST #1 — inner loop (the task in prod)"
	@echo "  live: claude, then /triage on issues/incoming/how-do-i-rotate-keys.md"
	@echo "  the naive skill answers 'bug' (it sees 'error'); gold is 'question'."
	@echo "  held-out already shows this whole failure class:"
	@echo ""
	@cd sandbox && python3 eval/run.py

# Screencast #2 — outer loop: the skill rewrites itself and opens a draft PR.
# PRINTS the runbook. It does NOT run claude. Use `make apply-fix` for the
# deterministic stand-in that produces the same 19/20 without tokens.
outer pr:
	@echo "SCREENCAST #2 — outer loop (skill-improver rewrites the skill)"
	@echo "  live, in sandbox/:"
	@echo "    claude -p --agent skill-improver 'run one improvement cycle'"
	@echo "  the subagent: reads held-out misses + git relabels ->"
	@echo "    appends one lesson to lessons.md ->"
	@echo "    appends one rule to .claude/skills/triage/SKILL.md ->"
	@echo "    re-runs eval (14/20 -> 19/20) -> gh pr create --draft"
	@echo ""
	@echo "  deterministic stand-in (no tokens): make apply-fix"
	@echo "  NOTHING merges without a human — the PR stays a draft."

# Deterministic stand-in for the outer loop: append the rule + lesson, re-score.
apply-fix:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && bash scripts/apply-fix.sh
	@echo ""
	@cd sandbox && python3 eval/run.py

# Wrong-goal lesson: poison the held-out gold (questions -> bug). The naive skill
# now scores a "perfect" 20/20 against the poisoned target — optimising the wrong
# thing. `make fix-seed` restores the honest gold.
seed-bad:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && python3 -c "import json,pathlib; p=pathlib.Path('eval/gold.json'); d=json.loads(p.read_text()); \
[d.__setitem__(k,'bug') for k in list(d) if k.startswith('how-') or k.startswith('is-it')]; \
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)); print('poisoned: questions -> bug in gold.json')"
	@echo ""
	@cd sandbox && python3 eval/run.py

# Restore the honest held-out gold from the canonical labels.
fix-seed:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && rm -f eval/gold.json && python3 eval/run.py

clean:
	rm -rf sandbox

help:
	@echo "targets:"
	@echo "  setup      build sandbox/ (naive skill, held-out eval, relabel history)"
	@echo "  judge      score current skill against held-out (14/20 naive)"
	@echo "  inner      Screencast #1 runbook + score"
	@echo "  outer/pr   Screencast #2 runbook (PRINTS ONLY, never runs claude)"
	@echo "  apply-fix  deterministic outer-loop stand-in: append rule -> 19/20"
	@echo "  seed-bad   poison held-out gold (wrong-goal lesson): naive -> 20/20"
	@echo "  fix-seed   restore honest gold"
	@echo "  clean      remove sandbox/"
