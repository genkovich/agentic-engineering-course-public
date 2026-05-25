# Socratic loop — batch propose-all-then-validate for write-prd Protocol step 7

Goes between the draft (step 6) and the Phase 7.5 critic (step 7.5). Per-section batch validation via `AskUserQuestion` over the in-memory draft. The skill renders the full proposed list for a section first (so the user sees the big picture), then walks per-item resolutions. Don't write the file until step 7.5 + Self-check pass.

For concrete question wording + option `description` fields, see [ask-examples.md](./ask-examples.md).

## Contract

**Per-section batch, not per-item-across-sections.** For each of the 4 item-sections in order — §4 US → §5 AC → §6 NFR → §7 KPI — the skill:

1. **7a. Renders the full proposed list** in one message (e.g. all 12 proposed AC sequentially, numbered, with coverage-type tag in parentheses for §5). This gives the user the big picture before any resolution is requested — they can spot duplicates, gaps, or drop-the-whole-list problems before committing to per-item decisions.
2. **7b. Walks per-item resolutions** — one `AskUserQuestion` per item in the just-rendered section, using the 4-state machine below (5-state for §5 AC).
3. **7c. Applies transitions** to the in-memory draft as each resolution arrives.
4. **7d. Runs the coverage gate** (only for §5 AC) — after all resolutions in §5, verify ≥1 AC of each of the 5 coverage types remains. If broken, skill regenerates a replacement AC of the missing type, appends it, and runs a mini-batch on the new AC. Loop until coverage holds OR user `Save as Open Question`-s the regenerated AC (then F5 critic handles it downstream — user provides rationale).
5. **7e. Repeats 7a-7d for the next section**. The skill never returns to a previous section once it has moved on.

## Options by item-type

All four item-types share a 4-state machine; AC has one extra optional state.

- **For each US** — `Approve as-is` / `Reword` / `Save as Open Question` / `Drop`.
- **For each AC** — `Approve as-is` / `Reword GWT` / `Save as Open Question` / `Drop` / `Add another AC` (5th option — generates one more AC for the same US in a coverage type not yet present).
- **For each NFR row** — `Approve as-is` / `Edit target` / `Save as Open Question` / `Drop`.
- **For each KPI** — `Approve as-is` / `Edit baseline/target` / `Save as Open Question` / `Drop`.

Each option label must be paired with a `description` explaining the next mechanical step the skill will take after that choice — see [ask-examples.md](./ask-examples.md) for the canonical wording.

`Cancel` and `Reject` are synonyms for `Drop` — same transition, same edits-log action.

## State transitions

- **`Approve`** → no draft change. No edits-log entry. Move to next item.
- **`Edit` / `Reword`** → regenerate that item with the new constraint, then loop back on that item once. The user's **second** answer per item is final (single-iteration cap).
- **`Drop`** → delete the item, decrement subsequent numbering (US-03 → US-02, AC-04 → AC-03 etc.). For AC: if the dropped AC was the only one of its coverage type, the coverage gate in 7d regenerates a replacement of the same type.
- **`Save as Open Question`** → remove the item from its native section AND append an entry to §8 Open Questions in this exact shape: `- [ ] <item-id> (<verbatim text>) — чи цей <item-type> валідний? <inline rationale from user>. — owner: <user-typed>, due: <user-typed YYYY-MM-DD or stage trigger>`. Owner + due are **mandatory** — skill issues a follow-up `AskUserQuestion` immediately after the user picks this option to capture them. If the user leaves owner OR due blank, the resolution is **downgraded to `Drop`** with a warning surfaced to the user.
- **`Add another AC`** (AC only, 5th option) → generate one additional AC for that US, picking a coverage type not yet present on that US, then loop on the new AC with the same 4-state machine.

Persist edits into the in-memory draft after each resolution. The on-disk file is **not** touched yet.

## Edits-log (mandatory)

Maintain an edits-log throughout step 7. After each `Edit` / `Drop` / `Add` / `Save as Open Question` resolution (NOT for `Approve`), append one entry:

```
{item_id:    "US-06" | "AC-04" | "NFR-row-2" | "KPI-01",
 action:     "edit" | "drop" | "add" | "save_as_oq",
 before:     "<verbatim text of the item before user action, or null for add>",
 after:      "<verbatim text after — for save_as_oq this is the §8 entry incl. owner+due; null for drop>",
 user_reason:"<the rationale the user provided, verbatim>"}
```

`Approve` items do **not** go into the log — they are the baseline. The log is the **sole** signal the Phase 7.5 critic uses to detect upstream-coherence drift caused by user edits. Without it, the critic has no input for F1/F2/F3/F4.

If the user provides no reason on `Drop` or `Save as Open Question` — re-prompt once for it. Verbatim user wording matters: the critic uses it to judge whether a defer silently re-introduces a vector that idea-brief §13 / §11 / §6 named as load-bearing.

## Exit condition

Step 7 completes when:

- All 4 sections (§4 US, §5 AC, §6 NFR, §7 KPI) have been batch-rendered (7a) and walked (7b) with one resolution per item.
- The in-memory draft reflects every `Edit`/`Drop`/`Add`/`Save as OQ` resolution; `Save as OQ` items appear in §8 with owner+due.
- The §5 coverage gate (7d) is closed — ≥1 AC of each of the 5 coverage types remains AFTER drops + OQ-migrations (OQ-migrated items do NOT count toward coverage; they live in §8 now).
- The edits-log is closed (no pending entries).

Then proceed to step 7.5 (see [critic-phase.md](./critic-phase.md)).
