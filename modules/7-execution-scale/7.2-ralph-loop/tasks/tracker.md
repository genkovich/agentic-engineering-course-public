# tasks/tracker.md (abstract demo subset)

Один story для скринкаст-демо лекції 7.2. Ralph читає цей файл і бере першу story
у статусі `todo` без блокерів.

| Story | Wave | Status | Blocked by | Estimate | DoD |
|---|---|---|---|---|---|
| T-1 | 1 | done | — | 10m | `pytest -q` зелений + tracker оновлено |

## Status legend

- `todo` — у роботі ще не починалась.
- `wip` — взято у роботу.
- `done` — закрита, commit з тестом є у `git log`.

## Notes

- Single-story tracker навмисне мінімалістичний — фокус на механіці циклу.
- Реальний M6 tracker (8 stories у 4 waves) — у beer-lms:
  `~/sources/beer-lms/docs/features/course-lesson-mvp/tasks/tracker.md`. Як навести
  той самий harness на нього — див. секцію «beer-lms track» у README.
