# Guía de Pruebas - ADB Control API

## 📋 Descripción General

Esta guía documenta todos los procedimientos para probar la API de Control ADB que permite:
- Conectarse a dispositivos Android via ADB
- Reproducir videos de YouTube
- Controlar reproducción (pausa, salida)
- Descargar capturas de pantalla
- Enviar comandos ADB personalizados

## 🚀 Requisitos Previos

### Hardware
- Un dispositivo Android con:
  - Depuración ADB habilitada (`Configuración > Opciones de Desarrollador > Depuración ADB`)
  - USB habilitado (o red habilitada si se usa TCP/IP)
  - Acceso a la red desde la máquina que ejecuta Docker

### Software
- Docker y Docker Compose instalados
- Python 3.8+ (para script de pruebas)
- Postman (opcional, para pruebas interactivas)
- ADB instalado localmente (para verificación)

## 🏗️ Procedimiento de Instalación

### 1. Construir la imagen Docker

```bash
cd c:\docker-adb-api
docker-compose build
```

Esto creará la imagen `adb-control-api` con todas las dependencias necesarias.

### 2. Iniciar los contenedores

```bash
docker-compose up -d
```

Verifica que el contenedor esté corriendo:

```bash
docker ps | grep adb-control-api
```

Deberías ver algo como:

```
CONTAINER_ID   IMAGE             STATUS
a1b2c3d4e5f6   adb-control-api   Up 2 minutes
```

### 3. Verificar que la API está accesible

```bash
curl http://localhost:8000/
```

Deberías recibir un JSON con la información de la API.

## 🔌 Preparación del Dispositivo Android

### Opción A: Conexión USB

1. Conecta el dispositivo Android vía USB
2. En la máquina host, ejecuta:
   ```bash
   adb devices
   ```
3. Autoriza el acceso en el dispositivo cuando se solicite

### Opción B: Conexión TCP/IP

1. Conecta el dispositivo vía USB primero
2. Ejecuta en la máquina host:
   ```bash
   adb tcpip 5555
   adb connect <IP_DEL_DISPOSITIVO>:5555
   adb devices
   ```
3. Desconecta el USB si lo deseas

Nota: La IP del dispositivo la encuentras en:
`Configuración > Acerca del Dispositivo > Estado > Dirección IP`

## 🧪 Métodos de Prueba

### Método 1: Script de Prueba Automático (Recomendado)

```bash
# Instalar dependencias
pip install requests

# Editar el script para configurar la IP del dispositivo
# En test_api.py, cambiar TEST_DEVICE_IP = "192.168.1.100"

# Ejecutar pruebas
python test_api.py
```

El script ejecutará automáticamente:
- ✓ Pruebas básicas de API (sin dispositivo)
- ✓ Pruebas con dispositivo (si lo autorizas)
- ✓ Pruebas de manejo de errores

### Método 2: Postman

1. Abre Postman
2. Importa la colección: `ADB_Control_API.postman_collection.json`
3. Configura las variables de entorno:
   - `base_url`: http://localhost:8000
   - `device_ip`: IP de tu dispositivo Android
   - `device_port`: 5555
   - `youtube_url`: URL de YouTube a probar

4. Ejecuta las requests manualmente o automáticamente

### Método 3: cURL (Manual)

#### Conectar dispositivo
```bash
curl -X POST "http://localhost:8000/devices/connect?ip=192.168.1.100&port=5555"
```

#### Listar dispositivos
```bash
curl -X GET "http://localhost:8000/devices"
```

#### Reproducir video
```bash
curl -X POST "http://localhost:8000/play?device_ip=192.168.1.100&video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Pausar video
```bash
curl -X POST "http://localhost:8000/stop?device_ip=192.168.1.100"
```

#### Tomar captura de pantalla
```bash
curl -X GET "http://localhost:8000/screenshot?device_ip=192.168.1.100" --output screenshot.png
```

#### Enviar comando personalizado
```bash
curl -X POST "http://localhost:8000/command?device_ip=192.168.1.100&command=getprop%20ro.product.model"
```

#### Desconectar dispositivo
```bash
curl -X POST "http://localhost:8000/devices/disconnect?device_ip=192.168.1.100"
```

## 📊 Casos de Prueba

### TC-001: Conectar Dispositivo
**Requisito**: Dispositivo Android accesible en red  
**Pasos**:
1. Enviar POST a `/devices/connect?ip=<IP>&port=5555`

**Resultado Esperado**: 
- Status: 200
- Response: `{"status": "success", "message": "Conectado a..."}`

---

### TC-002: Listar Dispositivos
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/devices`

**Resultado Esperado**:
- Status: 200
- Response contiene array `devices` con dispositivo conectado

---

### TC-003: Reproducir Video
**Requisito**: Dispositivo conectado, YouTube instalado  
**Pasos**:
1. Enviar POST a `/play?device_ip=<IP>&video_url=<YOUTUBE_URL>`

**Resultado Esperado**:
- Status: 200
- Video se abre en el dispositivo

---

### TC-004: Pausar Video
**Requisito**: Video reproduciendo  
**Pasos**:
1. Enviar POST a `/stop?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Video se pausa

---

### TC-005: Descargar Captura de Pantalla
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/screenshot?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Se descarga archivo PNG con la captura

---

### TC-006: Enviar Comando Personalizado
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/command?device_ip=<IP>&command=getprop%20ro.product.model`

**Resultado Esperado**:
- Status: 200
- Response contiene output del comando

---

### TC-007: Obtener Estado Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/status?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Response indica estado "connected"

---

### TC-008: Desconectar Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/devices/disconnect?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Dispositivo ya no aparece en `/devices`

---

### TC-009: Error - URL No YouTube
**Pasos**:
1. Enviar POST a `/play?device_ip=<IP>&video_url=https://google.com`

**Resultado Esperado**:
- Status: 400
- Response: `{"detail": "URL debe ser de YouTube"}`

---

### TC-010: Error - Dispositivo No Conectado
**Pasos**:
1. Enviar POST a `/stop?device_ip=192.168.1.999`

**Resultado Esperado**:
- Status: 400
- Response: `{"detail": "Dispositivo no conectado"}`

---

## 🔍 Verificación de Logs

### Ver logs del contenedor
```bash
docker logs adb-control-api -f
```

Esto mostrará:
- Intentos de conexión
- Comandos ejecutados
- Errores si ocurren

### Ver logs con filtro
```bash
docker logs adb-control-api | grep "ERROR"
```

## 🐛 Solución de Problemas

### Problema: "Error de conexión - ¿La API está corriendo?"

**Solución**:
```bash
# Verificar que el contenedor está corriendo
docker ps | grep adb-control-api

# Si no aparece, iniciar
docker-compose up -d

# Ver logs
docker logs adb-control-api
```

### Problema: "Dispositivo no conectado"

**Solución**:
```bash
# Verificar que el dispositivo está en red
adb devices

# Si no aparece, reconectar
adb connect <IP>:5555

# Verificar que puede hacer ping
ping <IP>
```

### Problema: "Screenshot no se descarga"

**Solución**:
```bash
# Verificar permisos de screenshot en el dispositivo
# Algunos ROMs requieren aceptar permisos

# Verificar que la ruta es correcta
# Por defecto intenta /sdcard/screenshot.png
```

### Problema: "YouTube no se abre"

**Solución**:
- YouTube debe estar instalado en el dispositivo
- Verificar que la URL es válida
- Algunos dispositivos requieren Google Play Services

## 📈 Métricas de Prueba

### Checklist de Validación

- [ ] API responde en http://localhost:8000
- [ ] Endpoint GET / retorna información
- [ ] Dispositivo se conecta exitosamente
- [ ] Dispositivo aparece en GET /devices
- [ ] Video se reproduce en el dispositivo
- [ ] Video se pausa correctamente
- [ ] Captura de pantalla se descarga
- [ ] Comando personalizado se ejecuta
- [ ] Dispositivo se desconecta correctamente
- [ ] Manejo de errores funciona
- [ ] Logs registran todas las operaciones

## 🎯 Conclusiones

La API está lista para pruebas cuando:
1. ✅ Docker está corriendo
2. ✅ API responde en localhost:8000
3. ✅ Dispositivo se conecta exitosamente
4. ✅ Todos los endpoints responden correctamente
5. ✅ No hay errores en los logs

## 📝 Notas Adicionales

- La API mantiene conexiones en memoria durante la ejecución
- Las capturas de pantalla se guardan en `/tmp/screenshots`
- Cada dispositivo se identifica por su IP
- Se pueden conectar múltiples dispositivos simultáneamente
- Todos los comandos ADB están soportados vía `/command`

---

**Última actualización**: 2026-01-19  
**Versión API**: 1.0.0  
**Estado**: ✅ Listo para Pruebas
