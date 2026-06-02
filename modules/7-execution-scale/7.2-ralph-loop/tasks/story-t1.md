---
id: T-1
project: abstract-demo
wave: 1
status: todo
estimate: 10m
blocks: []
blocked_by: []
---

# T-1 · slugify(text) helper

Реалізувати чисту функцію `slugify`, яка перетворює довільний рядок на URL-slug.
Задача навмисне абстрактна (kata-рівня) — це підкладка для демонстрації Ralph loop,
а не частина якогось продукту.

## Acceptance criteria (GWT)

**AC-1 · Базовий slug**
- **Given** рядок `"Hello World"`.
- **When** викликаємо `slugify("Hello World")`.
- **Then** повертається `"hello-world"` (нижній регістр, пробіл → дефіс).

**AC-2 · Пунктуація і повтори**
- **Given** рядок `"Hello,   World!!!"`.
- **When** викликаємо `slugify(...)`.
- **Then** повертається `"hello-world"` (пунктуація прибрана, кратні роздільники
  схлопнуті в один дефіс).

**AC-3 · Обрізання країв**
- **Given** рядок `"--Hi--"`.
- **When** викликаємо `slugify(...)`.
- **Then** повертається `"hi"` (без провідних/завершальних дефісів).

## Atomic checklist

1. Створити `app/text_utils.py` з функцією `slugify(text: str) -> str`.
2. Реалізувати правила: lower-case, не-алфанумерик → дефіс, схлопнути кратні
   дефіси, обрізати дефіси з країв.
3. Запустити `pytest -q` — має бути зелений (тест уже існує в `tests/`).

## DoD

- `pytest -q` зелений (усі кейси в `tests/test_slugify.py`).
- Atomic commit `feat: slugify text helper`.
- Tracker оновлено: `status: done`.
