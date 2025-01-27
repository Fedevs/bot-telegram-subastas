from telegram import Update
from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN
from bot.commands import setup_commands

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    setup_commands(application)
    
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()