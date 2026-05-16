#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Audit a single HTTP endpoint at runtime for common production-readiness defects.

Black-box probe: fires one HTTP request, inspects the response.
Language- and framework-agnostic — works against any HTTP server.

Checks:
  * status code (2xx/3xx/4xx/5xx classification, reachability)
  * Content-Type header (present? matches body shape?)
  * body shape (valid JSON if claimed, basic plain text otherwise)
  * cache-related headers (info: Cache-Control, ETag, Last-Modified)
  * /health vs /ready hint (uptime-only health pattern)
  * wall-clock response time (info)

JSON to stdout, diagnostics to stderr.
Exit code 0 means no findings, 1 means findings present, 2 means usage error.

Examples:
  uv run scripts/audit_endpoint.py --url http://localhost:3000/health
  uv run scripts/audit_endpoint.py --url https://api.example.com/users/me --format markdown
  uv run scripts/audit_endpoint.py --url https://api.example.com/me --header "Authorization: Bearer $TOKEN"
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass


@dataclass
class Finding:
    severity: str  # error | warning | info
    category: str  # reachability | status | content_type | body | health | cache | latency
    message: str


def log(msg: str) -> None:
    print(f"[audit] {msg}", file=sys.stderr)


def probe(url: str, headers: list[str], timeout: float, follow: bool, insecure: bool):
    """Fire one GET request. Returns (status, headers_dict, body_bytes, elapsed_ms) or raises."""
    req = urllib.request.Request(url, method="GET")
    for h in headers:
        if ":" not in h:
            raise ValueError(f"--header must be 'Name: Value', got: {h!r}")
        name, _, value = h.partition(":")
        req.add_header(name.strip(), value.strip())

    ctx = None
    if insecure and url.startswith("https://"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    opener_args = {"timeout": timeout}
    if ctx is not None:
        opener_args["context"] = ctx

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, **opener_args) as resp:  # type: ignore[arg-type]
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if not follow and 300 <= resp.status < 400:
                return resp.status, dict(resp.headers), b"", elapsed_ms
            body = resp.read(1024 * 64)  # cap at 64 KiB
            return resp.status, dict(resp.headers), body, elapsed_ms
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        body = e.read(1024 * 64) if e.fp else b""
        return e.code, dict(e.headers or {}), body, elapsed_ms


def audit(url: str, status: int, headers: dict, body: bytes, elapsed_ms: int) -> list[Finding]:
    findings: list[Finding] = []

    if status >= 500:
        findings.append(Finding("error", "status", f"server error: {status} — endpoint is broken"))
    elif status >= 400:
        findings.append(Finding("warning", "status", f"client error: {status} — likely auth, missing path, or bad request"))
    elif status >= 300:
        findings.append(Finding("info", "status", f"redirect: {status} — pass --follow if you want the final response"))

    ct = headers.get("Content-Type") or headers.get("content-type")
    if ct is None:
        findings.append(Finding("warning", "content_type", "no Content-Type header — clients must guess"))
    else:
        ct_main = ct.split(";", 1)[0].strip().lower()
        if ct_main == "application/json":
            try:
                json.loads(body.decode("utf-8", errors="replace") or "null")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                findings.append(Finding("error", "body", f"Content-Type is application/json but body is not valid JSON: {e}"))
        elif body and ct_main.startswith("text/"):
            try:
                body.decode("utf-8")
            except UnicodeDecodeError:
                findings.append(Finding("warning", "body", f"Content-Type is {ct_main} but body is not valid UTF-8"))

    cache_hdrs = [h for h in ("Cache-Control", "ETag", "Last-Modified") if h in headers or h.lower() in headers]
    if not cache_hdrs and 200 <= status < 300:
        findings.append(Finding("info", "cache", "no Cache-Control / ETag / Last-Modified — every client refetches in full"))

    if "/health" in url and 200 <= status < 300:
        body_text = body.decode("utf-8", errors="replace").strip().lower()
        trivial = body_text in {"", "ok", "1", "true"} or body_text in {'{"status":"ok"}', '{"status": "ok"}'}
        if trivial:
            findings.append(Finding("info", "health", "uptime-only health response — consider a /ready endpoint that checks DB and downstreams"))

    if elapsed_ms > 1000:
        findings.append(Finding("warning", "latency", f"single-shot response took {elapsed_ms} ms — measure under load to confirm"))
    else:
        findings.append(Finding("info", "latency", f"single-shot response took {elapsed_ms} ms"))

    return findings


def render_markdown(url: str, status: int, findings: list[Finding]) -> str:
    out = [f"# Audit: {url}", "", f"**Status:** {status}", ""]
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
        prog="audit_endpoint",
        description="Probe one HTTP endpoint and report production-readiness defects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run scripts/audit_endpoint.py --url http://localhost:3000/health\n"
            "  uv run scripts/audit_endpoint.py --url https://api.example.com/me --header \"Authorization: Bearer $TOKEN\"\n"
            "  uv run scripts/audit_endpoint.py --url https://example.com --format markdown\n"
        ),
    )
    p.add_argument("--url", required=True, help="full URL to probe (http or https)")
    p.add_argument("--format", choices=["json", "markdown"], default="json", help="output format (default: json)")
    p.add_argument("--full", action="store_true", help="emit every finding instead of the first 3")
    p.add_argument("--header", action="append", default=[], metavar="NAME: VALUE", help="add a request header (repeatable)")
    p.add_argument("--insecure", action="store_true", help="skip TLS certificate verification")
    p.add_argument("--no-follow", action="store_true", help="do not follow 3xx redirects (default: follow)")
    p.add_argument("--timeout", type=float, default=5.0, help="request timeout in seconds (default: 5)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not (args.url.startswith("http://") or args.url.startswith("https://")):
        print(f"Error: --url must start with http:// or https://. Got: {args.url!r}", file=sys.stderr)
        return 2

    log(f"probing {args.url}")
    try:
        status, headers, body, elapsed_ms = probe(
            args.url, args.header, args.timeout, follow=not args.no_follow, insecure=args.insecure,
        )
    except urllib.error.URLError as e:
        print(f"Error: cannot reach {args.url}: {e.reason}", file=sys.stderr)
        return 1
    except (TimeoutError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    findings = audit(args.url, status, headers, body, elapsed_ms)

    if args.format == "markdown":
        print(render_markdown(args.url, status, findings))
    else:
        payload = {
            "url": args.url,
            "status": status,
            "elapsed_ms": elapsed_ms,
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
