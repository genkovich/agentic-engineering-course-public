"""Minimal CLI: list tasks and fire reminders for the ones due soon.

    python3 -m tasks.cli list
    python3 -m tasks.cli remind [days]   # default window: 3 days
"""

import sys

from . import model, reminders, store


def _seed_if_empty():
    """Give the demo something to show on a fresh checkout."""
    tasks = store.load()
    if not tasks:
        tasks = [
            model.make("Pay invoice", 2, "high"),
            model.make("Renew domain", 5, "normal"),
            model.make("File taxes", -1, "high"),
            model.make("Water plants", 0, "low"),
        ]
        store.save(tasks)
    return tasks


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "list"
    tasks = _seed_if_empty()

    if cmd == "list":
        for t in tasks:
            print(model.format_line(t))
    elif cmd == "remind":
        days = int(argv[1]) if len(argv) > 1 else 3
        for t in reminders.due_within(tasks, days):
            reminders.notify(t)
    else:
        print("usage: tasks.cli [list|remind [days]]")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
