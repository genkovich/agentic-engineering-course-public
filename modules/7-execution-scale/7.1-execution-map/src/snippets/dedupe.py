"""Пошук дублікатів сніпетів за тілом.

Рекомендований патерн: dynamic workflow (story SNIP-4).
SNIP-3 і SNIP-4 - незалежні підзадачі в різних файлах, тому їх можна
вести паралельними гілками dynamic workflow.

Контракт STUB - реалізації ще нема, усе кидає NotImplementedError.
"""

from snippets.models import Snippet


def find_duplicates(snippets: list[Snippet]) -> list[list[str]]:
    """Згрупувати id сніпетів з однаковим тілом.

    Два сніпети вважаються дублікатами, якщо їхні `body.strip()` рівні.
    Повертає список груп; кожна група - список id, і лише групи розміром
    від 2 (одинаків не повертаємо).
    """
    raise NotImplementedError("SNIP-4: find_duplicates ще не реалізовано")
