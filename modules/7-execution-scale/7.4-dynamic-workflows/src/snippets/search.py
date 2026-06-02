"""Пошук сніпетів за тегом і за текстом.

Це ЗАГЛУШКА (story SNIP-3). Обидві функції піднімають NotImplementedError -
`pytest` на чистому checkout червоний навмисно. Це один з трьох НЕЗАЛЕЖНИХ файлів
(search.py / dedupe.py / export.py), які workflow реалізує паралельно: кожен
агент пише рівно у свій файл, тож гонки за запис між ними немає.

Залежність: normalize_tag з tags.py (вже працює).
Контракт описаний у docstring кожної функції і в tasks/story-snip-3.md.
"""

from __future__ import annotations

from snippets.models import Snippet
from snippets.tags import normalize_tag


def search_by_tag(snippets: list[Snippet], tag: str) -> list[Snippet]:
    """Повернути сніпети, що мають заданий тег (звірка у нормалізованій формі).

    Шуканий `tag` і кожен тег кожного сніпета проганяються через normalize_tag,
    далі звіряються на рівність. Порядок результату - як у вхідному списку.

    Приклад:
        search_by_tag([s_python, s_go], "  Python ") поверне [s_python],
        якщо s_python має тег "python" (або будь-яке написання, що нормалізується
        в "python").
    """
    raise NotImplementedError("search_by_tag is story SNIP-3 - implement per docstring")


def search_by_text(snippets: list[Snippet], q: str) -> list[Snippet]:
    """Повернути сніпети, де `q` є підрядком title АБО body (без регістру).

    Звірка регістронезалежна (case-insensitive). Порожній запит `q` вважається
    підрядком будь-якого рядка, тож повертає всі сніпети. Порядок результату -
    як у вхідному списку.

    Приклад:
        search_by_text([s], "async") поверне [s], якщо "async" трапляється у
        s.title або s.body у будь-якому регістрі.
    """
    raise NotImplementedError("search_by_text is story SNIP-3 - implement per docstring")
