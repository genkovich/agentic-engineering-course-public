---
name: check-docs-drift
description: >-
  Find and fix where docs/api.md fell behind the code. Triggers on "check for doc drift",
  "is the API doc up to date", "/check-docs-drift", "перевір дрейф документації", "docs drift".
  Runs the deterministic scripts/check-docs-drift.py (parses the public NoteBook methods with ast,
  compares to what docs/api.md documents — NO LLM finds the gap), reports the drift, and PROPOSES the
  doc edit that closes it. The gap is found by parsing; the agent writes the missing documentation in
  the doc's existing style. Edits only docs/; never commits or pushes.
allowed-tools: Bash(./scripts/check-docs-drift.py), Bash(git log:*), Read(src/**), Read(docs/**), Edit(docs/**)
user-invocable: true
disable-model-invocation: true
argument-hint: ''
model: claude-haiku-4-5
effort: low
---

# Skill: check-docs-drift

Goal: catch the moment `docs/api.md` stops matching the code — and close the gap by documenting what the code grew.

Doc drift is what happens when code moves and the docs don't: a `feat:` adds a public method, but the API reference still lists the old surface. This skill makes that gap visible and fixable in one pass. The detection is deterministic (a script); the fix is the agent writing the missing line in the doc's own style.

## Inputs

- `scripts/check-docs-drift.py` — the deterministic detector.
- `src/notes.py` — the real public surface.
- `docs/api.md` — the documented surface.
- `templates/drift-report.md` — the report shape.

## Protocol

1. **Detect — run the script, do not eyeball the code.** Run exactly:

   ```
   ./scripts/check-docs-drift.py
   ```

   It prints the `NoteBook` methods in the code, the methods in the doc, and the gap both ways. Exit 0 = in sync (report that and stop); exit 1 = drift.

2. **Report the drift** using `templates/drift-report.md`: which methods are in the code but missing from `docs/api.md` (the doc fell behind), and which are documented but gone from the code (a ghost). Quote the script's findings — do not invent any.

3. **Propose the fix.** For each undocumented method, read its signature and docstring in `src/notes.py` and add a matching row to the `## NoteBook` table in `docs/api.md`, in the table's existing style. For a ghost, propose removing the stale row. Edit only `docs/api.md`.

4. **Re-run the script** to confirm the gap closed — exit 0 means the doc is back in sync. Leave the edit in the working tree.

## Definition of Done

- The drift was found by `scripts/check-docs-drift.py`, not guessed from reading the code.
- Every undocumented method got a table row matching its real signature and docstring; every ghost row was flagged.
- A second run of the script exits 0 (in sync).
- The edit is in the working tree only — not committed, not pushed.

## Anti-patterns

- **Skipping the script.** "The doc looks fine" is not a finding. The gap comes from parsing or it does not exist.
- **Inventing a method that is not in the code**, or describing it differently from its real signature. Copy the truth from `src/notes.py`.
- **Editing the code to match the doc.** The code is the truth; the doc follows it. Edit only `docs/api.md`.
- **Committing or pushing.** Leave the suggestion in the working tree.

## References & templates

- `scripts/check-docs-drift.py` — the deterministic detector.
- `templates/drift-report.md` — drift report scaffold.
