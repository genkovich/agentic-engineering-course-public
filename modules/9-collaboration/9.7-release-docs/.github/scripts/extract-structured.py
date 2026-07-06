#!/usr/bin/env python3
"""Pull the schema'd structured output out of a `claude -p` response.

Generic over the schema — used by both changelog.yml and release-notes.yml to
recover whatever structured object the agent returned.

`claude -p --output-format json` returns the full event stream as a JSON
array. Some events (e.g. Read tool results) embed raw tab characters in their
strings, which makes the array invalid under a strict JSON parser like jq.
`json.loads(..., strict=False)` tolerates those control characters, so we parse
here in Python and hand jq a clean object downstream.

Usage: extract-structured.py <response.json> <out.json>
Logs cost/turns, exits 1 if the agent reported an error, and writes the
schema'd structured output to <out.json>.
"""

import json
import sys


def main(resp_path, out_path):
    with open(resp_path, encoding="utf-8") as fh:
        data = json.loads(fh.read(), strict=False)

    events = data if isinstance(data, list) else [data]
    results = [m for m in events if isinstance(m, dict) and m.get("type") == "result"]
    result = results[-1] if results else (data if isinstance(data, dict) else {})

    cost = result.get("total_cost_usd", "n/a")
    duration = result.get("duration_ms", "n/a")
    turns = result.get("num_turns", "n/a")
    is_error = result.get("is_error", False)
    print(f"[claude] cost=${cost} duration={duration}ms turns={turns} is_error={is_error}")

    if is_error:
        print(f"::error::claude failed: {result.get('result')}")
        return 1

    notes = result.get("structured_output")
    if notes is None:
        raw = result.get("result", "")
        try:
            notes = json.loads(raw)
        except (TypeError, ValueError):
            print("::error::no structured output and result was not JSON")
            return 1

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(notes, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
