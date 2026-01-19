FROM python:3.11-slim

WORKDIR /app

# Instalar ADB y dependencias
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY main.py .

# Crear directorio para screenshots
RUN mkdir -p /tmp/screenshots

# Exponer puerto
EXPOSE 8000

# Ejecutar API
CMD ["python", "main.py"]
