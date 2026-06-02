---
id: SNIP-5
epic: snippets-demo
project: snippets
wave: 1
priority: Must
estimate: 20m
status: todo
context_budget: ~1800 tokens
files_touched: [src/snippets/export.py]
blocks: []
blocked_by: []
created: 2026-06-02
---

# SNIP-5 · Експорт сніпета у Markdown

**Epic:** snippets-demo (abstract substrate)
**Priority:** Must
**Estimate:** 20m
**Wave:** 1

Реалізувати чисту функцію у `src/snippets/export.py`: `to_markdown`
(відрендерити сніпет у секцію Markdown). Зараз - заглушка з
`NotImplementedError`, тести наперед написані й червоні. Це підкладка для
демонстрації паралельного fan-out у dynamic workflow, а не частина продукту.

## Незалежність

- **Пише тільки в:** `src/snippets/export.py`.
- **Читає (read-only):** `models.Snippet` - вже працює.
- **Не торкається:** `search.py`, `dedupe.py` - це паралельні сторіс SNIP-3/SNIP-4.
- **Чому безпечно паралелити:** жоден інший агент не пише у `export.py`.

## Interface (вже у репо як заглушка)

```python
def to_markdown(snippet: Snippet) -> str: ...
```

## Контракт

Рядки розділені `\n`, рівно у такому порядку:

```
## {title}
```{language}
{body}
```
Теги: tag1, tag2
```

1. Перший рядок - заголовок другого рівня з `title`.
2. Далі огороджений блок коду (fenced code block): рядок з мовою `language`,
   рядок з `body`, рядок-огорожа.
3. Останній рядок - `Теги: ` + теги через `, `. Якщо тегів немає - `Теги: -`.

## Acceptance criteria (GWT)

- [ ] **AC-snip5-1 (базова структура):** Given `Snippet(title="Hi", body="print(1)", language="python", tags=["py"])`, when `to_markdown(...)`, then `"## Hi\n```python\nprint(1)\n```\nТеги: py"`.
- [ ] **AC-snip5-2 (кілька тегів через кому):** Given `tags=["a","b","c"]`, when `to_markdown(...)`, then останній рядок `"Теги: a, b, c"`.
- [ ] **AC-snip5-3 (без тегів - дефіс):** Given `tags=[]`, when `to_markdown(...)`, then останній рядок `"Теги: -"`.
- [ ] **AC-snip5-4 (перший рядок - h2):** Given будь-який сніпет з `title="Async"`, when `to_markdown(...)`, then перший рядок `"## Async"`.
- [ ] **AC-snip5-5 (мова в огорожі):** Given `language="sql"`, when `to_markdown(...)`, then другий рядок `"```sql"`, а рядок-огорожа закриває блок.

## Checklist (atomic steps)

1. Реалізувати `to_markdown` за форматом контракту (`"\n".join([...])`).
2. Окремо обробити порожні теги → `Теги: -`.
3. `pytest tests/test_export.py -q` - має бути зелений (тести вже існують).
4. Не чіпати `tests/` - це контракт. Не чіпати `search.py`/`dedupe.py`.

## Definition of Done

- [ ] `pytest tests/test_export.py -q` зелений (`pytest` виходить з кодом 0).
- [ ] `tests/` не змінювалися (`git diff -- tests/` пустий).
- [ ] Змінено рівно один файл: `src/snippets/export.py`.
- [ ] Tracker оновлено: `status: done`.
