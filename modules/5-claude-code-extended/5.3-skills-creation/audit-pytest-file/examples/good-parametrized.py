"""good-parametrized.py — one test function, many parametrised cases.

The audit should produce only a single info finding (the summary line) and
report each parametrised case as a separate node id.
"""
import pytest


@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, -5, 5),
    (0, 0, 0),
])
def test_addition_is_associative(a, b, expected):
    assert a + b == expected
    assert b + a == expected
