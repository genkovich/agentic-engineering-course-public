.PHONY: demo validate validate-help analyze-help validate-bad clean help

SKILL_DIR := .claude/skills/pdf-form-filler
ANALYZE   := $(SKILL_DIR)/scripts/analyze.py
VALIDATE  := $(SKILL_DIR)/scripts/validate.sh

help:
	@echo "Targets:"
	@echo "  demo            - run validation against the good fixture (exits 0)"
	@echo "  validate        - same as demo"
	@echo "  validate-bad    - run validation against the bad fixture (exits 2 with JSON errors)"
	@echo "  validate-help   - show validate.sh --help"
	@echo "  analyze-help    - show analyze.py --help (resolves PEP 723 deps via uv)"
	@echo "  clean           - remove __pycache__"

demo: validate

validate:
	@echo "--- valid mapping (should exit 0) ---"
	bash $(VALIDATE) examples/form_fields.json examples/field_values.json

validate-bad:
	@echo "--- invalid mapping (should exit 2 with JSON errors) ---"
	bash $(VALIDATE) examples/form_fields.json examples/field_values_bad.json || true

validate-help:
	bash $(VALIDATE) --help

analyze-help:
	uv run $(ANALYZE) --help

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
