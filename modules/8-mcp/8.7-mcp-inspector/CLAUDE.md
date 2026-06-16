# CLAUDE.md · mcp-inspector (лекція 8.7)

Самодостатній debug-кит: чесний і навмисно зламаний MCP-сервер для практики з
Inspector. In-memory, без persistence - мінімум, щоб побачити контраст
isError vs success: true на виклику complete_task з фейковим id.

## Стек

- Node 20+, TypeScript (ESM), `@modelcontextprotocol/sdk`, zod. Збірка tsc -> `dist/`.
- Контрактні таргети потребують `jq`.

## Конвенції

- `src/server.ts` - чесний сервер (3 tools, complete_task -> isError на неіснуючий id).
- `src/server.buggy.ts` - та сама форма, але complete_task рапортує success: true.
- Рівно 3 інструменти (`make smoke` перевіряє `length == 3`) - не додавай четвертий,
  бо зламаєш smoke-контракт і завдання уроку.

## Не робити

- Не «лагодь» `server.buggy.ts` поза складним рівнем завдання: баг там за сценарієм.
- Не додавати persistence/Python/HTTP - для цього є `../8.6-first-mcp-server`.
- Не комітити `node_modules/` і `dist/` (gitignored).
