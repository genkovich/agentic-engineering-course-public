#!/usr/bin/env bash
# setup-fixture.sh — recreate the deterministic fixture used by the
# Lecture 5.7 screencasts.
#
# What it does
#   Builds a tiny "url-shortener" project at ./fixture-repo/ with:
#     - Two existing releases (v1.0.0, v1.1.0) tagged in git history
#     - 6 unreleased commits since v1.1.0 (mix of feat/fix/refactor/chore)
#     - docs/CHANGELOG.md with prior releases populated and an empty
#       "## [Unreleased]" section ready for the agent to fill
#     - docs/README.md with project description for tone context
#     - Minimal src/ files so commits touch real code, not empty changes
#
# Why this fixture
#   The Lecture 5.7 demos illustrate Claude Agent SDK as an agent loop:
#   Read CHANGELOG → Bash git log → Read README → Edit CHANGELOG → Read CHANGELOG
#   (3-5 turns). The fixture must reliably reproduce the same git history
#   so both the recorded screencast and any student replay start identically.
#
# Usage
#   bash setup-fixture.sh           # creates ./fixture-repo
#   bash setup-fixture.sh --force   # wipe and recreate
#
# Idempotency
#   If ./fixture-repo already exists, exits with a hint unless --force.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FIXTURE_DIR="$SCRIPT_DIR/fixture-repo"
FORCE="${1:-}"

if [[ -e "$FIXTURE_DIR" ]]; then
  if [[ "$FORCE" == "--force" ]]; then
    echo "[setup-fixture] removing existing $FIXTURE_DIR"
    rm -rf "$FIXTURE_DIR"
  else
    echo "[setup-fixture] fixture-repo already exists at $FIXTURE_DIR"
    echo "[setup-fixture] pass --force to wipe and recreate"
    exit 0
  fi
fi

mkdir -p "$FIXTURE_DIR"
cd "$FIXTURE_DIR"

# ──────────────────────────────────────────────────────────────────
# Git init (local config, no global side effects)
# ──────────────────────────────────────────────────────────────────

git init --quiet --initial-branch=main
git config user.name "Demo Author"
git config user.email "demo@example.com"
git config commit.gpgsign false 2>/dev/null || true

commit_with_date() {
  local date="$1"
  local message="$2"
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
    git commit --quiet -m "$message"
}

# ──────────────────────────────────────────────────────────────────
# v1.0.0 — initial release
# ──────────────────────────────────────────────────────────────────

mkdir -p src docs

cat > pyproject.toml <<'EOF'
[project]
name = "url-shortener"
version = "1.0.0"
description = "Tiny local URL shortener CLI"
requires-python = ">=3.10"
EOF

cat > src/__init__.py <<'EOF'
EOF

cat > src/main.py <<'EOF'
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
EOF

cat > docs/README.md <<'EOF'
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
EOF

cat > docs/CHANGELOG.md <<'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-10

### Added

- Initial release with `shorten`, `list`, `delete` commands
- SQLite-backed local storage at `urls.db`
EOF

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
*.db
.venv/
EOF

git add -A
commit_with_date "2026-01-10T10:00:00" "feat: initial release with shorten/list/delete commands"
git tag v1.0.0

# ──────────────────────────────────────────────────────────────────
# Commits up to v1.1.0
# ──────────────────────────────────────────────────────────────────

cat > src/main.py <<'EOF'
"""url-shortener — tiny CLI for shortening URLs locally."""
import sys

DB_PATH = "urls.db"

COLOR_GREEN = "\033[32m"
COLOR_RESET = "\033[0m"


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
EOF
git add -A
commit_with_date "2026-02-20T12:00:00" "feat: add color output for terminal commands"

cat >> src/main.py <<'EOF'


def import_csv(path: str) -> int:
    """Bulk-import URLs from a CSV file. Returns number imported."""
    raise NotImplementedError
EOF
git add -A
commit_with_date "2026-03-01T15:30:00" "feat: support batch URL imports from CSV files"

cat >> src/main.py <<'EOF'


def _next_short_code() -> str:
    """Pick next unused short code under a write lock to avoid races."""
    raise NotImplementedError
EOF
git add -A
commit_with_date "2026-03-10T09:15:00" "fix: race condition when shortening URLs concurrently"

cat > docs/CHANGELOG.md <<'EOF'
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
EOF
sed -i.bak 's/version = "1.0.0"/version = "1.1.0"/' pyproject.toml && rm pyproject.toml.bak
git add -A
commit_with_date "2026-03-15T11:00:00" "chore: release v1.1.0"
git tag v1.1.0

# ──────────────────────────────────────────────────────────────────
# Commits since v1.1.0 — these will become the new Unreleased section
# ──────────────────────────────────────────────────────────────────

cat >> src/main.py <<'EOF'


def list_urls_json() -> str:
    """Same as list_urls but returns a JSON string."""
    raise NotImplementedError
EOF
git add -A
commit_with_date "2026-04-02T10:00:00" "feat: add JSON output format for list command"

cat >> src/main.py <<'EOF'


def set_expiration(short_code: str, ttl_seconds: int) -> None:
    """Attach a custom TTL to a shortened URL."""
    raise NotImplementedError
EOF
git add -A
commit_with_date "2026-04-10T14:30:00" "feat: support custom expiration times for shortened URLs"

cat >> src/main.py <<'EOF'


def _normalize(url: str) -> str:
    """Strip trailing slashes before storing/looking up."""
    return url.rstrip("/")
EOF
git add -A
commit_with_date "2026-04-15T16:00:00" "fix: handle URLs with trailing slashes correctly"

cat >> src/main.py <<'EOF'


def _ensure_db() -> None:
    """Create urls.db on first run instead of crashing."""
    raise NotImplementedError
EOF
git add -A
commit_with_date "2026-04-20T11:00:00" "fix: prevent crash when database file is missing"

cat > src/validation.py <<'EOF'
"""URL validation helpers extracted from main.py."""
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)
EOF
git add -A
commit_with_date "2026-04-25T13:00:00" "refactor: extract URL validation into separate module"

sed -i.bak 's/requires-python = ">=3.10"/requires-python = ">=3.11"/' pyproject.toml && rm pyproject.toml.bak
git add -A
commit_with_date "2026-05-01T09:00:00" "chore: bump Python requirement to 3.11"

# ──────────────────────────────────────────────────────────────────
# Verification — print state so the screencaster sees the fixture is ready
# ──────────────────────────────────────────────────────────────────

echo
echo "[setup-fixture] done. fixture-repo created at $FIXTURE_DIR"
echo
echo "[setup-fixture] tags:"
git tag -l | sed 's/^/  /'
echo
echo "[setup-fixture] commits since v1.1.0 (these are what the agent will summarise):"
git log v1.1.0..HEAD --oneline | sed 's/^/  /'
echo
echo "[setup-fixture] current docs/CHANGELOG.md '## [Unreleased]' section is empty —"
echo "[setup-fixture] running the demo will fill it in."
echo
echo "[setup-fixture] you're ready to record:"
echo "    cd sdk-cli    && make demo-fixture"
echo "    cd sdk-python && make demo-fixture"
