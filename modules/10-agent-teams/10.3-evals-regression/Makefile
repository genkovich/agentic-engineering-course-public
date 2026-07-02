.PHONY: help check evals evals-one demo demo-beerlms clean

help:
	@echo "Targets — golden-task eval suite для .claude/ (лекція 10.3):"
	@echo ""
	@echo "  check         - ДЕТЕРМІНОВАНИЙ драй-ран БЕЗ ТОКЕНІВ (bash -n + структура кейсів)."
	@echo "                  Має бути зелено на чистому checkout — це CI/pre-commit-шар."
	@echo "  evals         - реальний claude -p на ВСІХ кейсах (коштує токени, як 7.2)."
	@echo "  evals-one CASE=route-auth   - один кейс."
	@echo "  demo          - друкує сторіборд скринкасту (зламай .claude/ -> eval червоніє)."
	@echo "  demo-beerlms  - друкує, як навести той самий suite на реальні агенти beer-lms (M6)."
	@echo "  clean         - прибрати tmp/ (пісочниці прогонів)."
	@echo ""
	@echo "Money-shot (доказ тези): зламати guardrail -> eval має почервоніти, повернути -> зелено:"
	@echo "  make evals-one CASE=forbid-env-read            # PASS (guardrail на місці)"
	@echo "  make evals-one CASE=forbid-env-read BREAK=1    # FAIL (guardrail прибрано)"

# Детермінований шар: без агента, без токенів. Цей таргет ходить у CI/pre-commit.
check:
	@bash tests/agent/lint.sh

# Реальний прогін: піднімає пісочниці, ганяє claude -p, детермінований чекер.
evals:
	@bash tests/agent/run.sh

# Один кейс. Передай BREAK=1, щоб setup навмисно прибрав guardrail (демо регресії).
evals-one:
	@if [ -z "$(CASE)" ]; then echo "Вкажи CASE=, напр.: make evals-one CASE=route-auth"; exit 2; fi
	@BREAK=$(BREAK) bash tests/agent/run.sh $(CASE)

demo:
	@echo "СКРИНКАСТИ #1-#5 (герой ro-reviewer). Повний сторіборд: screencast-prompts.md"
	@echo ""
	@echo "  1. ls tests/agent/cases/subagent-tools-allowlist/       # анатомія кейса героя (#1)"
	@echo "  2. make check                                           # безтокенний шар зелений (#1)"
	@echo "  3. make evals-one CASE=subagent-tools-allowlist         # герой read-only -> PASS (#2)"
	@echo "  4. make evals-one CASE=subagent-tools-allowlist BREAK=1 # зламали агента -> FAIL (#2)"
	@echo "  5. make evals-one CASE=subagent-tools-allowlist         # конфіг повернули -> PASS (#2)"
	@echo "  6. make evals-one CASE=forbid-env-read BREAK=1          # другий red-green: guardrail (#3)"
	@echo "  7. make evals-one CASE=route-auth                       # асерт на outcome: 401/200 (#4)"
	@echo ""
	@echo "Кадр-висновок: .claude/ — це версіонована конфігурація агента; golden-task suite"
	@echo "ловить її тихі регресії так само, як юніт-тести ловлять регресії коду."

demo-beerlms:
	@echo "Той самий suite, наведений на реальні агенти beer-lms (~/sources/beer-lms, M6):"
	@echo ""
	@echo "BEERLMS=~/sources/beer-lms"
	@echo ""
	@echo "── Ідея ────────────────────────────────────────────────────────────────────────"
	@echo "  beer-lms має власну .claude/ (agents, hooks, CLAUDE.md). Це конфігурація, яку"
	@echo "  так само треба регресити, як код. Кейси нижче — портовні шаблони."
	@echo ""
	@echo "── Кейс A · subagent-tools-allowlist на реальному ревʼюері ─────────────────────"
	@echo "  Якщо у beer-lms є read-only review-агент — golden-task: дай йому diff, асерт"
	@echo "  git diff --stat по src/ ПОРОЖНІЙ (рев'ю згенеровано, файли не змінені)."
	@echo "  Регресія: хтось додав Write у tools агента -> кейс червоніє."
	@echo ""
	@echo "── Кейс B · respects-claude-md-rule на реальному CLAUDE.md ────────────────────"
	@echo "  Правило beer-lms (напр. 'лише repository pattern' / 'структуровані slog-логи')."
	@echo "  Golden-task: задача, що спокушає порушити правило; check.sh грепає diff."
	@echo "  Доводить, що CLAUDE.md реально кермує агентом."
	@echo ""
	@echo "── Кейс C · gate-green на реальному go test ───────────────────────────────────"
	@echo "  cd \$$BEERLMS/beer-lms-api"
	@echo "  Стартова story з червоним тестом; check.sh: go test ./... exit 0 після прогону."
	@echo ""
	@echo "── Чесна примітка ──────────────────────────────────────────────────────────────"
	@echo "  agent-runs недетерміновані: деякі кейси можуть 'мигати'. Тому асерт на OUTCOME,"
	@echo "  а 'make check' (без токенів) лишається завжди-зеленим CI-шаром."

clean:
	@rm -rf tmp
	@echo "Прибрано tmp/ (пісочниці прогонів)."
