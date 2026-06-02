# tasks/tracker.md (snippets demo - independent wave)

Три сторіс для демо лекції 7.4. Усі три у статусі `todo`, без блокерів між
собою - їх можна доставити **паралельно**. Колонка «Files touched» доводить
головне: множини файлів не перетинаються, тож гонки за запис немає, і workflow
безпечно запускає по одному агенту на сторіс одночасно.

| Story | Wave | Status | Blocked by | Files touched | Test | DoD |
|---|---|---|---|---|---|---|
| SNIP-3 · search | 1 | todo | - | `src/snippets/search.py` | `tests/test_search.py` | `pytest tests/test_search.py -q` зелений |
| SNIP-4 · dedupe | 1 | todo | - | `src/snippets/dedupe.py` | `tests/test_dedupe.py` | `pytest tests/test_dedupe.py -q` зелений |
| SNIP-5 · export | 1 | todo | - | `src/snippets/export.py` | `tests/test_export.py` | `pytest tests/test_export.py -q` зелений |

## Чому це безпечний паралельний fan-out

- **Нуль перетину по файлах.** SNIP-3 пише тільки в `search.py`, SNIP-4 - тільки
  в `dedupe.py`, SNIP-5 - тільки в `export.py`. Перетин множин порожній.
- **Спільні залежності - read-only.** Усі три читають `models.Snippet`; SNIP-3 ще
  й `tags.normalize_tag`. Це залежності, які вже працюють, і їх ніхто не змінює.
- **Незалежність як передумова.** Це не «можна паралелити для швидкості», а
  «паралелити безпечно, бо немає спільного запису». Якби дві сторіс писали в один
  файл - був би race на запис, і другий агент мовчки перетер би роботу першого.

## Status legend

- `todo` - у роботі ще не починалась.
- `wip` - взято у роботу.
- `done` - закрита, тест зелений.

## Notes

- Три-стори tracker навмисно мінімалістичний - фокус на тому, що незалежність
  робить паралелізм безпечним.
