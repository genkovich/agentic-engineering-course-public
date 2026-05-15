#!/usr/bin/env bash
# release-notes.sh — let Claude Agent SDK generate release notes from git
# history.
#
# Usage:
#   cd ../fixture-repo && ../sdk-cli/release-notes.sh
#
# Requirements:
#   - cwd is a git repository with at least one annotated/release tag and a
#     `docs/CHANGELOG.md` that follows Keep a Changelog conventions
#   - claude CLI in PATH
#   - jq
#   - Authenticated to Claude: either an active OAuth session
#     (`claude auth login`, recommended for local dev with Max/Pro/Team
#     subscription) or `ANTHROPIC_API_KEY` env var (CI/CD)
#
# What it demonstrates
#   - `claude -p` running headlessly with a real agent loop (3-5 turns:
#     Read CHANGELOG → Bash git log → Read README → Edit CHANGELOG → Read)
#   - Tight `--allowed-tools` prefix matching across three dimensions:
#     a Bash prefix, a Read directory glob, and an Edit directory glob
#   - `--max-turns` as a production budget guard
#   - `--output-format json` + `--json-schema` so the structured release
#     notes are validated against a schema, not parsed from prose
#   - `--model claude-haiku-4-5` — release notes is a structured rewriting
#     task (read → transform → write by schema), not a reasoning task.
#     Haiku handles it for cents on the dollar versus the default
#     Sonnet/Opus. Override if you want Sonnet.
#
# Trust model
#   Agent edits `docs/CHANGELOG.md` in the working tree as a *suggestion*.
#   The script does NOT commit or push. After the run, inspect `git diff`
#   and choose:
#     - `git restore docs/CHANGELOG.md`   — reject the suggestion
#     - `git add -p && git commit`        — accept it
#     - `git diff > release.patch &&
#        git apply release.patch elsewhere` — port to another worktree

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROMPT_FILE="$SCRIPT_DIR/prompts/generate-release-notes.md"

# ──────────────────────────────────────────────────────────────────
# Pre-flight
# ──────────────────────────────────────────────────────────────────

# Accept either OAuth session (claude auth login) or env var (CI/CD).
# Order matters: in CI the env var is always present, so we check it first
# and avoid invoking `claude auth status` (which may fail without OAuth).
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  : # env var present — OK
elif claude auth status --json 2>/dev/null | grep -q '"loggedIn": true'; then
  : # OAuth session active — OK
else
  echo "ERROR: not authenticated to Claude." >&2
  echo "       Choose one:" >&2
  echo "         - Run 'claude auth login' (OAuth, recommended for local dev)" >&2
  echo "         - Or export ANTHROPIC_API_KEY (CI/CD, GitHub Secrets)" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: claude CLI not found in PATH." >&2
  echo "       See https://docs.claude.com for installation." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not found in PATH." >&2
  exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "ERROR: prompt file missing: $PROMPT_FILE" >&2
  exit 1
fi

if [[ ! -d ".git" ]]; then
  echo "ERROR: cwd is not a git repository." >&2
  echo "       Expected to be invoked from inside fixture-repo/." >&2
  exit 1
fi

if [[ ! -f "docs/CHANGELOG.md" ]]; then
  echo "ERROR: docs/CHANGELOG.md not found." >&2
  echo "       Run setup-fixture.sh first." >&2
  exit 1
fi

if [[ -z "$(git tag -l)" ]]; then
  echo "ERROR: no git tags in cwd — release notes need a previous release to diff against." >&2
  exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"

# ──────────────────────────────────────────────────────────────────
# JSON schema — validated against Claude's final response
# ──────────────────────────────────────────────────────────────────
#
# This is the same schema used by sdk-python/generate_release_notes.py.
# Keep them in sync.

SCHEMA='{
  "type": "object",
  "properties": {
    "version":      {"type": "string"},
    "release_date": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string", "enum": ["Added", "Changed", "Fixed", "Removed"]},
          "items": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "items"]
      }
    }
  },
  "required": ["version", "release_date", "sections"]
}'

# ──────────────────────────────────────────────────────────────────
# Invoke Claude — real agent loop with three-dimensional permissions
# ──────────────────────────────────────────────────────────────────
#
# Permissions cheat-sheet (this is exactly Slide 8 in the lecture):
#   - Bash(git log *) — agent can run any `git log` invocation (and only
#                      that — `git tag`, `git push`, `rm` are blocked)
#   - Read(docs/**)  — agent can read everything under docs/ (CHANGELOG,
#                      README) but not src/, tests/, or root files
#   - Edit(docs/**)  — agent can only edit files under docs/, never src/
# Anything else (rm, git commit, curl, Write outside docs/, ...) is blocked.
#
# Three independent allowlist dimensions:
#   Bash → which shell commands
#   Read → which files can be read
#   Edit → which files can be modified
# This is the structure your CI/CD pipelines should mirror.
#
# --max-turns 6 is the production guardrail from Slide 13: enough for the
# 3-5 turn loop (Read CHANGELOG → Bash git log → Read README → Edit
# CHANGELOG → optional re-Read) with one turn of headroom.

RESPONSE="$(claude -p "$PROMPT" \
  --allowed-tools "Bash(git log *)" "Read(docs/**)" "Edit(docs/**)" \
  --model claude-haiku-4-5 \
  --output-format json \
  --json-schema "$SCHEMA" \
  --max-turns 6)"

# ──────────────────────────────────────────────────────────────────
# Normalize response shape across claude CLI versions
# ──────────────────────────────────────────────────────────────────
#
# Older claude (< 2.x): --output-format json returns a single object with
# `.result`, `.total_cost_usd`, `.is_error`, etc. at the top level.
# Newer claude (2.x+): same flag returns a JSON array of messages; the
# final element has `type: "result"` and carries those same fields.
# Pull the result-typed payload regardless of which shape we got.

RESULT_OBJ=$(echo "$RESPONSE" | jq -c '
  if type == "array"
  then (map(select(.type == "result")) | last // {})
  else .
  end
')

# ──────────────────────────────────────────────────────────────────
# Summary on stderr — cost, duration, turns, error status
# ──────────────────────────────────────────────────────────────────

COST=$(echo "$RESULT_OBJ" | jq -r '.total_cost_usd // "n/a"')
DURATION=$(echo "$RESULT_OBJ" | jq -r '.duration_ms // "n/a"')
TURNS=$(echo "$RESULT_OBJ" | jq -r '.num_turns // "n/a"')
IS_ERROR=$(echo "$RESULT_OBJ" | jq -r '.is_error // false')

echo "[claude] cost=\$${COST} duration=${DURATION}ms turns=${TURNS} is_error=${IS_ERROR}" >&2

if [[ "$IS_ERROR" == "true" ]]; then
  echo "[claude] agent reported an error — raw response below" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

# ──────────────────────────────────────────────────────────────────
# Schema-validated JSON payload → stdout
# ──────────────────────────────────────────────────────────────────
#
# Where the structured output lives depends on CLI version:
#   - claude 2.x+: `.structured_output` is a native JSON object built from
#     the response and validated against --json-schema.
#   - claude < 2.x: `.result` is a JSON string (also validated).
# Fall back to raw `.result` if neither shape parses — at least the viewer
# still sees what the agent said.

echo "$RESULT_OBJ" | jq '
  if (.structured_output // null) != null
  then .structured_output
  else (.result as $r | try ($r | fromjson) catch $r)
  end
'

# ──────────────────────────────────────────────────────────────────
# Trust-but-verify: show the actual git diff so the viewer sees exactly
# what the agent changed (separate from the JSON the agent returned).
# ──────────────────────────────────────────────────────────────────

echo >&2
echo "--- actual git diff (what agent edited in the working tree) ---" >&2
git diff -- docs/CHANGELOG.md >&2 || true
echo "--- end git diff ---" >&2
echo >&2
echo "[hint] inspect the diff above. To accept: git add -p && git commit." >&2
echo "[hint] To reject:                  git restore docs/CHANGELOG.md" >&2
echo "[hint] To port elsewhere:          git diff -- docs/CHANGELOG.md > release.patch && git apply release.patch" >&2
