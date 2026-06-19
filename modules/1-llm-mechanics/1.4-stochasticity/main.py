"""Stochasticity demo for Module 1 (Lecture 1.4).

Запускає той самий промпт з трьома значеннями temperature і показує що:
  1. T=0.0 дає стабільні виходи між запусками
  2. T=1.0 дає різні виходи
  3. Constrained prompt дає стабільний вихід навіть при T=1.0 (промпт як ручка temperature)
"""
import os
import sys
from difflib import SequenceMatcher

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

OPEN_PROMPT = "Перелічи переваги мікросервісів."
CONSTRAINED_PROMPT = (
    "Перелічи рівно 3 переваги мікросервісів у форматі:\n"
    "1. <Назва> - <одне речення опису>\n"
    "2. <Назва> - <одне речення опису>\n"
    "3. <Назва> - <одне речення опису>\n"
    "Без преамбули, без епілогу, тільки три рядки."
)
RUNS_PER_TEMP = 3


def require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)


def call(client: Anthropic, prompt: str, temperature: float) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def run_batch(
    client: Anthropic, label: str, prompt: str, temperature: float
) -> list[str]:
    print(f"--- {label} (T={temperature}, {RUNS_PER_TEMP} runs) ---")
    outputs = []
    for i in range(1, RUNS_PER_TEMP + 1):
        out = call(client, prompt, temperature)
        outputs.append(out)
        preview = out[:200].replace("\n", " | ")
        print(f"  Run {i}: {preview}{'...' if len(out) > 200 else ''}")
    pairs = [
        (i + 1, j + 1, similarity(outputs[i], outputs[j]))
        for i in range(len(outputs))
        for j in range(i + 1, len(outputs))
    ]
    avg = sum(s for _, _, s in pairs) / max(len(pairs), 1)
    pair_str = ", ".join(f"{i}~{j}={s:.2f}" for i, j, s in pairs)
    print(f"  Pairwise similarity (1.00 = identical): {pair_str}, avg={avg:.2f}")
    print()
    return outputs


def main() -> None:
    require_api_key()
    client = Anthropic()

    print()
    print("STOCHASTICITY DEMO")
    print(f"Model: {MODEL}")
    print()
    print(f'Open-ended prompt: "{OPEN_PROMPT}"')
    print()

    run_batch(client, "Open-ended @ T=0.0", OPEN_PROMPT, 0.0)
    run_batch(client, "Open-ended @ T=0.5", OPEN_PROMPT, 0.5)
    run_batch(client, "Open-ended @ T=1.0", OPEN_PROMPT, 1.0)

    print(f'Constrained prompt: "{CONSTRAINED_PROMPT[:80]}..."')
    print()
    run_batch(client, "Constrained @ T=1.0", CONSTRAINED_PROMPT, 1.0)

    print("Висновки:")
    print(
        "  1. T=0 дає високу similarity (~0.9+) бо модель завжди бере найвірогідніший токен."
    )
    print(
        "  2. T=1.0 з відкритим промптом дає низьку similarity (~0.3-0.5)."
    )
    print(
        "  3. T=1.0 з constrained промптом дає високу similarity бо формат фіксований."
    )
    print("  Промпт це теж ручка temperature, особливо для Claude.ai / Claude Code.")


if __name__ == "__main__":
    main()
