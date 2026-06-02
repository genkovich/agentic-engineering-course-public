# PROMPT.md · TDD discipline demo (Lecture 7.7, story S-24 SM-2)

## Контекст

Ти працюєш у мінімальному snippets-демо — pure-function модуль для інтервального повторення слів (SM-2). Стек: Python 3.12 + pytest + hypothesis + mutmut. Code під test — у `src/sm2.py`. Тести — у `tests/`.

Прочитай:

- `CLAUDE.md` у корені — конвенції проекту, тестовий контракт, заборони.
- `tasks/story-24-sm2.md` — повний контракт story: interface, AC (Given/When/Then), правила SM-2 алгоритму, edge cases.

## Завдання

Реалізувати story `S-24 · SM-2 algorithm` у статусі `todo`. Цикл — Red → Green → Refactor через 3 sub-agents:

1. **RED** (skill `/tdd-test-writer`): прочитати AC, написати failing tests (`tests/test_sm2.py` + `tests/test_sm2_properties.py`), запустити `pytest` → confirm red, commit `test(sm2): add failing tests per AC`, СТОП.
2. **GREEN** (skill `/tdd-implementer`): прочитати лише `src/sm2.py` interface + `tests/`, написати мінімальну реалізацію `sm2_next`, ганяти `pytest` до зеленого, commit `feat(sm2): implement to make tests pass`.
3. **REFACTOR** (skill `/tdd-refactorer`): зелений pytest + сирий код → витягнути helpers (`_apply_failure`, `_apply_success`), після КОЖНОЇ зміни ганяти `pytest`, тести лишаються зеленими, commit `refactor(sm2): extract helpers`.

Дисципліна:

- 3 atomic commits, у цьому порядку (`test:` → `feat:` → `refactor:`).
- Між фазами не накопичуй контексту — кожен агент стартує з чистого slate, бачить тільки те, що йому дозволено.

## DoD

- `pytest tests/` зелений після фази GREEN.
- `pytest tests/` лишається зеленим після фази REFACTOR.
- 3 atomic commits у `git log` з префіксами `test(sm2):`, `feat(sm2):`, `refactor(sm2):`.
- `git diff HEAD~2 HEAD -- tests/` показує пусто (тести не мінялись після фази RED).

## Не роби

- Не міняй тести після фази RED. Implementer і refactorer мають read-only доступ до `tests/`.
- Не вигадуй магічних чисел в реалізації — усі константи (1.3, 2.5, 0.08, 0.02) ідуть зі специфікації SM-2 у `tasks/story-24-sm2.md`.
- Не запускай `--dangerously-skip-permissions`. Permission-mode `acceptEdits` — максимум.
- Не змінюй `CLAUDE.md`, `tasks/story-24-sm2.md` — це contracts, зміни в них = окрема story.
