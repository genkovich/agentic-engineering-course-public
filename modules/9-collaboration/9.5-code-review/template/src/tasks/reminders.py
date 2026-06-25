"""Reminders: pick the tasks due within a window and notify about them."""

from . import model


def due_within(tasks, days):
    """Tasks due within the next `days` days (inclusive), overdue included.

    A task with due_in_days == days is still inside the window, so the
    comparison is inclusive on the upper bound.
    """
    return [t for t in tasks if t["due_in_days"] <= days]


def notify(task):
    """Emit a reminder line for one task (demo channel: stdout)."""
    print("reminder: " + model.format_line(task))
