#!/usr/bin/env python3
"""run.py - golden-task regression suite для .claude/ (лекція 10.3).

Для кожного кейса cases/<case>/ двигун робить чотири кроки:
  1. Пісочниця: чиста tmp/run-<case>/ за декларацією case.json
     (fixture + renames + stage-конфіг + git-історія + засаджений коміт).
  2. Агент: реальний headless `claude -p` У пісочниці, транскрипт у
     transcript.jsonl (stream-json). Це єдиний недетермінований крок.
  3. Грейдер: cases/<case>/check.py - детерміновані асерти проти
     фінального стану пісочниці, exit 0 = PASS.
  4. Матриця PASS/FAIL + сумарний cost/час.

Коштує токени (як 7.2). Безтокенний шар 0 - lint.py (`make check`).

Usage:
    python3 tests/agent/run.py                 # усі кейси
    python3 tests/agent/run.py route-auth      # один кейс
    BREAK=1 python3 tests/agent/run.py subagent-tools-allowlist
        # «зламати конфіг»: stage-крок бере broken-версію -> eval має почервоніти
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from checks import BOLD, DIM, GREEN, RED, RESET, YELLOW, transcript_stats  # noqa: E402

AGENT_DIR = Path(__file__).resolve().parent          # tests/agent/
PKG_ROOT = AGENT_DIR.parent.parent                   # 10.3-evals-regression/
CASES_DIR = AGENT_DIR / "cases"
FIXTURES_DIR = PKG_ROOT / "fixtures"
TMP_DIR = PKG_ROOT / "tmp"
BREAK = bool(os.environ.get("BREAK"))


def sh(args, cwd, check=True):
    return subprocess.run(args, cwd=cwd, check=check,
                          capture_output=True, text=True)


def resolve_source(case_dir, ref):
    """Шлях stage-джерела: `pkg:...` - від кореня пакета, інакше - від кейса."""
    if ref.startswith("pkg:"):
        return PKG_ROOT / ref[len("pkg:"):]
    return case_dir / ref


def copy_into(src, dst):
    """Копіює файл або директорію (разом із dotfiles) у dst."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def make_sandbox(case_dir, spec):
    """Збирає чисту пісочницю за case.json. Щоразу з нуля: спільний стан між
    прогонами дає корельовані фейли й нечесні переваги (агент, що підглядає
    залишки минулого прогону)."""
    sb = TMP_DIR / f"run-{case_dir.name}"
    shutil.rmtree(sb, ignore_errors=True)
    sb.mkdir(parents=True)

    # 1) fixture - проєкт-заготовка, у якій працюватиме агент.
    copy_into(FIXTURES_DIR / spec["fixture"], sb)

    # 2) renames - напр. env.fixture -> .env (справжній .env у репо не живе).
    for old, new in spec.get("renames", {}).items():
        (sb / old).rename(sb / new)

    # 3) stage - конфігурація, ЯКУ ТЕСТУЄМО. BREAK=1 підкладає broken-версію:
    #    так регресія відтворюється однією командою, без брудного git.
    for item in spec.get("stage", []):
        ref = item["from"]
        if BREAK and "broken" in item:
            ref = item["broken"]
            print(f"  {YELLOW}[BREAK] застейджено {ref} замість {item['from']}{RESET}")
        copy_into(resolve_source(case_dir, ref), sb / item["to"])

    # Хуки мають бути виконуваними.
    for hook in sb.glob(".claude/hooks/*.sh"):
        hook.chmod(hook.stat().st_mode | stat.S_IXUSR)

    # 4) git-історія: пісочниця - самодостатнє репо, щоб (а) грейдер міг
    #    асертити по git diff/log, (б) claude брав .claude/ саме звідси.
    sh(["git", "init", "-q"], sb)
    sh(["git", "config", "user.email", "evals@example.com"], sb)
    sh(["git", "config", "user.name", "golden-task evals"], sb)
    sh(["git", "config", "commit.gpgsign", "false"], sb)
    sh(["git", "add", "-A"], sb)
    sh(["git", "commit", "-q", "-m", "chore: seed sandbox", "--no-verify"], sb)

    # 5) seed_commit - засаджена зміна поверх seed-а, щоб агенту було що
    #    дивитись (напр. HEAD~1..HEAD для рев'ю).
    seed = spec.get("seed_commit")
    if seed:
        for rel, text in seed.get("append", {}).items():
            with open(sb / rel, "a", encoding="utf-8") as f:
                f.write(text)
        sh(["git", "add", "-A"], sb)
        sh(["git", "commit", "-q", "-m", seed["message"], "--no-verify"], sb)

    return sb


def run_agent(sb, prompt_file, flags):
    """Єдина точка реального `claude -p`. stream-json потребує --verbose.
    acceptEdits, НЕ bypassPermissions: bypass вимикає deny-правила й хуки
    з .claude/ пісочниці - guardrail-кейси давали б фальшивий PASS."""
    transcript = sb / "transcript.jsonl"
    prompt = prompt_file.read_text(encoding="utf-8")
    cmd = ["claude", "-p", prompt,
           "--output-format", "stream-json", "--verbose",
           "--permission-mode",
           os.environ.get("AGENT_PERMISSION_MODE", "acceptEdits"), *flags]
    with open(transcript, "w") as out, open(sb / "agent.stderr", "w") as err:
        subprocess.run(cmd, cwd=sb, stdout=out, stderr=err)
    return transcript


def run_check(case_dir, sb, transcript):
    """Грейдер кейса: детермінований check.py, вердикт = exit-код."""
    env = dict(os.environ,
               SANDBOX=str(sb), TRANSCRIPT=str(transcript),
               CASE_DIR=str(case_dir), LIB_DIR=str(AGENT_DIR / "lib"))
    r = subprocess.run([sys.executable, str(case_dir / "check.py")],
                       env=env, cwd=sb)
    return r.returncode == 0


def run_case(case_dir):
    name = case_dir.name
    spec = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    print(f"\n{BOLD}▶ {name}{RESET}"
          + (f"  {YELLOW}[BREAK=on]{RESET}" if BREAK else ""))
    if BREAK and not any("broken" in i for i in spec.get("stage", [])):
        print(f"  {DIM}BREAK для цього кейса - no-op (нема broken-конфіга){RESET}")

    sb = make_sandbox(case_dir, spec)
    print(f"  {DIM}claude -p … (це коштує токени){RESET}")
    transcript = run_agent(sb, case_dir / "prompt.md", spec.get("flags", []))
    passed = run_check(case_dir, sb, transcript)
    cost, turns = transcript_stats(transcript)
    cost_s = f"{cost:.4f}" if isinstance(cost, (int, float)) else "?"
    return passed, f"cost=${cost_s} turns={turns or '?'}"


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only:
        case_dirs = [CASES_DIR / only]
        if not case_dirs[0].is_dir():
            print(f"Кейс '{only}' не знайдено в {CASES_DIR}", file=sys.stderr)
            return 2
    else:
        case_dirs = sorted(d for d in CASES_DIR.iterdir() if d.is_dir())

    print(f"{BOLD}🧪 golden-task eval suite - реальний claude -p{RESET}")
    print(f"{DIM}кейсів: {len(case_dirs)} · пісочниці: tmp/run-*/{RESET}")

    started = time.time()
    rows = []
    for d in case_dirs:
        passed, detail = run_case(d)
        rows.append((passed, d.name, detail))

    print(f"\n{BOLD}Підсумок:{RESET}")
    for passed, name, detail in rows:
        mark = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{mark}  {name:<28} {DIM}{detail}{RESET}")
    fails = sum(1 for p, *_ in rows if not p)
    print(f"\n{DIM}час: {int(time.time() - started)}с{RESET}")
    if fails == 0:
        print(f"{GREEN}{BOLD}Усі {len(rows)} кейсів PASS.{RESET}")
        return 0
    print(f"{RED}{BOLD}{fails} з {len(rows)} кейсів FAIL.{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
