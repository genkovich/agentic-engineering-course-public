"""provider.py - кастомний Promptfoo-провайдер для агента ro-reviewer.

Навіщо свій: готовий провайдер anthropic:claude-agent-sdk не запускає
НАЗВАНОГО агента з .claude/agents/ головним потоком. А предмет тесту -
саме конфігурація ro-reviewer. Тож call_api - це наш eval/sandbox.sh
плюс claude -p, загорнуті в одну python-функцію.

Контракт провайдера Promptfoo: call_api(prompt, options, context)
повертає {"output": <текст відповіді>}.

BREAK=1 підкладає в пісочницю зламану версію агента (eval/broken/) -
асерти конфіга мають почервоніти.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent   # корінь пакета
SANDBOX = PKG / "tmp" / "pf-sandbox"


def call_api(prompt, options, context):
    # 1) Пісочниця: та сама логіка, що eval/sandbox.sh - копія проєкту
    #    (src + .claude + eval) і свіжий git, щоразу з нуля.
    shutil.rmtree(SANDBOX, ignore_errors=True)
    SANDBOX.mkdir(parents=True)
    for item in ("src", ".claude", "eval"):
        src = PKG / item
        if src.is_dir():
            shutil.copytree(src, SANDBOX / item)
        else:
            shutil.copy2(src, SANDBOX / item)
    if os.environ.get("BREAK"):
        shutil.copy2(PKG / "eval" / "broken" / "ro-reviewer.md",
                     SANDBOX / ".claude" / "agents" / "ro-reviewer.md")
        print("[BREAK] застейджено eval/broken/ro-reviewer.md")
    git = ["git", "-C", str(SANDBOX),
           "-c", "user.email=evals@example.com", "-c", "user.name=evals",
           "-c", "commit.gpgsign=false"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "seed", "--no-verify"], check=True)

    # 2) Реальний headless-прогін названого агента У пісочниці.
    run = subprocess.run(
        ["claude", "-p", prompt, "--agent", "ro-reviewer",
         "--output-format", "stream-json", "--verbose",
         "--permission-mode", "acceptEdits"],
        cwd=SANDBOX, capture_output=True, text=True)
    (SANDBOX / "transcript.jsonl").write_text(run.stdout, encoding="utf-8")

    # 3) Відповідь для асертів: лише текстові репліки асистента
    #    (сирий stream-json містить і вміст прочитаних файлів).
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
