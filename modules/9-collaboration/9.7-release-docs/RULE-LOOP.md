# Rule-loop fixture — the planted "error → durable rule" case

Self-contained material for the **error→rule loop** demo of lecture 9.7
(Section 4). It runs entirely in this repo — no dependency on any other project.
The live loop you record happens here.

## The setup

`.claude/rules/notes-style.md` is a **narrow** existing rule: docstrings,
argument order, serialization shape for `src/`. It says nothing about error
handling — that gap is the point.

The house convention for a lookup that can miss is shown once, correctly, in
`NoteBook.get` (`src/notes.py`): it raises `NotesError` naming the missing key
instead of a bare `KeyError`. `NotesError` lives in `src/errors.py`.

## The planted repeated mistake

Two other lookups regressed the same convention — the "twice = a pattern"
evidence:

| Where | Wrong shape | Should be |
|---|---|---|
| `NoteBook.remove` (`src/notes.py`) | `del self._notes[note_id]` → bare `KeyError` | raise `NotesError(f"no note with id {note_id!r}")` first |
| `NoteBook.find` (`src/notes.py`) | `next(...)` → bare `StopIteration` | raise `NotesError(f"no note titled {title!r}")` on a miss |

Both leak a cryptic built-in exception where the project wants a `NotesError`
with a message. Review flagged it on `remove`, then again on `find` — the
second hit is what makes it rule-worthy.

## Recording the loop (mirrors the lecture beats)

1. **Show the repeat.** Open `src/notes.py`; point at `get` (the right shape),
   then `remove` and `find` (the same miss, twice). Say: this is the second
   time, so it earns a rule, not another hand-fix.
2. **Codify.** In a Claude session run `/codify-rule` and describe the case —
   "lookups that can miss must raise `NotesError`, like `get`; `remove` and
   `find` regressed it." The command writes a narrow rule into `.claude/rules/`
   and stops (no commit).
3. **Read the diff.** `git diff .claude/rules/` — a new, concrete rule naming
   the wrong and right shapes. It reaches the team through the same git diff as
   code.
4. **(Optional) Prove inheritance.** New session, ask for another `NoteBook`
   lookup method. It now raises `NotesError` without being told — the rule
   carried the lesson.

## Reset

`./reset-demo.sh` reverts the codified rule (and any other working-tree edits)
so you can re-record. The planted regressions in `src/notes.py` stay — they are
committed baseline.
