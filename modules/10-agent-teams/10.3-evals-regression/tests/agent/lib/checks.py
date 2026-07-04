"""checks.py - спільні перевірки для грейдерів (cases/<case>/check.py).

Центральна теза 10.3: прогін агента недетермінований, тому асертимо на
РЕЗУЛЬТАТ (роут віддав 401? секрет не витік? рівно 3 коміти?), а не на текст.
Детермінований грейдер над недетермінованим агентом - це і є eval конфігурації.

Кожен check.py імпортує звідси Checker + потрібні читалки стану:
    sys.path.insert(0, os.environ["LIB_DIR"])
    from checks import Checker, clean_diff, transcript_text
і завершується sys.exit(c.exit_code()).

Залежності: тільки stdlib (subprocess, json, urllib). Жодного pip install.
"""
import json
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


class Checker:
    """Копить вердикт: кожен expect друкує ✓/✗, наприкінці exit 0/1."""

    def __init__(self):
        self.failed = False

    def ok(self, label):
        print(f"  {GREEN}✓{RESET} {label}")

    def fail(self, label):
        print(f"  {RED}✗{RESET} {label}")
        self.failed = True

    def info(self, text):
        print(f"  {DIM}ℹ {text}{RESET}")

    def expect(self, cond, label, detail=""):
        if cond:
            self.ok(label)
        else:
            self.fail(label + (f" - {detail}" if detail else ""))
        return cond

    def eq(self, actual, expected, label):
        return self.expect(
            actual == expected, f"{label} ({actual})",
            f"очікував {expected!r}, отримав {actual!r}",
        )

    def exit_code(self):
        return 1 if self.failed else 0


# ── Git: факти з репозиторію пісочниці ───────────────────────────────────────

def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    return r.stdout.strip()


def clean_diff(repo, pathspec):
    """Порожній рядок = під pathspec НЕМА змін (для read-only агента)."""
    diff = _git(repo, "--no-pager", "diff", "--stat", "--", pathspec)
    status = _git(repo, "status", "--porcelain", "--", pathspec)
    return (diff + status).strip()


def git_log_count(repo):
    """Кількість комітів на HEAD (включно з seed-комітом пісочниці)."""
    out = _git(repo, "rev-list", "--count", "HEAD")
    return int(out) if out else 0


def git_log_messages(repo, n):
    """Останні n commit-повідомлень, від найстаршого до найновішого."""
    out = _git(repo, "log", "--format=%s", "--reverse", "-n", str(n), "HEAD")
    return out.splitlines() if out else []


def diff_between(repo, rev_range, pathspec):
    """git diff --stat <range> -- <pathspec>; порожньо = нічого не мінялось."""
    return _git(repo, "--no-pager", "diff", "--stat", rev_range, "--", pathspec)


# ── HTTP: факти з живого сервісу ─────────────────────────────────────────────

def http_status(url, headers=None):
    """Фактичний HTTP-код відповіді (0, якщо сервіс не відповів)."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except OSError:
        return 0


def wait_for_port(host, port, timeout=10):
    """Чекає, поки сервіс відкриє порт. True = дочекались."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return True
        except OSError:
            time.sleep(0.1)
    return False


# ── Транскрипт: що агент казав і робив ───────────────────────────────────────
# Транскрипт - це ndjson від `claude -p --output-format stream-json`:
# один JSON-об'єкт на рядок (assistant-повідомлення, tool-виклики, фінальний result).

def _events(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def transcript_text(path):
    """Лише текстові репліки асистента - без вмісту прочитаних файлів.

    Сирий транскрипт містить і те, що агент ЧИТАВ; grep по ньому дає хибні
    збіги. Для асертів на «що агент сказав» бери саме цей зріз.
    """
    parts = []
    for ev in _events(path):
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
    return "\n".join(parts)


def transcript_tool_calls(path):
    """Імена викликаних інструментів, у порядку виклику."""
    names = []
    for ev in _events(path):
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if block.get("type") == "tool_use":
                names.append(block.get("name", "?"))
    return names


def transcript_stats(path):
    """(cost_usd, num_turns) з фінального result-рядка; (None, None) якщо нема."""
    cost, turns = None, None
    for ev in _events(path):
        if ev.get("type") == "result":
            cost = ev.get("total_cost_usd", cost)
            turns = ev.get("num_turns", turns)
    return cost, turns


def raw_contains(path, needle):
    """Пошук по СИРОМУ транскрипту (всі події). Для guardrail-асертів:
    «значення секрета не з'явилось НІДЕ» - навіть у прочитаних файлах."""
    try:
        with open(path, encoding="utf-8") as f:
            return needle in f.read()
    except OSError:
        return False


# ── Конфігурація: ручний парсер YAML-frontmatter (без pip-залежностей) ───────

def parse_frontmatter(path):
    """Читає блок між `---`-лініями як плоскі пари key: value.

    Свідомо не тягнемо PyYAML: frontmatter агентів - плоский, рядок `tools:`
    розбирається split-ом. Менше залежностей - надійніший шар 0.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def agent_tools(path):
    """Множина інструментів із рядка `tools:` frontmatter-а агента."""
    raw = parse_frontmatter(path).get("tools", "")
    return {t.strip() for t in raw.split(",") if t.strip()}


# ── Швидкий зріз транскрипта з термінала ─────────────────────────────────────
# python3 tests/agent/lib/checks.py tmp/run-<case>/transcript.jsonl

if __name__ == "__main__":
    import collections
    import sys

    if len(sys.argv) < 2:
        print("usage: python3 checks.py <transcript.jsonl>")
        sys.exit(2)
    t = sys.argv[1]
    calls = collections.Counter(transcript_tool_calls(t))
    cost, turns = transcript_stats(t)
    print(f"{BOLD}Виклики інструментів:{RESET}")
    for name, n in calls.most_common():
        print(f"  {n:3d}  {name}")
    print(f"{DIM}cost=${cost}  turns={turns}{RESET}")
