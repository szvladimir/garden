import sqlite3
import json
from openai import OpenAI

DB_PATH = "data/garden.db"
EMBED_MODEL = "text-embedding-3-small"

client = OpenAI()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT id, chunk_text
    FROM message_chunks
    WHERE embedding_json IS NULL
""").fetchall()

for row in rows:
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=row["chunk_text"]
    )

    embedding = response.data[0].embedding

    cur.execute("""
        UPDATE message_chunks
        SET embedding_json = ?
        WHERE id = ?
    """, (json.dumps(embedding), row["id"]))

    print("embedded chunk", row["id"])

conn.commit()
conn.close()