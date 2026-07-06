---
name: release-notes
description: >-
  Draft partner-facing release notes from the same commits as the changelog. Triggers on
  "draft release notes", "release notes for the next version", "/release-notes", "нотатки релізу",
  "release notes партнеру". Same input as curate-changelog, different audience and tone: a short,
  benefit-first narrative for a user or partner — "what's new for you" — not a categorized engineer's
  list. Keeps only changes a user actually notices; drops internal refactors and tooling. Prints the
  notes to the chat to seed a GitHub Release description or a partner announcement. Writes no file.
allowed-tools: Bash(git log:*), Bash(git describe:*), Bash(git tag:*), Read(docs/**)
user-invocable: true
disable-model-invocation: true
argument-hint: ''
model: claude-haiku-4-5
effort: low
---

# Skill: release-notes

Goal: write the human announcement of this release — a flowing, benefit-first narrative a non-engineer reads and immediately knows what changed for them.

Same commits as `curate-changelog`, different audience. The changelog is the engineer's categorized history; release notes are the user's story of one release. One input, two outputs — that contrast is the whole point.

## Inputs

- The commits since the last release (`git log <tag>..HEAD`) — the same raw input the changelog uses.
- `templates/release-notes.md` — the narrative shape.

## Protocol

1. **Find the baseline** in `docs/CHANGELOG.md` and run `git log <latest-tag>..HEAD --oneline --no-merges` for the raw input.
2. **Keep only what a user notices** — new capabilities and user-visible fixes. Drop internal refactors, tooling, and tests entirely.
3. **Write as flowing prose grouped by benefit**, not by commit, following `templates/release-notes.md`:
   - Lead with what the reader can now do.
   - No internal jargon, no file names, no commit hashes.
   - Each line passes the test of a reader who never saw the code.
4. **Print the notes to the chat** — do not write a file. They seed a GitHub Release description or a partner announcement.

## Definition of Done

- The notes read as a short benefit-first narrative, not a categorized list — that is what makes them different from the changelog on the very same input.
- No file names, hashes, or internal jargon survive.
- Printed to the chat; no file written, nothing committed.

## Anti-patterns

- **Restating the changelog.** If the output is a bulleted Added/Fixed list, you wrote a changelog, not release notes. Use prose, lead with the benefit.
- **Leaking internals.** A partner does not care about `refactor:` or a file path. If it is not a user-visible change, it is not in the notes.
- **Writing a file.** Print to the chat; the notes seed a Release description a human edits.

## References & templates

- `templates/release-notes.md` — partner-facing narrative scaffold.
