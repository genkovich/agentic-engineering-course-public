.PHONY: sdlc-check sdlc-metrics sdlc-docs-gen

sdlc-check:
	python3 scripts/sdlc_lint.py --root .

sdlc-metrics:
	python3 scripts/sdlc_lint.py --root . --metrics

sdlc-docs-gen:
	bash scripts/generate-gates.sh --inject CLAUDE.md
	@echo "Run 'git diff CLAUDE.md' to review the regenerated GATE table."
