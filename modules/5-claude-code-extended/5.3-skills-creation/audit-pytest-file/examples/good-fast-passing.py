"""good-fast-passing.py — clean tests with explicit assertions.

The audit should produce only a single info finding (the summary line). No
errors, no warnings.
"""


def test_addition():
    assert 1 + 1 == 2


def test_string_format():
    assert f"hello {'world'}" == "hello world"


def test_list_membership():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits
