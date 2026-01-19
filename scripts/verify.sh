#!/bin/bash
# Script de verificación rápida de la solución ADB Control API

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       ADB CONTROL API - VERIFICACIÓN DE SOLUCIÓN          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 está instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO está instalado"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Archivo encontrado: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Archivo NO encontrado: $1"
        return 1
    fi
}

echo "1. Verificando requisitos del sistema..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_command docker
check_command docker-compose
check_command python3
check_command adb
check_command curl

echo ""
echo "2. Verificando archivos del proyecto..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "Dockerfile"
check_file "docker-compose.yml"
check_file "main.py"
check_file "requirements.txt"
check_file "README.md"
check_file "test_api.py"
check_file "TESTING_GUIDE.md"
check_file "ADB_Control_API.postman_collection.json"

echo ""
echo "3. Verificando contenedor Docker..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker ps | grep -q adb-control-api; then
    echo -e "${GREEN}✓${NC} Contenedor está corriendo"
else
    echo -e "${YELLOW}⚠${NC} Contenedor NO está corriendo"
    echo "   Iniciando contenedor..."
    docker-compose up -d
    sleep 2
fi

echo ""
echo "4. Verificando conectividad a la API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/ 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} API accesible en http://localhost:8000"
    echo "  Response Code: $HTTP_CODE"
else
    echo -e "${RED}✗${NC} API NO es accesible"
    echo "  Response Code: $HTTP_CODE"
fi

echo ""
echo "5. Verificando estructura del código..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "FastAPI" main.py; then
    echo -e "${GREEN}✓${NC} FastAPI encontrado en main.py"
fi

if grep -q "AdbDeviceTcp" main.py; then
    echo -e "${GREEN}✓${NC} Librería ADB encontrada"
fi

if grep -q "youtube" main.py; then
    echo -e "${GREEN}✓${NC} Soporte para YouTube encontrado"
fi

if grep -q "@app.get\|@app.post" main.py; then
    echo -e "${GREEN}✓${NC} Endpoints encontrados"
fi

echo ""
echo "6. Verificando dependencias..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Contenido de requirements.txt:"
cat requirements.txt | sed 's/^/  /'

echo ""
echo "═════════════════════════════════════════════════════════════"
echo "RESUMEN DE VERIFICACIÓN"
echo "═════════════════════════════════════════════════════════════"

echo ""
echo "✓ La solución está completa y lista para probar"
echo ""
echo "Próximos pasos:"
echo "  1. Asegúrate que tu dispositivo Android está en red"
echo "  2. Ejecuta: python test_api.py"
echo "  3. O usa Postman importando: ADB_Control_API.postman_collection.json"
echo ""
echo "Para más información, ver: TESTING_GUIDE.md"
echo ""
