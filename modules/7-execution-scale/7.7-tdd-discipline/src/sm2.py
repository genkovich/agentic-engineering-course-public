"""SM-2 spaced repetition algorithm — empty stub.

This module is intentionally empty. The TDD demo agents fill it in via
the RGR cycle:
  1. tdd-test-writer commits failing tests.
  2. tdd-implementer fills sm2_next() with minimal implementation.
  3. tdd-refactorer extracts helpers (_apply_failure, _apply_success).

Spec lives in tasks/story-24-sm2.md.
"""


def sm2_next(card: dict, grade: int) -> dict:
    """Compute the next SM-2 card state given a recall grade.

    Args:
        card: {"repetitions": int, "ease_factor": float, "interval": int}
        grade: int in [0, 5]. 5 = perfect recall, 0 = total blackout.
               grade >= 3 is "pass", grade < 3 is "fail".

    Returns:
        Updated card dict with new repetitions, ease_factor, interval.
    """
    raise NotImplementedError("Implement per tasks/story-24-sm2.md")
