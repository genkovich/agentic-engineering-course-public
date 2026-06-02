"""Example-based tests for SM-2 algorithm (story S-24).

TDD discipline demo: these tests are RED until tdd-implementer fills
src/sm2.py. Do not modify these tests during the implementer / refactorer
phases — they are the executable spec.

Spec source: tasks/story-24-sm2.md
"""

import math

import pytest

from src.sm2 import sm2_next


# --- Test fixtures -----------------------------------------------------------


@pytest.fixture
def new_card() -> dict:
    """A brand-new card: never reviewed."""
    return {"repetitions": 0, "ease_factor": 2.5, "interval": 0}


# --- AC-1: New card, perfect recall ------------------------------------------


def test_new_card_grade_5_sets_interval_1_and_repetitions_1(new_card):
    """AC-1: New card + grade 5 → repetitions=1, interval=1, ease_factor ≈ 2.6."""
    result = sm2_next(new_card, grade=5)

    assert result["repetitions"] == 1
    assert result["interval"] == 1
    # ease_factor = 2.5 + (0.1 - 0 * (0.08 + 0 * 0.02)) = 2.5 + 0.1 = 2.6
    assert math.isclose(result["ease_factor"], 2.6, abs_tol=1e-9)


# --- AC-2: Failure on new card -----------------------------------------------


def test_new_card_grade_0_keeps_repetitions_0_interval_1_ef_unchanged(new_card):
    """AC-2: New card + grade 0 → repetitions=0, interval=1, ease_factor unchanged."""
    result = sm2_next(new_card, grade=0)

    assert result["repetitions"] == 0
    assert result["interval"] == 1
    assert math.isclose(result["ease_factor"], 2.5, abs_tol=1e-9)


# --- AC-3: Second successful repetition --------------------------------------


def test_second_success_grade_4_sets_interval_6():
    """AC-3: repetitions=1 + grade 4 → repetitions=2, interval=6."""
    card = {"repetitions": 1, "ease_factor": 2.6, "interval": 1}

    result = sm2_next(card, grade=4)

    assert result["repetitions"] == 2
    assert result["interval"] == 6


# --- AC-4: Third successful repetition uses ease_factor ----------------------


def test_third_success_grade_3_uses_previous_interval_times_ef():
    """AC-4: repetitions=2 + grade 3 → repetitions=3, interval = round(6 * ef_new).

    With grade=3: ef_delta = 0.1 - 2*(0.08 + 2*0.02) = 0.1 - 2*0.12 = -0.14
    ef_new = 2.5 - 0.14 = 2.36
    interval = round(6 * 2.36) = round(14.16) = 14
    """
    card = {"repetitions": 2, "ease_factor": 2.5, "interval": 6}

    result = sm2_next(card, grade=3)

    assert result["repetitions"] == 3
    assert math.isclose(result["ease_factor"], 2.36, abs_tol=1e-9)
    assert result["interval"] == 14


# --- AC-5: Failure after streak resets repetitions ---------------------------


def test_failure_after_streak_resets_repetitions_to_0():
    """AC-5: long streak + grade < 3 → repetitions reset to 0, interval=1."""
    card = {"repetitions": 7, "ease_factor": 2.8, "interval": 90}

    result = sm2_next(card, grade=2)

    assert result["repetitions"] == 0
    assert result["interval"] == 1
    # ease_factor unchanged on failure
    assert math.isclose(result["ease_factor"], 2.8, abs_tol=1e-9)


# --- AC-6: ease_factor floor at 1.3 ------------------------------------------


def test_ease_factor_never_goes_below_1_3():
    """AC-6: Even with grade 3 repeated, ease_factor floors at 1.3."""
    # Start just above the floor — grade=3 should still trigger clamp.
    card = {"repetitions": 5, "ease_factor": 1.35, "interval": 30}

    result = sm2_next(card, grade=3)

    # ef_delta = 0.1 - 2*(0.08 + 2*0.02) = -0.14
    # raw ef = 1.35 - 0.14 = 1.21 → clamped to 1.3
    assert math.isclose(result["ease_factor"], 1.3, abs_tol=1e-9)


# --- AC-7: Perfect grade grows interval monotonically ------------------------


def test_perfect_grade_5_grows_interval_monotonically():
    """AC-7: Successive grade=5 → interval strictly increases."""
    card = {"repetitions": 0, "ease_factor": 2.5, "interval": 0}

    intervals = []
    for _ in range(6):
        card = sm2_next(card, grade=5)
        intervals.append(card["interval"])

    # First two are fixed schedule (1, 6), then geometric growth.
    assert intervals[0] == 1
    assert intervals[1] == 6
    for i in range(2, len(intervals)):
        assert intervals[i] > intervals[i - 1], (
            f"interval should grow monotonically on perfect recall, "
            f"got {intervals}"
        )


# --- AC-8: Grade boundary (3 passes, 2 fails) --------------------------------


def test_grade_3_is_pass_grade_2_is_fail():
    """AC-8: grade=3 increments repetitions; grade=2 resets."""
    card = {"repetitions": 4, "ease_factor": 2.5, "interval": 20}

    pass_result = sm2_next(card, grade=3)
    fail_result = sm2_next(card, grade=2)

    assert pass_result["repetitions"] == 5
    assert fail_result["repetitions"] == 0
    assert fail_result["interval"] == 1
