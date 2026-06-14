from telethon.sync import TelegramClient
from telethon import events
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
session_name = os.getenv("TG_SESSION_NAME", "telegram_session")
phone = os.getenv("TG_PHONE")

DB_PATH = "data/garden.db"

client = TelegramClient(session_name, api_id, api_hash)

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

client.start(phone=phone)

me = client.get_me()
print("Connected as:", me.first_name, me.username)

print("Listening for new messages...")
client.run_until_disconnected()