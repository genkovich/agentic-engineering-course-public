# `notes` API reference

The public surface of the `notes` library, for someone who depends on it.

> This file is **hand-written** and lives next to the code in the same repo. It
> is the exact surface `check-docs-drift` checks: when the code grows a public
> `NoteBook` method that this table does not list, that gap is **doc drift** —
> the doc fell behind the code. Keep the table in sync, or let the drift tool
> catch it for you.

## `NoteBook`

An in-memory collection of notes. Construct one with `NoteBook()`.

| Method | What it does |
|---|---|
| `add(title, body, tags=None)` | Add a note and return it. |
| `get(note_id)` | Return the note with this id; raises `NotesError` if absent. |
| `list()` | Return all notes in insertion order. |
| `remove(note_id)` | Remove the note with this id. |
| `find(title)` | Return the first note with this exact title. |

## `Note`

A single note: `id`, `title`, `body`, `tags` (a list).
