# CLAUDE.md · task-store MCP server (лекція 8.6)

Demo-сервер до лекцій 8.6-8.8 і 8.10-8.11: один TaskStore, три примітиви
протоколу (tools, resource, prompt) поверх нього.

## Стек

- Node 20+, TypeScript (ESM, `"type": "module"`), `@modelcontextprotocol/sdk`, zod.
- Тести: vitest (`make test`). Збірка: tsc → `dist/` (`make build`).

## Конвенції

- Логіка сховища - `src/store.ts` (`TaskStore`, чистий клас без MCP).
- MCP-шар - `src/server.ts`: фабрика `createServer(store)` з dependency
  injection, щоб тести підкладали in-memory store без файлу на диску.
- `src/server-http.ts` - той самий `createServer` через Streamable HTTP
  на :3335 (`make run-http`); міняється тільки транспортний wiring (лекція 8.8).
- `src/server.buggy.ts` - НАВМИСНО зламаний варіант для лекції 8.7:
  Inspector знаходить баг через `make inspect-buggy`.
- stdout у stdio-сервері належить JSON-RPC: жодного `console.log`,
  діагностика тільки через stderr (`console.error`).

## Не робити

- Не змінювати тести `src/*.test.ts` - якщо тест падає, фіксити код.
- Не «лагодити» `server.buggy.ts` - баг там за сценарієм лекції 8.7.
- Не комітити `node_modules/`, `dist/`, `data/` (gitignored).
