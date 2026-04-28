import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import logging

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8681530789:AAFj7QjUkaE1xfjhcrUA7_twTI6-PEQ8czM')
FLASK_SERVER_URL = 'https://imageo-mm44.onrender.com'
NETLIFY_URL = 'https://dancing-tiramisu-fc6a7a.netlify.app'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 Bot OSINT Activo\n\n"
        f"Enlace de rastreo: {NETLIFY_URL}\n\n"
        f"Envía una foto con /compartir."
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()
        files = {'file': ('image.jpg', photo_bytes, 'image/jpeg')}
        try:
            response = requests.post(f"{FLASK_SERVER_URL}/upload", files=files)
            if response.status_code == 200:
                await update.message.reply_text(f"✅ Enlace listo:\n{NETLIFY_URL}")
            else:
                await update.message.reply_text("❌ Error en servidor.")
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Error.")
    else:
        await update.message.reply_text("📸 Envía una imagen.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compartir", share_image))
    app.add_handler(MessageHandler(filters.PHOTO, share_image))
    print("Bot corriendo 24/7...")
    app.run_polling()

if __name__ == '__main__':
    main()