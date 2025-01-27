from telegram.ext import CommandHandler,MessageHandler,filters
from .handlers import comando_desconocido, get_auction_handler, start, ofertar, mis_subastas, mis_ofertas, ayuda

def setup_commands(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ayuda", ayuda))
    application.add_handler(get_auction_handler())
    application.add_handler(CommandHandler("ofertar", ofertar))
    application.add_handler(CommandHandler("missubastas", mis_subastas))
    application.add_handler(CommandHandler("misofertas", mis_ofertas))
    application.add_handler(MessageHandler(filters.COMMAND, comando_desconocido))