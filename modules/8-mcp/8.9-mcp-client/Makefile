# Demo 8.9: власний MCP-клієнт.
#
#   make install        встановити залежності
#   make run-01         мінімальний клієнт (SERVER=... щоб підключитись до свого сервера)
#   make run-resources  resources/prompts проти task-store з 8.6 (без ключа)
#   make run-02         tool-use loop з Claude API (потрібен ANTHROPIC_API_KEY)
#   make run-utilities  ping, таймаут і pagination проти фікстур (без ключа)
#   make run-03         loop поверх `claude mcp serve` (потрібен Claude Code CLI)
#   make test           vitest, без API-ключа і зовнішніх процесів
#   make clean          прибрати node_modules і артефакти

# Команда MCP-сервера для run-01. За замовчуванням fixture echo-server.
SERVER ?= npx tsx test/fixtures/echo-server.ts

# Запит для run-02/run-03 (можна перевизначити: make run-02 PROMPT="...").
PROMPT ?=

.PHONY: install run-01 run-resources run-02 run-utilities run-03 test build clean

install:
	npm install

run-01:
	npx tsx src/01-list-and-call.ts $(SERVER)

run-resources:
	npx tsx src/resources.ts

run-02:
	npx tsx src/02-claude-loop.ts $(PROMPT)

run-utilities:
	npx tsx src/utilities.ts

run-03:
	npx tsx src/03-claude-serve.ts $(PROMPT)

test:
	npm test

build:
	npm run build

clean:
	rm -rf node_modules dist
