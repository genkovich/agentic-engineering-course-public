# Demo: mcp-client

**Module:** 8 — MCP
**Lecture:** 8.9 — Будуємо власний MCP-клієнт

## Що показує

У лекціях 8.6 і 8.8 ми будували MCP-сервери і підключали їх до Claude Code. Тепер дивимось на протокол з іншого боку: пишемо власний MCP-клієнт. Тобто свою маленьку версію тієї частини Claude Code, яка підключається до серверів, питає у них список tools і виконує виклики.

Демо складається з трьох прогресивних прикладів. Кожен наступний додає один шар:

1. **`src/01-list-and-call.ts`** - мінімальний клієнт без AI. Підключається до будь-якого stdio MCP-сервера, робить `listTools()` і викликає tool з аргументами з командного рядка. Тут видно голий протокол: handshake, список інструментів, виклик.
2. **`src/02-claude-loop.ts`** - повний tool-use loop. Клієнт перетворює MCP tools у формат Claude API, шле запит у Messages API, виконує `tool_use` блоки через MCP `callTool`, повертає `tool_result` і крутить цикл, поки Claude не скаже `end_turn`. Це центральний код лекції: так працює будь-який агент, від Claude Code до Cursor.
3. **`src/03-claude-serve.ts`** - кульмінація. Той самий цикл, але MCP-сервером стає `claude mcp serve` (Claude Code як MCP-сервер, лекція 8.5). Твій скрипт через Claude API керує інструментами Claude Code: Read, Write, Bash, Glob, Grep. Демо-сценарій: "прочитай файл і скажи, скільки в ньому рядків", і Claude сам викликає Read tool сервера.

Спільна логіка живе у `src/mcp-bridge.ts`: конверсія схем tools (MCP `inputSchema` у Claude `input_schema`), виконання `tool_use` у `tool_result` і сам цикл `runToolLoop`. Ключове спостереження лекції: обидва формати говорять JSON Schema, тому "міст" між MCP і Claude API - це приблизно 50 рядків коду, і більшість з них - це цикл, не конверсія.

Поряд з трьома прогресивними прикладами є два допоміжні, які показують решту клієнтського SDK - обидва без API-ключа:

- **`src/resources.ts`** - клієнт читає не тільки tools. Дзеркальні дієслова `listResources`/`readResource` і `listPrompts`/`getPrompt` проти task-store з 8.6. Видно обидві гілки обробки за `mimeType`: `text/plain` як є, `application/json` з парсингом.
- **`src/utilities.ts`** - службовий шар протоколу: `ping` (keepalive), таймаут і cancellation (`callTool` з `{ timeout }` проти повільного tool), pagination (цикл по `nextCursor` через каталог на 25 tools).

## Pre-requisites

- Node.js 20+
- `ANTHROPIC_API_KEY` у `.env` - для прикладів 02 і 03 (01 працює без ключа)
- Claude Code CLI (`claude` у PATH) - тільки для прикладу 03

## Як запустити

```bash
cd modules/8-mcp/8.9-mcp-client
npm install
cp .env.example .env   # і вписати свій ANTHROPIC_API_KEY

# 01: мінімальний клієнт проти fixture-сервера (без API-ключа)
make run-01
# або проти свого сервера:
make run-01 SERVER="npx -y @modelcontextprotocol/server-filesystem /tmp"
# виклик конкретного tool:
npx tsx src/01-list-and-call.ts npx tsx test/fixtures/echo-server.ts \
  --tool echo --tool-args '{"message":"привіт"}'

# resources/prompts проти task-store з 8.6 (без API-ключа)
make run-resources

# 02: tool-use loop з Claude API (echo-server за замовчуванням)
make run-02
make run-02 PROMPT="Додай 100 і 23 інструментом add"

# utilities: ping, таймаут, pagination проти фікстур (без API-ключа)
make run-utilities

# 03: loop поверх claude mcp serve
make run-03
make run-03 PROMPT="Прочитай package.json і скажи, які там scripts"

# тести: без API-ключа і без зовнішніх процесів
make test
```

> `make run-resources` сам піднімає task-store з 8.6 по stdio і кладе у нього
> пару демо-задач. Стан пишеться у `../8.6-first-mcp-server/data/` (gitignored);
> для чистого прогону видали той файл: `rm -f ../8.6-first-mcp-server/data/tasks.json`.

## Очікуваний output

**01** покаже список tools fixture-сервера і результат виклику:

```
Connected to: npx tsx test/fixtures/echo-server.ts

Tools (2):
  - echo: Echoes the message back
  - add: Adds two numbers
```

**02** покаже хід циклу: Claude коментує, просить tool, отримує результат, віддає фінальну відповідь:

```
User: Додай числа 21 і 21 інструментом add, а потім продублюй результат через echo.

  [tool_use]    add({"a":21,"b":21})
  [tool_result] 42
  [tool_use]    echo({"message":"42"})
  [tool_result] Echo: 42
Claude: Готово! 21 + 21 = 42 ...
```

Зверни увагу на порядок: `stop_reason: "tool_use"` означає "виконай і повернись", і тільки `end_turn` завершує цикл.

**03** спершу виведе список інструментів Claude Code (їх більше десятка), потім Claude викличе Read tool і відповість, скільки рядків у файлі.

**run-resources** покаже каталог даних task-store і чотири read-дієслова:

```
listResources (3):
  - tasks://summary  [text/plain]
  - tasks://task/task-1  [application/json]
  - tasks://task/task-2  [application/json]

readResource tasks://summary  (text/plain -> як є):
  Відкритих задач: 2
  ...
listPrompts (1):
  - plan-day(focus, priority): ...
getPrompt plan-day { focus: "..." }:
  [user] Сплануй мій день. ...
```

**run-utilities** покаже три службові механізми протоколу:

```
── ping ──
  ping -> pong за 2ms (з'єднання живе)
── timeout + cancellation ──
  callTool slow(2000ms) з timeout=500ms ...
  -> RequestTimeout: MCP error -32001: Request timed out
  callTool slow(2000ms) з timeout=5000ms ...
  -> успіх: Готово за 2000ms
── pagination ──
  сторінка 1: +10 tools (nextCursor: 10)
  сторінка 2: +10 tools (nextCursor: 20)
  сторінка 3: +5 tools (кінець)
  -> разом 25 tools за 3 сторінки
```

## Підключення до task-store по HTTP

Усі три приклади вище ходять по stdio. Але транспорт у MCP змінний: той самий клієнтський код працює і з HTTP-сервером, міняється лише транспорт. Підключимось до `task-store` з лекції 8.6 - того самого сервера, який ми збудували, тільки через його HTTP-варіант (`make run-http` у `8.6-first-mcp-server`, ендпоінт `http://localhost:3335/mcp`).

Уся різниця - один import і один рядок транспорту. Client, listTools, callTool, mcp-bridge не змінюються:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

// task-store має бути запущений по HTTP: у 8.6-first-mcp-server `make run-http`
const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:3335/mcp"),
);

const client = new Client({ name: "demo-mcp-client", version: "1.0.0" });
await client.connect(transport);

const { tools } = await client.listTools();
console.log(tools.map((t) => t.name)); // → ["add_task", "complete_task", "list_tasks"]

await client.close();
```

Збережи це у `src/connect-task-store.ts` і запусти проти піднятого task-store: той самий клієнт, що бачив echo-сервер по stdio, тепер бачить три реальні tools по мережі. Жодного нового коду в `mcp-bridge.ts` - він і не знає, який під ним транспорт.

Той самий клієнт може тримати кілька підключень одночасно: один Client на один сервер, а tools з усіх серверів складаються в один список для Claude. Саме так Claude Code збирає tools з усіх серверів у `.mcp.json`.

## Безпека: claude mcp serve

Приклад 03 дає моделі доступ до інструментів файлової системи **без жодних підтверджень**: сервер `claude mcp serve` виконує Read, Write і Bash так, як попросить клієнт. У цьому демо клієнт сам керується Claude API, тобто модель фактично отримує руки на твоїй машині.

- Запускай 03 тільки з запитами, які ти сам написав і розумієш.
- Не вставляй у промпт неперевірений текст (вивід інших програм, чужі файли): це класичний вектор prompt injection з лекцій модуля 6.
- Для експериментів з Write і Bash краще працювати в окремій тимчасовій директорії або контейнері.

## Структура

```
8.9-mcp-client/
├── src/
│   ├── 01-list-and-call.ts   мінімальний клієнт: listTools + callTool
│   ├── resources.ts          listResources/readResource + listPrompts/getPrompt
│   ├── 02-claude-loop.ts     повний tool-use loop з Claude API
│   ├── utilities.ts          ping, таймаут/cancellation, pagination
│   ├── 03-claude-serve.ts    той самий loop поверх claude mcp serve
│   └── mcp-bridge.ts         конверсія схем + виконання tool_use + цикл
├── test/
│   ├── fixtures/echo-server.ts        крихітний MCP-сервер (2 tools, dual-mode)
│   ├── fixtures/slow-server.ts        один повільний tool для демо таймауту
│   ├── fixtures/paginated-server.ts   25 tools, tools/list сторінками по 10
│   ├── fixtures/resource-server.ts    resources (text+json) + prompt для тестів
│   ├── client.test.ts                 клієнт бачить tools і викликає їх
│   ├── resources.test.ts              listResources/readResource, prompts
│   ├── utilities.test.ts              ping, таймаут, pagination
│   └── mcp-bridge.test.ts             конверсія, tool_result, loop з моком Claude
├── Makefile
├── package.json
└── .env.example
```

Тести працюють через `InMemoryTransport`: клієнт і сервер у одному процесі, без stdio і мережі. Loop тестується з замоканим Anthropic-клієнтом, але зі справжнім MCP-сервером, тому конверсія і виконання перевіряються на живому протоколі. Усього 19 тестів, усі без API-ключа.

## Source

- Лекція 8.5 - Claude Code як MCP-сервер (`claude mcp serve`)
- Лекція 8.6 - Будуємо власний MCP-сервер (task-store, stdio + HTTP)
- Лекція 8.8 - MCP по Streamable HTTP (транспорт, яким клієнт ходить до task-store)
- Лекція 8.9 - Будуємо власний MCP-клієнт
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Tool use у Claude API: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Anthropic SDK для TypeScript: https://github.com/anthropics/anthropic-sdk-typescript
