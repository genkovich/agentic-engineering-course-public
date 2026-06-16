# CLAUDE.md · connecting-servers (лекція 8.3)

Конфіг-кит до уроку про підключення MCP-серверів. Власного коду немає: чотири
приклади у `.mcp.json.example` (транспорти + env-expansion) і один живий
`make demo` на zero-key Context7.

## Стек

- Лише `npx` + MCP Inspector. Сервери з прикладів тягнуться через npx або по http.

## Конвенції

- `.mcp.json.example` - канон прикладів: context7/playwright (stdio), github (http
  + Bearer), slack (stdio + env з `${VAR:-default}`).
- `make demo` - єдиний таргет, який реально щось підключає (Context7 без ключа).

## Не робити

- Не вписувати справжні токени у `.mcp.json.example` - тільки `${VAR}`-плейсхолдери.
- Не додавати тут власний сервер: тека про підключення готових, не про написання.
