.PHONY: help test-hooks recipes-tour pre-commit-demo analytics tail-trace tail-subagent tail-transcript strip-demo hooks-list clean-logs

LOG_DIR := .claude/logs

help:
	@echo "Hooks toolkit — demo для лекції 5.4"
	@echo ""
	@echo "Quickstart (4 рецепти за 30 секунд):"
	@echo "  make recipes-tour     — end-to-end прогін 4 рецептів з headers Recipe N/4 (slide 6)"
	@echo "  make test-hooks       — isolation tests: 8 fixtures × 5 hooks → PASS/FAIL matrix (slide 5.5)"
	@echo "  make pre-commit-demo  — quick-start інструкції для examples/pre-commit-demo/ (slide 7)"
	@echo ""
	@echo "Live observability:"
	@echo "  make analytics       — запустити mock receiver на :8090 (CTRL-C щоб зупинити)"
	@echo "  make tail-trace      — live tail .claude/logs/tool-trace.jsonl"
	@echo "  make tail-subagent   — live tail .claude/logs/subagent.jsonl"
	@echo "  make tail-transcript — live tail .claude/logs/transcript.jsonl"
	@echo "  make strip-demo      — прогнати examples/secrets-strip-demo/input-dirty.json через secrets-strip.py"
	@echo "  make hooks-list      — claude /hooks (показати усі сконфігуровані)"
	@echo "  make clean-logs      — стерти .claude/logs/*.jsonl"
	@echo ""
	@echo "Підготовка: cp .claude/settings.local.json.example .claude/settings.local.json"
	@echo "            (потім впиши свої ANALYTICS_URL / TELEGRAM_*)"

test-hooks:
	bash examples/test-isolation/run-isolation-tests.sh

recipes-tour:
	bash examples/recipes-tour/run-tour.sh

pre-commit-demo:
	@echo "Pre-commit demo — копі-паст рецепт для Slide 7 + Slide 12 Variant D"
	@echo ""
	@echo "Setup (одноразово):"
	@echo "  cd examples/pre-commit-demo"
	@echo "  npm install        # ставить husky+lint-staged+tsc+vitest, активує hook"
	@echo "  git init && git add -A"
	@echo ""
	@echo "Happy path (pre-commit pass):"
	@echo "  git commit -m \"happy\""
	@echo "  # → 5/5 tests pass → коміт зелений"
	@echo ""
	@echo "Fail path (pre-commit блокує коміт):"
	@echo "  mv src/notes.ts src/notes-original.ts"
	@echo "  mv src/notes-broken.example.ts src/notes.ts"
	@echo "  git add -A && git commit -m \"broken\""
	@echo "  # → npm test fails → коміт ЗАБЛОКОВАНИЙ"
	@echo ""
	@echo "Перенос у власний SaaS-репо:"
	@echo "  cp -r examples/pre-commit-demo/{.husky,lint-staged.config.json,tsconfig.json} <your-repo>/"
	@echo "  + інтегруй scripts.prepare/test/tsc у свій package.json"
	@echo ""
	@echo "Деталі: examples/pre-commit-demo/README.md"

analytics:
	python3 examples/analytics-server/server.py

tail-trace:
	bash examples/debug-viewer/tail-trace.sh

tail-subagent:
	bash examples/debug-viewer/tail-subagent.sh

tail-transcript:
	bash examples/debug-viewer/tail-transcript.sh

strip-demo:
	@echo "--- INPUT (examples/secrets-strip-demo/input-dirty.json) ---"
	@cat examples/secrets-strip-demo/input-dirty.json
	@echo ""
	@echo "--- OUTPUT (через .claude/hooks/secrets-strip.py) ---"
	@cat examples/secrets-strip-demo/input-dirty.json | python3 .claude/hooks/secrets-strip.py

hooks-list:
	@command -v claude >/dev/null 2>&1 || { echo "claude CLI не знайдено в PATH"; exit 1; }
	claude /hooks

clean-logs:
	rm -f $(LOG_DIR)/*.jsonl
	@echo "logs cleared: $(LOG_DIR)"
