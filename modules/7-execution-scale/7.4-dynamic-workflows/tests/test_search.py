"""Контракт для search_by_tag і search_by_text (story SNIP-3).

На чистому checkout усі ці тести ЧЕРВОНІ: search.py - заглушка з
NotImplementedError. Тести - незмінний контракт: правильна реалізація робить
їх зеленими, не навпаки.
"""

from snippets.models import Snippet
from snippets.search import search_by_tag, search_by_text

_S = [
    Snippet(id="a", title="Async in Python", body="await foo()", language="python", tags=["Python", "async"]),
    Snippet(id="b", title="Goroutines", body="go run()", language="go", tags=["Go"]),
    Snippet(id="c", title="Context window", body="контекст моделі", language="text", tags=["llm", "python "]),
]


def test_search_by_tag_normalizes_query_and_stored_tags():
    # "  Python " і збережене "Python"/"python " нормалізуються в "python".
    result = search_by_tag(_S, "  Python ")
    assert [s.id for s in result] == ["a", "c"]


def test_search_by_tag_no_match_returns_empty():
    assert search_by_tag(_S, "rust") == []


def test_search_by_text_is_case_insensitive_over_title_and_body():
    # "async" є у title "Async in Python" (a) і у body "await..." немає, але
    # звірка по title OR body; "go" трапляється у title/body сніпета b.
    assert [s.id for s in search_by_text(_S, "ASYNC")] == ["a"]
    assert [s.id for s in search_by_text(_S, "goroutines")] == ["b"]


def test_search_by_text_matches_body_not_only_title():
    # "await" є лише у body сніпета a, не у title.
    assert [s.id for s in search_by_text(_S, "await")] == ["a"]


def test_search_by_text_empty_query_returns_all():
    assert [s.id for s in search_by_text(_S, "")] == ["a", "b", "c"]
