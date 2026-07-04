#!/usr/bin/env python3
"""lint.py - шар 0: статичний лінт конфігурації, НУЛЬ токенів (`make check`).

Агент не запускається. Лінт читає ТЕКСТ конфігурації і ловить дешеві регресії:
  1. Frontmatter агентів: allowlist tools збігається з очікуваним контрактом
     (диф `+Edit, +Write` у ro-reviewer червоніє тут - безкоштовно, за секунду).
  2. settings.json усіх конфігів парсяться; guard-конфіг таки МІСТИТЬ deny.
  3. Синтаксис харнесу і грейдерів (py_compile).
  4. Структура кейсів: prompt.md + case.json + check.py + expect.md,
     fixture і stage-джерела існують.

Чому цього шару МАЛО і потрібен run.py: статика бачит текст конфігурації,
а не поведінку. Bash-обхід (sed -i без Edit), накази в body, взаємодія з
CLAUDE.md, недетермінізм моделі - усе це видно лише в реальному прогоні.
Але як нижній щабель лінт обов'язковий: він у CI на кожен PR.
"""
import json
import py_compile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from checks import BOLD, RESET, Checker, agent_tools, parse_frontmatter  # noqa: E402

AGENT_DIR = Path(__file__).resolve().parent
PKG_ROOT = AGENT_DIR.parent.parent
CASES_DIR = AGENT_DIR / "cases"
FIXTURES_DIR = PKG_ROOT / "fixtures"

# Контракт конфігурації: очікуваний allowlist кожного агента пакета.
# Новий агент у .claude/agents/ без запису тут - теж помилка лінта:
# контракт мусить бути свідомим.
EXPECTED_AGENT_TOOLS = {
    "ro-reviewer": {"Read", "Grep", "Glob", "Bash"},
}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

c = Checker()

# ── 1. Контракт агентів ──────────────────────────────────────────────────────
print(f"{BOLD}1. Frontmatter агентів проти контракту{RESET}")
for agent_md in sorted((PKG_ROOT / ".claude" / "agents").glob("*.md")):
    fm = parse_frontmatter(agent_md)
    name = fm.get("name", agent_md.stem)
    for field in ("name", "description", "tools"):
        c.expect(field in fm, f"{agent_md.name}: поле `{field}` є")
    if name in EXPECTED_AGENT_TOOLS:
        tools = agent_tools(agent_md)
        expected = EXPECTED_AGENT_TOOLS[name]
        extra = tools - expected
        missing = expected - tools
        c.expect(not extra and not missing,
                 f"{name}: tools == контракт {sorted(expected)}",
                 f"зайве: {sorted(extra)}, бракує: {sorted(missing)}")
        c.expect(not (tools & WRITE_TOOLS),
                 f"{name}: write-інструментів немає (read-only контракт)",
                 f"знайдено {sorted(tools & WRITE_TOOLS)}")
    else:
        c.fail(f"{name}: агента немає в EXPECTED_AGENT_TOOLS - додай контракт")

# Негативний контроль: broken-версія МУСИТЬ порушувати контракт,
# інакше демо «BREAK=1 -> FAIL» не має чого показувати.
broken = CASES_DIR / "subagent-tools-allowlist" / "broken" / "ro-reviewer.md"
if broken.exists():
    c.expect(bool(agent_tools(broken) & WRITE_TOOLS),
             "broken/ro-reviewer.md справді зламаний (має write-інструменти)")

# ── 2. settings.json парсяться, guard тримає deny ────────────────────────────
print(f"\n{BOLD}2. settings.json{RESET}")
for sj in sorted(PKG_ROOT.rglob("settings.json")):
    if "tmp" in sj.parts or "node_modules" in sj.parts:
        continue
    rel = sj.relative_to(PKG_ROOT)
    try:
        data = json.loads(sj.read_text(encoding="utf-8"))
        c.ok(f"{rel} - валідний JSON")
    except json.JSONDecodeError as e:
        c.fail(f"{rel} - битий JSON: {e}")
        continue
    if "guard" in sj.parts:
        deny = data.get("permissions", {}).get("deny", [])
        c.expect(any(".env" in rule for rule in deny),
                 f"{rel} - deny на .env на місці")

# ── 3. Синтаксис харнесу і грейдерів ─────────────────────────────────────────
print(f"\n{BOLD}3. Синтаксис (py_compile){RESET}")
py_files = [AGENT_DIR / "run.py", AGENT_DIR / "lint.py",
            AGENT_DIR / "lib" / "checks.py",
            *sorted(CASES_DIR.glob("*/check.py"))]
for py in py_files:
    try:
        py_compile.compile(str(py), doraise=True)
        c.ok(f"py_compile {py.relative_to(AGENT_DIR)}")
    except py_compile.PyCompileError as e:
        c.fail(f"py_compile {py.relative_to(AGENT_DIR)}: {e.msg}")

# ── 4. Структура кейсів ──────────────────────────────────────────────────────
print(f"\n{BOLD}4. Структура кейсів{RESET}")
case_dirs = sorted(d for d in CASES_DIR.iterdir() if d.is_dir())
c.expect(bool(case_dirs), f"у {CASES_DIR.name}/ є кейси")
for d in case_dirs:
    for req in ("prompt.md", "case.json", "check.py", "expect.md"):
        c.expect((d / req).exists(), f"{d.name}/{req} є")
    cj = d / "case.json"
    if not cj.exists():
        continue
    try:
        spec = json.loads(cj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        c.fail(f"{d.name}/case.json - битий JSON: {e}")
        continue
    c.expect((FIXTURES_DIR / spec.get("fixture", "")).is_dir(),
             f"{d.name} → fixtures/{spec.get('fixture')}")
    for item in spec.get("stage", []):
        for key in ("from", "broken"):
            if key not in item:
                continue
            ref = item[key]
            src = (PKG_ROOT / ref[4:]) if ref.startswith("pkg:") else d / ref
            c.expect(src.exists(), f"{d.name}: stage-{key} {ref} існує")

print()
if c.failed:
    print(f"{BOLD}make check FAIL - конфігурація або харнес поламані.{RESET}")
    sys.exit(1)
print(f"{BOLD}make check OK - контракт конфігурації і харнес цілі "
      f"(0 токенів).{RESET}")
