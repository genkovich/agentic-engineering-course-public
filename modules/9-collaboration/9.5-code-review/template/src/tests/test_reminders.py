"""Behaviour spec for the reminders window.

Green on the baseline (main). On feat/reminders the refactored due_within
flips the boundary to a strict `<`, so the task due exactly on the window
edge is dropped and `test_due_on_boundary_is_included` goes red.
"""

import unittest

from tasks import model, reminders


class DueWithinTest(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            model.make("overdue", -1),
            model.make("today", 0),
            model.make("edge", 3),
            model.make("later", 4),
        ]

    def test_overdue_is_included(self):
        titles = [t["title"] for t in reminders.due_within(self.tasks, 3)]
        self.assertIn("overdue", titles)

    def test_due_on_boundary_is_included(self):
        # A task due exactly `days` away is still within the window.
        titles = [t["title"] for t in reminders.due_within(self.tasks, 3)]
        self.assertIn("edge", titles)

    def test_beyond_window_is_excluded(self):
        titles = [t["title"] for t in reminders.due_within(self.tasks, 3)]
        self.assertNotIn("later", titles)


if __name__ == "__main__":
    unittest.main()
