---
name: ralph-prep
description: Generate a PROMPT.md scaffold for the Ralph loop from a story file. Triggers on '/ralph-prep <story-id>' (e.g. '/ralph-prep story-t1'), or when the user asks to 'підготуй PROMPT для Ralph', 'згенеруй PROMPT.md з story', 'prepare Ralph PROMPT from <story>'. Reads tasks/<story-id>.md + CLAUDE.md and writes the 3-section prompt to ./PROMPT.md.
argument-hint: <story-id> (e.g. story-t1)
allowed-tools: Read, Write, Glob
disable-model-invocation: false
---

# ralph-prep — згенерувати PROMPT.md з story

Маленький helper для запису скринкаста лекції 7.2: викликаємо `/ralph-prep <story-id>`,
отримуємо тонкий `PROMPT.md` у корені, який далі забирає `./ralph.sh` як вхід.

Скіл стек-агностик: працює і над абстрактним демо в цій теці, і над будь-яким
зовнішнім трекером (`TASKS_DIR=path/to/your/tasks`). Він не вигадує контракт —
лише переносить те, що вже є в story-файлі й `CLAUDE.md`.

## Аргументи

- `<story-id>` — ім'я файлу story без `.md` і без шляху (напр. `story-t1`, `S-1`).
  Скіл шукає файл у `${TASKS_DIR:-tasks}/`.

## Inputs

- `${TASKS_DIR:-tasks}/<story-id>.md` — обов'язково. Має містити опис, AC, checklist, DoD.
- `CLAUDE.md` у корені — обов'язково (стек, конвенції, заборони).
- Якщо `PROMPT.md` уже існує — попередь користувача і запитай дозвіл на перезапис.

## Output

Записує `PROMPT.md` у корені з трьома секціями + блоком «Не роби»:

```markdown
# PROMPT.md · Ralph loop (<story-id>)

## Контекст
Ти працюєш у проекті <project з CLAUDE.md>. Стек: <витяг із секції «Стек»>.
Прочитай: CLAUDE.md, tasks/tracker.md (обери todo без блокерів), tasks/<story-id>.md.

## Завдання
Реалізувати story <ID> зі статусом todo. Дотримуйся конвенцій CLAUDE.md.
Один atomic commit на story. Застряг за 3 ітерації → BLOCKED у tracker і вихід.
Усі stories done → створи файл DONE.

## DoD
<DoD зі story, 1-в-1 bullet list. Без вигаданих критеріїв.>

## Не роби
- Не міняй тести; падає тест → фіксь код.
- Жодних --dangerously-skip-permissions; максимум acceptEdits.
- Не змінюй CLAUDE.md / контракти без окремої story.
```

## Acceptance criteria

- `PROMPT.md` створено у корені (cwd).
- Секція «Контекст» згадує конкретний `<story-id>` файл (не загальне «story-файл»).
- Секція «Завдання» цитує `<ID>` story.
- Секція «DoD» — bullet list, 1-в-1 з DoD у story-файлі.
- Якщо PROMPT.md уже існує — спершу питає, тоді перезаписує.

## Anti-patterns

- **Не вигадуй DoD-пунктів** — чого нема у story, того нема й у PROMPT.md.
- **Не накопичуй контекст у PROMPT.md** — він тонкий; усе, що росте, тримай у
  `CLAUDE.md` і story-файлах, PROMPT.md лише посилається.
- **Не мовчазно перезаписуй** існуючий PROMPT.md — питай дозвіл.
