"""Task model and human-readable formatting.

feat/reminders carries DEFECT 2 (duplication / over-complication): a second
near-identical formatter (`format_short`) was copy-pasted from `format_line`,
and both grew a needlessly nested if/elif ladder for the same "when" string.
The two helpers beg to be collapsed into one shared `_when(due)`.
"""


def make(title, due_in_days, priority="normal"):
    """Build a task dict. due_in_days is days-from-today (0 = today)."""
    return {"title": title, "due_in_days": due_in_days, "priority": priority}


def format_line(task):
    """One-line summary of a task, e.g. '[high] Pay invoice (in 2d)'."""
    due = task["due_in_days"]
    if due == 0:
        when = "today"
    else:
        if due > 0:
            when = "in %dd" % due
        else:
            when = "%dd overdue" % -due
    return "[%s] %s (%s)" % (task["priority"], task["title"], when)


def format_short(task):
    """Short summary without priority, e.g. 'Pay invoice (in 2d)'.

    DEFECT 2 (duplication): the entire "when" ladder below is copy-pasted
    from format_line — same branches, same strings. Both should call one
    shared helper instead.
    """
    due = task["due_in_days"]
    if due == 0:
        when = "today"
    else:
        if due > 0:
            when = "in %dd" % due
        else:
            when = "%dd overdue" % -due
    return "%s (%s)" % (task["title"], when)
