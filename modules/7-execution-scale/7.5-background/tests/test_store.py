"""Тести сховища сніпетів.

На чистому checkout усі ці тести ЗЕЛЕНІ - `store.py` уже реалізований. Це
навмисно: 7.5 не про задачу «з червоного в зелене», а про рівні розкладу.
Зелений `make verify` тут - конкретна ціль, яку `/loop`-рецепт опитує
(«крути наступну todo-story і зупинись, коли pytest зелений»).
"""

from snippets.models import Snippet
from snippets.store import SnippetStore


def test_add_generates_id_when_empty():
    # Порожній id → store генерує uuid4().hex і проставляє його в сам обʼєкт.
    store = SnippetStore()
    snippet = Snippet(id="", title="Loop recipe", body="...", tags=["claude"])
    new_id = store.add(snippet)
    assert new_id
    assert snippet.id == new_id
    assert store.get(new_id) is snippet


def test_add_keeps_explicit_id():
    # Якщо id заданий - store його не чіпає.
    store = SnippetStore()
    store.add(Snippet(id="fixed-1", title="Schedule", body="..."))
    got = store.get("fixed-1")
    assert got is not None
    assert got.id == "fixed-1"


def test_all_returns_inserted_in_order():
    # all() повертає всі сніпети у порядку додавання; get неіснуючого → None.
    store = SnippetStore()
    store.add(Snippet(id="a", title="A", body="..."))
    store.add(Snippet(id="b", title="B", body="..."))
    assert [s.id for s in store.all()] == ["a", "b"]
    assert store.get("missing") is None
