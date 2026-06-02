# 7.1 · Execution map - demo (seed-проєкт + мапа патернів)

Demo-проект для лекції **7.1 Execution map** (Module 7 · Execution & Scale).
Це **seed-домен** усього модуля: маленький менеджер код-сніпетів, на якому
наступні лекції показують свій патерн виконання. І це **мапа**: яка форма задачі
→ який патерн.

## Що показує

- Наскрізний приклад модуля - домен `snippets` (один WORKING-модуль + п'ять STUB-ів).
- Мапу «яка задача → який патерн виконання»: Ralph (7.2), /goal (7.3),
  dynamic workflow (7.4), background (7.5), feedback loops (7.6), TDD (7.7).
- Як читати власний backlog через цю мапу: дивишся на форму story - береш патерн.
- Що 7.5 і 7.6 - це **осі** (ЯК і ДЕ виконується й перевіряється робота), а не
  окремі stories: вони накладаються на будь-який рядок tracker-а.
- Стартовий стан репо навмисне **RED**: п'ять модулів - стаби з `NotImplementedError`,
  тож `make verify` падає. Кожна наступна лекція «зеленить» свій модуль своїм патерном.

## Snippets - наскрізний приклад модуля

`snippets` - маленький менеджер код-сніпетів на чистій стандартній бібліотеці
Python 3.12 (без зовнішніх залежностей). Це **наскрізний приклад усіх runnable-частин**
Module 7: кожна лекція гонить свій патерн на цьому self-contained Python-домені - його
видно цілком, він запускається одним `pytest`, і його не треба нізвідки клонувати.

Домен - один пакет `src/snippets/` із шести модулів:

| Модуль | Що робить | Стан на checkout | Story | Патерн (лекція) |
|---|---|---|---|---|
| `models.py` | dataclass `Snippet` (id, title, body, language, tags) | **WORKING** | none | контракт для решти |
| `store.py` | `SnippetStore`: add / get / all (in-memory) | STUB | SNIP-1 | Ralph loop (7.2) |
| `tags.py` | `normalize_tag`, `count_by_tag` | STUB | SNIP-2 | /goal (7.3) |
| `search.py` | `search_by_tag`, `search_by_text` | STUB | SNIP-3 | dynamic workflow (7.4) |
| `dedupe.py` | `find_duplicates` (за `body.strip()`) | STUB | SNIP-4 | dynamic workflow (7.4) |
| `export.py` | `to_markdown` (Markdown-секція) | STUB | SNIP-5 | TDD (7.7) |

`models.py` робочий і служить контрактом; решта п'ять кидають `NotImplementedError` -
це і є RED-старт, який наступні лекції доводять до зеленого, кожна своїм патерном.

## Setup

```bash
cd modules/7-execution-scale/7.1-execution-map

make verify          # RED на чистому checkout: NotImplementedError у 5 стабах - це стартовий стан
```

`uv` підтягне `pytest` сам. Жодних бізнес-залежностей - тільки стандартна бібліотека.

## Як запустити

| Команда | Що робить |
|---|---|
| `make verify` | DoD-проба (`pytest -q`). Червоно на чистому checkout (NotImplementedError) - це стартовий стан. |
| `make map` | Друкує дерево рішень «яка задача → який патерн» (та сама мапа, що нижче). |
| `make clean` | Прибрати кеші (`.pytest_cache`, `__pycache__`). |
| `make help` | Список таргетів. |

## Мапа патернів

Дивишся на форму задачі - береш патерн. Те саме друкує `make map`:

| Форма задачі | Патерн | Лекція | Приклад на seed-домені |
|---|---|---|---|
| Бінарний так/ні критерій «готово», маленька замкнена задача | Ralph loop | 7.2 | SNIP-1 `store` |
| Автономний фініш без саморобної обв'язки (цикл/sentinel руками не пишемо) | /goal | 7.3 | SNIP-2 `tags` |
| Багато незалежних підзадач (різні файли, не блокують одна одну) | dynamic workflow | 7.4 | SNIP-3 `search` + SNIP-4 `dedupe` паралельно |
| Робота поза чатом / за розкладом (довгий прогін, AFK) | background execution | 7.5 | вісь ЯК/ДЕ, не окрема story |
| «Готово» треба довести (перевірка результату, а не лише запуск) | feedback loops | 7.6 | вісь ЯК/ДЕ, не окрема story |
| Критична логіка з точними правилами - тест-першим | TDD | 7.7 | SNIP-5 `export` |

**7.5 (background) і 7.6 (feedback) - це осі ЯК і ДЕ** виконується й перевіряється
робота, а не окремі рядки backlog-а. Будь-яку story (SNIP-1…SNIP-5) можна гнати
фоново і обгорнути feedback loop-ом. Тому вони не мають свого рядка в tracker-і -
вони накладаються на будь-який.

Повний backlog із цими мітками - у `tasks/tracker.md`; детальні story-файли (GWT + DoD) -
`tasks/story-snip-1.md` (Ralph) і `tasks/story-snip-2.md` (/goal).

## Очікуваний вивід

`make verify` на чистому checkout - **червоно**: усі тести впираються в стаби.

```
tests/test_dedupe.py F...
tests/test_export.py ...
tests/test_search.py ...
tests/test_store.py ...
tests/test_tags.py ...
E   NotImplementedError: SNIP-1: SnippetStore.add ще не реалізовано
...
=== N failed in ...s ===
```

Це **by design**: п'ять STUB-модулів кидають `NotImplementedError`, тож `pytest`
падає одразу на імпорт-виклику кожного. Зеленим конкретний модуль стає лише після
того, як відповідна лекція доведе свою story своїм патерном (SNIP-1 → Ralph, і т.д.).

## Як перенести у свій проєкт

1. **Промаркуй stories свого tracker-а рекомендованим патерном.** Додай колонку
   «Рекомендований патерн» (як у `tasks/tracker.md`) і проти кожної story постав
   Ralph / /goal / dynamic workflow / TDD - за формою задачі.
2. **Користуйся деревом рішень** (`make map` або таблиця вище): бінарний замкнений
   критерій → Ralph; автономний фініш без саморобної обв'язки → /goal; багато
   незалежних підзадач → dynamic workflow; робота поза чатом/за розкладом →
   background; «готово» треба довести → feedback loops; критична логіка тест-першим
   → TDD. background і feedback - осі поверх будь-якої story, не окремі рядки.

## Sources

- Module 7, Lecture 1 (`Execution map`) - конспект і повний `Sources.md` лекції.
