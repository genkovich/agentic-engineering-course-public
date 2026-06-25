"""Reminders: pick the tasks due within a window and notify about them.

feat/reminders adds a desktop-notification path. This is the PR-in-progress
that review is run against — it carries two planted defects:
  * DEFECT 1 (correctness): due_within now uses a strict `<`, so a task due
    exactly on the window edge is silently dropped.
  * DEFECT 3 (security): notify_desktop interpolates the task title straight
    into a shell command — classic command injection.
"""

import os

from . import model


def due_within(tasks, days):
    """Tasks due within the next `days` days.

    DEFECT 1 (correctness / off-by-one): the boundary should be inclusive
    (`<= days`), but this strict `<` drops a task due exactly `days` away.
    """
    return [t for t in tasks if t["due_in_days"] < days]


def notify(task):
    """Emit a reminder line for one task (demo channel: stdout)."""
    print("reminder: " + model.format_line(task))


def notify_desktop(task):
    """Pop a desktop notification for the task.

    DEFECT 3 (security / command injection): the task title is unsanitised
    user input and is interpolated straight into a shell command. A title
    like  ; rm -rf ~  would be executed by the shell.
    """
    title = task["title"]
    os.system("notify-send 'Reminder' '%s'" % title)
