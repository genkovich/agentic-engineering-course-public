# Demo: first-mcp-server

**Module:** 8 — MCP
**Lecture:** 8.6 — Будуємо власний MCP-сервер

## Що показує

Повний MCP-сервер `task-store` на TypeScript SDK, з усіма трьома примітивами протоколу на одному простому домені. Домен навмисно нудний (локальне сховище задач), щоб уся увага лишалась на механіці MCP, не на бізнес-логіці.

Три примітиви в одному сервері:

- **Tools** (`add_task`, `complete_task`, `list_tasks`). Дії, які модель викликає сама. Кожен tool описаний zod-схемою: SDK конвертує її у JSON Schema для `tools/list` і валідує аргументи ще до того, як виклик дійде до твого коду.
- **Resource** (`tasks://summary`). Канал тільки для читання: текстовий підсумок, скільки задач відкрито і закрито, яка відкрита найстаріша. URI-схему `tasks://` вигадуємо самі.
- **Prompt** (`plan-day`). Шаблон, який юзер викликає явно. Приймає аргумент `focus` і сам підставляє у текст актуальний список відкритих задач.

Окремо демо показує два рішення, які відрізняють робочий сервер від іграшки:

1. **Error handling.** `complete_task` з неіснуючим id повертає `isError: true` зі зрозумілим текстом і підказкою викликати `list_tasks`. Сервер не падає, модель розуміє, що пішло не так, і може виправитись сама.
2. **Шари відокремлені.** Уся логіка сховища живе у `store.ts` без жодного import з SDK. MCP-шар у `server.ts` тільки описує примітиви і мапить помилки. Завдяки цьому store тестується звичайними unit-тестами, а сервер цілком через `InMemoryTransport` без зовнішніх процесів.

Стан зберігається у `data/tasks.json`: перезапуск сервера не втрачає задачі.

## Структура

```
8.6-first-mcp-server/
├── README.md            цей файл
├── Makefile             install / run / run-http / build / test / inspect / inspect-buggy / clean
├── package.json         build=tsc, test=vitest run, start=node dist/server.js
├── tsconfig.json
├── .mcp.json.example    приклад підключення у Claude Code
├── src/
│   ├── server.ts        MCP-шар: 3 tools + resource + prompt, докладні коментарі
│   ├── server-http.ts   той самий createServer через Streamable HTTP на :3335 (лекція 8.8)
│   ├── server.buggy.ts  навмисно зламана копія для лекції 8.7 (див. нижче)
│   ├── store.ts         логіка сховища, без жодної згадки про MCP
│   ├── store.test.ts    unit-тести сховища
│   └── server.test.ts   тести MCP-шару через InMemoryTransport (без stdio і процесів)
└── data/tasks.json      зʼявляється після першого add_task (у .gitignore)
```

## Pre-requisites

- Node.js 20+
- npm

API-ключі не потрібні: сервер локальний, нікуди не ходить.

## Як запустити

```bash
cd 8.6-first-mcp-server

make test       # npm install + vitest: 17 тестів, store + сервер через InMemoryTransport
make inspect    # збірка + MCP Inspector у CLI-режимі: tools/list через справжній stdio
make run        # запустити сервер вручну (чекає JSON-RPC на stdin, Ctrl+C щоб вийти)
make run-http   # той самий сервер через Streamable HTTP на :3335 (лекція 8.8)
make clean      # прибрати node_modules, dist, data
```

`make run-http` піднімає той самий task-store на `http://localhost:3335/mcp`: уся
різниця з stdio-варіантом - транспортний wiring у `src/server-http.ts`, секції
register* без змін. Підключення: `claude mcp add --transport http task-store-http http://localhost:3335/mcp`.

`make run` корисний хіба що подивитись, що сервер стартує. Сам по собі stdio-сервер у терміналі мовчить: він чекає повідомлення протоколу на stdin. Спілкуються з ним клієнти (Claude Code, Inspector), не людина.

## Як підключити до Claude Code

Спершу зібрати: `make build`. Далі два варіанти.

Варіант 1, через CLI (рекомендований, працює з будь-якого проекту):

```bash
claude mcp add task-store -- node /абсолютний/шлях/до/8.6-first-mcp-server/dist/server.js
claude mcp list   # перевірка: task-store ... ✓ Connected
```

Варіант 2, через `.mcp.json` у корені свого проекту (project scope, файл комітиться в репо):

```bash
cp .mcp.json.example /шлях/до/свого/проекту/.mcp.json
# і поправ args на абсолютний шлях до dist/server.js
```

Перевірка зсередини сесії Claude Code:

- `/mcp` показує сервер task-store і його примітиви;
- «додай задачу підготувати скрінкаст з high пріоритетом» викликає `add_task`;
- `@task-store:tasks://summary` підкладає resource у контекст;
- `/mcp__task-store__plan-day` викликає prompt (Claude Code попросить аргумент focus).

## Очікуваний output

`make test`:

```
 ✓ src/store.test.ts (8 tests)
 ✓ src/server.test.ts (9 tests)
 Test Files  2 passed (2)
      Tests  17 passed (17)
```

`make inspect` повертає JSON зі списком трьох tools. Зверни увагу: `priority` і `status` уже не zod-код, а згенерована JSON Schema з `enum` і `default`:

```json
{
  "tools": [
    { "name": "add_task", "inputSchema": { "properties": { "priority": { "enum": ["low", "medium", "high"], "default": "medium" } } } },
    { "name": "complete_task", ... },
    { "name": "list_tasks", ... }
  ]
}
```

Виклик `complete_task` з фейковим id на правильному сервері:

```json
{
  "content": [{ "type": "text", "text": "Задачі з id \"task-999\" не існує. Виклич list_tasks, щоб побачити актуальні id." }],
  "isError": true
}
```

## Для лекції 8.7 (MCP Inspector)

`src/server.buggy.ts` це копія сервера з одним підкладеним багом: `complete_task` тихо ковтає помилку про неіснуючий id і повертає `success: true`. Зовні сервер виглядає здоровим, `tools/list` чистий, схеми валідні. Тести цей файл не покривають, він зламаний навмисно.

У демо лекції 8.7 баг знаходимо Inspector-ом: викликаємо `complete_task` з фейковим id і порівнюємо відповідь з очікуваною. Швидкий спосіб відтворити з CLI:

```bash
make inspect-buggy
```

Очікувана правильна поведінка: `isError: true` з поясненням. Фактична відповідь зламаного сервера:

```json
{
  "content": [{ "type": "text", "text": "{\n  \"success\": true,\n  \"id\": \"task-999\"\n}" }]
}
```

Задачі `task-999` не існує, але сервер рапортує успіх. Модель, яка довіриться такій відповіді, вважатиме задачу закритою. Це клас багів, які видно тільки на рівні викликів, і саме для цього потрібен Inspector.

Той самий буггі-сервер можна відкрити і в UI-режимі Inspector:

```bash
npx @modelcontextprotocol/inspector node dist/server.buggy.js
```

## Source

- TypeScript SDK: `https://github.com/modelcontextprotocol/typescript-sdk`
- MCP Inspector: `https://github.com/modelcontextprotocol/inspector`
- Специфікація MCP: `https://modelcontextprotocol.io/specification`
