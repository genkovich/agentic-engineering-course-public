# audit-pytest-file skill

Audit one Python test file for production-readiness defects: failing tests,
errored fixtures, slow tests, empty files, all-skipped suites. The skill is a
black-box runtime probe — it runs pytest against the file and turns the JSON
report log into a structured findings list. Pytest-specific.

## Install (personal scope)

Copy this directory into your personal skills folder:

```bash
cp -r .claude/skills/audit-pytest-file ~/.claude/skills/
```

The skill is self-contained — only `SKILL.md`, `scripts/audit_pytest.py`,
`templates/audit-report.md`, and this README live inside the skill directory.
Nothing else is required.

## Requirements

- [`uv`](https://docs.astral.sh/uv/) — runs the audit script and resolves its
  declared dependencies (the script is stdlib-only). Install:
  `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `pytest` 6.2+ installed in the environment that imports the test file. The
  skill delegates to `pytest` on PATH; it does not bundle its own version.
  Pass `--pytest "uv run pytest"` or `--pytest "poetry run pytest"` if your
  project uses a wrapped runner.
- `pytest-reportlog` plugin (provides `--report-log`, which the script needs
  to read structured pytest output). Install with
  `pip install pytest-reportlog` or `uv add --dev pytest-reportlog`. For an
  ad-hoc audit that does not touch the project's deps, pass
  `--pytest "uv run --with pytest --with pytest-reportlog pytest"` instead —
  uv pulls both into a one-shot venv.

That is it. No project layout assumptions, no `requirements.txt` for the skill
itself.

## Usage

In Claude Code:

```
/audit-pytest-file tests/test_users.py
/audit-pytest-file src/myapp/tests/test_billing.py
```

Standalone (without the skill harness):

```
uv run ~/.claude/skills/audit-pytest-file/scripts/audit_pytest.py \
  --file tests/test_users.py
```

## What it checks

- File exists and pytest can collect it (collection error → finding)
- Per-test outcome from pytest: failed / errored / skipped / passed
- Fixture and teardown failures (separated from test-body failures)
- Per-test duration above `--slow-threshold` (default 0.5s)
- All-skipped file (the suite produces no signal)
- Zero tests collected (file silently emits no signal)

## What it does NOT check

- Coverage. Run `pytest --cov` separately.
- Static structure (assertion count, AAA, naming, mocking discipline). Pair
  with an AST-based skill for that.
- Flakiness. One run cannot distinguish flaky from broken.
- Whole-suite or cross-file behaviour. The probe scopes to one file.
- Non-pytest test runners (raw `unittest`, `nose`, `doctest`-only). The script
  relies on pytest's `--report-log`, which has no equivalent there.
