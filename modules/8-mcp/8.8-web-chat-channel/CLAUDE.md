# web-chat-channel — контекст для Claude Code

Демо лекції 8.8 «Канали: чат прямо у твою Claude Code сесію» (Module 8, MCP).

## Що це

Найпростіший двосторонній **канал** Claude Code: один Bun-файл `server.ts`, який
одночасно є MCP-сервером на stdio (capability `claude/channel`) і веб-чатом на
`127.0.0.1:8788`. Повідомлення з браузера приходять у сесію як
`<channel source="webchat" chat_id="web">…</channel>`; Claude відповідає tool-ом
`reply`, текст летить у браузер через SSE (`GET /events`).

Спрощений `fakechat` з офіційного claude-plugins-official: SSE замість WebSocket,
без файлів/редагувань/доступу. Патерн узято з офіційних доксів Channels
(channels-reference, two-way приклад).

## Контракт каналу (не ламати)

- `new McpServer({name:'webchat'}, { capabilities: { experimental: {'claude/channel': {}} }, instructions })` — `claude/channel` робить сервер каналом. Той самий `McpServer`, що у 8.6 (low-level `Server` — `@deprecated`, не використовувати).
- `mcp.registerTool('reply', {inputSchema: {chat_id, text}}, handler)` — двосторонній канал; `registerTool` сам оголошує `tools`-capability і discovery (як у 8.6). Жодного `setRequestHandler(ListTools/CallTool)`.
- `mcp.server.notification({ method: 'notifications/claude/channel', params: { content, meta: { chat_id } } })` — server-initiated push через нижній шар (`mcp.server`, який McpServer лишає доступним саме для нотифікацій). `content` → тіло тегу, кожен ключ `meta` (літери/цифри/підкреслення) → атрибут. `source` ставиться автоматично з імені сервера.
- `await mcp.connect(new StdioServerTransport())` — stdio, тому **нічого не писати у stdout** (тільки `process.stderr`).

## Команди

- Запуск як канал: `claude --dangerously-load-development-channels server:webchat` (з цієї папки).
- Smoke: `make run` (standalone), `make events` (SSE), `make test` (e2e-контракт).
- Порт через `WEBCHAT_PORT` (default 8788).

## Межі

Навмисно голий приклад. Gating відправника (anti-prompt-injection), permission
relay (`claude/channel/permission`), пакування у plugin+marketplace — це advanced,
тут їх немає. Готові канали (fakechat, telegram, discord, imessage) — у
claude-plugins-official.
