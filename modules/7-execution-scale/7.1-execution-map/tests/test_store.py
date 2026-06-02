"""Тести SnippetStore (SNIP-1). RED на чистому checkout: store.py = NotImplementedError."""

from snippets.models import Snippet
from snippets.store import SnippetStore


def test_add_assigns_id_when_empty():
    store = SnippetStore()
    new_id = store.add(Snippet(id="", title="t", body="b"))
    assert new_id
    assert store.get(new_id).id == new_id


def test_add_keeps_explicit_id():
    store = SnippetStore()
    returned = store.add(Snippet(id="fixed", title="t", body="b"))
    assert returned == "fixed"
    assert store.get("fixed").title == "t"


def test_get_missing_returns_none():
    store = SnippetStore()
    assert store.get("nope") is None


def test_all_returns_every_added_snippet():
    store = SnippetStore()
    store.add(Snippet(id="a", title="A", body="1"))
    store.add(Snippet(id="b", title="B", body="2"))
    ids = {s.id for s in store.all()}
    assert ids == {"a", "b"}
