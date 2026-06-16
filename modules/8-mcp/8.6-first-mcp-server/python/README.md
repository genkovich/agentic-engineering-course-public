# task-store на Python (FastMCP)

Той самий сервер `task-store`, що й у TypeScript-версії з кореня демо, але на
офіційному **Python SDK** через `FastMCP`. Це дзеркало до секції 9 лекції 8.6:
наочний доказ, що **протокол MCP не залежить від мови**. Клієнт (Claude Code,
Inspector) не бачить різниці між TS- і Python-сервером - однакові tools, схеми,
помилки, той самий файл `data/tasks.json`.

## Що всередині

Ті самі три примітиви і та сама межа між шарами, що й у TS:

- **`store.py`** - логіка сховища (`TaskStore`, `Task`, `TaskNotFoundError`).
  Жодного import з MCP SDK. Поля `createdAt`/`completedAt` навмисно у camelCase,
  щоб `data/tasks.json` був байт-сумісний з TS-версією: обидва сервери читають і
  пишуть один і той самий файл.
- **`server.py`** - MCP-шар на FastMCP. Те, що у TS робить зв'язка `zod` +
  `registerTool`, тут робить сама сигнатура функції:
  - type hints на параметрах + `Field(description=...)` → JSON Schema входу;
  - docstring функції → `description` tool-а;
  - анотація повернення `-> Task` → **structured output** (FastMCP сам генерує
    `outputSchema` і `structuredContent`, без ручного коду);
  - `raise ValueError(...)` у tool-функції → відповідь з `isError: true`;
  - resource `tasks://summary` і prompt `plan_day` - звичайні функції з декораторами.
- **`test_server.py`** - 17 тестів за духом TS-версії: unit-тести `TaskStore` +
  тести MCP-шару через in-memory клієнт SDK (без stdio і процесів) + тест інтеропу
  файлу з TS.

## Запуск

Потрібен [`uv`](https://docs.astral.sh/uv/) (менеджер пакетів і оточень Python).
Усе - з кореня демо через Makefile:

```bash
make py-install   # uv sync: створює .venv і ставить mcp + pytest
make py-test      # uv run pytest: 17 зелених тестів
make py-run       # запуск сервера на stdio (Ctrl+C щоб вийти)
```

Або напряму з цієї папки: `uv sync`, `uv run pytest`, `uv run server.py`.

## Підключення до Claude Code

Сервер локальний, API-ключі не потрібні. Один рядок (абсолютний шлях до `python/`):

```bash
claude mcp add task-store-py -- \
  uv run --directory /абсолютний/шлях/до/8.6-first-mcp-server/python server.py
claude mcp list   # task-store-py ... ✔ Connected
```

Усередині сесії:

- `/mcp` показує `task-store-py` з трьома tools, resource і prompt;
- «додай задачу ... з high пріоритетом» викликає `mcp__task-store-py__add_task`;
- `@task-store-py:tasks://summary` підкладає resource;
- `/mcp__task-store-py__plan_day` запускає prompt.

> Імена tools (`add_task`, `complete_task`, `list_tasks`) і схеми ідентичні
> TS-версії. Якщо запустити обидва сервери поряд, вони ділять `data/tasks.json`:
> задачу, додану Python-сервером, прочитає TS-сервер, і навпаки.

## Smoke-тест через Inspector

Inspector CLI читає `package.json` з поточної директорії, тому запускай **з кореня
демо** (а не з `python/`):

```bash
cd ..   # корінь 8.6-first-mcp-server
npx @modelcontextprotocol/inspector --cli \
  uv run --directory python server.py --method tools/list
```

У відповіді - три tools зі згенерованою JSON Schema: `priority` має
`"enum": ["low","medium","high"]` і `"default": "medium"`, а `add_task` має
`outputSchema` (structured output з анотації повернення).
