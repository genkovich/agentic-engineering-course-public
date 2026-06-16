# Module 8 - MCP

Model Context Protocol від юзера до автора: підключення готових серверів, екосистема,
власний сервер, транспорти, дебаг через Inspector і безпека MCP.
Demo-тека під кожну лекцію: легкі config/inspection-кити для 8.1-8.5 і
повноцінні проєкти на TypeScript + Node 20 (Bun для каналу) для 8.6-8.9.

## Лекції модуля

- 8.1 Що таке MCP - архітектура клієнт-сервер, конектори
- 8.2 MCP примітиви - tools, resources, prompts
- 8.3 Підключення MCP серверів - транспорти, scope, `.mcp.json`, дозволи
- 8.4 Екосистема MCP - готові сервери в роботі (Context7, Playwright, GitHub)
- 8.5 Claude як MCP-сервер - `claude mcp serve`
- 8.6 Будуємо власний MCP-сервер - task-store з нуля
- 8.7 MCP Inspector - дебаг і тестування серверів
- 8.8 Канали - чат прямо у твою Claude Code сесію
- 8.9 Безпека MCP - модель загроз і захисти

## Демо модуля

| Папка | Що це | Лекції |
|---|---|---|
| [8.1-what-is-mcp](./8.1-what-is-mcp) | config-кит: підключення публічного zero-key сервера (Context7) через Inspector, 12-кроковий flow живцем; без власного коду | 8.1 |
| [8.2-mcp-primitives](./8.2-mcp-primitives) | крихітний read-only сервер з трьома примітивами (1 tool + 1 resource + 1 prompt) - побачити їх у Inspector до того, як будувати у 8.6 | 8.2 |
| [8.3-connecting-servers](./8.3-connecting-servers) | config-кит: приклади `.mcp.json` (Playwright/GitHub/Slack/Context7) - транспорти, scope, env-expansion; `make demo` на Context7 без ключа | 8.3 |
| [8.4-mcp-ecosystem](./8.4-mcp-ecosystem) | config-кит: куровані сервери першого кола (Context7/GitHub/Playwright) + `DECISION.md` (чек-лист довіри, матриця MCP vs CLI) | 8.4 |
| [8.5-claude-mcp-serve](./8.5-claude-mcp-serve) | скрипт-кит навколо вбудованого `claude mcp serve`: tools/list, resources/list → -32601, tools/call Read без моделі і без підтверджень | 8.5 |
| [8.6-first-mcp-server](./8.6-first-mcp-server) | task-store: перший власний MCP-сервер - tools + resource + prompt поверх stdio, HTTP-варіант транспорту, навмисно зламаний `server.buggy.ts` для практики з Inspector | 8.6, 8.7, 8.10 |
| [8.7-mcp-inspector](./8.7-mcp-inspector) | самодостатній debug-кит: чесний vs зламаний сервер на одному межовому виклику; `make smoke`/`make contract` ловлять брехню про успіх у CI | 8.7 |
| [8.8-web-chat-channel](./8.8-web-chat-channel) | канал Claude Code: один Bun-файл `server.ts` = MCP-канал (`McpServer` + capability `claude/channel` + нотифікація + tool `reply`) + веб-чат на SSE; повідомлення з браузера пушаться прямо у сесію через `--dangerously-load-development-channels server:webchat` | 8.8 |
| [8.9-mcp-security](./8.9-mcp-security) | інспекційна фікстура tool poisoning: отруєний vs безпечний сервер; аудит описів очима моделі через Inspector (без реального ексфільтрейту) | 8.9 |
| [8.9-mcp-client](./8.9-mcp-client) | власний MCP-клієнт: від listTools до tool-use loop з Claude API і поверх `claude mcp serve` | довідково (клієнт-контент → Agent SDK 5.7) |

Кожна лекція 8.1-8.9 має власну demo-теку вище. Концептуальні уроки 8.1-8.5
несуть легкі config/inspection-кити (підключення й інспекція готових серверів),
а власний сервер з нуля будуємо лише у 8.6.

> Урок 8.11 (дистрибуція) заархівовано - заготовки лежать у [`_archived/8.11-distribution`](./_archived/8.11-distribution). Фікстура аудиту «MCP чи CLI» переїхала разом з уроком у Модуль 11: [`modules/11-production/11.3-audit-config`](../11-production/11.3-audit-config).

## Швидкий старт

```bash
# task-store: тести і запуск
cd 8.6-first-mcp-server && make install && make test
make run                                                 # stdio
make run-http                                            # Streamable HTTP на :3335

# web-chat-channel: тести контракту каналу (stdio MCP-клієнт + SSE)
cd 8.8-web-chat-channel && bun install && make test
# як канал: claude --dangerously-load-development-channels server:webchat (з цієї папки) → http://localhost:8788

# task-store: деплойний образ (Dockerfile + compose)
cd 8.6-first-mcp-server && make seed && docker compose up --build   # :3335 + /healthz

# mcp-client: мінімальний клієнт проти echo-фікстури
cd 8.9-mcp-client && make install && make test && make run-01

# config/inspection-кити 8.1-8.5, 8.7, 8.9-security: інспекція через MCP Inspector
cd 8.1-what-is-mcp && make inspect            # публічний Context7 очима клієнта
cd 8.2-mcp-primitives && make inspect         # три примітиви у Inspector
cd 8.7-mcp-inspector && make smoke && make contract   # чесний vs зламаний сервер
cd 8.9-mcp-security && make inspect-poisoned  # tool poisoning в описі
```

У кожному демо є власний README (покрокова інструкція) і CLAUDE.md (контекст для Claude Code).
