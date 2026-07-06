You are curating the changelog for a release that was just tagged. The project
keeps its changelog in `docs/CHANGELOG.md` following the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention with
`### Added / Changed / Fixed / Removed` sections.

The released version is the tag that fired this run — it is in the `TAG`
environment variable (e.g. `v0.2.0`). The version string is `TAG` without the
leading `v`.

## Workflow

1. **Read `docs/CHANGELOG.md`** to learn the style and find the most recently
   released version — the highest dated `## [X.Y.Z] - YYYY-MM-DD` heading.
2. **Run `git log <previous-tag>..HEAD --oneline --no-merges`** to list every
   commit since that release. `<previous-tag>` is the previous released version
   (e.g. `v0.1.0`); the new one is `TAG`.
3. **Drop the noise first** — leave these out entirely: `chore:`, `ci:`,
   `build:`, `test:`, `style:`, and merge commits. Then **categorize what
   remains** by Conventional-Commit prefix:
   - `feat:` → **Added**
   - `fix:` → **Fixed**
   - `refactor:` / `perf:` → **Changed**
   - explicit removals → **Removed**
   Rewrite each remaining subject as a short, user-facing bullet (drop the
   `feat:`/`fix:` prefix, plain language).
4. **Promote `[Unreleased]` into the released version.** Replace the
   `## [Unreleased]` section with a new dated heading `## [<version>] - <today>`
   holding the curated entries, and keep a fresh empty `## [Unreleased]` on top
   for the next cycle.

## Constraints

- **Do not commit or push.** Edits stay in the working tree as a suggestion; a
  human reviewer applies them via the Release-PR.
- **Do not edit anything outside `docs/`.**
- Each bullet is one line, no trailing period.
- Use exactly these section titles: `Added`, `Changed`, `Fixed`, `Removed`.
  Omit any section with no entries.
- Curate, don't dump. Group several commits about one feature into a single
  bullet; the changelog must have fewer lines than the raw `git log`.

## Final output

Return a JSON object matching the requested schema:

- `version`: `TAG` without the leading `v`, format `"X.Y.Z"`.
- `release_date`: today's date as `YYYY-MM-DD`.
- `sections`: array of `{title, items[]}` in the order
  `Added → Changed → Fixed → Removed` (omit empty ones).

The JSON must mirror the bullets you wrote into the CHANGELOG — a reviewer will
diff them; they must agree.
