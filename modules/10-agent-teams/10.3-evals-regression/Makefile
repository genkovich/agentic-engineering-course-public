.PHONY: help lint eval-one evals demo demo-beerlms clean

help:
	@echo "Targets - evals для агентів цього проєкту (лекція 10.3):"
	@echo ""
	@echo "  lint      - статичний лінт конфігурації агентів (0 токенів, секунди)."
	@echo "  eval-one  - головний кейс (ro-reviewer) у Promptfoo. Коштує токени."
	@echo "              BREAK=1 make eval-one - зламаний агент -> FAIL."
	@echo "  evals     - сьют: решта 5 кейсів у Promptfoo. Коштує токени."
	@echo "  demo      - друкує сторіборд скринкастів лекції."
	@echo "  demo-beerlms - як навести ті самі evals на реальні агенти beer-lms (M6)."
	@echo "  clean     - прибрати tmp/ і workdir-* (пісочниці прогонів)."
	@echo ""
	@echo "Руками (шлях лекції, без інструментів):"
	@echo "  bash eval/check.sh      # перший тест: рев'ю є, код незайманий"
	@echo "  bash eval/judge.sh      # суддя: бал за рубрикою eval/rubric.md"
	@echo "  bash eval/sandbox.sh    # пісочниця: копія проєкту + свіжий git"

# Статичний лінт: без агента, без токенів. Ходить у CI на кожен PR.
lint:
	@python3 eval/lint.py

# Головний кейс лекції у Promptfoo (провайдер provider.py + llm-rubric).
eval-one:
	@cd promptfoo && npx promptfoo@latest eval --no-cache

# Сьют: 5 кейсів (claude-agent-sdk + власний провайдер).
evals:
	@cd promptfoo/suite && bash setup.sh && npx promptfoo@latest eval --no-cache

demo:
	@echo "СКРИНКАСТИ лекції 10.3. Повний сторіборд: screencast-prompts.md"
	@echo ""
	@echo "  1. cat .claude/agents/ro-reviewer.md      # агент, написаний з нуля"
	@echo "  2. bash eval/check.sh                     # перший тест руками -> PASS"
	@echo "  3. cp eval/broken/ro-reviewer.md .claude/agents/ && bash eval/check.sh  # FAIL"
	@echo "  4. git checkout .claude/agents/ro-reviewer.md && make lint             # лінт"
	@echo "  5. bash eval/judge.sh                     # суддя: JSON {score, reason}"
	@echo "  6. make eval-one && npx promptfoo@latest view   # той самий кейс у Promptfoo"
	@echo "  7. make evals                             # сьют: решта 5 кейсів"
	@echo ""
	@echo "Кадр-висновок: .claude/ - версіонована конфігурація агента; evals ловлять"
	@echo "її тихі регресії так само, як юніт-тести ловлять регресії коду."

demo-beerlms:
	@echo "Ті самі evals, наведені на реальні агенти beer-lms (~/sources/beer-lms, M6):"
	@echo ""
	@echo "── Ідея ────────────────────────────────────────────────────────────────────────"
	@echo "  beer-lms має власну .claude/ (agents, hooks, CLAUDE.md). Це конфігурація, яку"
	@echo "  так само треба захищати від регресій, як код."
	@echo ""
	@echo "── Кейс A · read-only рев'юер ──────────────────────────────────────────────────"
	@echo "  Якщо у beer-lms є review-агент: golden-задача 'зроби рев'ю', асерт"
	@echo "  git diff по src/ ПОРОЖНІЙ + llm-rubric на якість тексту (як головний кейс)."
	@echo ""
	@echo "── Кейс B · правило CLAUDE.md ──────────────────────────────────────────────────"
	@echo "  Задача, що спокушає порушити правило (напр. 'лише repository pattern');"
	@echo "  python-грейдер грепає diff на порушення."
	@echo ""
	@echo "── Кейс C · gate-green на go test ──────────────────────────────────────────────"
	@echo "  Стартова story з червоним тестом; грейдер: go test ./... exit 0."
	@echo ""
	@echo "── Чесна примітка ──────────────────────────────────────────────────────────────"
	@echo "  Прогони агента недетерміновані: кейси можуть 'мигати'. Асерт на OUTCOME,"
	@echo "  а 'make lint' (0 токенів) лишається завжди-зеленим CI-шаром."

clean:
	@rm -rf tmp promptfoo/suite/workdir-route promptfoo/suite/workdir-nplusone review.md
	@echo "Прибрано tmp/, workdir-* і review.md."
