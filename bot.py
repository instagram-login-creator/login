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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-app-name.onrender.com

# Initialize Flask and Bot
app = Flask(__name__)
bot = telebot.TeleBot(BOT_A_TOKEN)
user_states = {}  # Track user flow

# --- UI Helpers ---
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📬 Chat ID", callback_data="chat_id"),
        InlineKeyboardButton("📺 YouTube", callback_data="youtube")
    )
    return markup

def resolution_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("360p", callback_data="res_360"),
        InlineKeyboardButton("480p", callback_data="res_480"),
        InlineKeyboardButton("720p", callback_data="res_720")
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

# --- Handlers ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    user_states.pop(user_id, None)
    send_intro(user_id, name)
    notify_admin(user_id, name, "/start")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    if user_states.get(user_id) == "awaiting_link":
        user_states[user_id] = {"state": "awaiting_resolution", "link": message.text}
        bot.send_message(user_id, "🎞️ Choose a resolution:", reply_markup=resolution_menu())
    else:
        send_intro(user_id, name)
        notify_admin(user_id, name, message.text)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    name = call.from_user.first_name

    if call.data == "chat_id":
        bot.send_message(user_id, f"Your Chat ID is: `{user_id}`", parse_mode="Markdown")
        send_intro(user_id, name)

    elif call.data == "youtube":
        user_states[user_id] = "awaiting_link"
        bot.send_message(user_id, "📥 Send the YouTube link to download:")

    elif call.data.startswith("res_"):
        res = call.data.split("_")[1]
        link_info = user_states.get(user_id)
        if not isinstance(link_info, dict) or "link" not in link_info:
            bot.send_message(user_id, "❌ No link found. Please try again.")
            send_intro(user_id, name)
            return

        url = link_info["link"]
        bot.send_message(user_id, f"⏬ Downloading video at {res}p... Please wait.")
        download_and_send_video(user_id, url, res)
        user_states.pop(user_id, None)
        send_intro(user_id, name)

# --- Downloading ---
def download_and_send_video(chat_id, url, resolution):
    format_map = {
        "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "720": "bestvideo[height<=720]+bestaudio/best[height<=720]"
    }

    ydl_opts = {
        'format': format_map.get(resolution, 'best'),
        'merge_output_format': 'mp4',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'ffmpeg_location': "ffmpeg",
        'prefer_ffmpeg': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        with open(file_path, 'rb') as f:
            bot.send_video(chat_id, f)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Failed to download video.\nError: {e}")

# --- Webhook ---
@app.route(f"/{BOT_A_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_A_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
