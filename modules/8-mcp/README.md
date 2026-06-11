# Module 8 - MCP

Model Context Protocol від юзера до автора: підключення готових серверів, екосистема,
власний сервер і клієнт, транспорти, дистрибуція, прод і межі застосовності (MCP vs CLI).
Три clone-and-run демо на TypeScript + Node 20, два набори фікстур.

## Лекції модуля

- 8.1 Що таке MCP - архітектура клієнт-сервер, конектори
- 8.2 MCP примітиви - tools, resources, prompts
- 8.3 Підключення MCP серверів - транспорти, scope, `.mcp.json`, дозволи
- 8.4 Екосистема MCP - готові сервери в роботі (Context7, Playwright, GitHub)
- 8.5 Claude як MCP-сервер - `claude mcp serve`
- 8.6 Будуємо власний MCP-сервер - task-store з нуля
- 8.7 MCP Inspector - дебаг і тестування серверів
- 8.8 Канали і транспорти - stdio → Streamable HTTP + notify-hub
- 8.9 Будуємо власний MCP-клієнт - від listTools до tool-use loop
- 8.10 Advanced - sampling, elicitation, roots + безпека MCP
- 8.11 Поліровка і дистрибуція - completion, icons, mcpb, MCP Registry
- 8.12 MCP у продакшні - деплой, health checks, observability
- 8.13 MCP vs CLI - коли сервер зайвий
- 8.14 Куди їде протокол - SEP-и і стратегія

## Демо модуля

| Папка | Що це | Лекції |
|---|---|---|
| [8.6-first-mcp-server](./8.6-first-mcp-server) | task-store: перший власний MCP-сервер - tools + resource + prompt поверх stdio, HTTP-варіант транспорту, навмисно зламаний `server.buggy.ts` для практики з Inspector | 8.6, 8.7, 8.8, 8.10, 8.11 |
| [8.8-notify-hub](./8.8-notify-hub) | webhook-приймач CI/CD (GitHub/GitLab) + MCP endpoint через Streamable HTTP в одному Express-процесі; Dockerfile + DEPLOY.md для прод-деплою | 8.8, 8.12 |
| [8.9-mcp-client](./8.9-mcp-client) | власний MCP-клієнт: від listTools до tool-use loop з Claude API і поверх `claude mcp serve` | 8.9 |
| [8.11-distribution](./8.11-distribution) | заготовки дистрибуції task-store: `manifest.json` (mcpb-бандл), `server.json` (MCP Registry), `.mcpbignore` | 8.11 |
| [8.13-audit-config](./8.13-audit-config) | фікстура `.mcp.json` з 4 серверами для домашки «аудит конфігу: MCP чи CLI» | 8.13 |

Лекції 8.1-8.5 і 8.14 окремого демо-коду не потребують: практика там іде на готових
клієнтах (Claude Desktop, claude.ai, Claude Code) і каталожних серверах.

## Швидкий старт

```bash
# task-store: тести і запуск
cd 8.6-first-mcp-server && make install && make test
make run                                                 # stdio
make run-http                                            # Streamable HTTP на :3335

# notify-hub: тести, сервер, фейкові CI/CD-події
cd 8.8-notify-hub && make test && make run               # :3334
make seed                                                # 3 події у чергу

# mcp-client: мінімальний клієнт проти echo-фікстури
cd 8.9-mcp-client && make install && make test && make run-01
```

У кожному демо є власний README (покрокова інструкція) і CLAUDE.md (контекст для Claude Code).
