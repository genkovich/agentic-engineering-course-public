# Audit report: {file}

**pytest exit code:** {pytest_returncode}
**Date:** {date}
**Verdict:** {pass_or_fail}

## Summary

{one or two sentences: how many findings, what severity dominates, is the file shippable as-is}

## Findings

### {category} - {severity}

**What:** {message}
**Suggested fix:** {one-line proposal, or "out of scope of runtime audit"}

(repeat per finding; if there are none, write "No findings - the runtime probe did not flag this file")

## Verification steps already performed

- [x] File existence check
- [x] pytest runner version check
- [x] Collection (file is parseable and discoverable)
- [x] Per-test outcomes (passed / failed / errored / skipped)
- [x] Per-test duration (slow tests flagged)
- [x] All-skipped detection (no signal warning)

## Out of scope

- Coverage (line / branch coverage gaps; run `pytest --cov` separately)
- Static review (assertion count, AAA structure, mocking discipline)
- Flakiness (one run cannot distinguish flaky from broken)
- Cross-file or session-level state pollution (this scopes to one file)

## Next step proposed

{exactly one action the user can take next, e.g. "fix the failing assertion in tests/test_users.py::test_login_with_token" or "raise --slow-threshold to 5s for the IO-heavy suite"}
