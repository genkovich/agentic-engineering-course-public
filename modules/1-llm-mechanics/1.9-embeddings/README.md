# Demo: Embeddings (Vector Representations)

**Module:** 1 - LLM Mechanics
**Lectures:** 1.9

## Що показує

Реальні embeddings через Voyage AI (Anthropic рекомендує саме цього провайдера, бо власних embedding моделей у Anthropic немає) або OpenAI як fallback. Три класичні демонстрації:

1. **Cosine similarity для пар слів.** Порівняння схожості: ("король", "королева"), ("король", "банан"), ("кіт", "котик"), ("кіт", "автомобіль"). Видно що семантично близькі пари мають similarity ~0.6-0.9, а далекі ~0.1-0.3.
2. **Vector arithmetic.** Класичний приклад: `king - man + woman ≈ queen`. Скрипт обчислює цей вектор і шукає найближчі слова з невеликого word set. Queen зазвичай у топ-3.
3. **Семантичний пошук.** 5 документів-іграшок (FAQ TeamHub), користувацький запит, повертаємо документи відсортовані за cosine similarity. Видно що пошук знаходить релевантний документ навіть якщо точних слів запиту в ньому немає.

Ключове розуміння з лекції: embedding це список чисел (1024-3072 виміри), і близькість векторів у цьому просторі відповідає семантичній близькості. На цьому побудований весь RAG. Розмір вектора: voyage-3.5 1024d, OpenAI text-embedding-3-small 1536d, GPT-3 12288d.

## Pre-requisites

- Python 3.10+
- `VOYAGE_API_KEY` (рекомендовано, лекція згадує саме Voyage AI) АБО `OPENAI_API_KEY` (fallback)

Для отримання Voyage API ключа: https://www.voyageai.com (200 безкоштовних 1M токенів). OpenAI: https://platform.openai.com.

## Як запустити

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # додай VOYAGE_API_KEY або OPENAI_API_KEY
make run
```

Скрипт спочатку пробує Voyage AI, потім OpenAI як fallback. Якщо обидва ключі відсутні, gracefully падає з інструкцією.

## Очікуваний output

1. Який провайдер використовується і модель: `Using Voyage AI: voyage-3.5 (1024 dims)` або `Using OpenAI: text-embedding-3-small (1536 dims)`.
2. Таблиця cosine similarity для пар слів.
3. Vector arithmetic: top-3 найближчих до `king - man + woman` з заданого word set.
4. Семантичний пошук: запит "Як підключити Slack нотифікації?" → 5 документів відсортовані за similarity, видно що FAQ про Slack у топі навіть якщо точних слів запиту в ньому нема.

## Source

- Lecture 1.9 у курсі "Agentic Engineering з Claude"
- Voyage AI docs: https://docs.voyageai.com
- Anthropic embeddings guide: https://docs.claude.com/en/docs/build-with-claude/embeddings
- OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings
- Anthropic "Mapping the Mind of a Large Language Model": https://www.anthropic.com/news/mapping-mind-language-model
