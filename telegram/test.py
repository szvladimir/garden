from telethon import TelegramClient

from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

client = TelegramClient(
    "telegram_session",
    api_id,
    api_hash
)

client.start(phone="+491792673516")

print("SUCCESS")

