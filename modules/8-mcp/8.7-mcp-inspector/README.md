# Demo: mcp-inspector

**Module:** 8 - MCP
**Lecture:** 8.7 - MCP Inspector: дебаг і тестування серверів

## Що показує

Самодостатній debug-кит для практики з MCP Inspector: **дві версії того самого
сервера** на одному межовому виклику. Чесний `server.ts` на неіснуючий id повертає
`isError: true` з підказкою; зламаний `server.buggy.ts` тихо рапортує
`success: true`. Зовні обидва виглядають здоровими - tools/list чистий, схеми
валідні, happy-path працює. Різницю видно тільки на рівні конкретного виклику, і
саме це робить Inspector.

Тека навмисно мінімальна (in-memory, без persistence) - уся увага на контрасті
чесність/брехня і на тому, як CLI-режим Inspector ставить цю перевірку під CI.

## Структура

```
8.7-mcp-inspector/
├── README.md             цей файл
├── Makefile              install / build / inspect / inspect-buggy / smoke / contract / clean
├── package.json          build=tsc
├── tsconfig.json
└── src/
    ├── server.ts         чесний сервер: 3 tools, complete_task -> isError на фейк id
    └── server.buggy.ts   зламаний: complete_task -> success: true на фейк id
```

## Pre-requisites

- Node.js 20+ і npm
- `jq` (для контрактних таргетів `smoke` і `contract`)

## Як запустити

```bash
cd 8.7-mcp-inspector

make inspect         # tools/list чесного сервера: 3 інструменти зі схемами
make inspect-buggy   # complete_task id=task-999 на зламаному: success: true (баг!)
make smoke           # контракт #1: рівно 3 інструменти (jq, exit 0)
make contract        # контракт #2: чесний сервер -> isError: true (jq, exit 0)
```

Порівняй своїми руками. `make contract` проти `dist/server.js` завершується з
кодом 0 (чесний сервер чесно червонить на фейк id). Той самий рядок проти
`dist/server.buggy.js` дасть exit 1 - бо зламаний сервер бреше про успіх:

```bash
npx @modelcontextprotocol/inspector --cli node dist/server.buggy.js \
  --method tools/call --tool-name complete_task --tool-arg id=task-999 \
  | jq -e '.isError == true'; echo "exit=$?"     # exit=1
```

## UI-режим

CLI зручний для CI, а очима баг шукають у браузері:

```bash
make build
npx @modelcontextprotocol/inspector node dist/server.buggy.js
```

Браузер відкриється сам з токеном. Tools -> `complete_task`, введи id `task-999`,
подивись відповідь. Потім те саме проти `dist/server.js` - і порівняй у вкладці
History сирий JSON-RPC обох викликів.

## Source

- Повний task-store (з persistence і Python-дзеркалом): `../8.6-first-mcp-server`
- MCP Inspector: `https://github.com/modelcontextprotocol/inspector`
