#!/usr/bin/env bash
# Ralph loop — canonical Geoffrey Huntley pattern with three safety nets.
# Lecture 7.2 (Module 7 · Execution & Scale).
#
# The loop is intentionally dumb: it re-runs ONE prompt against `claude -p`
# (headless, fresh context each turn) until the model creates a `DONE` file.
# Everything that survives between turns lives on disk (git, tracker), never
# in the model's memory.

set -euo pipefail

# --- Knobs (override via env) ---------------------------------------------
MAX_ITER="${MAX_ITER:-10}"          # Safety net 1: hard iteration ceiling
PROMPT_FILE="${PROMPT_FILE:-PROMPT.md}"
COST_LOG="${COST_LOG:-cost.log}"    # Safety net 2: per-turn audit trail
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"

ITER=0

if [ ! -f "$PROMPT_FILE" ]; then
  echo "No $PROMPT_FILE found. Generate one first (see README: /ralph-prep)." >&2
  exit 2
fi

echo "=== Ralph run started: $(date -Iseconds) (prompt=$PROMPT_FILE, max_iter=$MAX_ITER) ===" >> "$COST_LOG"

# --- Safety net 3: graceful Ctrl-C ----------------------------------------
trap 'echo "Interrupted at iteration $ITER. State preserved — check git status."' INT

# --- The loop -------------------------------------------------------------
while [ ! -f DONE ]; do
  ITER=$((ITER + 1))

  if [ "$ITER" -gt "$MAX_ITER" ]; then
    echo "Iteration limit ($MAX_ITER) reached. Exiting without DONE."
    echo "=== Hit MAX_ITER at $(date -Iseconds) ===" >> "$COST_LOG"
    exit 1
  fi

  echo "--- Iteration $ITER ---"
  echo "$(date -Iseconds) iter=$ITER" >> "$COST_LOG"

  # Cold start every turn: a fresh `claude -p` invocation with no accumulated
  # context. The model re-reads PROMPT.md and the current filesystem from
  # scratch — this is what prevents context rot on long runs.
  claude -p "$(cat "$PROMPT_FILE")" --permission-mode "$PERMISSION_MODE"

  sleep 1   # make Ctrl-C reliable between turns
done

echo "=== DONE found at $(date -Iseconds), total iterations: $ITER ===" >> "$COST_LOG"
echo "Ralph completed in $ITER iterations. Check 'git log' for results."
