# CLAUDE.md · notify-hub (лекція 8.8, деплой у 8.12)

Webhook-приймач GitHub/GitLab + MCP-сервер через Streamable HTTP в одному
Express-процесі. Черга подій посередині: `/webhook` пише, `/mcp` читає.

## Стек

- Node 20+ (Docker-образ: Node 22 slim), TypeScript ESM, express 5,
  `@modelcontextprotocol/sdk`, zod, dotenv.
- Тести: vitest + supertest (`make test`). Dev-запуск: tsx (`make run`, порт 3334).

## Конвенції

- `src/server.ts` - Express wiring: `/webhook`, `/mcp` (stateless,
  `sessionIdGenerator: undefined`), `/healthz`, `/events`. Фабрика
  `createApp(config)` з DI - тести піднімають app без мережі через supertest.
- `src/mcp.ts` - `buildMcpServer`: tools `list_events` / `ack_event` /
  `send_notification`.
- `src/normalize.ts` - payload GitHub/GitLab → внутрішній формат події.
- `src/queue.ts` - `EventQueue` з персистом у `data/events.json`.
- `src/telegram.ts` - відправка у Telegram; без токена - dry-run у `data/sent.json`.
- Секрети тільки через `.env` (зразок - `.env.example`). HMAC-підпис webhook
  рахується від raw body, тому body-parser зберігає сирі байти.

## Не робити

- Не змінювати `tests/` - якщо тест падає, фіксити код.
- Не комітити `data/`, `.env`, `dist/`, `node_modules/` (gitignored).
- Не вмикати живу відправку у Telegram у тестах - тести працюють у dry-run.
