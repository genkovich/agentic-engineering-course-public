# Demo: mcp-primitives

**Module:** 8 - MCP
**Lecture:** 8.2 - MCP примітиви: Tools, Resources, Prompts

## Що показує

Найменший можливий MCP-сервер, у якому є **всі три примітиви одразу** - по
одному представнику кожної моделі контролю. Мета теки: побачити tools, resources
і prompts у Inspector рівно так, як їх отримує клієнт, **ще до того**, як будувати
повноцінний сервер у 8.6.

| Примітив | Хто контролює | У демо |
|---|---|---|
| Tool | модель | `word_count` - рахує слова, read-only |
| Resource | додаток | `primitives://cheatsheet` - статична шпаргалка |
| Prompt | людина | `explain-primitive` - шаблон з аргументом `name` |

Сервер навмисно read-only: жодного стану, жодного запису. Уся увага - на тому, як
кожен примітив виглядає у відповіді протоколу.

## Структура

```
8.2-mcp-primitives/
├── README.md         цей файл
├── Makefile          install / build / inspect / inspect-resources / inspect-prompts / clean
├── package.json      build=tsc
├── tsconfig.json
└── src/server.ts     один сервер, три примітиви, докладні коментарі
```

## Pre-requisites

- Node.js 20+ і npm

Ключі не потрібні: сервер локальний, нікуди не ходить.

## Як запустити

```bash
cd 8.2-mcp-primitives

make inspect            # tools/list:     побачиш word_count з його схемою
make inspect-resources  # resources/list: побачиш primitives://cheatsheet
make inspect-prompts    # prompts/list:   побачиш explain-primitive з аргументом name
```

Кожен таргет сам поставить залежності і збере проект перед запуском Inspector.

## На що дивитись

- У `tools/list` поле `inputSchema` - це згенерована з zod **JSON Schema**: рівно
  те, що читає модель перед рішенням про виклик.
- У `resources/list` ресурс має `uri` (`primitives://cheatsheet`) і `mimeType` -
  його читають за адресою, а не викликають як функцію.
- У `prompts/list` промпт оголошує аргумент `name` - у Claude Code такий промпт
  став би slash-командою `/mcp__primitives-demo__explain-primitive`.

## Source

- Лекція 8.2 у Obsidian vault: `Own Brand/AI Course/Claude Course/Module 8/Lecture 2/`
- Повний сервер з усіма примітивами і тестами: `../8.6-first-mcp-server`
- Специфікація трьох примітивів: `https://modelcontextprotocol.io`
