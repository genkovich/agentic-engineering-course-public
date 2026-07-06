You are drafting a short pull-request comment that explains the next version
this change would release. The deterministic script has already computed the
number — it is in the `NEXT_VERSION` environment variable (e.g. `0.2.0`), and
the current released version is in `CURRENT_VERSION` (e.g. `0.1.0`).

## Workflow

1. Read `NEXT_VERSION` and `CURRENT_VERSION`. The number is decided by the rule
   in `scripts/next-version.sh` — do not recompute it; explain it.
2. Run `git log <last-tag>..HEAD --oneline` and identify the strongest change
   that drove the bump: a `BREAKING CHANGE` → MAJOR, a `feat:` → MINOR, only
   `fix:` → PATCH.
3. Write a short comment: state the proposed bump (`CURRENT_VERSION → NEXT_VERSION`),
   name which part moved (MAJOR/MINOR/PATCH), and point at the deciding commit
   in one plain sentence (e.g. "MINOR — a new capability landed: `feat: filter
   notes by tag`").

## Constraints

- **Do not edit any file.** This is a comment only.
- The number comes from the script; you explain it, you do not change it.
- Keep it to a few sentences.

## Final output

Print the Markdown comment body to stdout (plain text, no JSON wrapper).
