import logging
from telegram import Update
from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN
from bot.commands import setup_commands

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    setup_commands(application)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
