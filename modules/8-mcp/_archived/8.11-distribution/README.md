# 8.11-distribution · зразки дистрибуції task-store

Reference-файли до лекції 8.11 (pack → install → publish): як виглядають готові
`manifest.json` (mcpb-бандл) і `server.json` (MCP Registry) для сервера task-store.
`mcpb init` і `mcp-publisher init` генерують лише кістяки - тут лежить стан «після
правок», з яким можна звірятись. Використовуй як зразок для кроку 5 складного рівня
домашки модуля 8.

| Файл | Інструмент | Що це |
|---|---|---|
| `manifest.json` | `@anthropic-ai/mcpb` | маніфест бандла `.mcpb` для one-click install у Claude Desktop; entry - `dist/server.js` |
| `.mcpbignore` | `@anthropic-ai/mcpb` | що не повинно потрапити у бандл (сирці, тести, секрети) |
| `server.json` | `mcp-publisher` | запис для MCP Registry: name `io.github.<нік>/task-store`, npm-пакет як спосіб доставки |

## Як спробувати самому

```bash
# 1. Зібрати бандл-директорію з task-store
cd ../8.6-first-mcp-server && make build
mkdir -p /tmp/task-store-bundle && cp -r dist package.json package-lock.json /tmp/task-store-bundle
cd /tmp/task-store-bundle && npm ci --omit=dev

# 2. Маніфест: init генерує кістяк, поправ entry_point (звірся з manifest.json звідси)
npx @anthropic-ai/mcpb init --yes
npx @anthropic-ai/mcpb pack        # → Archive Details: розмір, файли, shasum

# 3. Registry: init генерує server.json, заповни name/version/package (звірся з server.json)
mcp-publisher init                  # brew install mcp-publisher
mcp-publisher validate              # schema-перевірка без публікації
```

Перед `mcpb pack` перевір, що у бандл не затягнувся `.env` - саме для цього існує
`.mcpbignore`.

## Якщо хочеш опублікувати свій сервер по-справжньому

Публікуй власний сервер (не демо-task-store): namespace `io.github.<твій-нік>/*`
підтверджується через `mcp-publisher login github`, а npm-пакет з `packages[].identifier`
має існувати і мати у своєму `package.json` поле `mcpName: "io.github.<твій-нік>/<server>"` -
так реєстр перевіряє, що пакет справді твій. Після цього - `mcp-publisher publish`.
