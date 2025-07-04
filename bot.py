import os
import telebot
import requests
import yt_dlp
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables
BOT_A_TOKEN = os.getenv("BOT_A_TOKEN")
BOT_B_TOKEN = os.getenv("BOT_B_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Flask and Telegram bot
app = Flask(__name__)
bot = telebot.TeleBot(BOT_A_TOKEN)
user_states = {}  # For tracking user actions

# -- Helpers --

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📬 Chat ID", callback_data="chat_id"),
        InlineKeyboardButton("📺 YouTube", callback_data="youtube")
    )
    return markup

def send_intro(chat_id, name):
    bot.send_message(
        chat_id,
        f"Hello {name}! 👋\nThis bot can:\n✅ Tell your Chat ID\n✅ Download YouTube videos\n\nChoose an option below:",
        reply_markup=main_menu()
    )

def notify_admin(user_id, name, msg=""):
    full_msg = f"⚠️ Used by: {name} (Chat ID: {user_id})\nMessage: {msg}"
    requests.get(
        f"https://api.telegram.org/bot{BOT_B_TOKEN}/sendMessage",
        params={'chat_id': ADMIN_CHAT_ID, 'text': full_msg}
    )

# -- Handlers --

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    user_states.pop(chat_id, None)
    send_intro(chat_id, name)
    notify_admin(chat_id, name, "/start")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    state = user_states.get(chat_id)

    if state == "awaiting_link":
        url = message.text.strip()
        bot.send_message(chat_id, "⏬ Downloading your video...")
        download_and_send_video(chat_id, url)
        user_states.pop(chat_id, None)
        send_intro(chat_id, name)
    else:
        send_intro(chat_id, name)
        notify_admin(chat_id, name, message.text)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    name = call.from_user.first_name

    if call.data == "chat_id":
        bot.send_message(chat_id, f"Your Chat ID is: `{chat_id}`", parse_mode="Markdown")
        send_intro(chat_id, name)

    elif call.data == "youtube":
        user_states[chat_id] = "awaiting_link"
        bot.send_message(chat_id, "📥 Please send the YouTube video link.")

# -- YouTube Downloader --

def download_and_send_video(chat_id, url):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'ffmpeg_location': "ffmpeg",
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        with open(file_path, 'rb') as video:
            bot.send_video(chat_id, video)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Failed to download video.\nError: {str(e)}")

# -- Flask Webhook Endpoints --

@app.route(f"/{BOT_A_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!", 200

# -- Start the App --

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_A_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
