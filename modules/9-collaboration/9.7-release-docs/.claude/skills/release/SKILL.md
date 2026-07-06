---
name: release
description: >-
  Run the whole local release pipeline in order, stopping at each human gate. Triggers on
  "run the release", "prepare a release", "/release", "зроби реліз", "підготуй реліз". Drives the
  four stages back to back — bump-version → curate-changelog → release-notes → check-docs-drift —
  pausing after each so the human reviews the diff before the next stage. Prepares everything in the
  working tree; never tags, commits, or pushes. The tag push (which fires CI) stays the human's action.
allowed-tools: Bash(./scripts/next-version.sh), Bash(./scripts/check-docs-drift.py), Bash(git log:*), Bash(git diff:*), Bash(git tag:*), Bash(git describe:*), Read(src/**), Read(docs/**), Read(pyproject.toml), Edit(pyproject.toml), Edit(docs/**)
user-invocable: true
disable-model-invocation: true
argument-hint: ''
model: claude-haiku-4-5
effort: medium
---

# Skill: release (orchestrator)

Goal: walk the full local release prep — version, changelog, release notes, doc drift — in one run, so the human reviews four small diffs instead of remembering four commands. Each stage follows the protocol of its own skill; this skill just sequences them and stops at the gates.

Nothing here pushes. The pipeline prepares a reviewable working tree; tagging and pushing — the thing that fires CI — stays the human's call.

## Inputs

- The seeded Conventional-Commit history since the last tag.
- `pyproject.toml`, `docs/CHANGELOG.md`, `docs/api.md` — the artifacts each stage touches.
- The four stage skills as the source of truth for each stage's protocol:
  `bump-version`, `curate-changelog`, `release-notes`, `check-docs-drift`.

## Protocol

Run the four stages **in order**. After each, show the diff (or output) and **pause for the human** before starting the next.

1. **Version.** Follow the `bump-version` protocol: run `./scripts/next-version.sh`, explain which part moved and why, edit the `version` line in `pyproject.toml`, and propose `git tag v<new>`. → **Gate:** show the pyproject diff; the human decides whether to tag now or after reviewing the rest.
2. **Changelog.** Follow the `curate-changelog` protocol: curate `[Unreleased]` in `docs/CHANGELOG.md` from the log since the last tag. → **Gate:** show `git diff docs/CHANGELOG.md`; fewer lines than the log = curated.
3. **Release notes.** Follow the `release-notes` protocol: print the partner-facing narrative from the same input. → **Gate:** the human reads it next to the changelog (one input, two outputs).
4. **Doc drift.** Follow the `check-docs-drift` protocol: run `./scripts/check-docs-drift.py`, then propose the `docs/api.md` fix for anything the feature left undocumented. → **Gate:** show `git diff docs/api.md`; re-run the script to confirm exit 0.

At the end, summarize the prepared working tree (version, changelog, notes, doc fix) and restate the one human action left: `git tag v<new> && git push origin v<new>`.

## Definition of Done

- All four stages ran in order, each producing its artifact in the working tree.
- A diff (or printed output) was shown after each stage, with a pause for review.
- Nothing was tagged, committed, or pushed — the working tree is prepared and the tag command is proposed.
- The final summary lists what changed and the single remaining human action.

## Anti-patterns

- **Running stages out of order or silently.** Version first; show each diff; pause. The human reviews four small steps, not one big surprise.
- **Tagging or pushing to "finish the job".** The gate is the tag push. Propose it; never run it.
- **Skipping a stage because it "probably has nothing".** Run `check-docs-drift` even when you expect it clean — a green run is a result worth showing.

## References & templates

- `bump-version`, `curate-changelog`, `release-notes`, `check-docs-drift` — the per-stage skills this orchestrator sequences.
