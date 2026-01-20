import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# 1. ADD YOUR DATA HERE
TOKEN = '8398377608:AAFz-1BO20B325T5e4TrYXJPxwrwWpWruAI'
WEB_APP_URL = 'https://trulegendbot.netlify.app'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    # This button opens your Web App
    markup.add(InlineKeyboardButton("💎 Play TRULEGEND", web_app=WebAppInfo(url=WEB_APP_URL)))
    
    bot.reply_to(message, "Welcome Legend! 🏆\n\nTap the button below to start mining $TRU and building your legacy.", reply_markup=markup)

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()