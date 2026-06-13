import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


SEPARATOR_PATTERN = re.compile(r"\n-{10,}\n")


def _normalize_text(text: Any) -> Optional[str]:
    if text is None:
        return None
    if isinstance(text, list):
        parts: List[str] = []
        for item in text:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                item_text = item.get("text")
                if isinstance(item_text, str):
                    parts.append(item_text)
        text = "".join(parts)
    if not isinstance(text, str):
        return None
    cleaned = text.strip()
    return cleaned or None


def _split_messages(text: str) -> List[str]:
    if not text:
        return []
    parts = [part.strip() for part in SEPARATOR_PATTERN.split(text) if part and part.strip()]
    return parts if len(parts) > 1 else [text.strip()]


def parse_json_file(json_path: str | Path, db_path: str | Path = "data/garden.db") -> int:
    json_path = Path(json_path)
    db_path = Path(db_path)

    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        raise ValueError("Expected 'messages' to be a list")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_msg_id INTEGER,
            chat_name TEXT,
            date TEXT,
            sender TEXT,
            text TEXT,
            reply_to_msg_id INTEGER,
            has_media INTEGER,
            media_type TEXT,
            source_file TEXT
        )
        """
    )

    chat_name = payload.get("name") or payload.get("title") or None
    inserted = 0

    for message in messages:
        if not isinstance(message, dict):
            continue

        text = _normalize_text(message.get("text"))
        if not text:
            continue

        for part in _split_messages(text):
            sender = None
            if isinstance(message.get("from"), str):
                sender = message.get("from")
            elif isinstance(message.get("actor"), str):
                sender = message.get("actor")

            has_media = 1 if any(key in message for key in ("photo", "video", "document", "sticker", "voice")) else 0
            media_type = None
            if "photo" in message:
                media_type = "photo"
            elif "video" in message:
                media_type = "video"
            elif "document" in message:
                media_type = "document"
            elif "sticker" in message:
                media_type = "sticker"
            elif "voice" in message:
                media_type = "voice"

            conn.execute(
                """
                INSERT INTO messages (
                    telegram_msg_id, chat_name, date, sender, text, reply_to_msg_id, has_media, media_type, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.get("id"),
                    chat_name,
                    message.get("date"),
                    sender,
                    part,
                    None,
                    has_media,
                    media_type,
                    str(json_path),
                ),
            )
            inserted += 1

    conn.commit()
    conn.close()
    return inserted
