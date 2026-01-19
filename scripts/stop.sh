#!/bin/bash

# Script para detener la API Docker ADB

echo "🛑 Deteniendo API ADB Control..."

docker-compose down

echo "✅ API detenida correctamente"
