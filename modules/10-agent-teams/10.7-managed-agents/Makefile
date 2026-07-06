# Demo 10.7 — Managed Agents (лекція «Managed Agents: агентний harness як API»).
# Один hosted code-reviewer ревʼює review-target/ (course-репо з посіяним багом)
# через чотири сценарії: run / interrupt / outcome / multiagent.
#
# ⚠️ Кожен live-скрипт б'є в hosted Managed Agents API і КОШТУЄ токенів.
# demo-* цілі лише ДРУКУЮТЬ runbook - вони НІКОЛИ не запускають скрипти самі.
# Для запису без витрат і без недетермінізму дивись fallback/*.txt.

.PHONY: install setup run interrupt outcome multiagent parse fallback clean help \
        demo-1 demo-2 demo-3 demo-4

install:
	pip install -r requirements.txt

# Крок 0 (платний, один раз): створити агента + оточення, записати .env.
setup:
	python setup.py

run:
	python run.py

interrupt:
	python interrupt.py

outcome:
	python outcome.py

multiagent:
	python multiagent.py

# Гейт без грошей: перевірити, що всі скрипти парсяться.
parse:
	python -m py_compile common.py setup.py run.py interrupt.py outcome.py multiagent.py
	@echo "✅ усі скрипти парсяться"

# Детермінований фолбек під кожен скринкаст (нічого не витрачає).
fallback:
	@for f in run interrupt outcome multiagent; do \
	  echo "===== fallback/$$f.txt ====="; cat fallback/$$f.txt; echo; \
	done

clean:
	rm -rf __pycache__ review-target/node_modules

help:
	@echo "make install    - pip install anthropic"
	@echo "make setup      - створити агента+оточення, записати .env (ПЛАТНО, раз)"
	@echo "make run        - скринкаст #1: рев'ю course-репо (ПЛАТНО)"
	@echo "make interrupt  - скринкаст #2: перебити+перенаправити (ПЛАТНО)"
	@echo "make outcome    - скринкаст #3: define-outcome + grader (ПЛАТНО)"
	@echo "make multiagent - скринкаст #4: координатор+треди (ПЛАТНО)"
	@echo "make parse      - гейт: всі скрипти парсяться (безкоштовно)"
	@echo "make fallback   - надрукувати фолбек-транскрипти (безкоштовно)"
	@echo "make demo-N     - runbook скринкаста N (лише друк, без запуску)"

demo-1:
	@echo "🎬 #1 hosted code-reviewer ревʼює course-репо"
	@echo "Pre-state: cat review-target/src/invoice.js; make setup (раз); .env з AGENT_ID/ENV_ID"
	@echo "Запуск: python run.py"
	@echo "Дивимось: стрім [Using tool: read/bash], знахідка 58.42 vs 58.43;"
	@echo "паралельно - session-viewer на platform.claude.com."
	@echo "Фолбек: fallback/run.txt"

demo-2:
	@echo "🎬 #2 перебити рев'ю посеред і перенаправити"
	@echo "Pre-state: .env готовий; python interrupt.py"
	@echo "Дивимось: user.interrupt зупиняє хід, новий user.message звужує до discount.js."
	@echo "Фолбек: fallback/interrupt.txt"

demo-3:
	@echo "🎬 #3 define-outcome: рубрика «спіймати баг» -> grader ітерує (КЛІМАКС #1)"
	@echo "Pre-state: cat rubric.md; python outcome.py"
	@echo "Дивимось: grader FAIL на ітерації 1, PASS на ітерації 2 (баг названо)."
	@echo "Фолбек: fallback/outcome.txt"

demo-4:
	@echo "🎬 #4 координатор розкидає рев'ю на треди bug/test/docs (КЛІМАКС #2)"
	@echo "Pre-state: python multiagent.py"
	@echo "Дивимось: три session threads, зведений звіт координатора."
	@echo "Фолбек: fallback/multiagent.txt"
