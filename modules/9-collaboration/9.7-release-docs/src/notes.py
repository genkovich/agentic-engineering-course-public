"""In-memory notebook: add, list, fetch, remove and find short notes.

Deliberately tiny. Its only job is to give the demo repo real source files
that the seeded Conventional-Commit history can touch, so `git log` has
something meaningful to summarize.
"""

from dataclasses import dataclass, field

from errors import NotesError


@dataclass
class Note:
    id: int
    title: str
    body: str
    tags: list = field(default_factory=list)


class NoteBook:
    def __init__(self):
        self._notes = {}
        self._next_id = 1

    def add(self, title, body, tags=None):
        """Add a note and return it."""
        note = Note(self._next_id, title, body, list(tags or []))
        self._notes[note.id] = note
        self._next_id += 1
        return note

    def get(self, note_id):
        """Return the note with this id.

        House convention: a lookup that can miss raises NotesError naming the
        missing key — never a bare KeyError. This is the shape to copy.
        """
        if note_id not in self._notes:
            raise NotesError(f"no note with id {note_id!r}")
        return self._notes[note_id]

    def list(self):
        """Return all notes in insertion order."""
        return list(self._notes.values())

    def remove(self, note_id):
        """Remove the note with this id."""
        del self._notes[note_id]

    def find(self, title):
        """Return the first note with this exact title."""
        return next(n for n in self._notes.values() if n.title == title)
