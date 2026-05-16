You are generating release notes for the next version of this project. The
project keeps its changelog in `docs/CHANGELOG.md` following the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention with
`### Added / Changed / Fixed / Removed` sections.

## Workflow

1. **Read `docs/CHANGELOG.md`** to learn the project's existing style and to
   find the most recently released version. The latest released version is
   the highest version under a dated `## [X.Y.Z] - YYYY-MM-DD` heading —
   ignore the `## [Unreleased]` entry, which is what you will be filling in.
2. **Run `git log <latest-tag>..HEAD --oneline --no-merges`** to list every
   commit added since that release. The tag name matches the version (e.g.
   `v1.1.0` for `[1.1.0]`).
3. **Read `docs/README.md`** for project context — gives you tone and
   terminology to match.
4. **Categorize each commit** into one of the four sections by inspecting
   the conventional-commit prefix:
   - `feat:` → **Added**
   - `fix:` → **Fixed**
   - `refactor:` / `chore:` / `perf:` / `style:` → **Changed**
   - explicit removals → **Removed**
   Rewrite each commit subject as a short, user-facing bullet (drop the
   `feat:` / `fix:` prefix and make it readable to a non-engineer).
5. **Edit `docs/CHANGELOG.md`**: replace the empty `## [Unreleased]` section
   with the new entries. Keep the `## [Unreleased]` heading itself — it
   stays on top so the next release cycle can repeat the process.
6. (Optional) **Re-read `docs/CHANGELOG.md`** to confirm the edit applied
   cleanly and the formatting matches the prior releases.

## Constraints

- **Do not commit or push.** Edits stay in the working tree as a suggestion;
  a human reviewer applies them.
- **Do not edit `src/`, `tests/`, or anything outside `docs/`.**
- Each bullet must be one line, no trailing period.
- Use exactly these section titles: `Added`, `Changed`, `Fixed`, `Removed`.
  Skip any section that has no entries — don't emit empty sections.
- Match the formatting of the existing v1.1.0 / v1.0.0 entries (blank line
  after each `###` heading, `-` bullets).

## Final output

Return a JSON object describing what you wrote, matching the requested
schema. The fields:

- `version`: the next semver bump you'd suggest, based on the commit mix.
  Any `feat:` since the last tag → minor bump; otherwise patch. Format
  `"X.Y.Z"`, no leading `v`.
- `release_date`: today's date as `YYYY-MM-DD`.
- `sections`: array of `{title, items[]}` matching the categorized bullets,
  in the order `Added → Changed → Fixed → Removed` (omit empty ones).

The JSON must mirror the bullets you wrote into the CHANGELOG. A reviewer
will diff them — they must agree.
