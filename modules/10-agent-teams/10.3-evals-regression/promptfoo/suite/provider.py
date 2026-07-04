"""provider.py (suite) - узагальнення провайдера головного кейса.

Той самий адаптер «наш спосіб запускати агента -> Promptfoo», тільки
середовище кожного тесту описане у vars конфіга:
  case    - ім'я пісочниці: tmp/suite-<case>
  fixture - папка з fixtures/, з якої збирається проєкт
  config  - (опц.) .claude-конфігурація під тестом (шлях від suite/)
  broken  - (опц.) зламана версія config; стейджиться при BREAK=1
  rename  - (опц.) "старе:нове", напр. env.fixture:.env
            (справжній .env у репозиторії не живе)
"""
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

SUITE = Path(__file__).resolve().parent
PKG = SUITE.parent.parent                      # корінь пакета


def call_api(prompt, options, context):
    v = context.get("vars", {})
    sb = PKG / "tmp" / f"suite-{v['case']}"

    # 1) Пісочниця: fixture + rename + конфігурація, щоразу з нуля.
    shutil.rmtree(sb, ignore_errors=True)
    shutil.copytree(PKG / "fixtures" / v["fixture"], sb)
    if v.get("rename"):
        old, new = v["rename"].split(":")
        (sb / old).rename(sb / new)
    config = v.get("config")
    if config and os.environ.get("BREAK") and v.get("broken"):
        config = v["broken"]                   # BREAK=1 - зламана конфігурація
        print(f"[BREAK] застейджено {config}")
    if config:
        shutil.copytree(SUITE / config, sb / ".claude", dirs_exist_ok=True)
    for hook in sb.glob(".claude/hooks/*.sh"):
        hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
    git = ["git", "-C", str(sb),
           "-c", "user.email=evals@example.com", "-c", "user.name=evals",
           "-c", "commit.gpgsign=false"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "seed", "--no-verify"], check=True)

    # 2) Реальний headless-прогін у пісочниці.
    run = subprocess.run(
        ["claude", "-p", prompt,
         "--output-format", "stream-json", "--verbose",
         "--permission-mode", "acceptEdits"],
        cwd=sb, capture_output=True, text=True)
    (sb / "transcript.jsonl").write_text(run.stdout, encoding="utf-8")

    # 3) Відповідь для асертів: лише текстові репліки асистента.
    parts = []
    for line in run.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []) or []:
                if block.get("type") == "text":
                    parts.append(block["text"])
    return {"output": "\n".join(parts)}
