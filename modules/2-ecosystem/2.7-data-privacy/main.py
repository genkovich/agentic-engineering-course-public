"""Data privacy demo for Module 2 (Lecture 2.7).

Інспектує environment variables які контролюють що Claude Code відправляє
на Anthropic сервери. Не робить жодних мережевих запитів, тільки читає env.

Запускати з env (приклад):
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 python3 main.py
"""
import os
import sys

VARS = [
    {
        "name": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
        "purpose": "Master switch: вимикає телеметрію + error reporting + /feedback + survey + автооновлення",
        "truthy": {"1", "true", "yes"},
    },
    {
        "name": "DISABLE_TELEMETRY",
        "purpose": "Анонімна статистика: latency, кількість запитів, помилки. Код НЕ йде",
        "truthy": {"1", "true", "yes"},
    },
    {
        "name": "DISABLE_ERROR_REPORTING",
        "purpose": "Звіти про збої програми (stack traces, без коду користувача)",
        "truthy": {"1", "true", "yes"},
    },
    {
        "name": "DISABLE_FEEDBACK_COMMAND",
        "purpose": "Команда /feedback. УВАГА: /feedback зберігає повну історію 5 років",
        "truthy": {"1", "true", "yes"},
    },
    {
        "name": "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY",
        "purpose": "Опитування 'How is Claude doing?'. Без контексту розмови, тільки число",
        "truthy": {"1", "true", "yes"},
    },
    {
        "name": "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB",
        "purpose": "Прибирає API ключі/паролі з env при запуску subprocess (захист від prompt injection)",
        "truthy": {"1", "true", "yes"},
    },
]


def is_truthy(val: str | None, truthy: set[str]) -> bool:
    if val is None:
        return False
    return val.strip().lower() in truthy


def status_for(var: dict) -> tuple[str, str]:
    raw = os.environ.get(var["name"])
    if raw is None:
        return ("<not set>", "default behavior (data sent)")
    if is_truthy(raw, var["truthy"]):
        if var["name"] == "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB":
            return (raw, "subprocess env scrubbed")
        return (raw, "DISABLED (no data sent)")
    return (raw, "explicitly enabled (data sent)")


def section_current_state() -> dict[str, bool]:
    print("=" * 78)
    print("CURRENT STATE OF CLAUDE CODE PRIVACY ENV VARS")
    print("=" * 78)
    print()
    print(f"{'Variable':<48} {'Value':<14} {'Effect'}")
    print("-" * 78)
    states = {}
    for var in VARS:
        raw = os.environ.get(var["name"])
        states[var["name"]] = is_truthy(raw, var["truthy"])
        value, effect = status_for(var)
        name = var["name"]
        if len(name) > 47:
            name = name[:44] + "..."
        print(f"{name:<48} {value:<14} {effect}")
    print()
    print("Purposes:")
    for var in VARS:
        print(f"  {var['name']}")
        print(f"    {var['purpose']}")
    print()
    return states


def section_three_channels(states: dict[str, bool]) -> None:
    print("=" * 78)
    print("THREE DATA CHANNELS (з лекції 2.7)")
    print("=" * 78)
    print()
    master_off = states["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"]
    telemetry_off = master_off or states["DISABLE_TELEMETRY"]
    error_off = master_off or states["DISABLE_ERROR_REPORTING"]
    feedback_off = master_off or states["DISABLE_FEEDBACK_COMMAND"]
    survey_off = master_off or states["CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY"]

    print("  Channel 1: PRIMARY REQUEST (prompt + response)")
    print("    Status: ALWAYS ON (інакше Claude Code не працює)")
    print("    Що йде: твій код, файли, контекст. Шифрується TLS.")
    print("    Retention: 30 днів стандарт. Zero Data Retention доступний всім через API.")
    print()
    print("  Channel 2: TELEMETRY (anonymous usage stats)")
    print(
        f"    Status: {'OFF' if telemetry_off else 'ON'} "
        f"(controlled by DISABLE_TELEMETRY або master switch)"
    )
    print("    Що йде: latency, request counts, error counts. Код НЕ йде.")
    print()
    print("  Channel 3: FEEDBACK / CRASH REPORTS")
    print(
        f"    Crash reports: {'OFF' if error_off else 'ON'} (DISABLE_ERROR_REPORTING)"
    )
    print(
        f"    /feedback command: {'OFF' if feedback_off else 'ON'} (DISABLE_FEEDBACK_COMMAND)"
    )
    print(
        f"    Quality survey: {'OFF' if survey_off else 'ON'} "
        "(CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY)"
    )
    print(
        "    Що йде: при /feedback - ВСЯ історія розмови, retention 5 років (!)."
    )
    print(
        "    При survey - тільки число 1-3 без контексту."
    )
    print()


def section_recommended() -> None:
    print("=" * 78)
    print("РЕКОМЕНДОВАНИЙ SETUP ДЛЯ КОДУ КОМПАНІЇ")
    print("=" * 78)
    print()
    print("Один рядок у ~/.zshrc або ~/.bashrc вимикає все зайве:")
    print()
    print("  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1")
    print("  export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1")
    print()
    print("Або через Claude Code settings.json (.claude/settings.json у проекті):")
    print()
    print("  {")
    print('    "env": {')
    print('      "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",')
    print('      "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB": "1"')
    print("    }")
    print("  }")
    print()
    print("Додатково через UI: claude.ai/settings -> Data Privacy Controls")
    print("  -> перевір що навчання моделі вимкнене (актуально для безкоштовного tier).")
    print()
    print("Через хмарні платформи (AWS Bedrock, Google Vertex, Azure Foundry)")
    print("  телеметрія і error reporting вимкнені за замовчуванням.")
    print()
    print("Правило з лекції: код компанії = платний тариф, завжди.")
    print("  Безкоштовний tier для навчання і pet-проектів.")
    print()


def main() -> None:
    states = section_current_state()
    section_three_channels(states)
    section_recommended()
    return None


if __name__ == "__main__":
    sys.exit(main() or 0)
