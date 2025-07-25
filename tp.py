import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8258792690:AAH9QgR6epUv3zKyMFMUF48ZOUkKqRCcuTA"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! This is your Telegram bot.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
