import json
import os
import sqlite3

from fastapi.testclient import TestClient


def test_upload_json_file_is_saved(tmp_path):
    os.environ["UPLOAD_DIR"] = str(tmp_path / "upload")
    db_path = tmp_path / "garden.db"
    os.environ["GARDEN_DB_PATH"] = str(db_path)

    from app.main import app

    client = TestClient(app)
    data = {
        "name": "garden",
        "messages": [
            {
                "id": 101,
                "type": "message",
                "date": "2026-01-01T00:00:00",
                "from": "Alice",
                "text": "First message",
            }
        ],
    }
    response = client.post(
        "/api-call/upload",
        files={"file": ("sample.json", json.dumps(data), "application/json")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "sample.json"
    assert body["saved_to"].endswith("sample.json")
    assert body["inserted_messages"] == 1
    assert (tmp_path / "upload" / "sample.json").exists()

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT telegram_msg_id, text FROM messages LIMIT 1").fetchone()
    conn.close()
    assert row == (101, "First message")
