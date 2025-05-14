import asyncio
import nest_asyncio
from datetime import datetime, timedelta
from flask import Flask
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from db import init_db, add_message, get_messages, delete_message
import os

# Apply fix for Replit/Render event loop
nest_asyncio.apply()

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1002577038744

bot = Bot(BOT_TOKEN)

# === FLASK APP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# === TELEGRAM HANDLER ===
async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message and update.effective_chat.id == CHANNEL_ID:
        add_message(message.message_id)
        print(f"✅ Saved message {message.message_id}")

# === DELETION LOOP ===
async def delete_old_posts():
    while True:
        data = get_messages()
        now = datetime.utcnow()

        for item in data:
            post_time = datetime.fromisoformat(item['time'])
            if now - post_time > timedelta(minutes=15):
                try:
                    await bot.delete_message(chat_id=CHANNEL_ID, message_id=item['id'])
                    delete_message(item['id'])
                    print(f"🗑️ Deleted message {item['id']}")
                except Exception as e:
                    print(f"⚠️ Failed to delete {item['id']}: {e}")

        await asyncio.sleep(60)

# === MAIN FUNCTION ===
async def main():
    init_db()
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.ALL, handle_post))
    asyncio.create_task(delete_old_posts())

    print("🚀 Bot is running...")
    await app_telegram.run_polling()

# === RUN ===
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    asyncio.get_event_loop().run_until_complete(main())
