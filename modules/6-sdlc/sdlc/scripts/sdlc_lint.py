#!/usr/bin/env python3
"""Repo-local checks for SDLC artifacts.

The script intentionally uses Python stdlib only. If PyYAML is already
available in the environment, OpenAPI files get a stronger YAML parse; if not,
the fallback validates the root structure used by SDLC contracts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
INLINE_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
PLACEHOLDER_RE = re.compile(r"<([A-Za-z][A-Za-z0-9_.:/ -]{0,80})>")
ADR_STATUS_RE = re.compile(r"(?im)^\s*(?:-\s*)?\*\*Status:\*\*\s*([A-Za-z -]+)\s*$")
TODAY = dt.date.today()


CORE_REQUIRED = [
    "idea-brief.md",
    "SPEC.md",
    "architecture-brief.md",
    "task-breakdown.md",
    "claude-context.md",
    "review-checklist.md",
    "kb-note.md",
]

MVP_REQUIRED = CORE_REQUIRED + [
    "diagrams/c4-container.md",
    "api/openapi.yaml",
]

FULL_REQUIRED = MVP_REQUIRED + [
    "arc42.md",
    "diagrams/c4-context.md",
    "diagrams/c4-component.md",
    "diagrams/deployment.md",
    "data-model.md",
    "migration-plan.md",
    "rollback-plan.md",
    "api/events.md",
    "test-plan.md",
    "feature-rollout-plan.md",
    "security-review.md",
]

METADATA_FILES = {
    "idea-brief.md",
    "SPEC.md",
    "architecture-brief.md",
    "data-model.md",
    "task-breakdown.md",
    "claude-context.md",
    "test-plan.md",
    "review-checklist.md",
    "kb-note.md",
    "security-review.md",
    "feature-rollout-plan.md",
}

METADATA_KEYS = {
    "status",
    "owner",
    "reviewers",
    "updated_at",
    "feature_size",
    "stage",
    "ticket",
}


@dataclass
class Issue:
    path: Path
    line: int
    message: str

    def format(self, root: Path) -> str:
        rel = self.path.relative_to(root) if self.path.is_relative_to(root) else self.path
        return f"{rel}:{self.line}: {self.message}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_markdown(root: Path) -> Iterable[Path]:
    ignored = {".git", "node_modules", ".venv", "venv"}
    for path in root.rglob("*.md"):
        if any(part in ignored for part in path.parts):
            continue
        yield path


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def strip_code_and_comments(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    fenced = False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("\n")
            continue
        if fenced:
            out.append("\n")
            continue
        line = re.sub(r"`[^`\n]*`", "", line)
        line = re.sub(r"<!--.*?-->", "", line)
        out.append(line)
    return "".join(out)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    data: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def feature_dirs(root: Path) -> list[Path]:
    dirs: list[Path] = []
    for parent_name in ("delivery", "examples"):
        parent = root / parent_name
        if not parent.exists():
            continue
        for child in sorted(parent.iterdir()):
            if child.is_dir() and not child.name.startswith("_"):
                dirs.append(child)
    return dirs


def feature_size(feature: Path) -> str:
    candidates = [
        feature / "idea-brief.md",
        feature / "SPEC.md",
        feature / "PRD.md",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = read_text(path)
        fm = parse_frontmatter(text)
        size = fm.get("feature_size", "").upper()
        if size in {"XS", "S", "M", "L", "XL"}:
            return size
        match = re.search(r"(?im)^\*\*Rough size:\*\*\s*(XS|S|M|L|XL)\s*$", text)
        if match:
            return match.group(1).upper()
    return "M"


def check_markdown_links(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in iter_markdown(root):
        text = read_text(path)
        for match in INLINE_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if target.startswith("app://") or target.startswith("plugin://"):
                continue
            if "<" in target or ">" in target:
                continue
            clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not clean:
                continue
            candidate = (path.parent / clean).resolve()
            if not candidate.exists():
                issues.append(Issue(path, line_number(text, match.start(1)), f"broken local link: {target}"))
    return issues


def check_placeholders(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for feature in feature_dirs(root):
        for path in feature.rglob("*.md"):
            text = read_text(path)
            searchable = strip_code_and_comments(text)
            for match in PLACEHOLDER_RE.finditer(searchable):
                value = match.group(1).strip()
                if value.lower().startswith("br/"):
                    continue
                issues.append(Issue(path, line_number(searchable, match.start()), f"unresolved placeholder: <{value}>"))
    return issues


def check_required_artifacts(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for feature in feature_dirs(root):
        size = feature_size(feature)
        required = FULL_REQUIRED if size in {"M", "L", "XL"} else MVP_REQUIRED
        for rel in required:
            if not (feature / rel).exists():
                issues.append(Issue(feature, 1, f"missing required artifact for {size}: {rel}"))

        if (feature / "adr").exists() and not list((feature / "adr").glob("*.md")) and size in {"M", "L", "XL"}:
            issues.append(Issue(feature / "adr", 1, f"missing ADR document for {size} feature"))
    return issues


def check_metadata(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for feature in feature_dirs(root):
        for path in feature.rglob("*.md"):
            rel_name = path.relative_to(feature).as_posix()
            if rel_name not in METADATA_FILES:
                continue
            fm = parse_frontmatter(read_text(path))
            missing = sorted(METADATA_KEYS - set(fm))
            if missing:
                issues.append(Issue(path, 1, f"missing frontmatter keys: {', '.join(missing)}"))
    return issues


def check_adr_status(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for feature in feature_dirs(root):
        # Trigger when feature has a task-breakdown (stage 13) — ADRs must be Accepted before tasks.
        if not (feature / "task-breakdown.md").exists() and not (feature / "tasks" / "_epic.md").exists():
            continue
        adr_dir = feature / "adr"
        if not adr_dir.exists():
            continue
        for adr in sorted(adr_dir.glob("*.md")):
            text = read_text(adr)
            fm_status = parse_frontmatter(text).get("status", "")
            match = ADR_STATUS_RE.search(text)
            body_status = match.group(1).strip() if match else ""
            status = (body_status or fm_status).lower()
            if status != "accepted":
                issues.append(Issue(adr, 1, "ADR must be Accepted before task-breakdown (stage 13)"))
    return issues


def yaml_available_parse(path: Path) -> tuple[bool, str | None]:
    try:
        import yaml  # type: ignore
    except Exception:
        return False, None

    try:
        data = yaml.safe_load(read_text(path))
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        return True, str(exc)

    if not isinstance(data, dict):
        return True, "OpenAPI root must be a mapping"
    for key in ("openapi", "info", "paths"):
        if key not in data:
            return True, f"OpenAPI missing root key: {key}"
    if not isinstance(data.get("paths"), dict):
        return True, "OpenAPI paths must be a mapping"
    return True, None


def fallback_openapi_check(path: Path) -> str | None:
    text = read_text(path)
    if "\t" in text:
        return "YAML contains tabs; use spaces"
    root_keys: set[str] = set()
    for idx, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            root_keys.add(line.split(":", 1)[0].strip())
        if line.startswith(" ") and (len(line) - len(line.lstrip(" "))) % 2 != 0:
            return f"odd indentation at line {idx}; use 2-space YAML indentation"
    for key in ("openapi", "info", "paths"):
        if key not in root_keys:
            return f"OpenAPI missing root key: {key}"
    if not re.search(r"(?m)^openapi:\s*3\.", text):
        return "OpenAPI version must start with 3.x"
    if not re.search(r"(?m)^paths:\s*$", text):
        return "OpenAPI paths root must be present"
    if "responses:" not in text:
        return "OpenAPI must define at least one responses block"
    return None


def check_openapi(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for feature in feature_dirs(root):
        for path in sorted((feature / "api").glob("openapi.y*ml")) if (feature / "api").exists() else []:
            parsed, parse_error = yaml_available_parse(path)
            error = parse_error if parsed else fallback_openapi_check(path)
            if error:
                issues.append(Issue(path, 1, f"invalid OpenAPI YAML/structure: {error}"))
    return issues


def run_checks(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(check_markdown_links(root))
    issues.extend(check_placeholders(root))
    issues.extend(check_required_artifacts(root))
    issues.extend(check_metadata(root))
    issues.extend(check_adr_status(root))
    issues.extend(check_openapi(root))
    return issues


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value[:10])
    except Exception:
        return None


def artifact_statuses(feature: Path) -> list[tuple[Path, dict[str, str]]]:
    result: list[tuple[Path, dict[str, str]]] = []
    for path in feature.rglob("*.md"):
        fm = parse_frontmatter(read_text(path))
        if fm:
            result.append((path, fm))
    return result


def metrics(root: Path) -> str:
    dirs = feature_dirs(root)
    lines = [
        "# SDLC metrics",
        "",
        f"Features scanned: {len(dirs)}",
        "",
        "| Feature | Size | Required coverage | Statuses | Stale artifacts |",
        "|---|---|---:|---|---:|",
    ]

    complete_mplus = 0
    total_mplus = 0
    stale_total = 0

    for feature in dirs:
        size = feature_size(feature)
        required = FULL_REQUIRED if size in {"M", "L", "XL"} else MVP_REQUIRED
        present = sum(1 for rel in required if (feature / rel).exists())
        coverage = round((present / len(required)) * 100) if required else 100

        statuses: dict[str, int] = {}
        stale = 0
        for _, fm in artifact_statuses(feature):
            status = fm.get("status", "unknown").strip() or "unknown"
            statuses[status] = statuses.get(status, 0) + 1
            date = parse_date(fm.get("updated_at", ""))
            if status.lower() in {"draft", "review"} and date and (TODAY - date).days > 30:
                stale += 1

        if size in {"M", "L", "XL"}:
            total_mplus += 1
            if coverage == 100:
                complete_mplus += 1
        stale_total += stale

        status_text = ", ".join(f"{key}:{value}" for key, value in sorted(statuses.items())) or "n/a"
        rel = feature.relative_to(root).as_posix()
        lines.append(f"| {rel} | {size} | {coverage}% | {status_text} | {stale} |")

    pct = round((complete_mplus / total_mplus) * 100) if total_mplus else 100
    lines.extend(
        [
            "",
            f"M+ complete DoR artifact coverage: {pct}% ({complete_mplus}/{total_mplus})",
            f"Stale Draft/Review artifacts (>30d): {stale_total}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint SDLC artifacts")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--metrics", action="store_true", help="Print static process metrics instead of linting")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.metrics:
        print(metrics(root))
        return 0

    issues = run_checks(root)
    if issues:
        for issue in issues:
            print(issue.format(root), file=sys.stderr)
        print(f"\nSDLC check failed: {len(issues)} issue(s)", file=sys.stderr)
        return 1

    print("SDLC check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
