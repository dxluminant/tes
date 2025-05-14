import json
import asyncio
import nest_asyncio
from datetime import datetime, timedelta
from flask import Flask
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Apply fix for Replit's already-running event loop
nest_asyncio.apply()

# === CONFIG ===
BOT_TOKEN = "7612545709:AAEOwWndy32oudCA7u5DvRkps9xMfygEnKs"
CHANNEL_ID = -1002577038744  # Replace with your full channel ID (-100 prefix)
DATA_FILE = "data.json"

bot = Bot(BOT_TOKEN)

# === FLASK SETUP ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# === DATA STORAGE ===
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# === POST HANDLER ===
async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if message and update.effective_chat.id == CHANNEL_ID:
        message_id = message.message_id
        post_time = datetime.utcnow().isoformat()

        data = load_data()
        data.append({'id': message_id, 'time': post_time})
        save_data(data)

        print(f"✅ Saved message {message_id} at {post_time}")

# === DELETION TASK ===
async def delete_old_posts():
    while True:
        data = load_data()
        new_data = []
        now = datetime.utcnow()

        for item in data:
            post_time = datetime.fromisoformat(item['time'])
            if now - post_time > timedelta(minutes=1):
                try:
                    await bot.delete_message(chat_id=CHANNEL_ID, message_id=item['id'])
                    print(f"🗑️ Deleted message {item['id']}")
                except Exception as e:
                    print(f"⚠️ Failed to delete {item['id']}: {e}")
            else:
                new_data.append(item)

        save_data(new_data)
        await asyncio.sleep(60)

# === MAIN APP ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, handle_post))
    asyncio.create_task(delete_old_posts())

    print("🚀 Bot is running...")
    await app.run_polling()

# === RUN ===
if __name__ == "__main__":
    # Run the Flask app for uptime ping
    from threading import Thread
    def run_flask():
        app.run(host="0.0.0.0", port=8080)

    Thread(target=run_flask).start()

    # Start the Telegram bot
    asyncio.get_event_loop().run_until_complete(main())
