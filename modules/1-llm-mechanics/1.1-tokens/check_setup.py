"""Перевірка середовища перед домашкою: Python, пакети, ключ, API.

Якщо щось не працює, запусти цей скрипт і скинь його вивід у чат курсу.

Usage: uv run check_setup.py
   or: python3 check_setup.py
"""
import os
import platform
import sys
import sysconfig
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ok = True


def line(status: str, text: str) -> None:
    print(f"[{status}] {text}")


def bad(text: str) -> None:
    global ok
    ok = False
    line("FAIL", text)


free_threaded = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
version = platform.python_version()
build = "free-threaded" if free_threaded else "звичайна збірка"
print(f"Python {version} ({build}), {platform.system()} {platform.release()}, {sys.executable}")

if sys.version_info < (3, 10):
    bad("Потрібен Python 3.10 або новіший.")
elif free_threaded:
    line("WARN", "Free-threaded Python: пакети для скрипта токенізаторів можуть не встановитись. "
                 "Для домашки це не заважає. Простіше за все запускати через uv run.")
else:
    line("OK", "Версія Python підходить.")

try:
    import anthropic
    import dotenv  # noqa: F401
    line("OK", f"anthropic {anthropic.__version__} і python-dotenv встановлені.")
except ImportError as err:
    bad(f"Не встановлено {err.name}. Запусти через uv run або постав пакети з requirements.txt.")
    anthropic = None

# Same lookup as load_dotenv(): the nearest .env going up from this folder,
# so one .env in the repo root works for every lesson.
env_file = next((d / ".env" for d in Path(__file__).resolve().parents if (d / ".env").is_file()), None)
if env_file is None:
    bad("Не знайшов .env. Скопіюй .env.example з кореня репо в .env у корені і впиши ключ.")
else:
    line("OK", f"Беру ключ з {env_file}.")
    if anthropic is not None:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        bad(f"У {env_file} порожній ANTHROPIC_API_KEY. Впиши ключ одразу після знака «=».")
    elif not key.startswith("sk-ant-"):
        bad("Ключ у .env не схожий на ключ Anthropic (має починатися з sk-ant-).")
    else:
        line("OK", f"Ключ знайдено, закінчується на ...{key[-4:]}.")

if ok and anthropic is not None:
    from claude_api import count_tokens, make_client
    tokens = count_tokens(make_client(), "claude-sonnet-5-5", "Перевірка")
    line("OK", f"API відповідає: count_tokens повернув {tokens} токенів.")

print()
print("Усе готово, можна робити домашку." if ok else "Є проблеми вище. Скинь цей вивід у чат курсу.")
sys.exit(0 if ok else 1)
