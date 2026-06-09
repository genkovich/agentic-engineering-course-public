#!/usr/bin/env bash
# setup-fixture.sh — thin wrapper around setup_fixture.py.
#
# The fixture content lives in setup_fixture.py (single source of truth,
# runs the same on macOS / Linux / Windows). This wrapper keeps the
# `bash setup-fixture.sh` command from the recorded screencasts working.
#
# Usage
#   bash setup-fixture.sh           # creates ./fixture-repo
#   bash setup-fixture.sh --force   # wipe and recreate
#
# Windows: run `python setup_fixture.py` directly — see ../../../WINDOWS.md.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec python3 "$SCRIPT_DIR/setup_fixture.py" "$@"
