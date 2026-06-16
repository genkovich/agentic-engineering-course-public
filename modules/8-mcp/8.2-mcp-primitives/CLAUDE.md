# CLAUDE.md · mcp-primitives (лекція 8.2)

Крихітний read-only MCP-сервер з трьома примітивами (по одному tool/resource/
prompt). Призначення - інспекція у Inspector, щоб побачити три моделі контролю
до того, як будувати власний сервер у 8.6.

## Стек

- Node 20+, TypeScript (ESM, `"type": "module"`), `@modelcontextprotocol/sdk`, zod.
- Збірка tsc -> `dist/` (`make build`). Тестів немає - це інспекційна фікстура.

## Конвенції

- Один файл `src/server.ts`, фабрика `createServer()` без аргументів (стану немає).
- Кожен примітив - найпростіший представник своєї моделі контролю, з коментарем.
- stdout належить JSON-RPC: жодного `console.log`, діагностика через stderr.

## Не робити

- Не додавати стан, запис на диск, persistence чи тести - це матеріал 8.6.
  Тут сервер свідомо тримається read-only і мінімальним.
- Не комітити `node_modules/` і `dist/` (gitignored).
