FROM python:3.11-slim

WORKDIR /app

# Instalar ADB y dependencias
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/main.py .

# Crear directorios necesarios
RUN mkdir -p /tmp/screenshots /app/.android

# Exponer puerto
EXPOSE 8000

# Ejecutar API
CMD ["python", "main.py"]
