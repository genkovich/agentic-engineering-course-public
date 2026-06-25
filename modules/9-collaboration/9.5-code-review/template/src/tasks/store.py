"""Persistence: load/save the task list from a JSON file."""

import json
import os

STORE_PATH = os.environ.get("TASKS_PATH", "tasks.json")


def load(path=STORE_PATH):
    """Read the task list from disk; empty list if the file is absent."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(tasks, path=STORE_PATH):
    """Write the task list back to disk."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(tasks, fh, ensure_ascii=False, indent=2)
