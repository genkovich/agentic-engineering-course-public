---
name: curate-changelog
description: >-
  Curate the [Unreleased] section of docs/CHANGELOG.md from git history. Triggers on
  "curate the changelog", "update the changelog", "/curate-changelog", "онови changelog",
  "курування журналу". Reads git log since the last tag, FILTERS out what a reader never feels
  (test/ci/chore/merge), GROUPS commits about one feature into one bullet, and REWRITES technical
  subjects into plain language under the six Keep a Changelog categories (Added/Changed/Deprecated/
  Removed/Fixed/Security). The result must have FEWER lines than the raw log — that is the proof of
  curation, not a dump. Leaves the edit in the working tree; never commits or pushes.
allowed-tools: Bash(git log:*), Bash(git describe:*), Bash(git tag:*), Read(docs/**), Edit(docs/**)
user-invocable: true
disable-model-invocation: true
argument-hint: ''
model: claude-haiku-4-5
effort: low
---

# Skill: curate-changelog

Goal: turn the raw commit log since the last release into the curated `## [Unreleased]` section of `docs/CHANGELOG.md` — a list a non-engineer reads once and understands.

This is the manual half of the changelog step. The same curation discipline runs headless in `.github/workflows/changelog.yml` on a tag push; the logic is identical, only where it runs changes.

## Inputs

- `docs/CHANGELOG.md` — its existing style and the latest released version.
- The commits since that release (`git log <tag>..HEAD`).
- `templates/changelog-entry.md` — the shape of a curated `[Unreleased]` block.

## Protocol

1. **Find the baseline.** Read `docs/CHANGELOG.md`. The latest released version is the highest `## [X.Y.Z] - YYYY-MM-DD` heading — ignore `## [Unreleased]`, which you are about to fill.
2. **Read the raw input.** Run `git log <latest-tag>..HEAD --oneline --no-merges` (the tag matches the version, e.g. `v0.1.0`).
3. **Curate — three moves, this is the whole point:**
   - **Filter out** what a reader never feels: `test:`, `ci:`, tooling-only `chore:`, merge commits.
   - **Group** several commits about one feature into a single bullet.
   - **Rewrite** the technical subject into plain language. Drop the `feat:` / `fix:` prefix.
4. **Place each bullet** under one of the six Keep a Changelog categories — **Added · Changed · Deprecated · Removed · Fixed · Security** — and write them into `## [Unreleased]`. Skip any empty category. Follow `templates/changelog-entry.md`.
5. **Keep the `## [Unreleased]` heading on top** so the next cycle repeats.

## Definition of Done

- `## [Unreleased]` holds curated bullets under the right Keep a Changelog categories.
- The result has **fewer lines than the raw `git log`** — noise filtered, one-feature commits grouped.
- Each bullet is one line, plain language, no `feat:`/`fix:` prefix, no trailing period.
- The edit is in the working tree only — not committed, not pushed.

## Anti-patterns

- **Transcribing, not curating.** If the changelog has as many lines as the log, you dumped it. Filter and group.
- **Leaving in the noise.** `test:`, `ci:`, tooling `chore:`, and merge commits never reach a user-facing changelog.
- **Technical phrasing.** "add idx on users.email" is a commit subject, not a changelog line. Write "faster lookup of users by email".
- **Committing or pushing.** Leave the suggestion in the working tree; a human applies it.
- **Editing outside `docs/`.**

## References & templates

- `templates/changelog-entry.md` — curated `[Unreleased]` scaffold (Keep a Changelog categories).
