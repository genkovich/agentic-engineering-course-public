# tasks/tracker.md · snippets seed backlog (Lecture 7.1)

П'ять stories домену `snippets`. Кожна закріплена за рекомендованим патерном
виконання з Module 7 - це і є мапа уроку 7.1 у дії: дивишся на форму задачі,
береш патерн. SNIP-1 (`models`) уже WORKING; решта модулів - STUB, тож
`make verify` червоний на чистому checkout.

| Story | Модуль | Рекомендований патерн | Урок | Status | Blocked by | Паралельність |
|---|---|---|---|---|---|---|
| SNIP-1 | `store.py` | Ralph loop | 7.2 | todo | none | - |
| SNIP-2 | `tags.py` | /goal | 7.3 | todo | none | - |
| SNIP-3 | `search.py` | dynamic workflow | 7.4 | todo | SNIP-2 | паралельна до SNIP-4 |
| SNIP-4 | `dedupe.py` | dynamic workflow | 7.4 | todo | none | паралельна до SNIP-3 |
| SNIP-5 | `export.py` | TDD | 7.7 | todo | none | - |

SNIP-3 і SNIP-4 - незалежні підзадачі в **різних файлах** (`search.py` vs
`dedupe.py`), тому йдуть паралельно. SNIP-3 м'яко спирається на нормалізацію
тегів із SNIP-2 (`search_by_tag` звіряє нормалізовану форму), тож позначена
`blocked_by: SNIP-2`; SNIP-4 ні від чого не залежить.

## Чому саме ці патерни

- **SNIP-1 store → Ralph loop.** Бінарний критерій «готово» (`pytest` зелений),
  маленька замкнена задача. Канонічна підкладка для одного циклу Ralph.
- **SNIP-2 tags → /goal.** Чіткий контракт двох функцій; даємо агенту фініш-ціль,
  він сам доводить до зеленого під вбудованими точками контролю команди `/goal` -
  без саморобного `while`-циклу і sentinel-файлу.
- **SNIP-3 search + SNIP-4 dedupe → dynamic workflow.** Дві незалежні підзадачі в
  різних файлах. Динамічний workflow веде їх паралельними гілками і зводить разом.
- **SNIP-5 export → TDD.** Точний формат виводу (Markdown-секція з огородженим
  блоком коду) - критична логіка з вузьким контрактом. Тест-першим фіксуємо
  формат до реалізації.

## Status legend

- `todo` - у роботі ще не починалась.
- `wip` - взято у роботу.
- `done` - закрита, commit з реалізацією є у `git log`, `make verify` по цьому модулю зелений.

## Notes

- **7.5 (background execution) і 7.6 (feedback loops) - це осі ЯК/ДЕ** виконується й
  перевіряється робота, а **не окремі stories**. Будь-яку з SNIP-1…SNIP-5 можна
  гнати фоново (поза чатом, за розкладом) і обгорнути feedback loop-ом (довести
  «готово» перевіркою, а не лише запуском). Тому їх нема в таблиці як рядків -
  вони накладаються на будь-який рядок.
- Детальні story-файли (frontmatter + GWT + DoD) є для SNIP-1 і SNIP-2
  (`story-snip-1.md`, `story-snip-2.md`). SNIP-3/4/5 описані one-liner-ами тут;
  контракт кожного - у docstring відповідного STUB-модуля та в його тестах.
- SNIP-3: реалізувати `search_by_tag` / `search_by_text` у `src/snippets/search.py`
  → `tests/test_search.py` зелений. Патерн: dynamic workflow (паралельно з SNIP-4).
- SNIP-4: реалізувати `find_duplicates` у `src/snippets/dedupe.py` → `tests/test_dedupe.py`
  зелений. Патерн: dynamic workflow (паралельно з SNIP-3).
- SNIP-5: реалізувати `to_markdown` у `src/snippets/export.py` → `tests/test_export.py`
  зелений. Патерн: TDD (тести вже написані - це і є RED-фаза).
