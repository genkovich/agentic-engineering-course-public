.PHONY: help test test-fast coverage mutation demo demo-beerlms clean

help:
	@echo "Targets:"
	@echo "  test          - run the DoD check (pytest -q). RED on a clean checkout (NotImplementedError) — that's the start state."
	@echo "  demo          - print the guided steps to run the synthetic /tdd story-24-sm2 cycle (inside 'claude')"
	@echo "  demo-beerlms  - print the worktree-isolated steps for the real TDD track on beer-lms M6 (story L-2, go test)"
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
	@echo ""
	@echo "Full storyboard: screencast-prompts.md (Screencast #1)."

# The 'even better' track: same RGR pattern, real Module 6 backlog (beer-lms, Go).
# We do NOT auto-run it (it would write Go code into beer-lms) — print the
# worktree-isolated steps instead. See README → 'beer-lms track'.
demo-beerlms:
	@echo "Point the SAME RGR pattern at the real M6 backlog, isolated in a git worktree:"
	@echo ""
	@echo "  BEERLMS=~/sources/beer-lms"
	@echo "  git -C \$$BEERLMS worktree add ../beer-lms-tdd -b tdd/l2"
	@echo "  cd \$$BEERLMS/../beer-lms-tdd"
	@echo "  # baseline:  cd beer-lms-api && go test ./..."
	@echo "  # inside 'claude':  /ralph-prep L-2   (story docs/features/course-lesson-mvp/tasks/L-2-postgres-lesson-repo.md)"
	@echo "  #                   or /tdd on a Go adaptation"
	@echo "  # DoD: cd beer-lms-api && go test ./...   (green — NOT pytest)"
	@echo ""
	@echo "When done: git -C \$$BEERLMS worktree remove ../beer-lms-tdd"
	@echo ""
	@echo "Note: /tdd here is tuned for pytest/Python. On Go the pattern is the same"
	@echo "(red-green-refactor + tests/ as an immutable contract), but the test run is"
	@echo "'go test ./...' — swap the gate command and test-writer accordingly."

clean:
	rm -rf .pytest_cache .mutmut-cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
