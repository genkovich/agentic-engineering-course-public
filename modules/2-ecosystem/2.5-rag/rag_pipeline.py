"""
RAG Pipeline Demo — PGVector + OpenAI Embeddings + Claude
Лекція 2.5: Fine-tuning vs Prompting vs RAG

Запуск:
  1. docker compose up -d
  2. export OPENAI_API_KEY=sk-...
  3. export ANTHROPIC_API_KEY=sk-ant-...
  4. pip install -r requirements.txt
  5. python rag_pipeline.py
"""

import os
import re
import psycopg2
from openai import OpenAI
from anthropic import Anthropic

# ── Конфігурація ──────────────────────────────────────────────────────

EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
EMBEDDING_DIMS = 1536
CLAUDE_MODEL = "claude-3-haiku-20240307"  # змініть на claude-sonnet-4-6-20250514 якщо доступний
CHUNK_SIZE = 500       # символів
CHUNK_OVERLAP = 100    # перетин між чанками
TOP_K = 5              # скільки чанків повертати

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "rag_demo",
    "user": "postgres",
    "password": "demo",
}

# ── Крок 1: Підключення до PGVector ──────────────────────────────────

def init_db():
    """Створює таблицю з vector extension."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(%s),
            source TEXT
        );
    """, (EMBEDDING_DIMS,))

    # Індекс для швидкого пошуку (ivfflat — для demo достатньо)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON documents USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10);
    """)

    print("✅ База даних готова")
    cur.close()
    conn.close()


# ── Крок 2: Завантаження та chunking ─────────────────────────────────

def load_and_chunk(filepath: str) -> list[dict]:
    """Завантажує markdown файл і розбиває на чанки."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Розбиваємо по секціях (### заголовки)
    sections = re.split(r"\n(?=### )", text)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section or len(section) < 50:
            continue

        # Якщо секція велика — додатково ріжемо по CHUNK_SIZE
        if len(section) > CHUNK_SIZE:
            for i in range(0, len(section), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk = section[i:i + CHUNK_SIZE]
                if len(chunk) > 50:  # мінімальний розмір чанку
                    chunks.append({"content": chunk, "source": filepath})
        else:
            chunks.append({"content": section, "source": filepath})

    print(f"📄 Завантажено {len(chunks)} чанків з {filepath}")
    return chunks


# ── Крок 3: Embedding через OpenAI ───────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Створює embeddings через OpenAI API."""
    client = OpenAI()
    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]


# ── Крок 4: Збереження в PGVector ────────────────────────────────────

def store_chunks(chunks: list[dict]):
    """Зберігає чанки з embeddings в базу."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Перевіряємо чи вже є дані
    cur.execute("SELECT COUNT(*) FROM documents;")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"⏭  В базі вже {count} чанків, пропускаємо вставку")
        cur.close()
        conn.close()
        return

    # Embedding всіх чанків одним запитом
    texts = [c["content"] for c in chunks]
    print("🔢 Створюємо embeddings...")
    embeddings = embed_texts(texts)

    # Вставляємо в базу
    for chunk, embedding in zip(chunks, embeddings):
        cur.execute(
            "INSERT INTO documents (content, embedding, source) VALUES (%s, %s, %s)",
            (chunk["content"], str(embedding), chunk["source"]),
        )

    conn.commit()
    print(f"💾 Збережено {len(chunks)} чанків в PGVector")
    cur.close()
    conn.close()


# ── Крок 5: Semantic search ──────────────────────────────────────────

def search(query: str, top_k: int = TOP_K) -> list[str]:
    """Шукає найрелевантніші чанки за запитом."""
    # Embedding запиту
    query_embedding = embed_texts([query])[0]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Cosine similarity пошук (<=> оператор в pgvector)
    cur.execute("""
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (str(query_embedding), str(query_embedding), top_k))

    results = cur.fetchall()
    cur.close()
    conn.close()

    print(f"\n🔍 Знайдено {len(results)} релевантних чанків:")
    for i, (content, sim) in enumerate(results):
        preview = content[:80].replace("\n", " ")
        print(f"   {i+1}. [{sim:.3f}] {preview}...")

    return [row[0] for row in results]


# ── Крок 6: RAG query — пошук + Claude ───────────────────────────────

def rag_query(question: str) -> str:
    """Повний RAG pipeline: пошук контексту → генерація відповіді Claude."""
    print(f"\n{'='*60}")
    print(f"❓ Питання: {question}")
    print(f"{'='*60}")

    # Шукаємо релевантний контекст
    context_chunks = search(question)
    context = "\n\n---\n\n".join(context_chunks)

    # Відправляємо Claude
    client = Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=(
            "Ти — бот підтримки TeamHub. Відповідай ТІЛЬКИ на основі наданого контексту. "
            "Якщо відповіді немає в контексті — скажи що не знаєш. "
            "Відповідай українською, коротко і по суті."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Контекст з бази знань:\n\n{context}\n\n---\n\nПитання: {question}",
            }
        ],
    )

    answer = response.content[0].text
    print(f"\n🤖 Відповідь Claude:\n{answer}")
    print(f"\n📊 Токени: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    return answer


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Перевіряємо API ключі
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Задайте OPENAI_API_KEY: export OPENAI_API_KEY=sk-...")
        exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Задайте ANTHROPIC_API_KEY: export ANTHROPIC_API_KEY=sk-ant-...")
        exit(1)

    # Pipeline
    print("\n🚀 RAG Pipeline Demo\n")

    # 1. Ініціалізація БД
    init_db()

    # 2. Завантаження та chunking
    chunks = load_and_chunk("knowledge-base.md")

    # 3-4. Embedding + збереження
    store_chunks(chunks)

    # 5-6. Демо запити
    rag_query("Як підключити Slack до TeamHub?")
    rag_query("Які є плани і скільки коштують?")
    rag_query("Як налаштувати SSO?")
    rag_query("Що робити якщо CI/CD pipeline падає?")
