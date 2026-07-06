---
description: House style for the notes library
globs: src/**
---

# notes library — house style

Standing conventions for code under `src/`. Narrow on purpose: each one is a
concrete shape, not general advice.

- **Docstrings.** Every public function and method opens with a one-line
  docstring in the imperative mood — "Return the notes…", "Build an empty…".
- **Argument order.** A module-level helper that operates on a notebook takes
  the `NoteBook` as its first argument — `search(book, query)`, not
  `search(query, book)` — so calls read left to right. (A method on the class
  takes `self` first, as usual.)
- **Serialization.** A note's on-disk shape is `vars(note)` (plain JSON). Do
  not pickle; do not invent a second row format.
