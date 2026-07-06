<!-- Doc-drift report. Fill from scripts/check-docs-drift.py output — quote its
findings, do not invent. Keep every section even if empty (write "none"). -->

# Doc drift report — `docs/api.md`

**Checked:** `NoteBook` public methods (`src/notes.py`) vs the documented surface (`docs/api.md`).

## In the code but missing from the doc (doc fell behind)

- `NoteBook.<method>(<signature>)` — <one line from its docstring>

## In the doc but gone from the code (ghost)

- none

## Proposed fix

- Add a row to the `## NoteBook` table in `docs/api.md` for each undocumented
  method, matching its real signature and docstring.
- Re-run `./scripts/check-docs-drift.py` — exit 0 confirms the doc is back in sync.
