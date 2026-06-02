---
id: SNIP-2
project: snippets-seed
module: tags.py
recommended_pattern: goal
lesson: "7.3"
status: todo
blocks: [SNIP-3]
blocked_by: []
---

# SNIP-2 · Нормалізація тегів і підрахунок

Реалізувати `normalize_tag` і `count_by_tag` у `src/snippets/tags.py`. Контракт
чіткий, фініш однозначний (`pytest` зелений) - даємо агенту ціль і він **сам**
доводить задачу під вбудованими точками контролю команди `/goal`, без саморобного
циклу й sentinel-файлу. Це рекомендований патерн для **7.3**.

## Інтерфейс

```python
def normalize_tag(raw: str) -> str: ...
def count_by_tag(snippets: list[Snippet]) -> dict[str, int]: ...
```

## Acceptance criteria (GWT)

**AC-1 · Нижній регістр + обрізання країв**
- **Given** рядок `"  Python  "`.
- **When** `normalize_tag("  Python  ")`.
- **Then** повертається `"python"`.

**AC-2 · Схлопування не-алфанумерик послідовностей**
- **Given** рядок `"Python 3.12"`.
- **When** `normalize_tag("Python 3.12")`.
- **Then** повертається `"python-3-12"` (пробіл і крапка → один дефіс кожна послідовність).

**AC-3 · Обрізання дефісів з країв**
- **Given** рядок `"--Go--"`.
- **When** `normalize_tag("--Go--")`.
- **Then** повертається `"go"`.

**AC-4 · Підрахунок за нормалізованою формою**
- **Given** два сніпети з тегами `["Python", "go"]` і `["python", "  GO  "]`.
- **When** `count_by_tag(snippets)`.
- **Then** повертається `{"python": 2, "go": 2}` (різні написання тега - один ключ).

## Atomic checklist

1. Замінити STUB у `src/snippets/tags.py` робочою реалізацією обох функцій.
2. `normalize_tag`: strip → lower → послідовність не-алфанумерик → один `-` →
   обрізати провідні/завершальні `-`.
3. `count_by_tag`: для кожного тега кожного сніпета взяти `normalize_tag`,
   збільшити лічильник у словнику.
4. Запустити `pytest -q tests/test_tags.py` - має бути зелений (тести вже існують).

## DoD

- `pytest -q tests/test_tags.py` зелений (усі кейси AC-1…AC-4).
- Atomic commit `feat: tag normalization and count_by_tag`.
- Tracker оновлено: SNIP-2 `status: done`.

> Примітка про залежність: SNIP-3 (`search_by_tag`) звіряє теги за нормалізованою
> формою, тож спирається на `normalize_tag` із цієї story (`blocks: [SNIP-3]`).
