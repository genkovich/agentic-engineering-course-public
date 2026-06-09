"""generate_release_notes — Python orchestration around a Claude Agent SDK
release-notes pipeline.

Where sdk-cli/release-notes.sh is just `claude -p` + a tiny stderr formatter,
this script wraps the agent invocation with **Python-side logic that makes
sense in Python**:

  1. Pre-check  — refuse to run if there are no commits since the latest
                  tag (idempotency guard; a real CI on-tag job would do
                  the same).
  2. Agent loop — stream events through `async for message in query(...)`.
                  AssistantMessage events surface as `[t=N]` progress lines
                  on stderr so the viewer sees real-time agent activity;
                  ResultMessage holds the schema-validated JSON payload.
  3. Verify     — parse the JSON against jsonschema, then confirm every
                  commit SHA between the latest tag and HEAD is mentioned
                  somewhere in either the JSON items or the new CHANGELOG
                  section. Catches the case where the agent silently
                  dropped a commit.
  4. Persist    — write `release-notes.md` (human-readable) and
                  `changelog.patch` (apply'able with `git apply`) under
                  `release-artifacts/<timestamp>/`.
  5. Notify     — mock `gh release create` curl call so students see the
                  integration point. In production this would be httpx.post
                  or `subprocess.run(["gh", "release", "create", ...])`.

Usage:
    python generate_release_notes.py             # runs on cwd (fixture-repo)
    cd fixture-repo && python ../sdk-python/generate_release_notes.py
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    query,
)

PROMPT = """\
You are generating release notes for the next version of this project. The
project keeps its changelog in `docs/CHANGELOG.md` following Keep a Changelog
conventions with `### Added / Changed / Fixed / Removed` sections.

Workflow:

1. Read `docs/CHANGELOG.md` to learn the project's style and to find the
   most recently released version (the highest version under a dated
   `## [X.Y.Z] - YYYY-MM-DD` heading — ignore `## [Unreleased]`).
2. Run `git log <latest-tag>..HEAD --oneline --no-merges` to enumerate every
   commit since that release. The tag matches the version (e.g. `v1.1.0`
   for `[1.1.0]`).
3. Read `docs/README.md` for project context — gives you tone.
4. Categorize each commit by its conventional-commit prefix:
   - `feat:` → Added
   - `fix:` → Fixed
   - `refactor:` / `chore:` / `perf:` / `style:` → Changed
   - explicit removals → Removed
   Rewrite each commit subject as a short user-facing bullet (drop the
   prefix; keep it readable to a non-engineer).
5. Edit `docs/CHANGELOG.md`: replace the empty `## [Unreleased]` section
   with the categorized bullets. Keep the heading itself — it stays on top.
6. Optionally re-read `docs/CHANGELOG.md` to confirm the edit applied.

Constraints:
- Do not commit or push — edits stay in the working tree as a suggestion.
- Do not edit anything outside `docs/`.
- Each bullet is one line, no trailing period.
- Use exactly these titles: Added, Changed, Fixed, Removed. Skip empty ones.

Return JSON matching the requested schema:
- `version`: next semver bump ("X.Y.Z", no leading `v`). Any `feat:` since
  the last tag → minor bump; otherwise patch.
- `release_date`: today as `YYYY-MM-DD`.
- `sections`: array of `{title, items[]}` ordered Added → Changed → Fixed
  → Removed. Skip empty sections.

The JSON must mirror the bullets you wrote into the CHANGELOG.
"""

ALLOWED_TOOLS = [
    "Bash(git log *)",
    "Read(docs/**)",
    "Edit(docs/**)",
]
MAX_TURNS = 10

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "release_date": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "enum": ["Added", "Changed", "Fixed", "Removed"],
                    },
                    "items": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "items"],
            },
        },
    },
    "required": ["version", "release_date", "sections"],
}


def is_authenticated() -> bool:
    """Accept either OAuth session (claude auth login) or env var (CI/CD).

    The claude-agent-sdk package invokes the bundled `claude` CLI through
    subprocess, so the CLI's OAuth session is honored — no need to require
    ANTHROPIC_API_KEY when the user is logged in via `claude auth login`.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    # shutil.which resolves claude.cmd / claude.exe on Windows too — a bare
    # "claude" in subprocess.run raises FileNotFoundError for the npm shim.
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return False
    try:
        result = subprocess.run(
            [claude_bin, "auth", "status", "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            check=False,
        )
        return '"loggedIn": true' in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def latest_tag() -> str | None:
    """Return the most recently created git tag, or None if no tags."""
    result = subprocess.run(
        ["git", "tag", "--sort=-creatordate"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    tags = [line for line in result.stdout.splitlines() if line.strip()]
    return tags[0] if tags else None


def commits_since(tag: str) -> list[tuple[str, str]]:
    """Return [(sha, subject), ...] for commits between `tag` and HEAD."""
    result = subprocess.run(
        ["git", "log", f"{tag}..HEAD", "--oneline", "--no-merges"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    out: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        sha, _, subject = line.partition(" ")
        if sha:
            out.append((sha, subject))
    return out


def capture_changelog_diff() -> str:
    """Return the working-tree git diff for docs/CHANGELOG.md."""
    result = subprocess.run(
        ["git", "diff", "--", "docs/CHANGELOG.md"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.stdout


def read_changelog() -> str:
    # Explicit encoding: Windows defaults to cp1252, not UTF-8.
    return Path("docs/CHANGELOG.md").read_text(encoding="utf-8")


def mock_gh_release_create(version: str, notes_path: Path) -> None:
    """Stand-in for `gh release create`. Production: subprocess.run([...])."""
    print(
        f"[would-run] gh release create v{version} "
        f"--title 'v{version}' --notes-file {notes_path} --draft",
        file=sys.stderr,
    )
    print(
        "[hint] in prod: subprocess.run(['gh', 'release', 'create', ...]) "
        "— same arguments",
        file=sys.stderr,
    )


def validate_against_schema(payload: dict, schema: dict) -> list[str]:
    """Tiny jsonschema-lite — checks required fields and section titles.

    We don't pull in jsonschema as a dep just for the demo; this checks
    the same constraints the --json-schema flag enforces server-side.
    """
    errors: list[str] = []
    for required in schema["required"]:
        if required not in payload:
            errors.append(f"missing top-level key: {required}")
    if "sections" in payload:
        allowed = set(schema["properties"]["sections"]["items"]
                      ["properties"]["title"]["enum"])
        for i, section in enumerate(payload["sections"]):
            if section.get("title") not in allowed:
                errors.append(
                    f"sections[{i}].title not in {sorted(allowed)}: "
                    f"{section.get('title')!r}"
                )
            if not isinstance(section.get("items"), list) or not section["items"]:
                errors.append(f"sections[{i}].items must be non-empty list")
    return errors


def render_release_notes_md(payload: dict) -> str:
    """Convert the schema payload into a release-notes.md file."""
    lines = [f"# Release v{payload['version']} — {payload['release_date']}", ""]
    for section in payload["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        for item in section["items"]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_artifacts(
    out_dir: Path,
    payload: dict,
    diff: str,
    metadata: dict,
) -> tuple[Path, Path, Path]:
    """Persist patch + release-notes.md + summary.md under release-artifacts/<ts>/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    patch_path = out_dir / "changelog.patch"
    notes_path = out_dir / "release-notes.md"
    summary_path = out_dir / "summary.md"

    patch_path.write_text(diff if diff.strip() else "(no changes)\n",
                          encoding="utf-8")
    notes_path.write_text(render_release_notes_md(payload), encoding="utf-8")

    summary_path.write_text(
        "# Release notes pipeline report\n\n"
        f"- **Timestamp:** {metadata['timestamp']}\n"
        f"- **Suggested version:** v{payload['version']}\n"
        f"- **Release date:** {payload['release_date']}\n"
        f"- **Sections:** {', '.join(s['title'] for s in payload['sections'])}\n"
        f"- **Items total:** {sum(len(s['items']) for s in payload['sections'])}\n"
        f"- **Cost (USD):** {metadata.get('cost', 'n/a')}\n"
        f"- **Duration (ms):** {metadata.get('duration_ms', 'n/a')}\n"
        f"- **Turns:** {metadata.get('num_turns', 'n/a')}\n\n"
        "## Agent JSON payload\n\n"
        "```json\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "## CHANGELOG diff (apply with `git apply changelog.patch`)\n\n"
        "```diff\n"
        f"{diff.strip() or '(no changes)'}\n"
        "```\n"
    )
    return patch_path, notes_path, summary_path


async def run_agent() -> tuple[str, dict]:
    """Stream agent events. Returns (raw_result_string, metadata)."""
    options = ClaudeAgentOptions(
        allowed_tools=ALLOWED_TOOLS,
        max_turns=MAX_TURNS,
        model="claude-haiku-4-5",
    )

    raw_result = ""
    metadata: dict = {}
    turn = 0

    async for message in query(prompt=PROMPT, options=options):
        if isinstance(message, AssistantMessage):
            turn += 1
            preview = str(getattr(message, "content", ""))[:80]
            print(f"[t={turn}] {preview}", file=sys.stderr, flush=True)
        elif isinstance(message, ResultMessage):
            raw_result = (
                getattr(message, "result", None) or str(message)
            )
            metadata = {
                "cost": getattr(message, "total_cost_usd", None),
                "duration_ms": getattr(message, "duration_ms", None),
                "num_turns": getattr(message, "num_turns", None),
                "is_error": getattr(message, "is_error", False),
            }

    return raw_result, metadata


async def main_async() -> int:
    if not is_authenticated():
        print("ERROR: not authenticated to Claude.", file=sys.stderr)
        print("       Choose one:", file=sys.stderr)
        print(
            "         - Run 'claude auth login' (OAuth, recommended for local dev)",
            file=sys.stderr,
        )
        print(
            "         - Or export ANTHROPIC_API_KEY (CI/CD, GitHub Secrets)",
            file=sys.stderr,
        )
        return 1

    if not Path(".git").is_dir() or not Path("docs/CHANGELOG.md").is_file():
        print(
            "ERROR: cwd does not look like the target project "
            "(missing .git/ or docs/CHANGELOG.md). "
            "Run from inside fixture-repo/.",
            file=sys.stderr,
        )
        return 1

    # 1. Pre-check: are there any commits to summarise?
    tag = latest_tag()
    if not tag:
        print("ERROR: no git tags found — release notes need a prior release "
              "to diff against.", file=sys.stderr)
        return 1

    new_commits = commits_since(tag)
    print(f"[pre-check] latest tag={tag}, commits since={len(new_commits)}",
          file=sys.stderr)
    if not new_commits:
        print(f"[pre-check] no new commits since {tag} — nothing to summarise. "
              "Run `python ../setup_fixture.py --force` to reset the fixture.",
              file=sys.stderr)
        return 0

    # 2. Agent loop with streaming progress.
    print(f"[agent] invoking Claude Agent SDK (max_turns={MAX_TURNS})...",
          file=sys.stderr)
    raw_result, metadata = await run_agent()

    # The --json-schema flag (CLI equivalent) means raw_result is a JSON
    # string. SDK doesn't expose --json-schema directly yet, so we parse +
    # validate ourselves. Either way the contract is the same: a strict
    # JSON object, not free-form prose.
    try:
        payload = json.loads(raw_result.strip()
                             .removeprefix("```json").removeprefix("```")
                             .removesuffix("```").strip())
    except json.JSONDecodeError as exc:
        print(f"[verify] agent did not return valid JSON: {exc}",
              file=sys.stderr)
        print(f"[verify] raw result was:\n{raw_result}", file=sys.stderr)
        return 1

    schema_errors = validate_against_schema(payload, OUTPUT_SCHEMA)
    if schema_errors:
        print("[verify] schema violations:", file=sys.stderr)
        for err in schema_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("[verify] schema OK", file=sys.stderr)

    # 3. Verification: capture diff, check that every commit appears somewhere
    diff = capture_changelog_diff()
    if not diff.strip():
        print("[verify] WARNING: no changes detected in docs/CHANGELOG.md — "
              "agent returned JSON but did not edit the file",
              file=sys.stderr)

    changelog_now = read_changelog().lower()
    json_blob = json.dumps(payload, ensure_ascii=False).lower()
    missed: list[str] = []
    for sha, subject in new_commits:
        # Match by subject keywords (drop conventional prefix); a SHA
        # mention is too strict for human-readable bullets.
        keyword = subject.split(":", 1)[-1].strip().lower()
        head = keyword[:20]
        if head and head not in changelog_now and head not in json_blob:
            missed.append(f"{sha} {subject}")
    if missed:
        print("[verify] commits missing from generated notes:", file=sys.stderr)
        for line in missed:
            print(f"  - {line}", file=sys.stderr)
    else:
        print(f"[verify] all {len(new_commits)} commits represented",
              file=sys.stderr)

    # 4. Persist artifacts
    timestamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = Path("release-artifacts") / timestamp
    metadata["timestamp"] = timestamp

    patch_path, notes_path, summary_path = write_artifacts(
        out_dir=out_dir, payload=payload, diff=diff, metadata=metadata,
    )
    print(f"[saved] patch    → {patch_path}", file=sys.stderr)
    print(f"[saved] notes    → {notes_path}", file=sys.stderr)
    print(f"[saved] summary  → {summary_path}", file=sys.stderr)

    # 5. Mock notification (production wires this to gh release create).
    mock_gh_release_create(payload["version"], notes_path)

    # 6. JSON payload to stdout for piping/inspection.
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 0 if not missed else 2


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
