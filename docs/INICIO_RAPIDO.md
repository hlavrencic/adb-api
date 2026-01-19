# 🚀 INICIO RÁPIDO - ADB Control API

## ⚡ 3 Comandos para Empezar

```powershell
# 1. Construir y iniciar
wsl docker compose up -d

# 2. Ejecutar pruebas
wsl python3 test_api.py

# 3. Ver la API
curl http://localhost:8000/
```

---

## 📖 Documentos Principales

| Documento | Para | Tiempo |
|-----------|------|--------|
| **QUICK_START_WINDOWS.md** | Inicio rápido | 5 min |
| **TESTING_GUIDE.md** | Casos de prueba | 20 min |
| **REPORTE_PRUEBAS.md** | Resultados | 10 min |
| **RESUMEN_EJECUTIVO.md** | Detalles técnicos | 15 min |

---

## 🎯 Endpoints Principales

```
GET  /                    - Info de la API
POST /devices/connect     - Conectar dispositivo
GET  /devices             - Listar conectados
POST /play                - Reproducir video
POST /stop                - Pausar video
GET  /screenshot          - Descargar captura
POST /command             - Comando ADB
```

---

## ✅ Estado Actual

```
✅ API Funcional
✅ Docker Corriendo
✅ 16 Pruebas Pasadas
✅ Documentación Completa
✅ Listo para Usar
```

---

**Ver más**: Revisa QUICK_START_WINDOWS.md o TESTING_GUIDE.md
