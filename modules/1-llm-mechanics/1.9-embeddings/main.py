"""Embeddings demo for Module 1 (Lecture 1.9).

Три демонстрації на реальних embeddings:
  1. Cosine similarity для пар слів
  2. Vector arithmetic: king - man + woman ≈ queen
  3. Семантичний пошук на 5 FAQ документах

Try-fallback: спершу Voyage AI (Anthropic рекомендує), потім OpenAI.
Якщо немає жодного ключа, gracefully exits.
"""
import os
import sys
from typing import Callable

import numpy as np
from dotenv import load_dotenv

load_dotenv()


def require_provider() -> tuple[str, str, Callable[[list[str]], list[list[float]]]]:
    """Returns (provider_name, model, embed_fn). Tries Voyage first, then OpenAI."""
    if os.environ.get("VOYAGE_API_KEY"):
        try:
            import voyageai

            client = voyageai.Client()
            model = "voyage-3.5"

            def embed(texts: list[str]) -> list[list[float]]:
                result = client.embed(texts=texts, model=model, input_type="document")
                return result.embeddings

            return ("Voyage AI", model, embed)
        except ImportError:
            pass

    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI

        client = OpenAI()
        model = "text-embedding-3-small"

        def embed(texts: list[str]) -> list[list[float]]:
            response = client.embeddings.create(input=texts, model=model)
            return [item.embedding for item in response.data]

        return ("OpenAI", model, embed)

    print(
        "Не знайдено ані VOYAGE_API_KEY, ані OPENAI_API_KEY.\n"
        "Voyage: https://www.voyageai.com (рекомендовано лекцією, безкоштовно 200M токенів).\n"
        "OpenAI: https://platform.openai.com (fallback).\n"
        "Скопіюй .env.example у .env і додай хоча б один ключ.",
        file=sys.stderr,
    )
    sys.exit(1)


def cosine(a: list[float], b: list[float]) -> float:
    av, bv = np.array(a), np.array(b)
    return float(np.dot(av, bv) / (np.linalg.norm(av) * np.linalg.norm(bv)))


def demo_pair_similarity(embed: Callable) -> None:
    print("=" * 60)
    print("Demo 1: Cosine similarity для пар слів")
    print("=" * 60)
    pairs = [
        ("король", "королева"),
        ("король", "банан"),
        ("кіт", "котик"),
        ("кіт", "автомобіль"),
        ("software engineering", "розробка програмного забезпечення"),
        ("software engineering", "приготування борщу"),
    ]
    all_words = list({w for pair in pairs for w in pair})
    vectors = embed(all_words)
    word_to_vec = dict(zip(all_words, vectors))

    print(f"{'Pair':<55} {'Cosine':>8}")
    print("-" * 65)
    for a, b in pairs:
        sim = cosine(word_to_vec[a], word_to_vec[b])
        print(f'  "{a}"  vs  "{b}"'.ljust(55) + f"  {sim:>6.3f}")
    print()
    print("Висновок: семантично схожі пари ~0.5-0.9, далекі ~0.0-0.3.")
    print("На цьому побудований семантичний пошук.")
    print()


def demo_vector_arithmetic(embed: Callable) -> None:
    print("=" * 60)
    print("Demo 2: Vector arithmetic (king - man + woman ≈ queen)")
    print("=" * 60)
    candidates = [
        "king",
        "queen",
        "man",
        "woman",
        "prince",
        "princess",
        "boy",
        "girl",
        "father",
        "mother",
        "uncle",
        "aunt",
        "banana",
        "computer",
    ]
    vectors = embed(candidates)
    word_to_vec = dict(zip(candidates, vectors))

    target = (
        np.array(word_to_vec["king"])
        - np.array(word_to_vec["man"])
        + np.array(word_to_vec["woman"])
    )

    similarities = []
    for word, vec in word_to_vec.items():
        if word in {"king", "man", "woman"}:
            continue
        sim = float(
            np.dot(target, vec) / (np.linalg.norm(target) * np.linalg.norm(vec))
        )
        similarities.append((word, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    print("Target = king - man + woman")
    print()
    print(f"{'Rank':<6} {'Word':<15} {'Cosine':>8}")
    print("-" * 35)
    for rank, (word, sim) in enumerate(similarities[:5], 1):
        print(f"  {rank:<4} {word:<15} {sim:>6.3f}")
    print()
    print(
        "Queen зазвичай у топ-3. Це класична демонстрація що embeddings"
    )
    print("кодують абстрактні напрямки (стать, тощо) як вектори у просторі.")
    print()


def demo_semantic_search(embed: Callable) -> None:
    print("=" * 60)
    print("Demo 3: Семантичний пошук на 5 FAQ документах")
    print("=" * 60)
    docs = [
        "Перейдіть в Налаштування -> Інтеграції -> GitHub. Авторизуйтесь через OAuth, "
        "оберіть репозиторії для синхронізації.",
        "Pro план коштує $12 за користувача на місяць. При щорічній оплаті знижка 20%. "
        "Є 14-денний безкоштовний trial.",
        "Налаштування -> Сповіщення -> підключити Slack workspace. Бот відправить "
        "нотифікації про нові задачі і коментарі у вибрані канали.",
        "Двофакторна автентифікація доступна на всіх планах. Підтримує TOTP "
        "(Google Authenticator) і WebAuthn (YubiKey).",
        "API rate limit: 100 запитів на хвилину для Free, 1000 для Pro, 10000 для "
        "Enterprise. Доступний через REST на api.example.com/v1.",
    ]
    query = "Як підключити повідомлення з Slack коли хтось коментує задачу?"
    print(f'Query: "{query}"')
    print()

    doc_vectors = embed(docs)
    query_vector = embed([query])[0]

    ranked = sorted(
        [
            (i, doc, cosine(query_vector, doc_vec))
            for i, (doc, doc_vec) in enumerate(zip(docs, doc_vectors))
        ],
        key=lambda x: x[2],
        reverse=True,
    )

    print(f"{'Rank':<6} {'Cosine':>8}  Document")
    print("-" * 80)
    for rank, (idx, doc, sim) in enumerate(ranked, 1):
        preview = doc[:70] + ("..." if len(doc) > 70 else "")
        print(f"  {rank:<4} {sim:>6.3f}  [{idx}] {preview}")
    print()
    print(
        "Зверни увагу: топ-документ про Slack-нотифікації, хоча у запиті немає"
    )
    print("точного слова з документа. Семантичний пошук знаходить за змістом.")
    print()


def main() -> None:
    provider, model, embed = require_provider()
    print()
    print(f"EMBEDDINGS DEMO  -  Using {provider}: {model}")
    print()

    sample_vec = embed(["test"])[0]
    print(f"Embedding dimension: {len(sample_vec)}")
    print()

    demo_pair_similarity(embed)
    demo_vector_arithmetic(embed)
    demo_semantic_search(embed)


if __name__ == "__main__":
    main()
