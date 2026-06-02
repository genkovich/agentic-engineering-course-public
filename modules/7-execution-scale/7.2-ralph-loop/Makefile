.PHONY: help verify demo ralph prep demo-plugin clean

help:
	@echo "Targets:"
	@echo "  verify        - run the DoD check (pytest). RED on a clean checkout — that's the start state."
	@echo "  demo          - run the canonical Ralph loop on the abstract task (calls 'claude -p', costs tokens)"
	@echo "  ralph         - alias for demo (./ralph.sh)"
	@echo "  prep          - reminder how to (re)generate PROMPT.md from a story via /ralph-prep"
	@echo "  demo-plugin   - print the guided steps for the native /ralph-loop (ralph-wiggum plugin)"
	@echo "  clean         - remove run artifacts (app/, DONE, cost.log, __pycache__)"

# DoD probe. On a fresh checkout app/ is absent → ModuleNotFoundError (red).
# After a successful Ralph run → green.
verify:
	uv run --with pytest pytest -q

# Real claude-driven loop. Non-deterministic, spends tokens (~$1-5 per run).
# Watch ~3 cold-start iterations: import error → green → commit + touch DONE.
demo ralph:
	./ralph.sh

prep:
	@echo "Generate the thin PROMPT.md from the story (inside 'claude'):"
	@echo "    /ralph-prep story-t1"
	@echo "A ready-made PROMPT.md is already committed, so 'make demo' works out of the box."

# The same Ralph pattern, but native — the official ralph-wiggum plugin.
# Slash commands run INSIDE 'claude' (not plain shell), so we print the steps.
demo-plugin:
	@echo "Run the native Ralph 'in the box' — the official ralph-wiggum plugin (warm Stop-hook):"
	@echo ""
	@echo "  make clean                          # reset baseline (app/, DONE, cost.log)"
	@echo "  claude"
	@echo "    # /plugin                          install the ralph-wiggum plugin (Anthropic Verified)"
	@echo "    # /ralph-loop \"Make pytest -q green per tasks/story-t1.md\" \\"
	@echo "    #     --max-iterations 5 --completion-promise \"ALL TESTS PASSING\""
	@echo "    # Stop-hook re-feeds the prompt into the SAME session (warm context),"
	@echo "    # unlike ralph.sh which cold-starts a new 'claude -p' each turn."
	@echo "    # /cancel-ralph                     abort early if needed"
	@echo ""
	@echo "  --completion-promise is exact-string match (one condition, not many)."
	@echo "  --max-iterations is the primary safeguard (no default limit — always set it)."

clean:
	rm -rf app DONE cost.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
