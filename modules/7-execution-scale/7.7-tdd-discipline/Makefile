.PHONY: help test test-fast coverage mutation demo clean

help:
	@echo "Targets:"
	@echo "  test          - run the DoD check (pytest -q). RED on a clean checkout (NotImplementedError) — that's the start state."
	@echo "  demo          - print the guided steps to run the synthetic /tdd story-24-sm2 cycle (inside 'claude')"
	@echo "  test-fast     - re-run pytest on file change (needs 'pip install -e \".[dev]\"')"
	@echo "  coverage      - coverage report"
	@echo "  mutation      - mutation testing via mutmut (sanity check; needs '[dev]')"
	@echo "  clean         - remove caches (.pytest_cache, .mutmut-cache, htmlcov, __pycache__)"

# DoD probe. On a fresh checkout src/sm2.py is a NotImplementedError stub → 11 failures (red).
# After a successful /tdd run → green.
test:
	pytest -q

# Re-run on file change. Requires `pip install -e ".[dev]"` (pytest-watch).
test-fast:
	ptw --runner "pytest -q --tb=short"

coverage:
	coverage run -m pytest -q
	coverage report -m
	coverage html

# Mutation testing. Requires `pip install -e ".[dev]"` (mutmut).
mutation:
	mutmut run || true
	mutmut results

# Synthetic RGR cycle on the SM-2 kata via the /tdd orchestrator.
# The slash command runs INSIDE 'claude' (not plain shell), so we print the steps.
demo:
	@echo "Run the full Red-Green-Refactor cycle on the SM-2 kata with ONE command:"
	@echo ""
	@echo "  git status                          # clean tree; tests/ written but red"
	@echo "  pytest -q                           # 11 failing (8 example + 3 PBT) — NotImplementedError"
	@echo "  bat tasks/story-24-sm2.md           # show the AC (8 cases + 3 PBT invariants)"
	@echo "  claude"
	@echo "    # /tdd story-24-sm2               orchestrator: RED → GREEN → REFACTOR via 3 isolated agents"
	@echo "    # /tdd story-24-sm2 --review-tests   augmented-coding variant: STOP after Gate 1 for human review"
	@echo ""
	@echo "  git log --oneline -3                # test(sm2): → feat(sm2): → refactor(sm2):"
	@echo "  pytest -q                           # all green"
	@echo "  git diff HEAD~3 HEAD -- tests/      # tests untouched after the RED phase"

clean:
	rm -rf .pytest_cache .mutmut-cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
