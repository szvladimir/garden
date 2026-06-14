from telethon import TelegramClient, events
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

print(api_id)
print(api_hash[:8] + "...")

client = TelegramClient("telegram_session", api_id, api_hash)
client.start(phone="+491792673516")

print("Code requested")

DB_PATH = "data/garden.db"

def save_message(event):
    msg = event.message

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO messages
        (telegram_msg_id, chat_name, date, sender, text)
        VALUES (?, ?, ?, ?, ?)
    """, (
        msg.id,
        str(event.chat_id),
        msg.date.isoformat(),
        str(msg.sender_id),
        msg.message or ""
    ))

    conn.commit()
    conn.close()

@client.on(events.NewMessage)
async def handler(event):
    save_message(event)
    print("saved:", event.message.id, event.message.message)

client.start()
client.run_until_disconnected()