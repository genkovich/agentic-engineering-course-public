---
id: S-24
project: snippets-demo
wave: 2
priority: P1
estimate: 1.5h
blocks: []
blocked_by: [S-23]
status: todo
context_budget: 4000
created: 2026-05-26
---

# S-24 · SM-2 spaced repetition algorithm

Реалізувати pure-function `sm2_next(card, grade)`, що рахує наступний стан картки за алгоритмом SuperMemo-2 (SM-2). Це core scheduler для spaced repetition — після кожної відповіді користувача система викликає цю функцію, щоб дізнатись, через скільки днів показати слово знову.

## Linked artifacts

- External reference: SuperMemo SM-2 (Wozniak, 1985)

## Interface

```python
def sm2_next(card: dict, grade: int) -> dict:
    """Compute the next SM-2 card state given a recall grade.

    Args:
        card:  {"repetitions": int, "ease_factor": float, "interval": int}
               A new card starts at {"repetitions": 0, "ease_factor": 2.5, "interval": 0}.
        grade: int in [0, 5]. 5 = perfect recall, 0 = total blackout.
               grade >= 3 is "pass"; grade < 3 is "fail".

    Returns:
        Updated card dict with new repetitions, ease_factor, interval (days).
    """
```

## SM-2 rules (specification)

**On failure (grade < 3):**
- `repetitions := 0`
- `interval := 1` (review again tomorrow)
- `ease_factor` unchanged

**On success (grade >= 3):**
- `repetitions := repetitions + 1`
- `interval :=`
  - `1` if `repetitions == 1`
  - `6` if `repetitions == 2`
  - `round(previous_interval * ease_factor)` otherwise
- `ease_factor := max(1.3, ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)))`

**Initial state** of a brand-new card:
- `{"repetitions": 0, "ease_factor": 2.5, "interval": 0}`

## Acceptance criteria (GWT)

**AC-1 · New card, perfect recall**

- **Given** new card `{"repetitions": 0, "ease_factor": 2.5, "interval": 0}`.
- **When** `sm2_next(card, grade=5)`.
- **Then** result is `{"repetitions": 1, "ease_factor": 2.6, "interval": 1}`.

**AC-2 · New card, failure**

- **Given** new card `{"repetitions": 0, "ease_factor": 2.5, "interval": 0}`.
- **When** `sm2_next(card, grade=0)`.
- **Then** result is `{"repetitions": 0, "ease_factor": 2.5, "interval": 1}`.

**AC-3 · Second successful repetition**

- **Given** card `{"repetitions": 1, "ease_factor": 2.6, "interval": 1}`.
- **When** `sm2_next(card, grade=4)`.
- **Then** `repetitions == 2` and `interval == 6` (fixed second-step interval).

**AC-4 · Third successful repetition uses ease_factor**

- **Given** card `{"repetitions": 2, "ease_factor": 2.5, "interval": 6}`.
- **When** `sm2_next(card, grade=3)`.
- **Then** `repetitions == 3`, `ease_factor == 2.36`, `interval == 14` (= round(6 * 2.36)).

**AC-5 · Failure after streak resets repetitions**

- **Given** card with long streak, e.g. `{"repetitions": 7, "ease_factor": 2.8, "interval": 90}`.
- **When** `sm2_next(card, grade=2)`.
- **Then** `repetitions == 0`, `interval == 1`, `ease_factor == 2.8` (unchanged on failure).

**AC-6 · Ease factor floor at 1.3**

- **Given** card with ease_factor near the floor, e.g. `{"repetitions": 5, "ease_factor": 1.35, "interval": 30}`.
- **When** `sm2_next(card, grade=3)` (raw new ef would be 1.21).
- **Then** `ease_factor == 1.3` (clamped to the floor, never below).

**AC-7 · Perfect recall grows interval monotonically**

- **Given** new card.
- **When** we apply `sm2_next(card, grade=5)` six times in a row.
- **Then** `intervals[0] == 1`, `intervals[1] == 6`, and from index 2 onward `intervals[i] > intervals[i-1]` (strict monotonic growth).

**AC-8 · Grade boundary (3 passes, 2 fails)**

- **Given** card `{"repetitions": 4, "ease_factor": 2.5, "interval": 20}`.
- **When** we call `sm2_next` with grade=3 vs grade=2 separately.
- **Then** grade=3 → `repetitions == 5`; grade=2 → `repetitions == 0` and `interval == 1`.

## Property-based invariants (for `tests/test_sm2_properties.py`)

**P-1** · For any valid card and any `grade in [3, 5]`: `result["interval"] >= 1`.

**P-2** · For any valid card and any `grade in [0, 2]`: `result["repetitions"] == 0`.

**P-3** · For any valid card and any `grade in [0, 5]`: `result["ease_factor"] >= 1.3`.

## Atomic checklist (per RGR cycle)

1. **RED**: написати failing tests у `tests/test_sm2.py` (8 кейсів) і `tests/test_sm2_properties.py` (3 інваріанти). Запустити `pytest` — переконатись що ВСІ ці нові тести падають (NotImplementedError або AssertionError). Commit `test(sm2): add failing tests per AC`.
2. **GREEN**: написати мінімальну реалізацію `sm2_next` у `src/sm2.py`. Ганяти `pytest` доки всі тести зеленими. Commit `feat(sm2): implement to make tests pass`.
3. **REFACTOR**: витягнути 2 helpers (`_apply_failure(card)` і `_apply_success(card, grade)`), кожен повертає новий card-dict. Після КОЖНОЇ зміни прогнати `pytest` — має лишатись зеленим. Commit `refactor(sm2): extract helpers`.

## DoD

- AC-1...AC-8 покриті example-based тестами у `tests/test_sm2.py`.
- P-1...P-3 покриті PBT-тестами у `tests/test_sm2_properties.py`.
- `pytest tests/` зелений після фази GREEN.
- `pytest tests/` лишається зеленим після фази REFACTOR.
- 3 atomic commits з префіксами `test(sm2):`, `feat(sm2):`, `refactor(sm2):`.
- `git diff HEAD~2 HEAD -- tests/` пустий (тести не мінялись після фази RED).
- Optional sanity check: `make mutation` показує 0 survived mutants.
