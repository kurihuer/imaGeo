from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import asyncio
import requests

# Configuración
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8681530789:AAFj7QjUkaE1xfjhcrUA7_twTI6-PEQ8czM')
# SUSTITUYE 'tu-app-en-koyeb.koyeb.app' por la URL que te asigne Koyeb
FLASK_SERVER_URL = os.environ.get('FLASK_SERVER_URL', 'http://tu-app-en-koyeb.koyeb.app')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot de demostración de seguridad.\n\n"
        "Comandos:\n"
        "/compartir - Envia una imagen para procesar"
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        # Obtener la foto de mayor resolución
        photo_file = await update.message.photo[-1].get_file()
        file_url = photo_file.file_path
        
        # Descargar la imagen
        image_data = requests.get(file_url).content
        
        # Enviar la imagen al servidor Flask
        files = {'file': ('image.jpg', image_data, 'image/jpeg')}
        try:
            response = requests.post(f"{FLASK_SERVER_URL}/upload", files=files)
            if response.status_code == 200:
                image_url = response.json().get('url')
                # El enlace final que enviamos al usuario
                final_link = f"{FLASK_SERVER_URL}{image_url}"
                await update.message.reply_text(
                    f"Tu imagen ha sido procesada.\n\nAccede aquí para verla:\n{final_link}"
                )
            else:
                await update.message.reply_text("El servidor de imágenes no responde.")
        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            await update.message.reply_text("Error al procesar la imagen.")
    else:
        await update.message.reply_text("Por favor, envía una imagen.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compartir", share_image))
    app.add_handler(MessageHandler(filters.PHOTO, share_image))
    
    print("Bot iniciado. Esperando mensajes...")
    app.run_polling()

if __name__ == '__main__':
    main()