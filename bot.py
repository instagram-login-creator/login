import telebot
import requests
import os

# Get tokens from environment variables for security
BOT_A_TOKEN = os.getenv("BOT_A_TOKEN")
BOT_B_TOKEN = os.getenv("BOT_B_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot_a = telebot.TeleBot(BOT_A_TOKEN)

# /start handler
@bot_a.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name
    bot_a.reply_to(message, f"Hello {first_name}! 👋\nWelcome to the bot by vishaloriginals\nYour Chat ID: {user_id}")
    notify_admin_and_user(user_id, first_name)

# Handles all other messages
@bot_a.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name
    text = message.text
    bot_a.reply_to(message, f"Hello {first_name}! 👋\nWelcome to the bot by vishaloriginals\nThis bot is used to know your chat ID\nYour Chat ID: {user_id}")
    notify_admin_and_user(user_id, first_name, text)

def notify_admin_and_user(user_id, name, message_text=""):
    msg = f"⚠️ Bot used by: {name} (Chat ID: {user_id})\nMessage: {message_text}"
    requests.get(f"https://api.telegram.org/bot{BOT_B_TOKEN}/sendMessage",
                 params={'chat_id': ADMIN_CHAT_ID, 'text': msg})

print("Bot is running...")
bot_a.polling()
