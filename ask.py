import json
import sqlite3

import numpy as np
from openai import OpenAI

DB_PATH = "data/garden.db"

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4.1-mini"

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# client = OpenAI()
STOP_WORDS = {"stop", "ok", "quit", "exit"}


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def ask(question, top_k=5):
    q_emb = client.embeddings.create(
        model=EMBED_MODEL,
        input=question
    ).data[0].embedding

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, chat_name, start_date, end_date, chunk_text, embedding_json
        FROM message_chunks
        WHERE embedding_json IS NOT NULL
    """).fetchall()

    scored = []
    for row in rows:
        emb = json.loads(row["embedding_json"])
        score = cosine_similarity(q_emb, emb)
        scored.append((score, row))

    scored.sort(reverse=True, key=lambda x: x[0])
    best = scored[:top_k]

    context = "\n\n---\n\n".join(
        f"Chunk {row['id']} | {row['chat_name']} | {row['start_date']} - {row['end_date']}\n{row['chunk_text']}"
        for score, row in best
    )

    response = client.responses.create(
        model=CHAT_MODEL,
        input=f"""
Answer the question using only the context below.
If the answer is not in the context, say that it was not found.

Context:
{context}

Question:
{question}
"""
    )

    print(response.output_text)


def run_cli(input_func=input):
    print('Задавайте вопросы по домашнему огороду. Наберите "exit" или "ok" для выхода')

    while True:
        question = input_func("Вопрос: ").strip()
        if not question:
            continue

        if question.lower() in STOP_WORDS:
            break

        ask(question)


if __name__ == "__main__":
    run_cli()
    