# CLAUDE.md · TDD discipline demo (Lecture 7.7)

Мінімальний контекст проекту для TDD-демо (SM-2 spaced repetition).

## Стек

- Python 3.12, pytest 8.x, hypothesis 6.x (property-based testing), mutmut 2.x (mutation testing)
- Source: `src/sm2.py` — pure-function module, без I/O і БД
- Tests: `tests/test_sm2.py` (example-based), `tests/test_sm2_properties.py` (PBT)

## Тестовий контракт

- **Test command**: `pytest -q` (або `make test`).
- **Watch-mode**: `make test-fast` — re-run on file change.
- **Coverage**: `make coverage` — coverage report.
- **Mutation**: `make mutation` — запускає mutmut проти `src/sm2.py`, рапортує killed/survived.
- AC живуть у `tasks/story-24-sm2.md` — interface, GWT, edge cases.

## Конвенції

- **Pure functions** — `sm2_next(card, grade) -> card` без mutation вхідних аргументів. Усе чисте, нема глобального стану.
- **Test-first** — тести існують ДО реалізації. Файл `src/sm2.py` починається з `NotImplementedError`.
- **3 atomic commits per RGR cycle**:
  - `test(sm2): ...` — failing tests committed first.
  - `feat(sm2): ...` — minimal implementation that turns tests green.
  - `refactor(sm2): ...` — cleanup, tests stay green.
- **PBT як safety net** — Hypothesis генерує edge cases, які example-based тести можуть пропустити (наприклад, грейд на межі 2/3, дуже високі repetitions).

## Не робити

- **Не міняти `tests/`** після фази RED. Refactorer і implementer мають read-only доступ до тестів.
- **Не вгадувати «магічні константи»** в реалізації — усі числа (1.3, 2.5, 0.08, 0.02) ідуть зі specifікації SM-2 у `tasks/story-24-sm2.md`.
- **Не комітити** `.mutmut-cache`, `.venv/`, `__pycache__/`, `.coverage`.

## Domain glossary

- **SM-2** — SuperMemo 2 algorithm. Класичний алгоритм spaced repetition від Wozniak (1985), використовується в Anki, Mnemosyne, SuperMemo.
- **Card** — стан повторення для конкретного слова: dict з `repetitions` (скільки разів поспіль учень згадав), `ease_factor` (множник складності, default 2.5), `interval` (днів до наступного повтору).
- **Grade** — оцінка відповіді користувача, ціле число 0-5. 5 = "ідеально", 0 = "повністю забув". Поріг для "пройдено" — `grade >= 3`.
- **Ease factor** — як швидко інтервал росте. Базове значення 2.5. Не може опускатись нижче 1.3 (інакше інтервал ніколи не виросте).
