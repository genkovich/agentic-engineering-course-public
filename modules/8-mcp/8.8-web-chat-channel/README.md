# web-chat-channel

Найпростіший **канал** (channel) для Claude Code: маленький веб-чат у браузері,
повідомлення з якого прилітають **прямо у твою запущену локальну сесію** Claude
Code, а відповіді Claude повертаються назад у браузер.

Канал — це MCP-сервер, який не чекає, поки його спитають, а сам **пушить** події
у сесію. Подія приходить у контекст Claude як тег
`<channel source="webchat" chat_id="web">…</channel>`, і Claude відповідає
інструментом `reply`. Сесія лишається локальною — браузер це просто вікно у неї.

Один файл `server.ts`, рантайм [Bun](https://bun.sh), нуль збірки. Це спрощений
[fakechat](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat):
SSE замість WebSocket, без файлів і редагувань. Жодного зовнішнього сервісу,
токенів чи контролю доступу.

## Як це влаштовано

Один Bun-процес = дві речі в одному:

- **MCP-сервер на stdio** (`McpServer` + `registerTool`, рівно як у 8.6) з
  capability `claude/channel`. На `POST /send` він викликає
  `mcp.server.notification('notifications/claude/channel', …)` — це й інʼєктить
  `<channel>` у сесію. Tool `reply` дає Claude відповісти назад.
- **`Bun.serve` на `127.0.0.1:8788`** — крихітний веб-чат:
  - `GET /` — сторінка чату (textarea + журнал; JS POST-ить на `/send`, слухає `/events`);
  - `POST /send` — повідомлення з браузера → нотифікація у сесію;
  - `GET /events` — SSE-стрім, у який `reply` пушить відповіді Claude.

## Встановлення і запуск

Сам сервер запускати руками не треба — Claude Code спавнить `server.ts` як
підпроцес. Тобі лишається зареєструвати його і дозволити завантаження як каналу.

1. **Залежності.** З папки демо: `bun install` (один раз). Можна й пропустити —
   `.mcp.json` запускає сервер через `bun run start`, а той сам ставить
   залежності перед першим стартом (zero-setup, як у офіційного fakechat).

2. **Реєстрація у Claude Code.** Сервер уже описаний у проєктному `.mcp.json`
   під іменем `webchat` — нічого додавати руками не треба:

   ```json
   { "mcpServers": { "webchat": { "command": "bun", "args": ["run", "--silent", "start"] } } }
   ```

   Claude Code читає цей файл на старті, коли ти запускаєш `claude` саме з цієї
   папки. Імʼя `webchat` звідси і стає `server:webchat` у наступному кроці.

3. **Запуск як каналу.** Канали — research preview, тому кастомний канал
   вантажиться дев-прапорцем, який називає сервер з `.mcp.json`. З папки демо:

   ```sh
   claude --dangerously-load-development-channels server:webchat
   ```

4. **Згода.** Перший старт у проєкті спитає згоду на новий сервер («New MCP
   server found in this project: webchat») — обери **Use this MCP server**. Під
   банером старту зʼявиться приглушений рядок, що канал активний:

   ```
   Channels (experimental) messages from server:webchat inject directly in this session
   ```

HTTP піднімається автоматично на `:8788`. Відкрий `http://localhost:8788`, напиши
«що в цьому репо?» — у сесії зʼявиться `<channel>`, Claude подивиться файли і
відповість через `reply`, а відповідь зʼявиться у браузері.

## Дебаг

- `/mcp` у сесії — статус каналу (Failed to connect → дивись помилку імпорту);
- `curl -N localhost:8788/events` — живий SSE-стрім відповідей;
- `~/.claude/debug/<session-id>.txt` — stderr-трейс сервера.

## Standalone smoke (без сесії)

```sh
make install   # bun install (один раз)
make run        # bun server.ts → http://localhost:8788
make events     # curl -N localhost:8788/events в іншому терміналі
make test       # e2e-тест контракту каналу по stdio + SSE
```

Без Claude Code нотифікація `POST /send` нікуди не доходить (немає кому слухати
`<channel>`) — для smoke це нормально; контракт повністю перевіряє `make test`.
