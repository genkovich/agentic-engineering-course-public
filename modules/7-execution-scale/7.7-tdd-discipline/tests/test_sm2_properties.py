"""Property-based tests for SM-2 algorithm using Hypothesis.

These cover invariants that example-based tests can miss:
  - For any valid card and grade >= 3: new interval >= 1
  - For any valid card and grade <  3: new repetitions == 0
  - ease_factor >= 1.3 ALWAYS (post-condition invariant)

Spec source: tasks/story-24-sm2.md
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.sm2 import sm2_next


# --- Strategy: generate plausible cards --------------------------------------
#
# repetitions: 0..50 (50 is already > 20 years of perfect recall)
# ease_factor: 1.3..3.5 (algorithm spec keeps it in this band)
# interval:    0..3650 (~10 years)

card_strategy = st.fixed_dictionaries(
    {
        "repetitions": st.integers(min_value=0, max_value=50),
        "ease_factor": st.floats(
            min_value=1.3, max_value=3.5, allow_nan=False, allow_infinity=False
        ),
        "interval": st.integers(min_value=0, max_value=3650),
    }
)

grade_strategy = st.integers(min_value=0, max_value=5)


# --- Invariant 1: pass grade → interval at least 1 day -----------------------


@given(card=card_strategy, grade=st.integers(min_value=3, max_value=5))
@settings(max_examples=200)
def test_pass_grade_produces_interval_at_least_one(card, grade):
    """For any valid card + grade >= 3, new interval is >= 1 day."""
    result = sm2_next(card, grade)
    assert result["interval"] >= 1


# --- Invariant 2: fail grade → repetitions reset to 0 ------------------------


@given(card=card_strategy, grade=st.integers(min_value=0, max_value=2))
@settings(max_examples=200)
def test_fail_grade_resets_repetitions(card, grade):
    """For any valid card + grade < 3, new repetitions == 0."""
    result = sm2_next(card, grade)
    assert result["repetitions"] == 0


# --- Invariant 3: ease_factor floor at 1.3 always ----------------------------


@given(card=card_strategy, grade=grade_strategy)
@settings(max_examples=400)
def test_ease_factor_never_below_floor(card, grade):
    """Across the full grade range, ease_factor never falls below 1.3."""
    result = sm2_next(card, grade)
    assert result["ease_factor"] >= 1.3
