"""Token counter demo for Module 1.

Compares token counts for the same content in EN vs UA, prose vs code,
and shows estimated input/output cost for Sonnet 4.6.
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

# Pricing per million tokens (input / output) for Claude 4.x family.
# Output is 5x input across all tiers because tokens are generated sequentially
# (autoregression) while input is processed in parallel.
PRICING = {
    "Opus":   {"input": 5.0,  "output": 25.0},
    "Sonnet": {"input": 3.0,  "output": 15.0},
    "Haiku":  {"input": 1.0,  "output": 5.0},
}
INPUT_PRICE_PER_MTOK = PRICING["Sonnet"]["input"]
OUTPUT_PRICE_PER_MTOK = PRICING["Sonnet"]["output"]

SAMPLES = [
    {
        "label": "EN prose",
        "text": (
            "The quick brown fox jumps over the lazy dog. "
            "She sells seashells by the seashore. "
            "All work and no play makes Jack a dull boy."
        ),
    },
    {
        "label": "UA prose",
        "text": (
            "Швидкий рудий лис перестрибує через ледачого собаку. "
            "Вона продає мушлі біля моря. "
            "Робота без відпочинку робить Джека нудним."
        ),
    },
    {
        "label": "Code (Python)",
        "text": (
            "def fibonacci(n: int) -> int:\n"
            "    if n < 2:\n"
            "        return n\n"
            "    return fibonacci(n - 1) + fibonacci(n - 2)\n"
        ),
    },
    {
        "label": "Code (Go)",
        "text": (
            "func fibonacci(n int) int {\n"
            "    if n < 2 {\n"
            "        return n\n"
            "    }\n"
            "    return fibonacci(n-1) + fibonacci(n-2)\n"
            "}\n"
        ),
    },
]


def require_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_key


def count_tokens(client: Anthropic, text: str) -> int:
    result = client.messages.count_tokens(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
    )
    return result.input_tokens


def main() -> None:
    require_api_key()
    client = Anthropic()

    print(f"Token counts for {MODEL}\n")
    print(f"{'Sample':<20} {'Words':>6} {'Tokens':>7} {'Tok/Word':>9} {'Input $':>10}")
    print("-" * 60)

    for sample in SAMPLES:
        tokens = count_tokens(client, sample["text"])
        words = len(sample["text"].split())
        tok_per_word = tokens / max(words, 1)
        cost_input = (tokens / 1_000_000) * INPUT_PRICE_PER_MTOK
        print(
            f"{sample['label']:<20} {words:>6} {tokens:>7} "
            f"{tok_per_word:>9.2f} ${cost_input:>8.6f}"
        )

    print()
    print("Cost estimate for 1000 requests of ~500 input + ~200 output tokens each:")
    avg_in = 500
    avg_out = 200
    total_in_cost = (avg_in * 1000 / 1_000_000) * INPUT_PRICE_PER_MTOK
    total_out_cost = (avg_out * 1000 / 1_000_000) * OUTPUT_PRICE_PER_MTOK
    print(f"  Input  : 1000 x {avg_in} tok = ${total_in_cost:.4f}")
    print(f"  Output : 1000 x {avg_out} tok = ${total_out_cost:.4f}")
    print(f"  Total  : ${total_in_cost + total_out_cost:.4f}")
    print()
    print(
        "Note: UA prose typically takes ~2x more tokens than EN prose with the same "
        "meaning. If you write prompts and replies in UA, you pay roughly twice as "
        "much for the same task. Code is denser than prose because language keywords "
        "tokenize to 1 token each."
    )
    print()
    print("Pricing per million tokens (Claude 4.x family):")
    for tier, prices in PRICING.items():
        ratio = prices["output"] / prices["input"]
        print(
            f"  {tier:<7} input ${prices['input']:>5.2f} / output ${prices['output']:>5.2f} "
            f"(output is {ratio:.0f}x input, sequential generation)"
        )
    print()
    print("Hidden costs that count_tokens does NOT show:")
    print(
        "  Tool definitions: ~346 tokens fixed overhead + ~403 per tool definition. "
        "Adding 5 tools adds ~2,361 tokens to every request."
    )
    print(
        "  Images: ~(width x height) / 750 tokens. A 1024x1024 screenshot is ~1,365 tokens, "
        "a 4K image is ~11,000 tokens."
    )
    print(
        "  System prompt and conversation history: re-sent on every request "
        "(model is stateless, see context-window demo)."
    )


if __name__ == "__main__":
    main()
