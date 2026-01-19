# 🚀 Guía Rápida de Inicio - ADB Control API

## ⚡ Inicio en 5 Minutos (Windows)

### Paso 1: Construir y Iniciar
```powershell
cd c:\docker-adb-api
docker-compose build
docker-compose up -d
```

### Paso 2: Verificar que está corriendo
```powershell
# En PowerShell
docker ps | findstr adb-control-api

# Deberías ver:
# CONTAINER ID   IMAGE             STATUS
# ...            adb-control-api   Up X seconds
```

### Paso 3: Probar la API
Abre tu navegador y ve a:
```
http://localhost:8000
```

Deberías ver un JSON con la información de la API.

---

## 🧪 Tres Formas de Probar

### Forma 1️⃣: Script Automático (Recomendado)

```powershell
# Instalar dependencias (una sola vez)
pip install requests

# Ejecutar pruebas
python test_api.py

# Seguir las instrucciones interactivas
```

**Ventajas**:
- ✅ Pruebas completas automatizadas
- ✅ Fácil de usar
- ✅ Resultados detallados

---

### Forma 2️⃣: Postman (Para pruebas manuales)

1. Descarga [Postman](https://www.postman.com/downloads/)
2. Abre Postman
3. Click en **Import**
4. Selecciona: `ADB_Control_API.postman_collection.json`
5. Configura las variables:
   - `base_url` = `http://localhost:8000`
   - `device_ip` = `192.168.1.100` (tu dispositivo)
6. ¡Prueba los endpoints!

**Ventajas**:
- ✅ Interfaz gráfica
- ✅ Fácil de ver respuestas
- ✅ Guardar historial

---

### Forma 3️⃣: PowerShell / cURL (Manual)

**Ejemplo 1 - Información de API**:
```powershell
curl http://localhost:8000/
```

**Ejemplo 2 - Conectar dispositivo**:
```powershell
curl -X POST "http://localhost:8000/devices/connect?ip=192.168.1.100&port=5555"
```

**Ejemplo 3 - Listar dispositivos**:
```powershell
curl http://localhost:8000/devices
```

---

## 🔧 Configuración del Dispositivo Android

### Paso 1: Habilitar Depuración ADB

1. En tu Android: **Configuración > Acerca del Teléfono**
2. Toca **Número de Compilación** 7 veces
3. Atrás → **Opciones de Desarrollador**
4. Habilita **Depuración ADB**

### Paso 2: Conectar por Red

En tu PC (Windows):
```powershell
# Conectar vía USB primero
adb connect 192.168.1.100:5555

# Verificar que se conectó
adb devices
```

---

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info de la API |
| `/devices/connect` | POST | Conectar dispositivo |
| `/devices` | GET | Listar dispositivos |
| `/play` | POST | Reproducir video YouTube |
| `/stop` | POST | Pausar video |
| `/exit` | POST | Salir de app |
| `/screenshot` | GET | Descargar captura |
| `/command` | POST | Comando ADB personalizado |

---

## 🆘 Solución de Problemas

### Problema: "Error de conexión"

**Solución**:
```powershell
# Verificar que Docker está corriendo
docker ps | findstr adb-control-api

# Si no aparece, reiniciar
docker-compose up -d
```

### Problema: "Dispositivo no conectado"

**Solución**:
```powershell
# Verificar dispositivo
adb devices

# Si no aparece, conectar
adb connect 192.168.1.100:5555

# Verificar conectividad
ping 192.168.1.100
```

### Problema: YouTube no se abre

**Causas**:
- YouTube no está instalado en el dispositivo
- URL no es válida
- Dispositivo sin acceso a internet

---

## 📝 Ejemplos de Comandos

### Reproducir video
```powershell
$device_ip = "192.168.1.100"
$video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

curl -X POST "http://localhost:8000/play?device_ip=$device_ip&video_url=$video"
```

### Descargar captura de pantalla
```powershell
$device_ip = "192.168.1.100"

curl -X GET "http://localhost:8000/screenshot?device_ip=$device_ip" -o screenshot.png
```

### Enviar comando personalizado
```powershell
$device_ip = "192.168.1.100"
$cmd = "getprop ro.product.model"

curl -X POST "http://localhost:8000/command?device_ip=$device_ip&command=$cmd"
```

---

## 🎯 Checklist de Verificación

- [ ] Docker instalado y corriendo
- [ ] Contenedor `adb-control-api` está up
- [ ] API responde en `http://localhost:8000`
- [ ] Dispositivo Android tiene ADB habilitado
- [ ] Dispositivo conectado a la red
- [ ] `adb devices` muestra el dispositivo
- [ ] Puedo hacer ping al dispositivo
- [ ] YouTube instalado en dispositivo

---

## 📚 Documentación Completa

Para información más detallada, ver:
- **TESTING_GUIDE.md** - Guía completa con todos los casos de prueba
- **RESUMEN_EJECUTIVO.md** - Resumen técnico del proyecto

---

## 🛑 Detener la Solución

```powershell
docker-compose down
```

---

## 💡 Tips

1. **Usar variables en PowerShell**:
```powershell
$device = "192.168.1.100"
curl "http://localhost:8000/devices?device_ip=$device"
```

2. **Guardar respuestas**:
```powershell
curl "http://localhost:8000/" | Out-File response.json
```

3. **Ver logs en tiempo real**:
```powershell
docker logs adb-control-api -f
```

---

**¿Necesitas ayuda?** Ver TESTING_GUIDE.md para solución de problemas completa.

**Estado**: ✅ Listo para Pruebas  
**Versión**: 1.0.0
