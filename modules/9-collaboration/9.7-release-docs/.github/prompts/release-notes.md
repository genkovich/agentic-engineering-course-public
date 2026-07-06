You are writing partner-facing release notes for a version that was just
tagged. The tag is in the `TAG` environment variable (e.g. `v0.2.0`); the
version is `TAG` without the leading `v`.

Same input as the changelog, different audience. The changelog is the
engineer's categorized history; these notes are the user's story of one
release — a short, benefit-first narrative.

## Workflow

1. Find the previously released version in `docs/CHANGELOG.md` and run
   `git log <previous-tag>..HEAD --oneline --no-merges` for the raw input.
2. Keep only what a user or partner notices — new capabilities and user-visible
   fixes. Drop internal refactors, tooling, and tests entirely.
3. Write the notes as flowing Markdown prose grouped by benefit, not by commit:
   - Lead with what the reader can now do.
   - No internal jargon, no file names, no commit hashes.
   - Each line passes the test of a reader who never saw the code.

## Constraints

- **Do not commit, push, or edit any file.** These notes seed a draft GitHub
  Release that a human reviews and publishes.
- Benefit-first, written for a non-engineer.

## Final output

Return a JSON object matching the requested schema:

- `version`: `TAG` without the leading `v`, format `"X.Y.Z"`.
- `notes`: the release notes as a Markdown string (a short narrative — a
  heading is optional, prose paragraphs, no categorized bullet list).
