"""bad-failing-test.py — a passing assertion next to a failing one.

The audit should report the failing test as severity=error, category=failed,
and still emit an info summary that says 1/2 tests passed.
"""


def test_addition_is_correct():
    assert 1 + 1 == 2


def test_addition_is_wrong():
    assert 1 + 1 == 3, "math is fine, the test is wrong on purpose"
