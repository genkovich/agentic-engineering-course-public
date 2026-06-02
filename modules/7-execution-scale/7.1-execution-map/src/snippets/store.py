"""In-memory сховище сніпетів.

Рекомендований патерн: Ralph loop (story SNIP-1).
Бінарний критерій «готово» (pytest зелений), маленька замкнена задача -
ідеальна підкладка для одного циклу Ralph.

Контракт STUB - реалізації ще нема, усе кидає NotImplementedError.
"""

from snippets.models import Snippet


class SnippetStore:
    """Просте сховище сніпетів у пам'яті.

    Тримає сніпети за їхнім id. Не звертається до диска чи мережі.
    """

    def add(self, s: Snippet) -> str:
        """Додати сніпет у сховище і повернути його id.

        Якщо `s.id` порожній - призначити новий `uuid4().hex` і записати
        його назад у `s.id`. Якщо `s.id` уже заданий - лишити як є.
        Повертає фінальний id (той, під яким сніпет збережено).
        """
        raise NotImplementedError("SNIP-1: SnippetStore.add ще не реалізовано")

    def get(self, id: str) -> Snippet | None:
        """Повернути сніпет за id або None, якщо такого нема."""
        raise NotImplementedError("SNIP-1: SnippetStore.get ще не реалізовано")

    def all(self) -> list[Snippet]:
        """Повернути всі збережені сніпети списком."""
        raise NotImplementedError("SNIP-1: SnippetStore.all ще не реалізовано")
