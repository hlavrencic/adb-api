# Guía de Pruebas - ADB Control API

## 📋 Descripción General

Esta guía documenta todos los procedimientos para probar la API de Control ADB que permite:
- Conectarse a dispositivos Android via ADB
- Obtener información detallada del dispositivo
- Monitorear la aplicación actualmente en pantalla
- Consultar aplicaciones instaladas y logs del sistema
- Controlar el volumen del dispositivo
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

#### Obtener información del dispositivo
```bash
curl -X GET "http://localhost:8000/device/info?device_ip=192.168.1.100"
```

#### Obtener aplicación actualmente en pantalla
```bash
curl -X GET "http://localhost:8000/device/current-app?device_ip=192.168.1.100"
```

#### Obtener lista de aplicaciones instaladas
```bash
curl -X GET "http://localhost:8000/device/installed-apps?device_ip=192.168.1.100&limit=50"
```

#### Obtener logs del sistema (logcat)
```bash
curl -X GET "http://localhost:8000/device/logcat?device_ip=192.168.1.100&lines=100"
```

#### Obtener volumen actual
```bash
curl -X GET "http://localhost:8000/device/volume/current?device_ip=192.168.1.100"
```

#### Aumentar volumen
```bash
curl -X POST "http://localhost:8000/device/volume/increase?device_ip=192.168.1.100&steps=1"
```

#### Disminuir volumen
```bash
curl -X POST "http://localhost:8000/device/volume/decrease?device_ip=192.168.1.100&steps=1"
```

#### Establecer volumen a un nivel específico
```bash
curl -X POST "http://localhost:8000/device/volume/set?device_ip=192.168.1.100&level=7"
```

#### Silenciar dispositivo
```bash
curl -X POST "http://localhost:8000/device/volume/mute?device_ip=192.168.1.100"
```
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

### TC-003: Obtener Información del Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/device/info?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Response contiene:
  - `model`: Modelo del dispositivo
  - `manufacturer`: Fabricante
  - `android_version`: Versión de Android
  - `api_level`: Nivel API
  - `total_ram`: RAM total
  - `serial_number`: Número de serie
  - `battery_info`: Información de batería

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "info": {
    "model": "SM-G970F",
    "manufacturer": "Samsung",
    "android_version": "12",
    "api_level": "31",
    "total_ram": "MemTotal:        5926788 kB",
    "storage_info": "Filesystem      Size  Used Avail Use% Mounted on...",
    "serial_number": "R38M902XXXX",
    "battery_info": "  level: 85"
  },
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-004: Obtener Aplicación Actual
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/device/current-app?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Response contiene:
  - `package`: Nombre del package de la aplicación activa
  - `activity`: Nombre de la actividad (activity)
  - `info`: Información adicional de la app

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "current_app": {
    "package": "com.google.android.youtube",
    "activity": "com.google.android.youtube.MainActivity",
    "info": {}
  },
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-005: Obtener Aplicaciones Instaladas
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/device/installed-apps?device_ip=<IP>&limit=20`

**Resultado Esperado**:
- Status: 200
- Response contiene array de aplicaciones con:
  - `package_name`: Nombre del package
  - `is_system_app`: Booleano indicando si es app del sistema

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "total_apps": 20,
  "apps": [
    {
      "package_name": "com.android.systemui",
      "is_system_app": true
    },
    {
      "package_name": "com.google.android.youtube",
      "is_system_app": false
    }
  ],
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-006: Obtener Logs del Sistema
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/device/logcat?device_ip=<IP>&lines=50`

**Resultado Esperado**:
- Status: 200
- Response contiene array con las últimas líneas del logcat

**Parámetros Opcionales**:
- `lines`: Número de líneas a recuperar (default: 50)
- `filter_text`: Filtrar logs por texto (opcional)

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "filter": null,
  "total_lines": 50,
  "logs": [
    "01-22 10:30:45.123  1234  5678 I AndroidRuntime: Process com.google.android.youtube started",
    "01-22 10:30:45.456  1234  5678 D ActivityManager: Displaying activity com.google.android.youtube.MainActivity"
  ],
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-007: Reproducir Video
**Requisito**: Dispositivo conectado, YouTube instalado  
**Pasos**:
1. Enviar POST a `/play?device_ip=<IP>&video_url=<YOUTUBE_URL>`

**Resultado Esperado**:
- Status: 200
- Video se abre en el dispositivo

---

### TC-008: Pausar Video
**Requisito**: Video reproduciendo  
**Pasos**:
1. Enviar POST a `/stop?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Video se pausa

---

### TC-009: Descargar Captura de Pantalla
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/screenshot?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Se descarga archivo PNG con la captura

---

### TC-010: Enviar Comando Personalizado
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/command?device_ip=<IP>&command=getprop%20ro.product.model`

**Resultado Esperado**:
- Status: 200
- Response contiene output del comando

---

### TC-011: Obtener Estado Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/status?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Response indica estado "connected"

---

### TC-012: Desconectar Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/devices/disconnect?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Dispositivo ya no aparece en `/devices`

---

### TC-013: Error - URL No YouTube
**Pasos**:
1. Enviar POST a `/play?device_ip=<IP>&video_url=https://google.com`

**Resultado Esperado**:
- Status: 400
- Response: `{"detail": "URL debe ser de YouTube"}`

---

### TC-014: Error - Dispositivo No Conectado
**Pasos**:
1. Enviar POST a `/stop?device_ip=192.168.1.999`

**Resultado Esperado**:
- Status: 400
- Response: `{"detail": "Dispositivo no conectado"}`

---

### TC-015: Obtener Volumen Actual
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar GET a `/device/volume/current?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- Response contiene información de volumen actual

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "volume_info": {
    "raw_output": "speaker_volume_speaker: 7"
  },
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-016: Aumentar Volumen
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/device/volume/increase?device_ip=<IP>&steps=3`

**Resultado Esperado**:
- Status: 200
- Response indica éxito
- El volumen se aumenta 3 pasos

**Ejemplo de Response**:
```json
{
  "device": "192.168.1.100",
  "action": "increase_volume",
  "steps": 3,
  "status": "success",
  "timestamp": "2026-01-22T10:30:45.123456"
}
```

---

### TC-017: Disminuir Volumen
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/device/volume/decrease?device_ip=<IP>&steps=2`

**Resultado Esperado**:
- Status: 200
- El volumen se disminuye 2 pasos

---

### TC-018: Establecer Volumen a Nivel Específico
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/device/volume/set?device_ip=<IP>&level=7`

**Resultado Esperado**:
- Status: 200
- El volumen se establece al nivel 7 (rango 0-15)

**Validaciones**:
- `level` debe estar entre 0 y 15
- Si `level` < 0 o `level` > 15: retorna 400

---

### TC-019: Silenciar Dispositivo
**Requisito**: Dispositivo conectado  
**Pasos**:
1. Enviar POST a `/device/volume/mute?device_ip=<IP>`

**Resultado Esperado**:
- Status: 200
- El dispositivo se silencia

---

### TC-020: Error - Steps Inválido
**Pasos**:
1. Enviar POST a `/device/volume/increase?device_ip=<IP>&steps=20`

**Resultado Esperado**:
- Status: 400
- Response: `{"detail": "steps debe estar entre 1 y 15"}`

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

### Problema: "Información del dispositivo incompleta"

**Solución**:
- Algunos comandos pueden no disponerse en todos los dispositivos
- El endpoint devolverá los datos disponibles parcialmente
- Revisar los logs con `/device/logcat` para más detalles

---

## 📈 Métricas de Prueba

### Checklist de Validación

- [ ] API responde en http://localhost:8000
- [ ] Endpoint GET / retorna información actualizada
- [ ] Dispositivo se conecta exitosamente
- [ ] Dispositivo aparece en GET /devices
- [ ] GET /device/info retorna información del dispositivo
- [ ] GET /device/current-app muestra app activa
- [ ] GET /device/installed-apps lista aplicaciones
- [ ] GET /device/logcat muestra logs del sistema
- [ ] GET /device/volume/current obtiene volumen actual
- [ ] POST /device/volume/increase aumenta el volumen
- [ ] POST /device/volume/decrease disminuye el volumen
- [ ] POST /device/volume/set establece nivel específico
- [ ] POST /device/volume/mute silencia el dispositivo
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
- Los nuevos endpoints de información permiten monitoreo en tiempo real del dispositivo
- El endpoint `/device/logcat` es útil para debugging de aplicaciones

---

**Última actualización**: 2026-01-22  
**Versión API**: 1.2.0  
**Estado**: ✅ Listo para Pruebas



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
