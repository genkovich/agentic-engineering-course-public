.PHONY: help verify demo demo-weak clean

help:
	@echo "Targets:"
	@echo "  verify     - run the DoD check (pytest -q). RED on a clean checkout (tags.py is a NotImplementedError stub) - that's the start state."
	@echo "  demo       - print the /goal steps (good 3-part condition). Runs INSIDE 'claude', so not auto-run."
	@echo "  demo-weak  - print how to reproduce the evaluator blind spot with a weak prose condition."
	@echo "  clean      - remove caches (__pycache__, .pytest_cache)."

# DoD probe. On a fresh checkout src/snippets/tags.py is a NotImplementedError
# stub → tests/test_tags.py is RED. After a successful /goal run → green.
verify:
	uv run --with pytest pytest -q

# The good path: a 3-part completion condition driven by /goal.
# The slash command runs INSIDE 'claude' (not plain shell), so we print the steps.
demo:
	@echo "Drive SNIP-2 to done with a HEALTHY 3-part /goal condition:"
	@echo ""
	@echo "  make verify                          # RED: tests/test_tags.py fails (NotImplementedError) - start state"
	@echo "  claude"
	@echo "    # set the condition (measurable end-state + explicit check + constraint + soft bound):"
	@echo "    # /goal all tests in tests/test_tags.py pass, pytest exits 0, \\"
	@echo "    #       and git diff -- tests/ is empty, or stop after 12 turns"
	@echo "    #"
	@echo "    #   Claude makes the FIRST move immediately (the condition IS the task - no extra prompt)."
	@echo "    #   The '◎ /goal active' panel appears with live turn/token counters."
	@echo "    #   After each turn the evaluator (a separate fresh model) prints a short reason -"
	@echo "    #   it judges the TRANSCRIPT, so the printed 'pytest exits 0' is what closes the goal."
	@echo "    # /goal                              show full state (condition, turns, tokens, last reason)"
	@echo "    # /goal clear                        drop the goal by hand (synonyms: stop/off/reset/none/cancel)"
	@echo ""
	@echo "  make verify                          # GREEN after a successful run"
	@echo ""
	@echo "Full good-vs-weak breakdown: completion-condition.md."

# The blind spot: a weak PROSE condition the evaluator can close on text alone.
# Reproduces the core teaching point - the evaluator judges the transcript, not the world.
demo-weak:
	@echo "Reproduce the evaluator BLIND SPOT (it judges the transcript, not the world):"
	@echo ""
	@echo "  make verify                          # RED: stub still raises NotImplementedError"
	@echo "  claude"
	@echo "    # a WEAK prose condition with no measurable trace:"
	@echo "    # /goal the code is correct"
	@echo "    #"
	@echo "    #   Claude writes something like 'implementation looks correct' into the chat."
	@echo "    #   The evaluator reads that line - there is nothing to RUN - and may close the goal."
	@echo "    # /goal                              shows 'achieved' on prose alone"
	@echo ""
	@echo "  make verify                          # STILL RED - nobody checked reality; the goal closed on words"
	@echo ""
	@echo "Fix: use the 3-part condition from 'make demo'. The cure for the blind spot"
	@echo "is a machine check whose result lands in the transcript (pytest exits 0),"
	@echo "not a prettier prose condition. See completion-condition.md."

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
