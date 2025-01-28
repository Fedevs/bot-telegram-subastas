from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from bot.utils import format_end_date, validate_bid
from database.appwrite_client import get_active_auctions, get_auction_by_id, update_auction

# Estados del ConversationHandler
TYPING_BID, CONFIRM_BID = range(2)

# Función para listar las subastas activas
async def list_auctions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auctions = get_active_auctions()
    if not auctions:
        await update.message.reply_text("No hay subastas activas en este momento.")
        return

    for auction in auctions:
        message = (
            f"🏷 {auction['title']}\n"
            f"💰 Precio inicial: $ {auction['initial_price']}\n"
            f"📈 Precio actual: $ {auction['current_price']}\n"
            f"⬆️ Puja mínima: $ {auction['increment']}\n"
            f"⏳ Finaliza: {format_end_date(auction['end_date'])} hs\n"
        )

        if auction.get('description'):
            descr_trimmed = auction['description'][:100] + ('...' if len(auction['description']) > 100 else '')
            message += f"📝 Descripción: {descr_trimmed}\n"

        proposed_price = auction['current_price'] + auction['increment']
        
        keyboard = [
            [InlineKeyboardButton(f"Ofertar $ {proposed_price}", callback_data=f"bid_{auction['$id']}_{proposed_price}")],
            [InlineKeyboardButton("Ingresar otra oferta", callback_data=f"custom-bid_{auction['$id']}_{proposed_price}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        image_url = auction.get('image_url')
        if image_url:
            await update.message.reply_photo(photo=image_url, caption=message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)

# Manejador de ofertas
async def handle_bid_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    action, auction_id, proposed_price = data
    auction = get_auction_by_id(auction_id)

    keyboard = [
        [InlineKeyboardButton("Confirmar", callback_data='confirm'),
         InlineKeyboardButton("Cancelar", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

  
    context.user_data['auction_id'] = auction_id
    context.user_data['current_price'] = int(auction['current_price']),
    context.user_data['increment'] = int(auction['increment']),
    context.user_data['title'] = auction['title'],

    if action == "bid":
        if validate_bid(int(auction['current_price']), int(auction['increment']), int(proposed_price)):
            bid_amount = int(proposed_price)  # El monto ofrecido automáticamente
            await query.message.reply_text(f"¿Confirmas tu oferta de $ {bid_amount} para {auction['title'].upper()}?", reply_markup=reply_markup)
            context.user_data['bid_amount'] = bid_amount
            return CONFIRM_BID
        else:
            error_message = (
                "Tu oferta debe ser mayor al precio actual y cumplir con el incremento mínimo. "
                f"El precio actual es $ {auction['current_price']} y el incremento se hace de a $ {auction['increment']}. Por favor, intenta de nuevo."
            )
            await update.message.reply_text(error_message)
            return TYPING_BID
    
    elif action == "custom-bid":
        # Solicitar una oferta personalizada
        await query.message.reply_text(f"Por favor, ingresa el monto de tu oferta para la subasta de {auction['title'].upper()}")
        return TYPING_BID

# Manejador de ofertas personalizadas
async def custom_bid_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_bid = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return TYPING_BID

    current_price = context.user_data['current_price']
    min_increment = context.user_data['increment']
    title = context.user_data['title']
    if isinstance(title, tuple):
        title = title[0]

    if isinstance(current_price, tuple):
        current_price = current_price[0]

    if isinstance(min_increment, tuple):
        min_increment = min_increment[0]

    if validate_bid(current_price, min_increment, user_bid):
        context.user_data['bid_amount'] = user_bid
        keyboard = [
            [InlineKeyboardButton("Confirmar", callback_data='confirm'),
             InlineKeyboardButton("Cancelar", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"¿Confirmas tu oferta de $ {user_bid} para {title.upper()}?", reply_markup=reply_markup)
        return CONFIRM_BID
    else:
        error_message = (
            "Tu oferta debe ser mayor al precio actual y cumplir con el incremento mínimo. "
            f"El precio actual es $ {current_price} y el incremento se hace de a $ {min_increment}. Por favor, intenta de nuevo."
        )
        await update.message.reply_text(error_message)
        return TYPING_BID

# Confirmación de la oferta
async def auction_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        auction_id = context.user_data['auction_id']
        bid_amount = context.user_data['bid_amount']
        auction_data = {
            'current_price': bid_amount,
        }

        # Actualizar la base de datos con la nueva oferta
        update_auction(auction_id, auction_data)

        await query.message.reply_text(f"¡Oferta de $ {bid_amount} registrada con éxito!")
        return ConversationHandler.END
    elif query.data == "cancel":
        await query.message.reply_text("Oferta cancelada.")
        return ConversationHandler.END

# Cancelación del proceso de oferta
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proceso de oferta cancelado.")
    return ConversationHandler.END

# Configuración del manejador de ofertas
def get_bid_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_bid_query, pattern='^bid_|^custom-bid_')],
        states={
            TYPING_BID: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_bid_amount)],
            CONFIRM_BID: [CallbackQueryHandler(auction_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
