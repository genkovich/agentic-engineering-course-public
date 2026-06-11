# Demo: notify-hub

**Module:** 8 (MCP)
**Lecture:** 8.8 «Канали і транспорти: stdio → Streamable HTTP + notify-hub»

## Що показує

У лекціях до цієї ми будували MCP-сервери через stdio: Claude Code сам запускає процес і говорить з ним через stdin/stdout. Це працює, поки сервер живе на твоїй машині і потрібен одному клієнту. notify-hub показує наступний крок: **Streamable HTTP**. Сервер живе як звичайний HTTP-процес, слухає порт, і до нього можуть підключатися кілька клієнтів з різних місць. Транспорт змінився, а tools і resources лишилися тими самими. Це головна думка лекції: MCP-протокол не залежить від каналу доставки.

Другий пункт: HTTP-транспорт відкриває двері, яких у stdio немає в принципі. Той самий Express-процес, який віддає `/mcp`, одночасно приймає webhooks (HTTP-виклики, які GitHub/GitLab шлють самі при подіях у репозиторії) на `/webhook`. Зовнішній світ пише у чергу подій, агент читає її через MCP tools:

```
GitHub/GitLab ──POST /webhook──▶ ┌─────────────────────────┐
                                 │ notify-hub (Express)    │
                                 │  normalize → queue      │ ──▶ data/events.json
Claude Code  ──POST /mcp──────▶  │  MCP: list_events,      │
   (Streamable HTTP)             │  ack_event,             │ ──▶ Telegram Bot API
                                 │  send_notification      │     (або dry-run)
                                 └─────────────────────────┘
```

Tools сервера:

- `list_events` повертає події з черги. Фільтр: `all`, `unacked` (ще не опрацьовані) або конкретний kind (`pr_opened`, `pipeline_failed`, `push`...).
- `ack_event` позначає подію опрацьованою. На неіснуючий id повертає помилку.
- `send_notification` шле повідомлення у Telegram-канал через Bot API. Без токена працює у dry-run: текст іде у лог і `data/sent.json`, відповідь містить `dryRun: true`. Повний demo-flow проходить без жодного реального секрету.
- Resource `events://recent` віддає останні 20 подій текстом.

Події GitHub (`X-GitHub-Event`: pull_request, workflow_run, push) і GitLab (`X-Gitlab-Event`: Merge Request Hook, Pipeline Hook) нормалізуються у спільний формат `{id, source, kind, title, repo, url, receivedAt, acked}`. Невідомі типи теж зберігаються з `kind: "other"`: краще бачити у черзі, ніж мовчки губити. Якщо заданий `WEBHOOK_SECRET`, сервер перевіряє підпис GitHub (`X-Hub-Signature-256`, HMAC SHA-256 від тіла запиту) і токен GitLab (`X-Gitlab-Token`). Без секрету приймає все і пише warning у лог.

### Як влаштований транспорт

Server side: `StreamableHTTPServerTransport` з `@modelcontextprotocol/sdk/server/streamableHttp.js` у **stateless режимі** (`sessionIdGenerator: undefined`). На кожен `POST /mcp` створюємо новий `McpServer` + transport, обробляємо запит через `transport.handleRequest(req, res, req.body)` і прибираємо на закритті відповіді. Стан живе у черзі подій, а не у MCP-сесії, тому session id тут зайвий. У stateless режимі `GET /mcp` і `DELETE /mcp` відповідають 405. Альтернатива (stateful, `sessionIdGenerator: () => randomUUID()`) потрібна, коли сервер сам ініціює повідомлення клієнту через SSE-стрім або тримає стан між викликами однієї сесії.

Client side (в e2e-тесті): `Client` + `StreamableHTTPClientTransport` з того ж SDK. Claude Code використовує такий самий клієнт під капотом.

## Pre-requisites

- Node.js 20.19+ (краще 22+)
- Жодних обов'язкових ключів. `WEBHOOK_SECRET` і Telegram-токени опційні, без них працює dry-run.

## Як запустити

```bash
cd modules/8-mcp/8.8-notify-hub

npm install
cp .env.example .env      # опційно: PORT, WEBHOOK_SECRET, TELEGRAM_*

make run                  # dev-сервер на :3334
```

В іншому терміналі:

```bash
make seed                 # шле 3 фейкові CI/CD payload на /webhook
curl -s http://localhost:3334/events | jq .   # черга очима curl
```

Підключення до Claude Code (з директорії свого проєкту):

```bash
claude mcp add --transport http notify-hub http://localhost:3334/mcp
```

Або через конфіг: скопіюй `.mcp.json.example` у `.mcp.json` свого проєкту. Далі у сесії Claude Code:

```
> подивись unacked події у notify-hub, познач опрацьованими і надішли мені summary у Telegram
```

Тести і збірка:

```bash
npm test                  # unit (normalize, queue) + e2e (webhook → MCP client → tools)
npm run build             # tsc → dist/
```

## Очікуваний output

`make seed` повертає три підтвердження з id і kind:

```
→ GitHub pull_request (opened)
{"ok":true,"id":"de65...","kind":"pr_opened"}
→ GitHub workflow_run (failure)
{"ok":true,"id":"97dd...","kind":"pipeline_failed"}
→ GitLab Pipeline Hook (failed)
{"ok":true,"id":"52fb...","kind":"pipeline_failed"}
```

Після цього `list_events` у Claude Code покаже 3 події, `ack_event` прибере їх з фільтра `unacked`, а `send_notification` без токена відповість `{"ok":true,"dryRun":true}` і запише текст у `data/sent.json`. На що звернути увагу: черга переживає рестарт сервера (персист у `data/events.json`), а MCP-частина не знає нічого про GitHub/GitLab, вона бачить лише нормалізовані події.

## Реюз у Module 9

Це «сервер для майбутнього». У Module 9 (лекції про CI/CD) notify-hub стає приймачем справжніх подій з пайплайнів:

1. У репозиторії GitHub/GitLab додаєш webhook на `https://<твій тунель>/webhook` (для локалки підійде `ngrok http 3334` або `cloudflared tunnel`). Тунель тут: публічна адреса, яка прокидає запити на твій локальний порт.
2. Задаєш `WEBHOOK_SECRET` тут і в налаштуваннях webhook, щоб приймати тільки підписані запити.
3. Задаєш `TELEGRAM_BOT_TOKEN` і `TELEGRAM_CHAT_ID`, і `send_notification` шле у канал по-справжньому.
4. Агент у Claude Code розбирає чергу після кожного прогону CI: впав pipeline → подивитись лог → надіслати команді розбір у Telegram → `ack_event`.

Файли під цей сценарій уже на місці: нормалізація обох провайдерів, перевірка підписів, dry-run розв'язка для Telegram.

## Структура

```
8.8-notify-hub/
├── src/
│   ├── server.ts      Express wiring: /webhook, /mcp, /events, /health
│   ├── mcp.ts         McpServer: 3 tools + resource events://recent
│   ├── queue.ts       черга подій, in-memory + персист у data/events.json
│   ├── normalize.ts   GitHub/GitLab payload → внутрішній формат HubEvent
│   └── telegram.ts    Telegram Bot API + dry-run у data/sent.json
├── examples/          реалістичні скорочені webhook payload-и для make seed
├── tests/             normalize.test.ts, queue.test.ts, e2e.test.ts
├── .env.example       PORT, WEBHOOK_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
├── .mcp.json.example  підключення до Claude Code через type: http
└── Makefile           run / test / seed / clean
```

## Source

- Лекція 8.8 «Канали і транспорти: stdio → Streamable HTTP + notify-hub»
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk (Streamable HTTP, stateless приклад: `src/examples/server/simpleStatelessStreamableHttp.ts`)
- MCP специфікація транспортів: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports
- GitHub webhooks: https://docs.github.com/en/webhooks/webhook-events-and-payloads
- GitLab webhooks: https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html
- Telegram Bot API sendMessage: https://core.telegram.org/bots/api#sendmessage
