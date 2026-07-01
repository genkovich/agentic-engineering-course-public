# Demo: mcp-ecosystem

**Module:** 8 - MCP
**Lecture:** 8.4 - Екосистема MCP: готові сервери в роботі

## Що показує

Конфіг-кит з трьох курованих серверів **першого кола довіри** (офіційні від
вендорів) і дві шпаргалки для рішень про підключення у [`DECISION.md`](./DECISION.md):
чек-лист п'яти перевірок і матриця MCP vs CLI.

Три робочі коні з лекції у `.mcp.json.example`:

- **Context7** (Upstash) - свіжа документація бібліотек у контекст, 2 tools,
  близько тисячі токенів definitions, працює без ключа.
- **GitHub MCP** (GitHub) - 100+ tools у toolsets; за замовчуванням лише базовий
  набір, решта - прапорцем `--toolsets`; є `--read-only`. Потребує токена.
- **Playwright MCP** (Microsoft) - браузер для агента через accessibility tree
  (текст замість пікселів), 23 tools у дефолті.

## Структура

```
8.4-mcp-ecosystem/
├── README.md            цей файл
├── DECISION.md          чек-лист довіри (5 перевірок) + матриця MCP vs CLI
├── Makefile             make inspect
└── .mcp.json.example    куровані конфіги Context7 / GitHub MCP / Playwright MCP
```

## Три кола довіри

- **Перше** - офіційні сервери вендорів. Найвища довіра: вендор відповідає
  репутацією, сервер оновлюється разом з API.
- **Друге** - сім reference-серверів команди протоколу (Everything, Fetch,
  Filesystem, Git, Memory, Sequential Thinking, Time). Навчальні приклади.
- **Третє** - community: тисячі серверів, які реєстр не перевіряє перед
  публікацією. Тут чек-лист з `DECISION.md` обов'язковий.

## Pre-requisites

- Node.js 20+ і `npx`
- Доступ до мережі

## Як запустити

```bash
cd 8.4-mcp-ecosystem
make inspect      # tools/list Context7 (без ключа): найдешевший мешканець конфігу
```

GitHub і Playwright з `.mcp.json.example` підключаються у свій проект за тим самим
принципом, що в уроці 8.3 (GitHub потребує `${GITHUB_TOKEN}`).

## Source

- Лекція 8.4 у Obsidian vault: `Own Brand/AI Course/Claude Course/Module 8/Lecture 4/`
- Офіційний MCP Registry: `https://registry.modelcontextprotocol.io`
- github/github-mcp-server, microsoft/playwright-mcp, upstash/context7
