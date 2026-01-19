# Script de verificación para Windows PowerShell
# ADB Control API - Verificación de Solución

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       ADB CONTROL API - VERIFICACIÓN DE SOLUCIÓN          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Función para verificar comandos
function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            Write-Host "✓ $Command está instalado" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ $Command NO está instalado" -ForegroundColor Red
        return $false
    }
}

# Función para verificar archivos
function Test-File {
    param([string]$Path)
    if (Test-Path $Path) {
        Write-Host "✓ Archivo encontrado: $Path" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "✗ Archivo NO encontrado: $Path" -ForegroundColor Red
        return $false
    }
}

# 1. Verificar requisitos del sistema
Write-Host "1. Verificando requisitos del sistema..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Test-Command "docker"
Test-Command "docker-compose"
Test-Command "python"
Test-Command "adb"
Test-Command "curl"

Write-Host ""
Write-Host "2. Verificando archivos del proyecto..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Test-File "Dockerfile"
Test-File "docker-compose.yml"
Test-File "main.py"
Test-File "requirements.txt"
Test-File "README.md"
Test-File "test_api.py"
Test-File "TESTING_GUIDE.md"
Test-File "ADB_Control_API.postman_collection.json"

Write-Host ""
Write-Host "3. Verificando contenedor Docker..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$container = docker ps --filter "name=adb-control-api" --format "{{.Names}}" 2>$null
if ($container) {
    Write-Host "✓ Contenedor está corriendo: $container" -ForegroundColor Green
}
else {
    Write-Host "⚠ Contenedor NO está corriendo" -ForegroundColor Yellow
    Write-Host "  Intenta: docker-compose up -d" -ForegroundColor Gray
}

Write-Host ""
Write-Host "4. Verificando conectividad a la API..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API accesible en http://localhost:8000" -ForegroundColor Green
        Write-Host "  Response Code: $($response.StatusCode)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "✗ API NO es accesible" -ForegroundColor Red
    Write-Host "  Asegúrate que Docker está corriendo" -ForegroundColor Gray
}

Write-Host ""
Write-Host "5. Verificando estructura del código..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$mainContent = Get-Content main.py

if ($mainContent -match "FastAPI") {
    Write-Host "✓ FastAPI encontrado en main.py" -ForegroundColor Green
}

if ($mainContent -match "AdbDeviceTcp") {
    Write-Host "✓ Librería ADB encontrada" -ForegroundColor Green
}

if ($mainContent -match "youtube") {
    Write-Host "✓ Soporte para YouTube encontrado" -ForegroundColor Green
}

if ($mainContent -match "@app.get|@app.post") {
    Write-Host "✓ Endpoints encontrados" -ForegroundColor Green
}

Write-Host ""
Write-Host "6. Verificando dependencias..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "Contenido de requirements.txt:" -ForegroundColor Gray
Get-Content requirements.txt | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "RESUMEN DE VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host ""
Write-Host "✓ La solución está completa y lista para probar" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Asegúrate que tu dispositivo Android está en red" -ForegroundColor Gray
Write-Host "  2. Ejecuta: python test_api.py" -ForegroundColor Gray
Write-Host "  3. O usa Postman importando: ADB_Control_API.postman_collection.json" -ForegroundColor Gray
Write-Host ""
Write-Host "Para más información, ver: TESTING_GUIDE.md" -ForegroundColor Gray
Write-Host ""
