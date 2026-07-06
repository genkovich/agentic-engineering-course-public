#!/usr/bin/env bash
#
# seed-history.sh — turn this folder into a fresh repo with a realistic
# Conventional-Commit history. Run it once, right after you copy the folder out
# and `cd` into it:
#
#     cp -R 9.7-release-docs ~/my-release-demo && cd ~/my-release-demo
#     ./seed-history.sh
#
# It tags the current files as v0.1.0 (the "released" baseline that
# docs/CHANGELOG.md and docs/api.md already describe), then lands a mix of
# feat/fix/refactor commits plus noise (chore/test/merge) on top. That gives
# `git log v0.1.0..HEAD` something real to curate — the input for the release
# skills and workflows.
#
# The first feat — `feat: filter notes by tag` — is the release driver: it adds
# a NoteBook.filter_by_tag METHOD that docs/api.md (frozen at v0.1.0) does not
# list. One commit drives the whole pipeline: feat -> MINOR bump (v0.2.0) -> an
# `Added` changelog line -> release notes -> and a real docs drift the
# check-docs-drift tool catches in docs/api.md.
#
set -euo pipefail

if git rev-parse --git-dir >/dev/null 2>&1 && git rev-parse HEAD >/dev/null 2>&1; then
  echo "This folder already has commits. Run seed-history.sh in a fresh copy." >&2
  exit 1
fi

git init -q
git config user.name "Demo Author"
git config user.email "demo@example.com"

commit() { git add -A && git commit -q -m "$1"; }

# --- v0.1.0 baseline: everything shipped so far -----------------------------
commit "chore: import 0.1.0 baseline"
git branch -M main
git tag v0.1.0

# --- [Unreleased] work: this is what a release will curate -------------------

# feat: filter notes by tag — a METHOD on NoteBook (the release driver).
# Appended while NoteBook is still the last block in the file, so the 4-space
# indented def lands INSIDE the class. docs/api.md (baseline) does not list it
# yet — that gap is the doc drift the pipeline catches on HEAD.
cat >> src/notes.py <<'PY'

    def filter_by_tag(self, tag):
        """Return the notes carrying the given tag."""
        return [n for n in self._notes.values() if tag in n.tags]
PY
commit "feat: filter notes by tag"

# fix: keep tags unique
cat >> src/notes.py <<'PY'


def dedupe_tags(note):
    """Remove duplicate tags, preserving first-seen order."""
    note.tags = list(dict.fromkeys(note.tags))
    return note
PY
commit "fix: keep note tags unique"

# feat: export a notebook to a JSON string
cat > src/export.py <<'PY'
"""Export a notebook to a JSON string (no file needed)."""

import json


def to_json(book):
    return json.dumps([vars(n) for n in book.list()], indent=2)
PY
commit "feat: export a notebook to a JSON string"

# chore: tooling-only — should be dropped from the changelog
cat > .editorconfig <<'CFG'
root = true

[*]
indent_style = space
indent_size = 4
CFG
commit "chore: add .editorconfig"

# fix: clearer error when the notes file is missing
cat >> src/storage.py <<'PY'


def load_or_empty(path):
    """Load notes from path, or return an empty NoteBook if it is missing."""
    import os

    if not os.path.exists(path):
        return NoteBook()
    return load(path)
PY
commit "fix: report a clear error when the notes file is missing"

# refactor: single construction point for an empty notebook
cat >> src/notes.py <<'PY'


def new_notebook():
    """Build an empty notebook from one place."""
    return NoteBook()
PY
commit "refactor: extract a default-notebook factory"

# test: noise — should be dropped from the changelog
mkdir -p tests
cat > tests/test_storage.py <<'PY'
"""Round-trip check for storage.save / storage.load."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import storage  # noqa: E402
from notes import NoteBook  # noqa: E402


def test_round_trip(tmp_path):
    book = NoteBook()
    book.add("hello", "world", ["greeting"])
    path = tmp_path / "notes.json"
    storage.save(book, path)
    again = storage.load(path)
    assert again.list()[0].title == "hello"
PY
commit "test: cover storage save/load round-trip"

# feat on a short-lived branch, merged with --no-ff (the merge commit is noise)
git checkout -q -b feat/search
cat >> src/notes.py <<'PY'


def search(book, query):
    """Return notes whose title or body contains the query (case-insensitive)."""
    q = query.lower()
    return [n for n in book.list() if q in n.title.lower() or q in n.body.lower()]
PY
commit "feat: full-text search across notes"
git checkout -q main
git merge -q --no-ff feat/search -m "Merge branch 'feat/search'"
git branch -q -d feat/search

echo
echo "Seeded. v0.1.0 is tagged; here is the raw input a release will curate:"
echo
git log v0.1.0..HEAD --oneline --no-merges
echo
echo "The next version is decided deterministically from these commits:"
echo "  ./scripts/next-version.sh        # prints 0.2.0 (a feat landed -> MINOR)"
echo "And the docs already drifted — filter_by_tag is undocumented:"
echo "  ./scripts/check-docs-drift.py    # flags NoteBook.filter_by_tag"
echo
echo "Next: run the /release orchestrator in a Claude session (or each skill —"
echo "/bump-version, /curate-changelog, /release-notes, /check-docs-drift), or"
echo "push to GitHub and 'git tag v0.2.0 && git push origin v0.2.0' to fire CI."
