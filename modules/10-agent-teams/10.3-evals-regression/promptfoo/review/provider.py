"""provider.py - кастомний Promptfoo-провайдер для агента ro-reviewer.

Навіщо: готовий провайдер anthropic:claude-agent-sdk не запускає названого
агента з .claude/agents/ головним потоком. А наш предмет тесту - саме
конфігурація ro-reviewer. Тож провайдер збирає пісочницю ТИМ САМИМ двигуном,
що tests/agent/run.py (нуль дубльованого коду), і жене реальний
`claude -p --agent ro-reviewer`.

Контракт провайдера Promptfoo: call_api(prompt, options, context) повертає
{"output": <текст>} (+ опційно tokenUsage/metadata).

BREAK=1 працює і тут: двигун застейджить broken-версію агента -> асерти
конфіга (python + rubric) мають почервоніти.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
AGENT_DIR = os.path.join(PKG_ROOT, "tests", "agent")

sys.path.insert(0, os.path.join(AGENT_DIR, "lib"))
from checks import transcript_stats, transcript_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("run", os.path.join(AGENT_DIR, "run.py"))
_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_run)

CASE = "subagent-tools-allowlist"


def call_api(prompt, options, context):
    case_dir = _run.CASES_DIR / CASE
    spec = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))

    # Та сама дисципліна, що в харнесі: щоразу чиста пісочниця.
    sb = _run.make_sandbox(case_dir, spec)

    # Промпт приходить від Promptfoo (vars.task із конфіга), а не з prompt.md
    # кейса: Promptfoo керує матрицею завдань, двигун - середовищем.
    prompt_file = sb / "promptfoo-task.md"
    prompt_file.write_text(prompt, encoding="utf-8")

    transcript = _run.run_agent(sb, prompt_file, spec.get("flags", []))

    cost, turns = transcript_stats(transcript)
    return {
        "output": transcript_text(transcript),
        "metadata": {
            "sandbox": str(sb),
            "cost_usd": cost,
            "num_turns": turns,
        },
    }
