#!/bin/bash

# Script para iniciar la API Docker ADB

echo "🚀 Iniciando API ADB Control..."

# Construir imagen
echo "🔨 Construyendo imagen Docker..."
docker-compose build

# Iniciar contenedor
echo "📦 Iniciando contenedor..."
docker-compose up -d

# Esperar a que esté listo
echo "⏳ Esperando a que la API esté lista..."
sleep 3

# Verificar que está corriendo
if docker ps | grep -q adb-control-api; then
    echo "✅ API iniciada correctamente"
    echo ""
    echo "📍 URLs:"
    echo "   API: http://localhost:8000"
    echo "   Swagger: http://localhost:8000/docs"
    echo "   ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "📋 Logs:"
    docker logs -f adb-control-api
else
    echo "❌ Error al iniciar la API"
    docker logs adb-control-api
    exit 1
fi
