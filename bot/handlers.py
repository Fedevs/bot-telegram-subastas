from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from datetime import datetime, timedelta

from database.appwrite_client import create_auction

TITLE, IMAGE, PRICE, INCREMENT, END_DATE, URL, DESCRIPTION, CONFIRMATION = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f'Hola {user.first_name}! Bienvenido al bot de subastas. Usa /ayuda para ver los comandos disponibles.')

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/ayuda - Mostrar esta ayuda\n"
        "/subastar - Crear una nueva subasta\n"
        "/ofertar - Hacer una oferta en una subasta (no implementado)\n"
        "/missubastas - Ver tus subastas (no implementado)\n"
        "/misofertas - Ver tus ofertas (no implementado)"
    )

async def start_auction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vamos a crear una nueva subasta. Por favor, ingresa el título:")
    return TITLE

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Saltar", callback_data='skip_image')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ahora, envía una imagen del artículo o presiona 'Saltar' si no quieres incluir una imagen:",
        reply_markup=reply_markup
    )
    return IMAGE

async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['image_url'] = None
        await update.callback_query.edit_message_text("Imagen saltada. Ingresa el precio inicial:")
        return PRICE
    
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        context.user_data['image_url'] = file.file_path
        await update.message.reply_text("Imagen recibida. Ahora, ingresa el precio inicial (sin decimales):")
        return PRICE
    
    await update.message.reply_text("Por favor, envía una imagen o presiona el botón 'Saltar'.")
    return IMAGE

async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['price'] = int(update.message.text)
        keyboard = [
            [InlineKeyboardButton("1000", callback_data='increment_1000'),
             InlineKeyboardButton("2000", callback_data='increment_2000')],
            [InlineKeyboardButton("Personalizado", callback_data='custom_increment')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Selecciona el incremento mínimo o elige 'Personalizado' para ingresar un valor diferente:",
            reply_markup=reply_markup
        )
        return INCREMENT
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número entero válido para el precio.")
        return PRICE

async def receive_increment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == 'increment_1000':
            context.user_data['increment'] = 1000
        elif query.data == 'increment_2000':
            context.user_data['increment'] = 2000
        elif query.data == 'custom_increment':
            await query.edit_message_text("Por favor, ingresa el valor de incremento personalizado:")
            return INCREMENT
    else:
        try:
            context.user_data['increment'] = int(update.message.text)
        except ValueError:
            await update.message.reply_text("Por favor, ingresa un número entero válido para el incremento.")
            return INCREMENT

    # Pasar a la selección de fecha de finalización
    two_days_date = datetime.now() + timedelta(days=2)
    three_days_date = datetime.now() + timedelta(days=3)
    two_days_date = two_days_date.replace(hour=22, minute=0, second=0, microsecond=0)
    three_days_date = three_days_date.replace(hour=22, minute=0, second=0, microsecond=0)
    
    keyboard = [
        [InlineKeyboardButton(f"En 2 días ({two_days_date.strftime('%d/%m/%Y %H:%M')})", callback_data='end_date_2_days')],
        [InlineKeyboardButton(f"En 3 días ({three_days_date.strftime('%d/%m/%Y %H:%M')})", callback_data='end_date_3_days')],
        [InlineKeyboardButton("Ingresar fecha y hora manualmente", callback_data='custom_end_date')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await query.edit_message_text(
            "Selecciona la fecha y hora de finalización de la subasta:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Selecciona la fecha y hora de finalización de la subasta:",
            reply_markup=reply_markup
        )
    return END_DATE

async def handle_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'end_date_2_days':
        end_date = datetime.now() + timedelta(days=2)
        end_date = end_date.replace(hour=22, minute=0, second=0, microsecond=0)
    elif query.data == 'end_date_3_days':
        end_date = datetime.now() + timedelta(days=3)
        end_date = end_date.replace(hour=22, minute=0, second=0, microsecond=0)
    elif query.data == 'custom_end_date':
        await query.edit_message_text("Por favor, ingresa la fecha y hora de finalización en el formato DD/MM/YYYY HH:MM:")
        return END_DATE
    
    if query.data in ['end_date_2_days', 'end_date_3_days']:
        context.user_data['end_date'] = end_date
        await query.edit_message_text(f"Fecha de finalización establecida: {end_date.strftime('%d/%m/%Y %H:%M')}")
        
        keyboard = [
            [InlineKeyboardButton("Saltar", callback_data='skip_url')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Ahora, ingresa un enlace adicional o presiona 'Saltar':",
            reply_markup=reply_markup
        )
        return URL
    
    return END_DATE

async def receive_custom_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        end_date = datetime.strptime(update.message.text, "%d/%m/%Y %H:%M")
        if end_date <= datetime.now():
            await update.message.reply_text("La fecha y hora de finalización deben ser futuras. Por favor, intenta de nuevo:")
            return END_DATE
        
        context.user_data['end_date'] = end_date
        await update.message.reply_text(f"Fecha de finalización establecida: {end_date.strftime('%d/%m/%Y %H:%M')}")
        
        keyboard = [
            [InlineKeyboardButton("Saltar", callback_data='skip_url')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Ahora, ingresa un enlace adicional o presiona 'Saltar':",
            reply_markup=reply_markup
        )
        return URL
    except ValueError:
        await update.message.reply_text("Formato de fecha y hora inválido. Por favor, usa el formato DD/MM/YYYY HH:MM.")
        return END_DATE

async def receive_custom_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        end_date = datetime.strptime(update.message.text, "%d/%m/%Y %H:%M")
        if end_date <= datetime.now():
            await update.message.reply_text("La fecha y hora de finalización deben ser futuras. Por favor, intenta de nuevo:")
            return END_DATE
        
        context.user_data['end_date'] = end_date
        await update.message.reply_text(f"Fecha de finalización establecida: {end_date.strftime('%d/%m/%Y %H:%M')}")
        
        keyboard = [
            [InlineKeyboardButton("Saltar", callback_data='skip_url')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Ahora, ingresa un enlace adicional o presiona 'Saltar':",
            reply_markup=reply_markup
        )
        return URL
    except ValueError:
        await update.message.reply_text("Formato de fecha y hora inválido. Por favor, usa el formato DD/MM/YYYY HH:MM.")
        return END_DATE

async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['url'] = None
        keyboard = [
            [InlineKeyboardButton("Saltar", callback_data='skip_description')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "Enlace saltado. Ingresa una descripción del artículo o presiona 'Saltar':",
            reply_markup=reply_markup
        )
        return DESCRIPTION
    
    context.user_data['url'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Saltar", callback_data='skip_description')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ingresa una descripción del artículo o presiona 'Saltar':",
        reply_markup=reply_markup
    )
    return DESCRIPTION

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['description'] = None
    else:
        context.user_data['description'] = update.message.text
    
    # Mostrar resumen y pedir confirmación
    resumen = f"Resumen de la subasta:\n"
    resumen += f"Título: {context.user_data['title']}\n"
    resumen += f"Precio inicial: $ {context.user_data['price']}\n"
    resumen += f"Incremento: $ {context.user_data['increment']}\n"
    resumen += f"Fecha de finalización: {context.user_data['end_date'].strftime('%d/%m/%Y %H:%M')}\n"
    resumen += f"Enlace: {context.user_data['url'] or '-'}\n"
    resumen += f"Descripción: {context.user_data['description'] or '-'}\n"
    
    keyboard = [
        [InlineKeyboardButton("Confirmar", callback_data='confirm'),
         InlineKeyboardButton("Cancelar", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(resumen, reply_markup=reply_markup)
    else:
        await update.message.reply_text(resumen, reply_markup=reply_markup)
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm':
        # Guardar en Appwrite
        user = update.effective_user
        auction_data = {
            'telegram_user_id': user.id,
            'username': user.username,
            'title': context.user_data['title'],
            'image_url': context.user_data['image_url'],
            'price': context.user_data['price'],
            'increment': context.user_data['increment'],
            'end_date': context.user_data['end_date'].strftime("%m/%d/%Y %H:%M"),
            'url': context.user_data['url'],
            'description': context.user_data['description']
        }
        
        try:
            create_auction(auction_data)
            await query.edit_message_text("¡Subasta creada con éxito!")
        except Exception as e:
            await query.edit_message_text(f"Error al crear la subasta: {str(e)}")
    else:
        await query.edit_message_text("Creación de subasta cancelada.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

def get_auction_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('subastar', start_auction)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            IMAGE: [
                MessageHandler(filters.PHOTO, receive_image),
                CallbackQueryHandler(receive_image, pattern='^skip_image$')
            ],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price)],
            INCREMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_increment),
                CallbackQueryHandler(receive_increment, pattern='^increment_')
            ],
            END_DATE: [
                CallbackQueryHandler(handle_end_date, pattern='^end_date_'),
                CallbackQueryHandler(handle_end_date, pattern='^custom_end_date$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_end_date)
            ],
            URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url),
                CallbackQueryHandler(receive_url, pattern='^skip_url$')
            ],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description),
                CallbackQueryHandler(receive_description, pattern='^skip_description$')
            ],
            CONFIRMATION: [CallbackQueryHandler(confirmation)]
        },
        fallbacks=[CommandHandler('cancelar', cancel)]
    )

async def ofertar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementar la lógica para hacer una oferta
    pass

async def mis_subastas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementar la lógica para ver las subastas del usuario
    pass

async def mis_ofertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementar la lógica para ver las ofertas del usuario
    pass

async def comando_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Lo siento, no entiendo ese mensaje. Por favor, usa un comando válido. "
        "Escribe /ayuda para ver la lista de comandos disponibles."
    )

# Agregar más manejadores según sea necesario