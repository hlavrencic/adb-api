#!/bin/bash
# Script rápido para iniciar y probar la solución

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          ADB CONTROL API - INICIO RÁPIDO                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paso 1: Construir imagen
echo -e "${YELLOW}Paso 1: Construyendo imagen Docker...${NC}"
docker-compose build

echo ""
echo -e "${YELLOW}Paso 2: Iniciando contenedor...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}Paso 3: Esperando que la API esté lista...${NC}"
sleep 3

# Paso 3: Verificar API
echo ""
echo -e "${YELLOW}Paso 4: Verificando conectividad...${NC}"

RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/ 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ API está lista en http://localhost:8000${NC}"
else
    echo "✗ API no responde. Revisa los logs:"
    docker logs adb-control-api
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              PRÓXIMOS PASOS                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Solución lista para pruebas${NC}"
echo ""
echo "Opción 1 - Pruebas automáticas:"
echo "  python test_api.py"
echo ""
echo "Opción 2 - Postman:"
echo "  Importar: ADB_Control_API.postman_collection.json"
echo ""
echo "Opción 3 - Verificación:"
echo "  bash verify.sh  (Linux/Mac)"
echo "  .\verify.ps1    (Windows PowerShell)"
echo ""
echo "Opción 4 - Manual con cURL:"
echo "  curl http://localhost:8000/"
echo ""
echo "Ver documentación:"
echo "  - TESTING_GUIDE.md"
echo "  - RESUMEN_EJECUTIVO.md"
echo ""
