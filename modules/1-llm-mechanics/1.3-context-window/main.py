"""Context window demo for Module 1.

Simulates a long working session by appending messages one by one and
tracking accumulated token count via messages.count_tokens(). Visualizes
how the context window burns down and when /compact is needed.
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
# Claude 4.x context windows: Haiku 200K, Sonnet 1M, Opus 1M.
# Claude Code default tier mirrors Haiku (200K) regardless of selected model.
SONNET_MAX_TOKENS = 1_000_000
CLAUDE_CODE_DEFAULT_TOKENS = 200_000

WARN_THRESHOLD = 0.70
COMPACT_THRESHOLD = 0.90

CHECKPOINTS = [1, 3, 5, 10, 15, 20, 30, 50]

USER_MESSAGE = (
    "Я працюю над feature: нова сторінка з таблицею користувачів. "
    "Бекенд віддає JSON з полями id, email, role, created_at. "
    "Розкажи як написати React компонент з пагінацією, сортуванням "
    "і пошуком. Покажи приклад коду."
)
ASSISTANT_MESSAGE = (
    "Звичайно. Ось приклад React компонента з пагінацією, сортуванням і пошуком. "
    "Використаємо useState для локального стану і useMemo для оптимізації. "
    "Спершу опишемо типи: type User = { id: string; email: string; role: string; "
    "created_at: string }. Потім компонент UserTable приймає список і повертає "
    "JSX з таблицею. Для сортування - функція compareBy(field, dir), для пошуку "
    "case-insensitive includes по email. Пагінація через slice по індексу сторінки. "
    "Якщо хочеш скелет коду - можу написати повний приклад на 80 рядків."
)


def require_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_key


def count_tokens(client: Anthropic, messages: list[dict]) -> int:
    result = client.messages.count_tokens(model=MODEL, messages=messages)
    return result.input_tokens


def progress_bar(pct: float, width: int = 30) -> str:
    filled = int(width * pct)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def status_for(pct_cc: float) -> str:
    if pct_cc >= COMPACT_THRESHOLD:
        return "COMPACT NOW"
    if pct_cc >= WARN_THRESHOLD:
        return "warn"
    return "ok"


def main() -> None:
    require_api_key()
    client = Anthropic()

    messages: list[dict] = []
    print(f"Simulating long session with {MODEL}\n")
    print(
        f"{'Msgs':>4}  {'Tokens':>8}  {'% of 200K (CC)':<22}  "
        f"{'% of 1M (Sonnet)':<22}  Status"
    )
    print("-" * 90)

    for i in range(1, max(CHECKPOINTS) + 1):
        messages.append({"role": "user", "content": USER_MESSAGE})
        messages.append({"role": "assistant", "content": ASSISTANT_MESSAGE})
        if i not in CHECKPOINTS:
            continue
        tokens = count_tokens(client, messages)
        pct_cc = tokens / CLAUDE_CODE_DEFAULT_TOKENS
        pct_max = tokens / SONNET_MAX_TOKENS
        bar_cc = progress_bar(min(pct_cc, 1.0), 12)
        bar_max = progress_bar(min(pct_max, 1.0), 12)
        print(
            f"{i:>4}  {tokens:>8}  {bar_cc} {pct_cc * 100:>5.1f}%   "
            f"{bar_max} {pct_max * 100:>5.1f}%   {status_for(pct_cc)}"
        )

    last_tokens = count_tokens(client, messages)
    tokens_per_pair = last_tokens / max(CHECKPOINTS)
    pairs_until_compact = int(
        (CLAUDE_CODE_DEFAULT_TOKENS * COMPACT_THRESHOLD) / tokens_per_pair
    )
    print()
    print(
        f"At ~{tokens_per_pair:.0f} tokens per user/assistant pair, "
        f"Claude Code default (200K) hits 90% at ~{pairs_until_compact} message pairs."
    )
    print(
        "Run /compact at the warning level to summarize history and free context. "
        "The model is stateless: every request resends the full history, so longer "
        "sessions cost exponentially more."
    )
    print()
    print("Context window is not free even when it fits:")
    print(
        "  MRCR test (multi-fact recall): Opus 4.5 retains ~78% of facts at 1M context, "
        "Sonnet drops below 20%. Bigger window does not mean useful window."
    )
    print(
        '  Lost in the Middle (U-curve attention): models recall ~93% at the start, '
        "~70% in the middle, ~92% at the end. Put critical info first or last."
    )
    print()
    print("Five rules from Lecture 1.3:")
    print("  1. Run /compact when you see warn / COMPACT NOW threshold.")
    print("  2. Run /clear when switching to an unrelated task (cheaper than compact).")
    print("  3. CLAUDE.md under 200 lines, otherwise it dominates every request.")
    print("  4. Put critical context at the start or end of the message, not middle.")
    print("  5. ~15-20 message pairs per session, then split a new session.")


if __name__ == "__main__":
    main()
