.PHONY: demo audit audit-markdown examples examples-bad clean help

SKILL_DIR := .claude/skills/audit-api-endpoint
SCRIPT    := $(SKILL_DIR)/scripts/audit_endpoint.py
URL       ?= http://localhost:3000/health

help:
	@echo "Targets:"
	@echo "  demo            - probe $(URL) and print JSON (override with URL=...)"
	@echo "  audit           - same as demo"
	@echo "  audit-markdown  - same probe, markdown output"
	@echo "  examples        - run good examples (good-cli-flags, good-structured)"
	@echo "  examples-bad    - run bad examples; bad-interactive will hang, that is the demo"
	@echo "  clean           - remove __pycache__"

demo: audit

audit:
	uv run $(SCRIPT) --url "$(URL)"

audit-markdown:
	uv run $(SCRIPT) --url "$(URL)" --format markdown

examples:
	@echo "--- good-cli-flags.py ---"
	python3 examples/good-cli-flags.py --target /tmp --endpoint /health --yes
	@echo
	@echo "--- good-structured.py (stdout is JSON, stderr is logs) ---"
	python3 examples/good-structured.py

examples-bad:
	@echo "--- bad-prose-output.py ---"
	python3 examples/bad-prose-output.py
	@echo
	@echo "bad-interactive.py is intentionally not invoked by Make:"
	@echo "  python3 examples/bad-interactive.py"
	@echo "  it hangs forever waiting for input - that is the lesson"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
