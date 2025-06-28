import os
import telebot
import requests
from flask import Flask, request

# Load environment variables
BOT_A_TOKEN = os.getenv("BOT_A_TOKEN")
BOT_B_TOKEN = os.getenv("BOT_B_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-app-name.onrender.com

# Initialize Flask and Bot
app = Flask(__name__)
bot_a = telebot.TeleBot(BOT_A_TOKEN)

# /start handler
@bot_a.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name
    bot_a.reply_to(
        message,
        f"Hello {first_name}! 👋\nWelcome to the bot by vishaloriginals\nYour Chat ID: {user_id}"
    )
    notify_admin_and_user(user_id, first_name)

# Handle all other messages
@bot_a.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name
    text = message.text
    bot_a.reply_to(
        message,
        f"Hello {first_name}! 👋\nWelcome to the bot by vishaloriginals\nThis bot is used to know your chat ID\nYour Chat ID: {user_id}"
    )
    notify_admin_and_user(user_id, first_name, text)

# Notify admin using Bot B
def notify_admin_and_user(user_id, name, message_text=""):
    msg = f"⚠️ Bot used by: {name} (Chat ID: {user_id})\nMessage: {message_text}"
    requests.get(
        f"https://api.telegram.org/bot{BOT_B_TOKEN}/sendMessage",
        params={'chat_id': ADMIN_CHAT_ID, 'text': msg}
    )

# Route for Telegram webhook updates
@app.route(f"/{BOT_A_TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot_a.process_new_updates([update])
    return "OK", 200

# Route for UptimeRobot to ping
@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!", 200

# Run the app and set webhook
if __name__ == "__main__":
    bot_a.remove_webhook()
    bot_a.set_webhook(url=f"{WEBHOOK_URL}/{BOT_A_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
