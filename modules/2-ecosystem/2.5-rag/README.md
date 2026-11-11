# Demo: RAG (Retrieval-Augmented Generation)

**Module:** 2 - Ecosystem
**Lectures:** 2.5

## Що показує

Робочий RAG pipeline на PGVector + OpenAI embeddings + Claude. Це другий з трьох підходів які порівнює лекція 2.5 (prompting, RAG, fine-tuning). Скрипт демонструє повний цикл:

1. Підняти PGVector (Postgres з vector extension) через docker compose.
2. Завантажити `knowledge-base.md` (база знань про вигаданий продукт TeamHub) і розбити на чанки.
3. Створити embeddings через OpenAI `text-embedding-3-small` (1536 вимірів).
4. Зберегти чанки + embeddings у PGVector з ivfflat індексом для cosine similarity.
5. Семантичний пошук: query embedding порівнюється з документами через cosine, повертає top-K релевантних чанків.
6. Передати знайдений контекст Claude як system + user message, отримати відповідь обмежену контекстом.

Ключове розуміння: модель не бачила цю базу знань під час тренування, але через RAG може коректно відповідати на специфічні питання про продукт. Коли база оновлюється, не треба перетреновувати модель, треба тільки переіндексувати.

## Pre-requisites

- Docker (для PGVector)
- [uv](https://docs.astral.sh/uv/getting-started/installation/): сам поставить потрібний Python
- OpenAI API ключ (для embeddings)
- Anthropic API ключ (для Claude)

## Як запустити

Перший раз (один на весь курс): постав [uv](https://docs.astral.sh/uv/getting-started/installation/), у корені репо скопіюй `.env.example` у `.env` і впиши ключі. Далі з папки уроку:

```bash
docker compose up -d       # підняти PGVector (або make up)
uv run rag_pipeline.py     # запустити pipeline, потрібні OPENAI_API_KEY і ANTHROPIC_API_KEY
docker compose down        # зупинити PGVector, дані залишаються (або make down)
docker compose down -v     # повне очищення разом з volume (або make clean)
```

Перший `uv run` створює одне `.venv` у корені репо і ставить туди пакети для всіх уроків модулів 1-2, далі воно береться готовим. На Windows команди ті самі.

## Очікуваний output

Покрокова трасування:

1. `База даних готова`: створена таблиця `documents` і ivfflat індекс.
2. `Завантажено N чанків з knowledge-base.md`: chunking результат.
3. `Створюємо embeddings...` → `Збережено N чанків в PGVector`.
4. Чотири демо-запити (Slack, плани, SSO, CI/CD), для кожного видно top-5 знайдених чанків з similarity score, потім відповідь Claude обмежену цим контекстом.
5. Кількість input/output токенів кожного виклику.

При повторному запуску чанки не вставляються заново (перевірка `COUNT(*)`), пошук і генерація працюють без перерахунку embeddings.

## Source

- Lecture 2.5 у курсі "Agentic Engineering з Claude"
- Anthropic Contextual Retrieval blog: https://www.anthropic.com/engineering/contextual-retrieval
- PGVector документація: https://github.com/pgvector/pgvector
- OpenAI embeddings docs: https://platform.openai.com/docs/guides/embeddings
