"""Тести пошуку дублікатів (SNIP-4). RED на чистому checkout: dedupe.py = NotImplementedError."""

from snippets.models import Snippet
from snippets.dedupe import find_duplicates


def test_groups_identical_bodies_ignoring_whitespace():
    snippets = [
        Snippet(id="1", title="a", body="print(1)"),
        Snippet(id="2", title="b", body="  print(1)  "),
        Snippet(id="3", title="c", body="print(2)"),
    ]
    groups = find_duplicates(snippets)
    assert groups == [["1", "2"]]


def test_no_duplicates_returns_empty():
    snippets = [
        Snippet(id="1", title="a", body="x"),
        Snippet(id="2", title="b", body="y"),
    ]
    assert find_duplicates(snippets) == []


def test_singletons_are_not_groups():
    snippets = [Snippet(id="1", title="a", body="solo")]
    assert find_duplicates(snippets) == []
