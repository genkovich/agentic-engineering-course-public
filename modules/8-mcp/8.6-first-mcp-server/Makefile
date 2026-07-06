# task-store MCP server demo (лекція 8.6)
# Стандартний API: make run / make clean (+ build, test, inspect, inspect-buggy, run-http)
# Python-дзеркало (python/): make py-install / py-run / py-test

.PHONY: install run run-http seed build test inspect inspect-buggy \
	run-advanced inspect-advanced clean py-install py-run py-test

node_modules: package.json
	npm install

install: node_modules

build: node_modules
	npm run build

run: build
	node dist/server.js

# Лекція 8.8: той самий сервер через Streamable HTTP на :3335 (src/server-http.ts).
# Register-секції без змін - інший лише транспортний wiring.
run-http: build
	node dist/server-http.js

# Лекція 8.12: кладе 2-3 демо-задачі у data/tasks.json через store, щоб у
# задеплоєного task-store одразу було що показати через list_tasks і /healthz.
seed: build
	node dist/seed.js

test: node_modules
	npm test

# Смок-тест через MCP Inspector у CLI-режимі: список tools без UI.
inspect: build
	npx @modelcontextprotocol/inspector --cli node dist/server.js --method tools/list

# Для лекції 8.7: викликаємо complete_task з фейковим id на зламаному сервері.
# Очікувана ПРАВИЛЬНА поведінка: isError + пояснення.
# Фактична: success: true. Це і є баг, який шукаємо Inspector-ом.
inspect-buggy: build
	npx @modelcontextprotocol/inspector --cli node dist/server.buggy.js \
		--method tools/call --tool-name complete_task --tool-arg id=task-999

# Лекція 8.10: розширений сервер - 7 tools поверх task-store (src/server-advanced.ts).
# Чотири advanced-tools демонструють client features: sampling, roots, elicitation,
# progress/logging. Це клієнтські можливості, тож сервер їх лише викликає.
run-advanced: build
	node dist/server-advanced.js

# UI-режим Inspector: показати sampling/elicit/roots/progress наживо.
# CLI на цьому сервері вміє лише tools/list - відповісти на sampling/elicit
# (вкладка Sampling, форма Elicitation, конфіг Roots) можна тільки у UI.
inspect-advanced: build
	npx @modelcontextprotocol/inspector node dist/server-advanced.js

# ─── Python-дзеркало (python/, лекція 8.6 секція 9) ───
# Той самий task-store на офіційному Python SDK (FastMCP). Той самий домен,
# той самий файл data/tasks.json - клієнт не бачить різниці мов.

# Залежності у власне віртуальне оточення (mcp + pytest).
py-install:
	cd python && uv sync

# Запуск Python-сервера на stdio (чекає JSON-RPC на stdin, Ctrl+C щоб вийти).
py-run:
	cd python && uv run server.py

# pytest: ті самі 17 тестів за духом (store + MCP-шар через in-memory клієнт).
py-test:
	cd python && uv run pytest

clean:
	rm -rf node_modules dist data
