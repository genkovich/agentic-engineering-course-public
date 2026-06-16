.PHONY: install run test events

# Поставити залежності (один раз)
install:
	bun install

# Підняти канал standalone, без сесії Claude — для smoke-перевірки.
# GET /  → сторінка чату, GET /events → SSE, POST /send → нотифікація у stdout.
# (Без Claude Code нотифікація нікуди не доходить — це нормально для smoke.)
run:
	bun server.ts

# E2E-тест контракту каналу: MCP-клієнт по stdio бачить tool reply;
# POST /send і виклик reply долітають у SSE-стрім /events.
test:
	bun install --no-summary
	bun test

# Подивитися живий SSE-стрім (коли сервер уже піднятий через make run)
events:
	curl -N localhost:8788/events
