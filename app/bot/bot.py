import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers import register_handlers

load_dotenv()

tg_bot_token=os.getenv("TG_BOT_TOKEN", None)


def start_bot():

    app = Application.builder().token(tg_bot_token).build()

    register_handlers(app)

    print("Bot started...")
    app.run_polling()
