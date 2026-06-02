---
id: SNIP-1
project: snippets-seed
module: store.py
recommended_pattern: ralph-loop
lesson: "7.2"
status: todo
blocks: []
blocked_by: []
---

# SNIP-1 · SnippetStore (in-memory сховище)

Реалізувати `SnippetStore` у `src/snippets/store.py` - просте сховище сніпетів
у пам'яті. Маленька замкнена задача з бінарним критерієм «готово»
(`pytest -q` зелений) - канонічна підкладка для **одного циклу Ralph loop**.

## Інтерфейс

```python
class SnippetStore:
    def add(self, s: Snippet) -> str: ...
    def get(self, id: str) -> Snippet | None: ...
    def all(self) -> list[Snippet]: ...
```

## Acceptance criteria (GWT)

**AC-1 · Порожній id → новий uuid**
- **Given** сніпет `Snippet(id="", title="t", body="b")`.
- **When** викликаємо `store.add(s)`.
- **Then** повертається непорожній id, і `store.get(<цей id>)` повертає той самий сніпет.

**AC-2 · Явний id зберігається**
- **Given** сніпет `Snippet(id="fixed", title="t", body="b")`.
- **When** викликаємо `store.add(s)`.
- **Then** повертається `"fixed"`, і `store.get("fixed")` повертає сніпет.

**AC-3 · Відсутній id → None**
- **Given** порожнє сховище.
- **When** викликаємо `store.get("nope")`.
- **Then** повертається `None`.

**AC-4 · all() повертає всі додані**
- **Given** додано два сніпети з id `"a"` і `"b"`.
- **When** викликаємо `store.all()`.
- **Then** результат містить рівно сніпети з id `{"a", "b"}`.

## Atomic checklist

1. Замінити STUB у `src/snippets/store.py` робочою реалізацією
   (внутрішнє сховище - `dict[str, Snippet]`).
2. У `add`: якщо `s.id` порожній - призначити `uuid4().hex`, записати назад у `s.id`,
   зберегти, повернути фінальний id.
3. Запустити `pytest -q tests/test_store.py` - має бути зелений (тести вже існують).

## DoD

- `pytest -q tests/test_store.py` зелений (усі кейси AC-1…AC-4).
- Atomic commit `feat: in-memory SnippetStore`.
- Tracker оновлено: SNIP-1 `status: done`.
