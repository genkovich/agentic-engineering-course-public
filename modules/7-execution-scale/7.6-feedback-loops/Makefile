.PHONY: help dev verify gate install-hooks clean

help:
	@echo "Targets:"
	@echo "  dev           - запустити dev-сервер (npm run dev) на :5173"
	@echo "  verify        - юніт-тести (vitest). story-28 ЧЕРВОНИЙ на старті (test-first, премиса скринкасту #1)."
	@echo "  gate          - детермінований гейт: npx tsc --noEmit && npm test (як pre-commit/Stop-hook)"
	@echo "  install-hooks - вказати git на scripts/pre-commit через core.hooksPath (увага: впливає на монорепо)"
	@echo "  clean         - прибрати tmp/ та артефакти прогонів"
	@echo ""
	@echo "СКРИНКАСТ #1 (детермінований гейт) — story-28 ships RED (test-first):"
	@echo "  1. make gate                      # ЧЕРВОНО: queue-sort.test.ts падає (sortQueue — стаб)"
	@echo "  2. у 'claude':  /verify-gate story-28  # реалізує sortQueue, не каже DONE поки гейт червоний"
	@echo "  3. make gate                      # ЗЕЛЕНО -> коміт із виводом тесту як доказом"
	@echo "     (Stop-hook .claude/hooks/verify.sh — той самий гейт на завершенні ходу; опт-ін)"
	@echo ""
	@echo "СКРИНКАСТ #2 (готовий) — розробка через Playwright (CLI-first):"
	@echo "  1. make dev                       # підняти :5173 в окремому терміналі"
	@echo "  2. playwright-cli install --skills # одноразово: дати агенту навички CLI"
	@echo "  3. у 'claude':  /verify-ui story-26  # відкрив->прочитав getComputedStyle->8px->фікс px-3->12px"
	@echo ""
	@echo "Опційні референси (в репо, поза скринкастами):"
	@echo "  /verify-ui story-25               - off-by-one у черзі (браузер ловить, юніт ні)"
	@echo "  /screenshot-diff story-26         - піксельний diff проти baseline (старий канал)"
	@echo "  /code-review story-27             - localStorage-регресія (рев'юер: REJECT -> ACCEPT)"

# Dev-сервер для браузерного каналу. Скринкаст #2 жене playwright-cli (CLI-first);
# Playwright MCP лишається в .mcp.json для живого дебагу, Figma Dev Mode MCP — для design-input.
dev:
	npm run dev

# DoD-проба. story-28 (queue-sort.test.ts) ЧЕРВОНИЙ на старті — test-first премиса скринкасту #1.
# story-25 queue.test.ts ЗЕЛЕНИЙ навмисно попри off-by-one (юніт-канал сліпий до такого — урок 7.6).
verify:
	npm test

# Детермінований гейт: той самий набір, що його ганяють pre-commit і Stop-hook.
# Ненульовий код = червоно (коміт/хід заблокувався б).
gate:
	npx tsc --noEmit && npm test

# Вказати git на committed-хук scripts/pre-commit. УВАГА: демо — піддиректорія монорепо,
# core.hooksPath глобальний для репо. Для самодостатнього демо краще `make gate` вручну.
install-hooks:
	git config core.hooksPath "$(CURDIR)/scripts" && echo "core.hooksPath -> $(CURDIR)/scripts (pre-commit активний)"

clean:
	rm -rf tmp
	@echo "Прибрано tmp/. node_modules і baselines/ лишаються."
