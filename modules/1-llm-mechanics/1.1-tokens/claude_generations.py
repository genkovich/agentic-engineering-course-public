"""One paragraph in EN and UA on two generations of the Claude tokenizer.

Sonnet 4.6 runs on the old tokenizer, Sonnet 5.5 on the new one (Opus 4.7
and everything later). count_tokens is free, but needs an API key.

Usage:
  python3 claude_generations.py
  python3 claude_generations.py --model claude-haiku-4-5 --model claude-opus-5-5
  python3 claude_generations.py --file my_prompt.md
"""
import argparse
import datetime
import re
from pathlib import Path

from claude_api import count_tokens, fail, make_client

DEFAULT_MODELS = ["claude-sonnet-4-6", "claude-sonnet-5-5"]

PARAGRAPH = {
    "EN": (
        "Before deploying the new version, the team must run all tests, check the "
        "database migrations and update the documentation. If something goes wrong, "
        "we roll back the release and write a short incident report for the rest of "
        "the company."
    ),
    "UA": (
        "Перед розгортанням нової версії команда має запустити всі тести, перевірити "
        "міграції бази даних і оновити документацію. Якщо щось піде не так, ми "
        "відкочуємо реліз і пишемо короткий звіт про інцидент для решти компанії."
    ),
}


def generation(model: str) -> str:
    """New tokenizer: Opus 4.7 and later, every 5.x model and Fable."""
    if "fable" in model:
        return "новий"
    m = re.match(r"claude-(opus|sonnet|haiku)-(\d+)-(\d+)", model)
    if not m:
        return "?"
    family, major, minor = m.group(1), int(m.group(2)), int(m.group(3))
    if major >= 5 or (family == "opus" and (major, minor) >= (4, 7)):
        return "новий"
    return "старий"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", action="append", help="можна передати кілька разів")
    parser.add_argument("--file", type=Path, help="свій текст замість абзацу EN/UA")
    args = parser.parse_args()

    models = args.model or DEFAULT_MODELS
    if args.file and not args.file.is_file():
        fail(f"Файл {args.file} не знайдено.")
    texts = {args.file.name: args.file.read_text()} if args.file else PARAGRAPH

    client = make_client()
    today = datetime.date.today().isoformat()
    counts = {m: {k: count_tokens(client, m, t) for k, t in texts.items()} for m in models}

    labels = list(texts)
    has_ratio = labels == ["EN", "UA"]
    width = max(len(m) for m in models)
    header = f"{'Модель':<{width}}  {'Дата':<10}  {'Токенізатор':<11}"
    header += "".join(f"  {k:>8}" for k in labels)
    if has_ratio:
        header += f"  {'UA/EN':>6}"
    print(f"count_tokens, input_tokens\n\n{header}")
    print("-" * len(header))
    for m in models:
        line = f"{m:<{width}}  {today:<10}  {generation(m):<11}"
        line += "".join(f"  {counts[m][k]:>8}" for k in labels)
        if has_ratio:
            line += f"  {counts[m]['UA'] / counts[m]['EN']:>5.2f}×"
        print(line)

    base = models[0]
    for m in models[1:]:
        growth = ", ".join(
            f"{k} {counts[m][k] / counts[base][k] - 1:+.0%}" for k in labels
        )
        print(f"\n{m} проти {base}: {growth}")

    if has_ratio:
        print(
            "\nUA/EN рахуй на тій моделі, якою користуєшся: на іншому токенізаторі "
            "множник інший."
        )


if __name__ == "__main__":
    main()
