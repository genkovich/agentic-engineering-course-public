# Demo 10.4 — Agent Teams. Будує пісочницю: той самий монореп, що в 10.1
# (5 seed-комітів), плюс 6-й team-prep коміт — стабільний reports-тест,
# командний етикет у CLAUDE.md, env-флаг CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
# і хуки task-gate.sh / task-log.sh у .claude/. ANTHROPIC_API_KEY для бази не
# потрібен: живий прогін ведеться інтерактивно в Claude Code.

.PHONY: sandbox reset clean test gate-test

# Побудувати чисту пісочницю (seed-історія 10.1 + team-prep коміт).
sandbox:
	bash setup.sh

# Перебудувати чисто між дублями.
reset: clean sandbox

# Прибрати sandbox/.
clean:
	rm -rf sandbox

# Увесь сьют у пісочниці. На відміну від 10.1 тут ВСІ пакети зелені:
# flaky-тест reports замінено детермінованим, щоб TaskCompleted-гейт не мигав.
test:
	cd sandbox && node --test

# Ізольована перевірка обох гілок task-gate.sh, ДО будь-яких агентів:
#   гілка 1 — тести зелені            → очікуємо exit 0;
#   гілка 2 — підкинутий червоний тест → очікуємо exit 2 і stderr-фідбек.
# Червоний тест — тимчасовий untracked-файл, після перевірки прибирається.
gate-test:
	@test -d sandbox || { echo "спершу: make sandbox"; exit 1; }
	@echo "→ гілка 1: тести зелені, очікуємо exit 0"
	@cd sandbox && bash .claude/hooks/task-gate.sh && echo "   OK: гейт пропустив (exit 0)"
	@echo "→ гілка 2: ламаємо тест billing, очікуємо exit 2 + stderr-фідбек"
	@printf '%s\n' \
		'const test = require("node:test");' \
		'const assert = require("node:assert");' \
		'test("BREAK: навмисно червоний тест для gate-test", () => {' \
		'  assert.fail("зламано gate-test-ом");' \
		'});' > sandbox/packages/billing/__tests__/break.gate.test.js
	@rc=0; err="$$(cd sandbox && bash .claude/hooks/task-gate.sh 2>&1 >/dev/null)" || rc=$$?; \
	rm -f sandbox/packages/billing/__tests__/break.gate.test.js; \
	echo "   stderr: $$err"; \
	if [ "$$rc" -ne 2 ]; then echo "   FAIL: очікували exit 2, отримали rc=$$rc"; exit 1; fi; \
	echo "$$err" | grep -q "Тести червоні" || { echo "   FAIL: очікуваного stderr-фідбеку немає"; exit 1; }; \
	echo "   OK: гейт завернув (exit 2, stderr-фідбек на місці)"
