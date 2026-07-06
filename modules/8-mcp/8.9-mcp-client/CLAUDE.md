# CLAUDE.md · mcp-client (лекція 8.9)

Власний MCP-клієнт на TypeScript: три кроки від `listTools` до повного
tool-use loop з Claude API і поверх `claude mcp serve`.

## Стек

- Node 20+, TypeScript ESM, tsx (запуск без build-кроку),
  `@modelcontextprotocol/sdk`, `@anthropic-ai/sdk`, dotenv.
- Тести: vitest проти фікстури `test/fixtures/echo-server.ts` - без
  API-ключа і зовнішніх процесів (`make test`).

## Конвенції

- `src/01-list-and-call.ts` - мінімальний клієнт: connect → listTools → callTool.
- `src/resources.ts` - дзеркальні дієслова resources/prompts проти task-store
  з 8.6 (`listResources`/`readResource`, `listPrompts`/`getPrompt`); без ключа.
- `src/02-claude-loop.ts` - tool-use loop з Claude API (потрібен
  `ANTHROPIC_API_KEY` у `.env`).
- `src/utilities.ts` - службовий шар: ping, таймаут/cancellation, pagination;
  без ключа, проти фікстур `slow-server` і `paginated-server`.
- `src/03-claude-serve.ts` - той самий loop поверх `claude mcp serve`
  (потрібен Claude Code CLI).
- `src/mcp-bridge.ts` - спільний шар: переклад MCP tools у формат
  Claude Messages API, виконання tool_use через callTool, runToolLoop.
- Сервер для run-01 передається параметром:
  `make run-01 SERVER="node ../8.6-first-mcp-server/dist/server.js"`.
- Фікстури в `test/fixtures/` dual-mode (імпорт у тестах + прямий запуск
  по stdio): `echo-server` (2 tools), `slow-server` (повільний tool),
  `paginated-server` (25 tools сторінками), `resource-server` (resources+prompt).

## Не робити

- Не змінювати `test/` - якщо тест падає, фіксити код.
- Не хардкодити API-ключі у `src/` - тільки через `.env`.
- Не комітити `.env`, `node_modules/`, `dist/` (gitignored).
