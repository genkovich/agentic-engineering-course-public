# Sample `release-artifacts/<timestamp>/` directory after a successful run

After `make demo-fixture` completes, the script writes three artefacts under
`fixture-repo/release-artifacts/<YYYY-MM-DD-HHMMSS>/`:

```
fixture-repo/release-artifacts/
└── 2026-05-11-002455/
    ├── changelog.patch      # raw git diff for docs/CHANGELOG.md (apply'able)
    ├── release-notes.md     # human-readable rollup for gh release create
    └── summary.md           # full pipeline report with metadata + JSON payload
```

## changelog.patch — what the agent edited

Raw `git diff -- docs/CHANGELOG.md` captured *after* the agent finished
editing the working tree. Apply elsewhere with `git apply changelog.patch`.
Typical content on the lecture fixture:

```diff
diff --git a/docs/CHANGELOG.md b/docs/CHANGELOG.md
index abc123..def456 100644
--- a/docs/CHANGELOG.md
+++ b/docs/CHANGELOG.md
@@ -7,6 +7,21 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),

 ## [Unreleased]

+### Added
+
+- JSON output format for the `list` command
+- Custom expiration times for shortened URLs
+
+### Changed
+
+- Extracted URL validation into a separate module
+- Bumped Python requirement to 3.11
+
+### Fixed
+
+- URLs with trailing slashes are now handled correctly
+- Crash prevented when the database file is missing
+
 ## [1.1.0] - 2026-03-15
```

## release-notes.md — payload for `gh release create`

Human-readable markdown rendered from the JSON payload. Designed to be
piped straight into `gh release create v1.2.0 --notes-file release-notes.md`.

```markdown
# Release v1.2.0 — 2026-05-11

## Added

- JSON output format for the `list` command
- Custom expiration times for shortened URLs

## Changed

- Extracted URL validation into a separate module
- Bumped Python requirement to 3.11

## Fixed

- URLs with trailing slashes are now handled correctly
- Crash prevented when the database file is missing
```

## summary.md — full pipeline report

Combined metadata + JSON payload + diff. Useful as a PR comment so a
reviewer sees both the structured contract and the actual file change in
one place.

```markdown
# Release notes pipeline report

- **Timestamp:** 2026-05-11-002455
- **Suggested version:** v1.2.0
- **Release date:** 2026-05-11
- **Sections:** Added, Changed, Fixed
- **Items total:** 6
- **Cost (USD):** 0.038
- **Duration (ms):** 18421
- **Turns:** 4

## Agent JSON payload

(JSON object matching the schema)

## CHANGELOG diff (apply with `git apply changelog.patch`)

(diff block)
```

## Why three artifacts

- **`changelog.patch`**: a real, apply'able artefact. A reviewer can read
  it, inline-comment, or `git apply` into another branch / worktree.
- **`release-notes.md`**: payload-ready for `gh release create` so the
  GitHub release page gets the same content the CHANGELOG got.
- **`summary.md`**: rollup for PR comments and Slack — combines the
  structured JSON, the raw diff, and the run metadata in one file.

In production the `[would-run] gh release create ...` line gets replaced
with a real `subprocess.run(["gh", "release", "create", ...])` call (or the
equivalent GitLab / Bitbucket release API). Same payload, real side effect.

## Trust but verify — the schema check + commit coverage check

The script does two independent post-checks the agent cannot bypass:

1. **Schema validation** — every section title must be one of `Added`,
   `Changed`, `Fixed`, `Removed`; every section must have at least one
   item; top-level `version` / `release_date` / `sections` are required.
2. **Commit coverage** — for each commit between the latest tag and
   `HEAD`, we check that a head-substring of its subject appears somewhere
   in either the JSON or the new CHANGELOG section. Catches "agent
   silently dropped commit #5" failures.

Both checks happen **after** `query()` returns, independent of what the
agent claimed in its JSON. Trust model: agent suggests, script verifies,
human approves.
