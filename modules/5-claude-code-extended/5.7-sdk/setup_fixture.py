#!/usr/bin/env python3
"""setup_fixture.py — recreate the deterministic fixture used by the
Lecture 5.7 screencasts.

What it does
  Builds a tiny "url-shortener" project at ./fixture-repo/ with:
    - Two existing releases (v1.0.0, v1.1.0) tagged in git history
    - 6 unreleased commits since v1.1.0 (mix of feat/fix/refactor/chore)
    - docs/CHANGELOG.md with prior releases populated and an empty
      "## [Unreleased]" section ready for the agent to fill
    - docs/README.md with project description for tone context
    - Minimal src/ files so commits touch real code, not empty changes

Why this fixture
  The Lecture 5.7 demos illustrate Claude Agent SDK as an agent loop:
  Read CHANGELOG → Bash git log → Read README → Edit CHANGELOG → Read CHANGELOG
  (3-5 turns). The fixture must reliably reproduce the same git history
  so both the recorded screencast and any student replay start identically.

Why Python
  Runs the same on macOS, Linux, and Windows — no bash, no sed, no make.
  stdlib only; the only external requirement is `git` in PATH.
  `setup-fixture.sh` is a thin wrapper around this script, kept so the
  command shown in the recorded screencasts still works.

Usage
  python setup_fixture.py           # creates ./fixture-repo
  python setup_fixture.py --force   # wipe and recreate

Idempotency
  If ./fixture-repo already exists, exits with a hint unless --force.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = SCRIPT_DIR / "fixture-repo"

# ──────────────────────────────────────────────────────────────────
# File contents — byte-identical to what the original bash heredocs
# produced (LF line endings, trailing newline).
# ──────────────────────────────────────────────────────────────────

PYPROJECT_V1 = '''\
[project]
name = "url-shortener"
version = "1.0.0"
description = "Tiny local URL shortener CLI"
requires-python = ">=3.10"
'''

MAIN_V1 = '''\
"""url-shortener — tiny CLI for shortening URLs locally."""
import sys

DB_PATH = "urls.db"


def shorten(url: str) -> str:
    """Insert URL, return short code."""
    raise NotImplementedError


def list_urls() -> list:
    """List all shortened URLs."""
    raise NotImplementedError


def delete(short_code: str) -> None:
    """Delete a URL by short code."""
    raise NotImplementedError


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: url-shortener {shorten|list|delete} ...")
        sys.exit(1)
'''

DOCS_README = '''\
# url-shortener

A tiny CLI tool for shortening URLs locally on your machine. Useful for
sharing links inside private notes or team chat where you don't want to
depend on an external service.

## Install

```
pip install url-shortener
```

## Usage

```
url-shortener shorten https://example.com/long/path
url-shortener list
url-shortener delete <short-code>
```

URLs are stored in a local SQLite database (`urls.db`). No network calls.

See `CHANGELOG.md` for what's new in each release.
'''

CHANGELOG_V1 = '''\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-10

### Added

- Initial release with `shorten`, `list`, `delete` commands
- SQLite-backed local storage at `urls.db`
'''

GITIGNORE = '''\
__pycache__/
*.pyc
*.db
.venv/
'''

MAIN_V2 = '''\
"""url-shortener — tiny CLI for shortening URLs locally."""
import sys

DB_PATH = "urls.db"

COLOR_GREEN = "\\033[32m"
COLOR_RESET = "\\033[0m"


def shorten(url: str) -> str:
    raise NotImplementedError


def list_urls() -> list:
    raise NotImplementedError


def delete(short_code: str) -> None:
    raise NotImplementedError


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: url-shortener {shorten|list|delete} ...")
        sys.exit(1)
'''

APPEND_IMPORT_CSV = '''\


def import_csv(path: str) -> int:
    """Bulk-import URLs from a CSV file. Returns number imported."""
    raise NotImplementedError
'''

APPEND_NEXT_SHORT_CODE = '''\


def _next_short_code() -> str:
    """Pick next unused short code under a write lock to avoid races."""
    raise NotImplementedError
'''

CHANGELOG_V2 = '''\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-03-15

### Added

- Color output for terminal commands
- Batch URL imports from CSV files via `import` subcommand

### Fixed

- Race condition when shortening multiple URLs concurrently

## [1.0.0] - 2026-01-10

### Added

- Initial release with `shorten`, `list`, `delete` commands
- SQLite-backed local storage at `urls.db`
'''

APPEND_LIST_URLS_JSON = '''\


def list_urls_json() -> str:
    """Same as list_urls but returns a JSON string."""
    raise NotImplementedError
'''

APPEND_SET_EXPIRATION = '''\


def set_expiration(short_code: str, ttl_seconds: int) -> None:
    """Attach a custom TTL to a shortened URL."""
    raise NotImplementedError
'''

APPEND_NORMALIZE = '''\


def _normalize(url: str) -> str:
    """Strip trailing slashes before storing/looking up."""
    return url.rstrip("/")
'''

APPEND_ENSURE_DB = '''\


def _ensure_db() -> None:
    """Create urls.db on first run instead of crashing."""
    raise NotImplementedError
'''

VALIDATION_PY = '''\
"""URL validation helpers extracted from main.py."""
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)
'''


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def git(*args: str, env_extra: dict[str, str] | None = None,
        check: bool = True, capture: bool = False) -> str:
    """Run git inside fixture-repo. Returns stdout when capture=True."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        ["git", *args],
        cwd=FIXTURE_DIR,
        env=env,
        check=check,
        capture_output=capture,
        text=True,
    )
    return result.stdout if capture else ""


def write(rel_path: str, content: str) -> None:
    """Write file with LF endings regardless of platform."""
    path = FIXTURE_DIR / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def append(rel_path: str, content: str) -> None:
    with open(FIXTURE_DIR / rel_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def replace_in_file(rel_path: str, old: str, new: str) -> None:
    path = FIXTURE_DIR / rel_path
    text = path.read_text(encoding="utf-8")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.replace(old, new))


def commit_with_date(date: str, message: str) -> None:
    git("commit", "--quiet", "-m", message,
        env_extra={"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date})


def indent(block: str) -> str:
    return "\n".join(f"  {line}" for line in block.splitlines())


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    force = "--force" in argv[1:]

    if FIXTURE_DIR.exists():
        if force:
            print(f"[setup-fixture] removing existing {FIXTURE_DIR}")
            shutil.rmtree(FIXTURE_DIR)
        else:
            print(f"[setup-fixture] fixture-repo already exists at {FIXTURE_DIR}")
            print("[setup-fixture] pass --force to wipe and recreate")
            return 0

    FIXTURE_DIR.mkdir(parents=True)

    # Git init (local config, no global side effects)
    git("init", "--quiet", "--initial-branch=main")
    git("config", "user.name", "Demo Author")
    git("config", "user.email", "demo@example.com")
    git("config", "commit.gpgsign", "false", check=False)
    # Keep LF endings in the working tree even on Windows with autocrlf=true,
    # so diffs and replays look identical across platforms.
    git("config", "core.autocrlf", "false")

    # v1.0.0 — initial release
    write("pyproject.toml", PYPROJECT_V1)
    write("src/__init__.py", "")
    write("src/main.py", MAIN_V1)
    write("docs/README.md", DOCS_README)
    write("docs/CHANGELOG.md", CHANGELOG_V1)
    write(".gitignore", GITIGNORE)
    git("add", "-A")
    commit_with_date("2026-01-10T10:00:00",
                     "feat: initial release with shorten/list/delete commands")
    git("tag", "v1.0.0")

    # Commits up to v1.1.0
    write("src/main.py", MAIN_V2)
    git("add", "-A")
    commit_with_date("2026-02-20T12:00:00",
                     "feat: add color output for terminal commands")

    append("src/main.py", APPEND_IMPORT_CSV)
    git("add", "-A")
    commit_with_date("2026-03-01T15:30:00",
                     "feat: support batch URL imports from CSV files")

    append("src/main.py", APPEND_NEXT_SHORT_CODE)
    git("add", "-A")
    commit_with_date("2026-03-10T09:15:00",
                     "fix: race condition when shortening URLs concurrently")

    write("docs/CHANGELOG.md", CHANGELOG_V2)
    replace_in_file("pyproject.toml",
                    'version = "1.0.0"', 'version = "1.1.0"')
    git("add", "-A")
    commit_with_date("2026-03-15T11:00:00", "chore: release v1.1.0")
    git("tag", "v1.1.0")

    # Commits since v1.1.0 — these will become the new Unreleased section
    append("src/main.py", APPEND_LIST_URLS_JSON)
    git("add", "-A")
    commit_with_date("2026-04-02T10:00:00",
                     "feat: add JSON output format for list command")

    append("src/main.py", APPEND_SET_EXPIRATION)
    git("add", "-A")
    commit_with_date("2026-04-10T14:30:00",
                     "feat: support custom expiration times for shortened URLs")

    append("src/main.py", APPEND_NORMALIZE)
    git("add", "-A")
    commit_with_date("2026-04-15T16:00:00",
                     "fix: handle URLs with trailing slashes correctly")

    append("src/main.py", APPEND_ENSURE_DB)
    git("add", "-A")
    commit_with_date("2026-04-20T11:00:00",
                     "fix: prevent crash when database file is missing")

    write("src/validation.py", VALIDATION_PY)
    git("add", "-A")
    commit_with_date("2026-04-25T13:00:00",
                     "refactor: extract URL validation into separate module")

    replace_in_file("pyproject.toml",
                    'requires-python = ">=3.10"', 'requires-python = ">=3.11"')
    git("add", "-A")
    commit_with_date("2026-05-01T09:00:00",
                     "chore: bump Python requirement to 3.11")

    # Verification — print state so the screencaster sees the fixture is ready
    print()
    print(f"[setup-fixture] done. fixture-repo created at {FIXTURE_DIR}")
    print()
    print("[setup-fixture] tags:")
    print(indent(git("tag", "-l", capture=True).rstrip("\n")))
    print()
    print("[setup-fixture] commits since v1.1.0 (these are what the agent will summarise):")
    print(indent(git("log", "v1.1.0..HEAD", "--oneline", capture=True).rstrip("\n")))
    print()
    print("[setup-fixture] current docs/CHANGELOG.md '## [Unreleased]' section is empty —")
    print("[setup-fixture] running the demo will fill it in.")
    print()
    print("[setup-fixture] you're ready to record:")
    print("    cd sdk-cli    && make demo-fixture")
    print("    cd sdk-python && make demo-fixture")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
