"""check_tdd.py - грейдер tdd-three-commits: дисципліна RED-GREEN-REFACTOR.
Асерт на ПРОЦЕС: 3 коміти у порядку test( -> feat( -> refactor(, тести
заморожені після RED, гейт зелений на HEAD."""
import subprocess
from pathlib import Path

SB = Path(__file__).resolve().parents[3] / "tmp" / "suite-tdd-three-commits"


def _git(*args):
    return subprocess.run(["git", "-C", str(SB), *args],
                          capture_output=True, text=True).stdout.strip()


def get_assert(output, context):
    problems = []
    n = int(_git("rev-list", "--count", "HEAD") or 0) - 1   # мінус seed-коміт
    if n != 3:
        problems.append(f"комітів {n}, а не 3")
    else:
        msgs = _git("log", "--format=%s", "--reverse", "-n", "3", "HEAD").splitlines()
        for msg, prefix in zip(msgs, ("test(", "feat(", "refactor(")):
            if not msg.startswith(prefix):
                problems.append(f"коміт «{msg}» не з префіксом {prefix}")
        if _git("diff", "--stat", "HEAD~2..HEAD", "--", "test"):
            problems.append("test/ змінювали після фази RED")
    if subprocess.run(["node", "--test"], cwd=SB, capture_output=True).returncode != 0:
        problems.append("гейт node --test червоний на HEAD")
    return {"pass": not problems, "score": 1.0 if not problems else 0.0,
            "reason": "3 коміти test->feat->refactor, тести заморожені, гейт зелений"
                      if not problems else "; ".join(problems)}
