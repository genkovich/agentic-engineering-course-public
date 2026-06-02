---
id: SNIP-2
epic: snippets-demo
project: snippets
wave: 1
priority: Must
estimate: 30m
status: todo
context_budget: ~2500 tokens
blocks: []
blocked_by: [SNIP-1]
created: 2026-06-02
---

# SNIP-2 · Нормалізація тегів + count_by_tag

**Epic:** snippets-demo (abstract substrate)
**Priority:** Must
**Estimate:** 30m
**Wave:** 1

Реалізувати дві чисті функції у `src/snippets/tags.py`: `normalize_tag` (звести
сирий тег до канонічної форми) і `count_by_tag` (порахувати сніпети за
нормалізованим тегом). Зараз обидві - заглушка з `NotImplementedError`, тести
наперед написані й червоні. Це підкладка для демонстрації `/goal` з вимірюваною
умовою завершення, а не частина якогось продукту.

## Місце в послідовності

- **Блокується:** SNIP-1 (модель `Snippet` + `SnippetStore` - вже готові).
- **Блокує:** нічого в межах демо.
- **Чому ця задача:** єдина у репо, де результат завершення вимірюється
  однозначно - `pytest tests/test_tags.py` зелений. Саме такий вимірюваний
  кінцевий стан і потрібен `/goal`, щоб умову не можна було закрити прозою.

## Interface (вже у репо як заглушка)

```python
def normalize_tag(raw: str) -> str: ...
def count_by_tag(snippets: list[Snippet]) -> dict[str, int]: ...
```

## Контракт normalize_tag

1. Прибрати пробіли з країв.
2. Перевести у нижній регістр.
3. Кожен непорожній прогін НЕ-алфанумерних символів → один `-`.
4. Прибрати `-` з початку і кінця.

## Acceptance criteria (GWT)

- [ ] **AC-snip2-1 (базова нормалізація):** Given `"  Hello World "`, when `normalize_tag(...)`, then `"hello-world"` (strip, нижній регістр, пробіл → дефіс).
- [ ] **AC-snip2-2 (схлопування роздільників):** Given `"Python,   3.12!!!"`, when `normalize_tag(...)`, then `"python-3-12"` (кратні не-алфанумерні символи → один дефіс).
- [ ] **AC-snip2-3 (обрізання країв):** Given `"--Hi--"` і `"C++"`, when `normalize_tag(...)`, then `"hi"` і `"c"` (без провідних/завершальних дефісів).
- [ ] **AC-snip2-4 (ідемпотентність):** Given вже нормалізований тег, when `normalize_tag(...)` повторно, then результат не змінюється.
- [ ] **AC-snip2-5 (count_by_tag групує):** Given сніпети з тегами `["Python", "python ", "PYTHON", "go"]` по об'єктах, when `count_by_tag(...)`, then `{"python": 3, "go": 1}`.
- [ ] **AC-snip2-6 (порожній тег відкидається):** Given сніпет з тегом `"!!!"` (нормалізується в порожній рядок), when `count_by_tag(...)`, then цей тег у результат не потрапляє.

## Checklist (atomic steps)

1. Реалізувати `normalize_tag` за чотирма правилами контракту (stdlib, без regex-залежностей поза `re`).
2. Реалізувати `count_by_tag`: прогнати кожен тег кожного сніпета через `normalize_tag`, відкинути порожні, порахувати частоту.
3. Запустити `pytest tests/test_tags.py -q` - має бути зелений (тести вже існують).
4. Не чіпати `tests/` - це контракт.

## Definition of Done

- [ ] `pytest tests/test_tags.py -q` зелений (усі 7 кейсів проходять, `pytest` виходить з кодом 0).
- [ ] `tests/` не змінювалися (`git diff -- tests/` пустий).
- [ ] Atomic commit `feat: tag normalization + count_by_tag`.
- [ ] Tracker оновлено: `status: done`.
