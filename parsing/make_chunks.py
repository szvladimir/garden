import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("GARDEN_DB_PATH", "data/garden.db")
MAX_CHARS = 2000


def build_chunks(db_path: str | Path | None = None):
    db_path = Path(db_path or DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS message_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_name TEXT,
            start_message_id INTEGER,
            end_message_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            chunk_text TEXT
        )
        """
    )
    cur.execute("DELETE FROM message_chunks")

    rows = cur.execute("""
        SELECT id, telegram_msg_id, chat_name, date, sender, text
        FROM messages
        WHERE text IS NOT NULL AND trim(text) <> ''
        ORDER BY chat_name, date, telegram_msg_id
    """).fetchall()

    current_chat = None
    chunk = []
    chunk_len = 0

    def save_chunk(chunk):
        if not chunk:
            return

        first = chunk[0]
        last = chunk[-1]

        text = "\n".join(
            f"[{r['date']}] {r['sender']}: {r['text']}"
            for r in chunk
        )

        cur.execute("""
            INSERT INTO message_chunks
            (chat_name, start_message_id, end_message_id, start_date, end_date, chunk_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            first["chat_name"],
            first["telegram_msg_id"],
            last["telegram_msg_id"],
            first["date"],
            last["date"],
            text
        ))

    for row in rows:
        line = f"[{row['date']}] {row['sender']}: {row['text']}"
        chat_changed = current_chat is not None and row["chat_name"] != current_chat

        if chat_changed or chunk_len + len(line) > MAX_CHARS:
            save_chunk(chunk)
            chunk = []
            chunk_len = 0

        current_chat = row["chat_name"]
        chunk.append(row)
        chunk_len += len(line)

    save_chunk(chunk)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_chunks()
    print("message_chunks filled")