# task-store MCP server demo (лекція 8.6)
# Стандартний API: make run / make clean (+ build, test, inspect, inspect-buggy, run-http)

.PHONY: install run run-http build test inspect inspect-buggy clean

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

clean:
	rm -rf node_modules dist data
