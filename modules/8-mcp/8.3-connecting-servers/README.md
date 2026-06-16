# Demo: connecting-servers

**Module:** 8 - MCP
**Lecture:** 8.3 - Підключення MCP серверів до Claude Code

## Що показує

Конфіг-кит з чотирма реальними прикладами підключення у `.mcp.json.example` -
по одному під кожне рішення, яке ухвалюєш при підключенні сервера: який
**транспорт**, де брати **секрети**, і один сервер, який можна підняти прямо
зараз без жодного ключа.

| Сервер | Транспорт | Секрет | Що демонструє |
|---|---|---|---|
| `context7` | stdio | немає | найпростіший випадок, працює одразу |
| `playwright` | stdio | немає | локальний процес через npx |
| `github` | http | `${GITHUB_TOKEN}` у header | хмарний сервер + Bearer-токен |
| `slack` | stdio | `${SLACK_BOT_TOKEN}` у env | env-expansion з default через `:-` |

## Транспорти

- **http** (streamable) - для хмарних серверів, рекомендований. `github` вище.
- **sse** - застарілий, документація радить замінювати на http.
- **stdio** - локальний процес: Claude Code сам його запускає і говорить через
  stdin/stdout. `context7`, `playwright`, `slack`.

## Scope: де житиме конфіг

При збігу імен пріоритет **Local > Project > User**:

- **Local** (default) - тільки ти, тільки цей проект (`~/.claude.json`). Для
  експериментів і серверів з особистими ключами.
- **Project** - файл `.mcp.json` у корені репо, комітиться в git, приїжджає всій
  команді. Саме сюди кладуть командні сервери з `${VAR}`-плейсхолдерами.
- **User** - усі твої проекти на машині. Для утиліт «скрізь зі мною».

## Секрети: env-expansion

`.mcp.json` підтримує `${VAR}` і `${VAR:-default}` у полях `command`, `args`,
`env`, `url` і `headers`. Правило для команди: **конфіг у git з плейсхолдерами,
токени - у середовищі кожного розробника**. Якщо потрібна змінна не задана і
default немає - Claude Code не розпарсить конфіг.

## Pre-requisites

- Node.js 20+ і `npx`
- Доступ до мережі

## Як запустити

```bash
cd 8.3-connecting-servers
make demo      # підключає Context7 (без ключа) і друкує tools/list
```

Щоб підключити будь-який із серверів у свій проект - скопіюй потрібний блок з
`.mcp.json.example` у `.mcp.json` свого репо і задай токени через змінні оточення.
Якщо працюєш у спільному репозиторії, не комить `.mcp.json` без згоди команди.

## Source

- Лекція 8.3 у Obsidian vault: `Own Brand/AI Course/Claude Course/Module 8/Lecture 3/`
- MCP у Claude Code: `https://code.claude.com/docs/en/mcp`
- CLI reference: `https://code.claude.com/docs/en/cli-reference`
