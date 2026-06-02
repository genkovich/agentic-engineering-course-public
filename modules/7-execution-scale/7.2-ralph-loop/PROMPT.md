# PROMPT.md · Ralph loop (abstract demo)

## Контекст

Ти працюєш у маленькому Python-проекті. Стек: Python 3.12 + pytest, без зовнішніх
залежностей у бізнес-коді. Код живе в `app/`, тести — у `tests/`.

Прочитай перед роботою:
- `CLAUDE.md` у корені — конвенції проекту.
- `tasks/tracker.md` — backlog, обери першу story у статусі `todo` без блокерів.
- Файл story з `tasks/` — повний контракт задачі: опис, acceptance criteria, checklist, DoD.

## Завдання

Реалізувати story у статусі `todo` з трекера. Подивись на існуючі файли в `app/` і
`tests/` як на reference, перш ніж писати свій код.

Дисципліна:
- Один atomic commit на одну закриту story (префікс `feat:`).
- Коли всі stories у трекері закриті — створи файл `DONE` у корені і завершуй.
- Якщо застряг (тест падає з причини, яку не можеш виправити за 3 ітерації) — додай
  рядок `BLOCKED: <причина>` у `tasks/tracker.md` і виходь.

## DoD

- `pytest -q` зелений.
- Story у `tasks/tracker.md` помічена `done`.
- Atomic commit з префіксом `feat:` для виконаної story.
- Коли всі stories `done` — у корені існує файл `DONE`.

## Не роби

- Не міняй тести у `tests/`. Якщо тест падає — фіксь код, не тест.
- Не запускай `--dangerously-skip-permissions`. Максимум — `acceptEdits`.
- Не змінюй `CLAUDE.md` і самі story-файли — це контракти.
