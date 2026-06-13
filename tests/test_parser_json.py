import json
import sqlite3
from pathlib import Path

from parsing.parser_json import parse_json_file


def test_parse_json_file_inserts_messages(tmp_path):
    json_path = tmp_path / "export.json"
    db_path = tmp_path / "garden.db"

    payload = {
        "name": "My Garden",
        "messages": [
            {
                "id": 1001,
                "type": "message",
                "date": "2026-01-01T00:00:00",
                "from": "Alice",
                "from_id": "user1",
                "text": "First part\n------------------------------\nSecond part",
                "text_entities": [],
            },
            {
                "id": 1002,
                "type": "message",
                "date": "2026-01-01T00:01:00",
                "from": "Alice",
                "from_id": "user1",
                "text": "",
                "text_entities": [],
            },
        ],
    }
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    parse_json_file(json_path, db_path)

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT telegram_msg_id, chat_name, sender, text FROM messages ORDER BY id").fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0][0] == 1001
    assert rows[0][1] == "My Garden"
    assert rows[0][2] == "Alice"
    assert rows[0][3] == "First part"
    assert rows[1][0] == 1001
    assert rows[1][3] == "Second part"
