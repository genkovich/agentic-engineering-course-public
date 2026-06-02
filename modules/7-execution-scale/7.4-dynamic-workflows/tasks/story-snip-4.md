---
id: SNIP-4
epic: snippets-demo
project: snippets
wave: 1
priority: Must
estimate: 20m
status: todo
context_budget: ~1800 tokens
files_touched: [src/snippets/dedupe.py]
blocks: []
blocked_by: []
created: 2026-06-02
---

# SNIP-4 · Пошук дублікатів за вмістом

**Epic:** snippets-demo (abstract substrate)
**Priority:** Must
**Estimate:** 20m
**Wave:** 1

Реалізувати чисту функцію у `src/snippets/dedupe.py`: `find_duplicates`
(згрупувати сніпети з ідентичним вмістом). Зараз - заглушка з
`NotImplementedError`, тести наперед написані й червоні. Це підкладка для
демонстрації паралельного fan-out у dynamic workflow, а не частина продукту.

## Незалежність

- **Пише тільки в:** `src/snippets/dedupe.py`.
- **Читає (read-only):** `models.Snippet` - вже працює.
- **Не торкається:** `search.py`, `export.py` - це паралельні сторіс SNIP-3/SNIP-5.
- **Чому безпечно паралелити:** жоден інший агент не пише у `dedupe.py`.

## Interface (вже у репо як заглушка)

```python
def find_duplicates(snippets: list[Snippet]) -> list[list[str]]: ...
```

## Контракт

1. Два сніпети - дублікати, якщо їхній `body` збігається після `body.strip()`.
2. Повертає список груп; кожна група - список `id` сніпетів зі спільним вмістом.
3. До результату потрапляють лише групи розміром >= 2 (одинаки не дублікати).
4. Порожній вхід - порожній результат.

## Acceptance criteria (GWT)

- [ ] **AC-snip4-1 (групує однакові body):** Given сніпети `a`,`b` з однаковим `body` і `c` з іншим, when `find_duplicates(...)`, then `[["a", "b"]]`.
- [ ] **AC-snip4-2 (strip перед звіркою):** Given `body="  same  "` і `body="same"`, when `find_duplicates(...)`, then вони в одній групі.
- [ ] **AC-snip4-3 (одинаки відкидаються):** Given усі `body` різні, when `find_duplicates(...)`, then `[]`.
- [ ] **AC-snip4-4 (порожній вхід):** Given `[]`, when `find_duplicates([])`, then `[]`.
- [ ] **AC-snip4-5 (група з трьох):** Given три сніпети з однаковим `body`, when `find_duplicates(...)`, then одна група з трьох `id`.

## Checklist (atomic steps)

1. Реалізувати `find_duplicates`: ключ групи - `body.strip()`, зібрати `id` у групи.
2. Відкинути групи розміром < 2.
3. `pytest tests/test_dedupe.py -q` - має бути зелений (тести вже існують).
4. Не чіпати `tests/` - це контракт. Не чіпати `search.py`/`export.py`.

## Definition of Done

- [ ] `pytest tests/test_dedupe.py -q` зелений (`pytest` виходить з кодом 0).
- [ ] `tests/` не змінювалися (`git diff -- tests/` пустий).
- [ ] Змінено рівно один файл: `src/snippets/dedupe.py`.
- [ ] Tracker оновлено: `status: done`.
