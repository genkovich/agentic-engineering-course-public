---
name: audit-pytest-file
description: Use when reviewing one Python test file for production-readiness — runs pytest as a black-box probe and surfaces failed tests, fixture errors, slow tests, empty files, all-skipped suites, and collection failures. Trigger when the user names a single test file path to audit, asks "are these tests OK", asks for a structured pytest health check on one file, or wants to grade test signal-to-noise.
allowed-tools: Bash(uv run *), Bash(pytest *), Bash(python *), Bash(test *), Read, Glob, Grep
disable-model-invocation: false
context: fork
agent: Explore
argument-hint: '[file]'
model: opus-4-7
effort: xhigh
---

# audit-pytest-file

Goal: produce a structured audit of one Python test file by running pytest against it and surfacing defects the engineer can fix in the same pass.

## Workflow

Use this checklist literally. Mark each step done before moving to the next.

- [ ] Step 1: Plan. Read `templates/audit-report.md` so you know the output shape. Run `uv run ${CLAUDE_SKILL_DIR}/scripts/audit_pytest.py --help` and confirm the flags exist.
- [ ] Step 2: Pre-flight. Run `test -f "$0" && echo ok || echo missing` to confirm the file exists, then `pytest --version 2>&1 | head -1` to confirm the runner is installed. If either fails, stop and tell the user (no point auditing a file pytest cannot reach).
- [ ] Step 3: Run the probe. Run exactly:

  ```
  uv run ${CLAUDE_SKILL_DIR}/scripts/audit_pytest.py --file "$0" --format json
  ```

  Do not modify the command. The script returns exit code 0 (no blocking findings) or 1 (findings present). Any other code is a usage error and must be reported as-is.

- [ ] Step 4: Validate. Parse the JSON. If `findings` is empty, write a short report saying so. Otherwise group findings by `category`.
- [ ] Step 5: Render. Use the template in `templates/audit-report.md`. Fill every section. Do not invent findings the script did not produce.

## Якщо файл не передано

When the user asks "audit my tests" without naming a file, do not guess. Ask one clarifying question — which file? Suggest concrete candidates first:

1. The test file the user is currently editing or that recently failed in CI.
2. A test file that owns a critical workflow (auth, billing, ingestion).
3. A specific module's test file when the user names a module.

Ask for the path relative to the project root (`tests/test_users.py`), not just a test name — the probe runs pytest against a file path.

## Calling the probe (rigid part)

The script is the source of truth. Run exactly the command in Step 3. Do not write your own pytest invocation, do not add `-k` filters, do not skip the run because "the file looks fine". Findings come from the script or they do not exist.

If the project uses a wrapped pytest (poetry, uv, custom shim), pass it explicitly: append `--pytest "uv run pytest"` (or `--pytest "poetry run pytest"`) to Step 3. Default is `pytest`.

If a single test file legitimately takes longer than the default 60-second timeout (large fixture, integration smoke), pass `--timeout 180`. Do not raise it casually — the timeout exists so a hung subprocess does not freeze the audit.

## Gotchas

- The script needs `uv` on PATH. If `uv run` fails with `command not found`, instruct the user to install uv (https://docs.astral.sh/uv) and stop.
- `pytest` itself must be installed in the environment that imports the test file. The script delegates to whatever `pytest` is on PATH — it does not bundle its own copy. If `pytest --version` fails, the user needs to install pytest in their project (`pip install pytest`, `uv add pytest`, or activate the project venv) before the audit can run.
- `--report-log` is provided by the **pytest-reportlog plugin**, not by core pytest. If the script reports `category: runner` with exit 4, the plugin is missing; tell the user to `pip install pytest-reportlog` (or `uv add --dev pytest-reportlog`). Alternatively, override the runner with `--pytest "uv run --with pytest --with pytest-reportlog pytest"` for an ad-hoc audit that does not require touching the project's deps.
- Conftest.py in parent directories will be loaded — that is pytest's normal behaviour, not a tool bug. Tests that depend on session-scope fixtures will work; tests that depend on app-level state (DB, cache, network) may fail in audit context. That failure is a finding ("test depends on external state and cannot run in isolation"), not a tool bug.
- 0 tests collected is a finding, not a tool bug. Common causes: file accidentally renamed off the `test_*.py` pattern, `pytestmark = pytest.mark.skip` at module level, conftest filtering everything out, all tests marked `@pytest.mark.skip`. Surface the warning verbatim.
- Slow threshold defaults to 0.5s per test. For IO-heavy or integration suites that is too aggressive — pass `--slow-threshold 5.0`. Do not disable the check; raise the bar.
- Output truncation: by default the JSON includes only the first 3 findings plus a `truncated: true` flag. Pass `--full` if you need every finding for a long report.
- Tests that print to stdout will not corrupt the audit — the report log is written to a separate file. But if a test calls `sys.exit()` or kills the runner, the log will be incomplete; that surfaces as a `category: collection` error in our output.
- A failed assertion is a finding, not necessarily a defect. The script reports outcomes; you decide which matter for the user's intent. Failures in tests that were already known broken (e.g. an open bug ticket) are still worth surfacing — they belong in the report so the user can confirm the bug is still reproducing.

## Output format

Use `templates/audit-report.md`. Keep the structure even if some sections are empty (write "no findings" instead of omitting the section).

## When NOT to use this skill

- Auditing a whole `tests/` directory or the project's full suite. The probe deliberately scopes to one file; for whole-project audits, use a higher-level orchestrator that calls this skill per file (or use a dedicated reporting plugin like `pytest-html`).
- Static-only review (assertion count, AAA structure, naming conventions, mocking discipline). The probe is runtime — it sees only what pytest reports. For static review, pair with a separate AST-based skill.
- Coverage analysis. The probe does not run with `coverage` enabled; it reports outcomes and durations only. For coverage gaps, run `pytest --cov` separately.
- Flakiness detection. One run cannot tell flaky from genuinely failing — re-run the file 10x with a different tool if you suspect flakes.
- Non-pytest test files (raw `unittest`, `nose`, `doctest`-only modules). The script depends on pytest's `--report-log`, which has no equivalent in those runners. pytest can collect `unittest.TestCase` subclasses, so unittest-style tests inside a pytest-discoverable file are fine; standalone `unittest` mains are not.
