"""Контракт для find_duplicates (story SNIP-4).

На чистому checkout усі ці тести ЧЕРВОНІ: dedupe.py - заглушка з
NotImplementedError. Тести - незмінний контракт: правильна реалізація робить
їх зеленими, не навпаки.
"""

from snippets.models import Snippet
from snippets.dedupe import find_duplicates


def test_find_duplicates_groups_identical_bodies():
    snippets = [
        Snippet(id="a", title="A", body="print(1)"),
        Snippet(id="b", title="B", body="print(1)"),
        Snippet(id="c", title="C", body="print(2)"),
    ]
    assert find_duplicates(snippets) == [["a", "b"]]


def test_find_duplicates_ignores_surrounding_whitespace():
    # body збігається після strip - провідні/завершальні пробіли не рахуються.
    snippets = [
        Snippet(id="a", title="A", body="  same  "),
        Snippet(id="b", title="B", body="same"),
    ]
    assert find_duplicates(snippets) == [["a", "b"]]


def test_find_duplicates_drops_singletons():
    # Жодного дубля - кожна група розміром < 2 відкидається.
    snippets = [
        Snippet(id="a", title="A", body="one"),
        Snippet(id="b", title="B", body="two"),
    ]
    assert find_duplicates(snippets) == []


def test_find_duplicates_empty_input():
    assert find_duplicates([]) == []


def test_find_duplicates_handles_three_in_a_group():
    snippets = [
        Snippet(id="a", title="A", body="dup"),
        Snippet(id="b", title="B", body="dup"),
        Snippet(id="c", title="C", body="dup"),
    ]
    assert find_duplicates(snippets) == [["a", "b", "c"]]
