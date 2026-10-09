.PHONY: demo audit audit-markdown examples examples-bad clean help

SKILL_DIR := .claude/skills/audit-pytest-file
SCRIPT    := $(SKILL_DIR)/scripts/audit_pytest.py
FILE      ?= examples/good-fast-passing.py

# Default to a self-contained pytest invocation: uv pulls pytest +
# pytest-reportlog (the latter provides --report-log, which the script needs)
# into a one-shot venv. Override PYTEST=... to point at a project-installed
# pytest instead, e.g. PYTEST=pytest or PYTEST="poetry run pytest".
PYTEST    ?= uv run --with pytest --with pytest-reportlog pytest

help:
	@echo "Targets:"
	@echo "  demo            - probe \$$(FILE) and print JSON (override with FILE=...)"
	@echo "  audit           - same as demo"
	@echo "  audit-markdown  - same probe, markdown output"
	@echo "  examples        - run probe against good examples (low-finding outputs)"
	@echo "  examples-bad    - run probe against bad examples (each one breaks one thing)"
	@echo "  clean           - remove __pycache__ and .pytest_cache"
	@echo
	@echo "Override the pytest runner with PYTEST=..., default is:"
	@echo "  $(PYTEST)"

demo: audit

audit:
	uv run $(SCRIPT) --file "$(FILE)" --pytest "$(PYTEST)"

audit-markdown:
	uv run $(SCRIPT) --file "$(FILE)" --pytest "$(PYTEST)" --format markdown

examples:
	@for f in examples/good-*.py; do \
		echo "--- $$f ---"; \
		uv run $(SCRIPT) --file "$$f" --pytest "$(PYTEST)" || true; \
		echo; \
	done

examples-bad:
	@for f in examples/bad-*.py; do \
		echo "--- $$f ---"; \
		uv run $(SCRIPT) --file "$$f" --pytest "$(PYTEST)" --full || true; \
		echo; \
	done

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -exec rm -rf {} +
