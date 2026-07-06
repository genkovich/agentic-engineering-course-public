#!/usr/bin/env bash
#
# next-version.sh — print the next semver from the commit history. NO LLM.
#
# This is the deterministic half of versioning. It reads the Conventional-Commit
# types landed since the last tag and applies the semver rule mechanically:
#
#     BREAKING CHANGE  -> MAJOR   (X+1.0.0)
#     feat:            -> MINOR   (X.Y+1.0)
#     fix: (only)      -> PATCH   (X.Y.Z+1)
#
# The strongest change in the batch wins. The `bump-version` skill calls this
# script for the number, then explains in plain language *why* that part moved
# and edits pyproject.toml — but the number itself is decided here, by a rule,
# not by a model.
#
# Usage:  ./scripts/next-version.sh
# Prints the next version with no leading `v` (e.g. `0.2.0`), or the current
# version unchanged if nothing release-worthy landed.
#
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# --- current version: the highest vX.Y.Z tag (the released baseline) ---------
last_tag="$(git tag --list 'v*' --sort=-v:refname | head -n1)"
if [[ -z "$last_tag" ]]; then
  echo "no v* tag found — tag a baseline (e.g. v0.1.0) first" >&2
  exit 1
fi
current="${last_tag#v}"
IFS=. read -r major minor patch <<<"$current"

# --- scan commits since the last tag for the strongest change type -----------
log="$(git log "${last_tag}..HEAD" --format='%s%n%b')"

bump="none"
if grep -qE 'BREAKING CHANGE|^[a-z]+(\([^)]*\))?!:' <<<"$log"; then
  bump="major"
elif grep -qE '^feat(\([^)]*\))?:' <<<"$log"; then
  bump="minor"
elif grep -qE '^fix(\([^)]*\))?:' <<<"$log"; then
  bump="patch"
fi

case "$bump" in
  major) echo "$((major + 1)).0.0" ;;
  minor) echo "${major}.$((minor + 1)).0" ;;
  patch) echo "${major}.${minor}.$((patch + 1))" ;;
  none)  echo "$current" ;;   # nothing release-worthy since the last tag
esac
