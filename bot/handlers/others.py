from telegram import Update
from telegram.ext import ContextTypes

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
        "/listar - Listar las subastas activas\n"
        "/missubastas - Ver tus subastas (no implementado)\n"
        "/misofertas - Ver tus ofertas (no implementado)"
    )

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
