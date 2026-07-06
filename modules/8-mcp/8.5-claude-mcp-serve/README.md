# Demo: claude-mcp-serve

**Module:** 8 - MCP
**Lecture:** 8.5 - Claude як MCP-сервер: claude mcp serve

## Що показує

Скрипт-кит навколо вбудованої команди `claude mcp serve`. Власного коду тут немає
зовсім - **сервер це сам Claude Code**. Тека дає готові команди, щоб заглянути у
цей сервер очима клієнта через MCP Inspector і переконатися на власні очі у трьох
речах з лекції:

1. Сервер віддає внутрішній тулбокс Claude Code (Read, Edit, Write, Bash і ще
   кілька десятків інструментів).
2. З трьох примітивів реалізований рівно один - **tools**. `resources/list`
   повертає помилку `-32601 Method not found`.
3. Усередині сервера **немає моделі**: `tools/call` з Read читає файл миттєво,
   без токенів і **без жодного підтвердження**.

## Структура

```
8.5-claude-mcp-serve/
├── README.md         цей файл
├── Makefile          serve-help / tools / no-resources / read
└── serve-demo.txt    файл, який читаємо через MCP без участі моделі
```

## Pre-requisites

- Встановлений Claude Code (`claude` у PATH) - саме він і є сервером
- Node.js 20+ і `npx` (для MCP Inspector)

## Як запустити

```bash
cd 8.5-claude-mcp-serve

make serve-help    # дві опції, нуль транспорту: це stdio-процес для клієнта
make tools         # tools/list: порахуй інструменти, знайди Read/Edit/Write/Bash
make no-resources  # resources/list -> -32601 Method not found (примітив лише один)
make read          # tools/call Read serve-demo.txt: вміст без моделі і без підтверджень
```

## Чому виклик проходить без підтверджень

Шар дозволів з інтерактивної сесії Claude Code сюди **не переїжджає**. Сервер
виконує кожен `tools/call` одразу. Звідси три правила безпеки з лекції:

- підключай лише клієнтів, яким довіряєш як власному терміналу;
- підтвердження небезпечних викликів - на боці клієнта;
- ніколи не виставляй цей сервер назовні в мережу.

Read читає будь-який файл, доступний твоєму користувачу (включно з `.env` і
ssh-ключами), Bash виконує довільні команди - відповідальність повністю на клієнті.

## Source

- CLI reference: `https://code.claude.com/docs/en/cli-reference`
- MCP Inspector: `https://github.com/modelcontextprotocol/inspector`
