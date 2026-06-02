"""Пошук дублікатів сніпетів за вмістом.

Це ЗАГЛУШКА (story SNIP-4). Функція піднімає NotImplementedError - `pytest`
на чистому checkout червоний навмисно. Це один з трьох НЕЗАЛЕЖНИХ файлів
(search.py / dedupe.py / export.py), які workflow реалізує паралельно: цей агент
пише рівно у dedupe.py і не торкається ні search.py, ні export.py.

Контракт описаний у docstring і в tasks/story-snip-4.md.
"""

from __future__ import annotations

from snippets.models import Snippet


def find_duplicates(snippets: list[Snippet]) -> list[list[str]]:
    """Знайти групи сніпетів з ідентичним вмістом.

    Два сніпети вважаються дублікатами, якщо їхній body збігається після
    body.strip() (пробіли з країв не рахуються). Повертає список груп; кожна
    група - це список id (рядків) сніпетів зі спільним вмістом. До результату
    потрапляють лише групи розміром >= 2 (одинаки не дублікати).

    Приклад:
        find_duplicates([a, b, c]), де a.body і b.body однакові після strip,
        а c унікальний, поверне [["a", "b"]].
    """
    raise NotImplementedError("find_duplicates is story SNIP-4 - implement per docstring")
