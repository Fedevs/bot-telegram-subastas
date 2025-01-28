from telegram.ext import CommandHandler,MessageHandler,filters
from bot.handlers.auction_handler import get_auction_handler
from bot.handlers.bid_handler import get_bid_handler, list_auctions
from bot.handlers.others import ayuda, comando_desconocido, mis_ofertas, mis_subastas, start

def setup_commands(application):
    application.add_handler(get_bid_handler())
    application.add_handler(get_auction_handler())
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ayuda", ayuda))
    application.add_handler(CommandHandler("listar", list_auctions))
    application.add_handler(CommandHandler("missubastas", mis_subastas))
    application.add_handler(CommandHandler("misofertas", mis_ofertas))
    application.add_handler(MessageHandler(filters.COMMAND, comando_desconocido))