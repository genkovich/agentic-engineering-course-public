#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Audit a single Python test file at runtime via pytest --report-log.

Black-box probe: invokes pytest as a subprocess, parses the JSON Lines report
log, surfaces production-readiness defects in the test file.

Checks:
  * collection: file is discoverable, importable, has tests
  * outcomes: failed tests, errored fixtures, all-skipped suites
  * durations: tests slower than --slow-threshold
  * summary: per-file pass count

JSON to stdout, diagnostics to stderr.
Exit code 0 means no blocking findings, 1 means findings present, 2 means usage error.

Examples:
  uv run scripts/audit_pytest.py --file tests/test_users.py
  uv run scripts/audit_pytest.py --file tests/test_slow.py --slow-threshold 5
  uv run scripts/audit_pytest.py --file tests/test_x.py --pytest "uv run pytest"
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass


@dataclass
class Finding:
    severity: str  # error | warning | info
    category: str  # collection | failed | fixture | slow | skipped | summary | runner
    message: str


def log(msg: str) -> None:
    print(f"[audit] {msg}", file=sys.stderr)


def run_pytest(pytest_cmd: str, file: str, timeout: float) -> tuple[int, str, str, list[dict]]:
    """Invoke pytest with --report-log, return (returncode, stdout, stderr, events)."""
    fd, report_path = tempfile.mkstemp(prefix="audit_pytest_", suffix=".jsonl")
    os.close(fd)
    try:
        cmd = shlex.split(pytest_cmd) + [
            file,
            "-p", "no:cacheprovider",
            f"--report-log={report_path}",
            "--tb=line",
            "-q",
            "--no-header",
            "--durations=0",
            "-rN",
        ]
        log(f"running: {shlex.join(cmd)}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        events: list[dict] = []
        with open(report_path, encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return proc.returncode, proc.stdout, proc.stderr, events
    finally:
        try:
            os.unlink(report_path)
        except FileNotFoundError:
            pass


def _short_longrepr(event: dict) -> str | None:
    """Extract a short single-line message from a TestReport longrepr."""
    lr = event.get("longrepr")
    if lr is None:
        return None
    if isinstance(lr, dict):
        crash = lr.get("reprcrash") or {}
        msg = crash.get("message")
        if msg:
            first = msg.splitlines()[0] if msg else ""
            return first[:160]
        return None
    if isinstance(lr, str):
        first = lr.strip().splitlines()[0] if lr.strip() else None
        return first[:160] if first else None
    if isinstance(lr, (list, tuple)) and len(lr) >= 3:
        return str(lr[2])[:160]
    return None


def _skip_reason(event: dict) -> str | None:
    lr = event.get("longrepr")
    raw: str | None = None
    if isinstance(lr, (list, tuple)) and len(lr) >= 3:
        raw = str(lr[2])
    elif isinstance(lr, str):
        raw = lr
    if raw is None:
        return None
    s = raw.strip()
    if s.startswith("Skipped:"):
        s = s[len("Skipped:"):].strip()
    return s or None


def _effective_outcome(phases: dict[str, dict]) -> str:
    """Collapse setup/call/teardown phases into a single outcome per test."""
    setup = phases.get("setup")
    call = phases.get("call")
    teardown = phases.get("teardown")
    if setup and setup.get("outcome") == "failed":
        return "errored"
    if teardown and teardown.get("outcome") == "failed":
        return "errored"
    if call:
        return call.get("outcome", "unknown")
    if setup and setup.get("outcome") == "skipped":
        return "skipped"
    return "unknown"


def audit(events: list[dict], slow_threshold: float, returncode: int) -> list[Finding]:
    findings: list[Finding] = []

    test_phases: dict[str, dict[str, dict]] = {}
    collect_errors: list[dict] = []

    for ev in events:
        rtype = ev.get("$report_type")
        if rtype == "CollectReport" and ev.get("outcome") == "failed":
            collect_errors.append(ev)
        elif rtype == "TestReport":
            nodeid = ev.get("nodeid", "?")
            phase = ev.get("when", "call")
            test_phases.setdefault(nodeid, {})[phase] = ev

    for ev in collect_errors:
        location = ev.get("nodeid") or ev.get("path") or "?"
        msg = _short_longrepr(ev) or "collection failed"
        findings.append(Finding("error", "collection", f"{location}: {msg}"))

    if not test_phases and not collect_errors:
        if returncode == 5:
            findings.append(Finding(
                "warning", "collection",
                "no tests collected — file may be empty, all tests filtered out, "
                "or marked skip at module level",
            ))
        elif returncode == 4:
            findings.append(Finding(
                "error", "runner",
                "pytest rejected the audit invocation (exit 4) and produced no reports. "
                "Most likely cause: the pytest-reportlog plugin is missing. "
                "Install it: pip install pytest-reportlog (or uv add --dev pytest-reportlog).",
            ))
        elif returncode != 0:
            findings.append(Finding(
                "error", "runner",
                f"pytest exited {returncode} with no test reports — "
                "check stderr for the actual failure",
            ))

    for nodeid, phases in test_phases.items():
        eff = _effective_outcome(phases)
        setup = phases.get("setup")
        call = phases.get("call")
        teardown = phases.get("teardown")

        if eff == "errored":
            failed_phase = None
            for phase_name in ("setup", "teardown"):
                ph = phases.get(phase_name)
                if ph and ph.get("outcome") == "failed":
                    failed_phase = (phase_name, ph)
                    break
            if failed_phase:
                phase_name, ph = failed_phase
                msg = _short_longrepr(ph) or f"{phase_name} failed"
                findings.append(Finding(
                    "error", "fixture",
                    f"{nodeid}: {phase_name} failed — {msg}",
                ))
        elif eff == "failed" and call:
            msg = _short_longrepr(call) or "assertion failed"
            findings.append(Finding("error", "failed", f"{nodeid}: {msg}"))
        elif eff == "skipped":
            skip_ev = (call if call and call.get("outcome") == "skipped" else setup) or {}
            reason = _skip_reason(skip_ev)
            if not reason or reason.lower() in {"unconditional skip", ""}:
                findings.append(Finding(
                    "info", "skipped",
                    f"{nodeid}: skipped without an explicit reason",
                ))

        total_dur = 0.0
        for p in ("setup", "call", "teardown"):
            d = (phases.get(p) or {}).get("duration") or 0.0
            try:
                total_dur += float(d)
            except (TypeError, ValueError):
                pass
        if total_dur > slow_threshold:
            findings.append(Finding(
                "warning", "slow",
                f"{nodeid}: ran in {total_dur:.2f}s (threshold {slow_threshold:.2f}s)",
            ))

    if test_phases:
        outcomes = [_effective_outcome(p) for p in test_phases.values()]
        if outcomes and all(o == "skipped" for o in outcomes):
            findings.append(Finding(
                "warning", "skipped",
                "every test in the file was skipped — the file produces no signal",
            ))

        passed = sum(1 for o in outcomes if o == "passed")
        total = len(test_phases)
        findings.append(Finding(
            "info", "summary",
            f"{passed}/{total} tests passed",
        ))

    return findings


def render_markdown(file: str, findings: list[Finding]) -> str:
    out = [f"# Audit: {file}", ""]
    if not findings:
        out.append("No findings.")
        return "\n".join(out)
    for f in findings:
        out.append(f"## [{f.severity}] {f.category}")
        out.append(f"- {f.message}")
        out.append("")
    return "\n".join(out)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="audit_pytest",
        description="Probe one Python test file with pytest and report defects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run scripts/audit_pytest.py --file tests/test_users.py\n"
            "  uv run scripts/audit_pytest.py --file tests/test_slow.py --slow-threshold 5\n"
            "  uv run scripts/audit_pytest.py --file tests/test_x.py --pytest \"uv run pytest\"\n"
        ),
    )
    p.add_argument("--file", required=True, help="path to the Python test file to audit")
    p.add_argument("--format", choices=["json", "markdown"], default="json", help="output format (default: json)")
    p.add_argument("--full", action="store_true", help="emit every finding instead of the first 3")
    p.add_argument("--pytest", default="pytest", metavar="CMD",
                   help="pytest command (default: pytest). Use 'uv run pytest' or 'poetry run pytest' for wrapped runners.")
    p.add_argument("--timeout", type=float, default=60.0, help="subprocess timeout in seconds (default: 60)")
    p.add_argument("--slow-threshold", type=float, default=0.5,
                   help="threshold in seconds above which a test is flagged as slow (default: 0.5)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if not os.path.isfile(args.file):
        print(f"Error: --file does not exist or is not a file: {args.file!r}", file=sys.stderr)
        return 2

    log(f"auditing {args.file}")
    try:
        rc, stdout, stderr, events = run_pytest(args.pytest, args.file, args.timeout)
    except FileNotFoundError as e:
        print(f"Error: cannot run pytest: {e}", file=sys.stderr)
        print("Install pytest in the project, or pass --pytest 'uv run pytest'.", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(f"Error: pytest timed out after {args.timeout}s on {args.file}", file=sys.stderr)
        print("Pass --timeout <seconds> to allow more, or check for hung tests / fixtures.", file=sys.stderr)
        return 1

    findings = audit(events, args.slow_threshold, rc)

    if args.format == "markdown":
        print(render_markdown(args.file, findings))
    else:
        payload = {
            "file": args.file,
            "pytest_returncode": rc,
            "events_seen": len(events),
            "findings": [asdict(f) for f in findings],
            "summary": f"{len(findings)} finding(s)",
        }
        if not args.full and len(findings) > 3:
            payload["findings"] = [asdict(f) for f in findings[:3]]
            payload["truncated"] = True
            payload["hint"] = "pass --full to print every finding"
        print(json.dumps(payload, indent=2))

    blocking = [f for f in findings if f.severity in ("error", "warning")]
    return 0 if not blocking else 1


if __name__ == "__main__":
    sys.exit(main())
