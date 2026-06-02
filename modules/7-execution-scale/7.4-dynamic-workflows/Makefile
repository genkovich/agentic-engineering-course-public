.PHONY: help verify check-workflow demo clean

help:
	@echo "Targets:"
	@echo "  verify          - run the DoD check (pytest). RED on a clean checkout - search/dedupe/export are NotImplementedError stubs."
	@echo "  check-workflow  - node --check on both .claude/workflows/*.mjs to prove the orchestration scripts are valid JS."
	@echo "  demo            - print how to TRIGGER the workflow (the word «workflow» in the prompt). Non-deterministic, ~15x tokens, NOT auto-run."
	@echo "  clean           - remove caches (__pycache__, .pytest_cache)."

# DoD probe. On a clean checkout search.py/dedupe.py/export.py raise
# NotImplementedError → pytest is RED. Green only after all three stories ship.
verify:
	uv run --with pytest pytest -q

# Prove the orchestration scripts are syntactically valid JavaScript.
# This does NOT run them (they need the Claude Code runtime + agent()/parallel()/…),
# it only parses them - a deterministic gate you can run in CI.
check-workflow:
	node --check .claude/workflows/ship-snippets.mjs && node --check .claude/workflows/audit-independence.mjs
	@echo "OK: both .mjs parse as valid JS"

# We do NOT auto-run the workflow - the runtime is non-deterministic and spends
# ~15x the tokens of a normal chat. You TRIGGER it by putting the word «workflow»
# in your prompt inside 'claude', then watch the phases with /workflows.
demo:
	@echo "Trigger the dynamic workflow (the word «workflow» is the trigger):"
	@echo ""
	@echo "  claude"
	@echo "    # промпт зі словом-тригером (Claude сам напише скрипт оркестрації):"
	@echo "    # «workflow: реалізуй SNIP-3, SNIP-4, SNIP-5 паралельно з tracker.md,"
	@echo "    #   потім перевір кожну незалежними рецензентами (збіжність)»"
	@echo "    # → картка підтвердження: Yes, run it / View raw script / No"
	@echo "    # /workflows                  дивитись фази Implement / Verify, лічильники агентів"
	@echo ""
	@echo "  Готовий скрипт уже лежить у .claude/workflows/ship-snippets.mjs -"
	@echo "  можна показати його як приклад того, що Claude згенерував би сам."
	@echo "  Аудит незалежності до запуску: .claude/workflows/audit-independence.mjs"
	@echo ""
	@echo "  УВАГА: прогін недетермінований і палить ~15x токенів проти звичайного"
	@echo "  чату. Тому 'make demo' лише друкує кроки, а не запускає workflow."

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
