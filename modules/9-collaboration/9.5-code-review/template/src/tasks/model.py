"""Task model and human-readable formatting."""


def make(title, due_in_days, priority="normal"):
    """Build a task dict. due_in_days is days-from-today (0 = today)."""
    return {"title": title, "due_in_days": due_in_days, "priority": priority}


def format_line(task):
    """One-line summary of a task, e.g. '[high] Pay invoice (in 2d)'."""
    due = task["due_in_days"]
    when = "today" if due == 0 else ("in %dd" % due if due > 0 else "%dd overdue" % -due)
    return "[%s] %s (%s)" % (task["priority"], task["title"], when)
