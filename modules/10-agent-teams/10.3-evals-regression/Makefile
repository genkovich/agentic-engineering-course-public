.PHONY: help check evals evals-one demo demo-beerlms clean

help:
	@echo "Targets - golden-task eval suite для .claude/ (лекція 10.3):"
	@echo ""
	@echo "  check         - ШАР 0: статичний лінт конфігурації БЕЗ ТОКЕНІВ (lint.py)."
	@echo "                  Frontmatter агентів проти контракту + структура кейсів."
	@echo "                  Має бути зелено на чистому checkout - це CI/pre-commit-шар."
	@echo "  evals         - реальний claude -p на ВСІХ кейсах (коштує токени, як 7.2)."
	@echo "  evals-one CASE=route-auth   - один кейс."
	@echo "  demo          - друкує сторіборд скринкастів лекції."
	@echo "  demo-beerlms  - друкує, як навести той самий suite на реальні агенти beer-lms (M6)."
	@echo "  clean         - прибрати tmp/ (пісочниці прогонів)."
	@echo ""
	@echo "Red-green цикл (доказ тези): зламати конфіг -> eval червоніє, повернути -> зелено:"
	@echo "  make evals-one CASE=subagent-tools-allowlist            # PASS (allowlist на місці)"
	@echo "  make evals-one CASE=subagent-tools-allowlist BREAK=1    # FAIL (staged broken-конфіг)"

# Шар 0: статичний лінт конфігурації. Без агента, без токенів. Ходить у CI на кожен PR.
check:
	@python3 tests/agent/lint.py

# Реальний прогін: пісочниці, claude -p, детерміновані грейдери.
evals:
	@python3 tests/agent/run.py

# Один кейс. Передай BREAK=1, щоб stage-крок підклав broken-конфіг (демо регресії).
evals-one:
	@if [ -z "$(CASE)" ]; then echo "Вкажи CASE=, напр.: make evals-one CASE=route-auth"; exit 2; fi
	@BREAK=$(BREAK) python3 tests/agent/run.py $(CASE)

demo:
	@echo "СКРИНКАСТИ лекції 10.3. Повний сторіборд: screencast-prompts.md"
	@echo ""
	@echo "  1. ls tests/agent/cases/subagent-tools-allowlist/       # анатомія кейса"
	@echo "  2. make check                                           # шар 0: статичний лінт, 0 токенів"
	@echo "  3. make evals-one CASE=subagent-tools-allowlist         # read-only агент -> PASS"
	@echo "  4. make evals-one CASE=subagent-tools-allowlist BREAK=1 # зламаний конфіг -> FAIL"
	@echo "  5. make evals-one CASE=subagent-tools-allowlist         # конфіг повернули -> PASS"
	@echo "  6. make evals                                           # весь сьют + підсумкова матриця"
	@echo "  7. cd promptfoo && bash setup.sh && npx promptfoo@latest eval && npx promptfoo@latest view"
	@echo ""
	@echo "Кадр-висновок: .claude/ - це версіонована конфігурація агента; golden-task suite"
	@echo "ловить її тихі регресії так само, як юніт-тести ловлять регресії коду."

demo-beerlms:
	@echo "Той самий suite, наведений на реальні агенти beer-lms (~/sources/beer-lms, M6):"
	@echo ""
	@echo "BEERLMS=~/sources/beer-lms"
	@echo ""
	@echo "── Ідея ────────────────────────────────────────────────────────────────────────"
	@echo "  beer-lms має власну .claude/ (agents, hooks, CLAUDE.md). Це конфігурація, яку"
	@echo "  так само треба захищати від регресій, як код. Кейси нижче - портовні шаблони."
	@echo ""
	@echo "── Кейс A · subagent-tools-allowlist на реальному рев'юері ─────────────────────"
	@echo "  Якщо у beer-lms є read-only review-агент - golden-task: дай йому diff, асерт"
	@echo "  git diff --stat по src/ ПОРОЖНІЙ (рев'ю згенеровано, файли не змінені)."
	@echo "  Регресія: хтось додав Write у tools агента -> кейс червоніє."
	@echo ""
	@echo "── Кейс B · respects-claude-md-rule на реальному CLAUDE.md ────────────────────"
	@echo "  Правило beer-lms (напр. 'лише repository pattern' / 'структуровані slog-логи')."
	@echo "  Golden-task: задача, що спокушає порушити правило; check.py грепає diff."
	@echo "  Доводить, що CLAUDE.md направду кермує агентом."
	@echo ""
	@echo "── Кейс C · gate-green на реальному go test ───────────────────────────────────"
	@echo "  cd \$$BEERLMS/beer-lms-api"
	@echo "  Стартова story з червоним тестом; check.py: go test ./... exit 0 після прогону."
	@echo ""
	@echo "── Чесна примітка ──────────────────────────────────────────────────────────────"
	@echo "  agent-runs недетерміновані: деякі кейси можуть 'мигати'. Тому асерт на OUTCOME,"
	@echo "  а 'make check' (без токенів) лишається завжди-зеленим CI-шаром."

clean:
	@rm -rf tmp
	@echo "Прибрано tmp/ (пісочниці прогонів)."
