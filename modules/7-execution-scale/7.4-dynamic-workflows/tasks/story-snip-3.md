---
id: SNIP-3
epic: snippets-demo
project: snippets
wave: 1
priority: Must
estimate: 25m
status: todo
context_budget: ~2000 tokens
files_touched: [src/snippets/search.py]
blocks: []
blocked_by: []
created: 2026-06-02
---

# SNIP-3 · Пошук за тегом і за текстом

**Epic:** snippets-demo (abstract substrate)
**Priority:** Must
**Estimate:** 25m
**Wave:** 1

Реалізувати дві чисті функції у `src/snippets/search.py`: `search_by_tag`
(фільтр за нормалізованим тегом) і `search_by_text` (регістронезалежний пошук
підрядка). Зараз обидві - заглушка з `NotImplementedError`, тести наперед
написані й червоні. Це підкладка для демонстрації паралельного fan-out у
dynamic workflow, а не частина якогось продукту.

## Незалежність

- **Пише тільки в:** `src/snippets/search.py`.
- **Читає (read-only):** `models.Snippet`, `tags.normalize_tag` - вже працюють.
- **Не торкається:** `dedupe.py`, `export.py` - це паралельні сторіс SNIP-4/SNIP-5.
- **Чому безпечно паралелити:** жоден інший агент не пише у `search.py`, тож
  гонки за запис немає.

## Interface (вже у репо як заглушка)

```python
def search_by_tag(snippets: list[Snippet], tag: str) -> list[Snippet]: ...
def search_by_text(snippets: list[Snippet], q: str) -> list[Snippet]: ...
```

## Контракт

**search_by_tag**
1. Нормалізувати шуканий `tag` через `normalize_tag`.
2. Сніпет потрапляє у результат, якщо хоч один його тег після `normalize_tag`
   дорівнює нормалізованому шуканому.
3. Порядок результату - як у вхідному списку.

**search_by_text**
1. Звірка регістронезалежна.
2. Сніпет потрапляє у результат, якщо `q` є підрядком `title` АБО `body`.
3. Порожній `q` - підрядок будь-чого, тож повертає всі сніпети.
4. Порядок результату - як у вхідному списку.

## Acceptance criteria (GWT)

- [ ] **AC-snip3-1 (тег нормалізується з обох боків):** Given сніпети з тегами `["Python"]` і `["python "]`, when `search_by_tag(s, "  Python ")`, then обидва у результаті.
- [ ] **AC-snip3-2 (немає збігу - порожньо):** Given жоден сніпет не має тегу `rust`, when `search_by_tag(s, "rust")`, then `[]`.
- [ ] **AC-snip3-3 (текст без регістру по title і body):** Given сніпет з title `"Async in Python"`, when `search_by_text(s, "ASYNC")`, then він у результаті.
- [ ] **AC-snip3-4 (текст матчить body, не лише title):** Given `body` містить `"await"`, а title - ні, when `search_by_text(s, "await")`, then сніпет у результаті.
- [ ] **AC-snip3-5 (порожній запит - усі):** Given будь-які сніпети, when `search_by_text(s, "")`, then усі у результаті у вхідному порядку.

## Checklist (atomic steps)

1. Реалізувати `search_by_tag` за контрактом (через `normalize_tag`).
2. Реалізувати `search_by_text` за контрактом (case-insensitive substring).
3. `pytest tests/test_search.py -q` - має бути зелений (тести вже існують).
4. Не чіпати `tests/` - це контракт. Не чіпати `dedupe.py`/`export.py`.

## Definition of Done

- [ ] `pytest tests/test_search.py -q` зелений (`pytest` виходить з кодом 0).
- [ ] `tests/` не змінювалися (`git diff -- tests/` пустий).
- [ ] Змінено рівно один файл: `src/snippets/search.py`.
- [ ] Tracker оновлено: `status: done`.
