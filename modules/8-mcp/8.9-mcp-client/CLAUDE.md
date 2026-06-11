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
- `src/02-claude-loop.ts` - tool-use loop з Claude API (потрібен
  `ANTHROPIC_API_KEY` у `.env`).
- `src/03-claude-serve.ts` - той самий loop поверх `claude mcp serve`
  (потрібен Claude Code CLI).
- `src/mcp-bridge.ts` - спільний шар: переклад MCP tools у формат
  Claude Messages API, виконання tool_use через callTool, runToolLoop.
- Сервер для run-01 передається параметром:
  `make run-01 SERVER="node ../8.6-first-mcp-server/dist/server.js"`.

## Не робити

- Не змінювати `test/` - якщо тест падає, фіксити код.
- Не хардкодити API-ключі у `src/` - тільки через `.env`.
- Не комітити `.env`, `node_modules/`, `dist/` (gitignored).
