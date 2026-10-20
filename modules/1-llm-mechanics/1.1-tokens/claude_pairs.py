"""Three pairs from the lecture on Claude: log vs sentence, ensure_ascii, ALL CAPS.

Each pair carries the same meaning, only the form differs. The same inputs
were measured on o200k in the lecture, here they go through count_tokens.

Usage:
  python3 claude_pairs.py
  python3 claude_pairs.py --model claude-sonnet-5-5
"""
import argparse
import json

from claude_api import count_tokens, make_client

DEFAULT_MODEL = "claude-opus-5-5"

LOG_LINE = (
    '2026-09-29T14:03:27.512Z ERROR [order-service] '
    '[trace_id=4bf92f3577b34da6a3ce929d0e0e4736 span_id=00f067aa0ba902b7] '
    'req_id=8f3a9c2e-41b7-4d0a-9e6f-2b7c1d5e8a90 POST /api/v2/orders 500 1843ms '
    'user_id=102934 msg="payment gateway timeout"'
)
LOG_SENTENCE = (
    "Order service returned 500 on POST /api/v2/orders after 1.8s: "
    "payment gateway timeout."
)

PEOPLE = [{"name": "Олена Петренко", "city": "Київ"}] * 20

UA_SENTENCE = (
    "Будь ласка, переглянь пул-реквест і перевір міграцію бази даних перед деплоєм."
)

PAIRS = [
    ("Лог-рядок проти речення", "лог-рядок", LOG_LINE, "речення", LOG_SENTENCE),
    (
        "json.dumps з українськими іменами",
        "ensure_ascii=True",
        json.dumps(PEOPLE),
        "ensure_ascii=False",
        json.dumps(PEOPLE, ensure_ascii=False),
    ),
    ("Регістр", "ALL CAPS", UA_SENTENCE.upper(), "звичайний", UA_SENTENCE),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    client = make_client()
    print(f"Модель: {args.model}, count_tokens, input_tokens")

    for title, label_a, text_a, label_b, text_b in PAIRS:
        a = count_tokens(client, args.model, text_a)
        b = count_tokens(client, args.model, text_b)
        width = max(len(label_a), len(label_b), len("різниця"))
        print(f"\n{title}")
        print(f"  {label_a:<{width}}  {a:>5}")
        print(f"  {label_b:<{width}}  {b:>5}")
        print(f"  {'різниця':<{width}}  {a / b:>5.1f}×")


if __name__ == "__main__":
    main()
