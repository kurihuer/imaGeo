FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias primero (cache de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear carpeta de uploads si no existe
RUN mkdir -p uploads

EXPOSE 5000

# Usar 1 worker sync para compatibilidad con asyncio
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 app:app
