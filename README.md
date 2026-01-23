# ADB Control API

API Docker para controlar dispositivos Android mediante ADB (Android Debug Bridge).

## Características

- ✅ Conectar/desconectar dispositivos Android
- ✅ Obtener información detallada del dispositivo (modelo, versión, RAM, batería)
- ✅ Monitorear la aplicación actualmente en pantalla
- ✅ Listar aplicaciones instaladas
- ✅ Acceder a logs del sistema (logcat)
- ✅ Controlar el volumen (aumentar, disminuir, silenciar, nivel específico)
- ✅ Reproducir videos de YouTube
- ✅ Control de reproducción (pausa, salir)
- ✅ Descargar capturas de pantalla
- ✅ Enviar comandos ADB personalizados
- ✅ Validación automática de conexión
- ✅ Documentación interactiva con Swagger

## Requisitos

- Docker
- Docker Compose
- Dispositivos Android con depuración ADB habilitada

## Instalación

### 1. Clonar o crear el proyecto

```bash
mkdir docker-adb-api
cd docker-adb-api
```

### 2. Construir la imagen

```bash
docker-compose build
```

### 3. Iniciar el contenedor

```bash
docker-compose up -d
```

### 4. Verificar que está corriendo

```bash
docker ps | grep adb-control-api
```

## Uso

### Acceso a la API

- **URL base:** `http://localhost:8000`
- **Documentación Swagger:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Ejemplos de uso

#### 1. Conectar a un dispositivo

```bash
curl -X POST "http://localhost:8000/devices/connect?ip=192.168.0.161&port=5555"
```

#### 2. Listar dispositivos conectados

```bash
curl "http://localhost:8000/devices"
```

#### 3. Obtener información detallada del dispositivo

```bash
curl "http://localhost:8000/device/info?device_ip=192.168.0.161"
```

#### 4. Obtener aplicación actualmente en pantalla

```bash
curl "http://localhost:8000/device/current-app?device_ip=192.168.0.161"
```

#### 6. Obtener lista de aplicaciones instaladas

```bash
curl "http://localhost:8000/device/installed-apps?device_ip=192.168.0.161&limit=20"
```

#### 7. Obtener logs del sistema

```bash
curl "http://localhost:8000/device/logcat?device_ip=192.168.0.161&lines=50"
```

#### 8. Obtener volumen actual

```bash
curl "http://localhost:8000/device/volume/current?device_ip=192.168.0.161"
```

#### 9. Aumentar volumen

```bash
curl -X POST "http://localhost:8000/device/volume/increase?device_ip=192.168.0.161&steps=2"
```

#### 10. Disminuir volumen

```bash
curl -X POST "http://localhost:8000/device/volume/decrease?device_ip=192.168.0.161&steps=1"
```

#### 11. Establecer volumen a un nivel específico

```bash
curl -X POST "http://localhost:8000/device/volume/set?device_ip=192.168.0.161&level=7"
```

#### 12. Silenciar dispositivo

```bash
curl -X POST "http://localhost:8000/device/volume/mute?device_ip=192.168.0.161"
```

#### 13. Reproducir video de YouTube

```bash
curl -X POST "http://localhost:8000/play?device_ip=192.168.0.161&video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### 14. Pausar video

```bash
curl -X POST "http://localhost:8000/stop?device_ip=192.168.0.161"
```

#### 15. Salir de la app

```bash
curl -X POST "http://localhost:8000/exit?device_ip=192.168.0.161"
```

#### 16. Descargar screenshot

```bash
curl "http://localhost:8000/screenshot?device_ip=192.168.0.161" -o screenshot.png
```

#### 17. Obtener estado

```bash
curl "http://localhost:8000/status?device_ip=192.168.0.161"
```

#### 18. Enviar comando personalizado

```bash
curl -X POST "http://localhost:8000/command?device_ip=192.168.0.161&command=input%20keyevent%20KEYCODE_HOME"
```

#### 19. Desconectar dispositivo

```bash
curl -X POST "http://localhost:8000/devices/disconnect?device_ip=192.168.0.161"
```

## Endpoints

| Método | Ruta | Descripción | Parámetros |
|--------|------|-------------|-----------|
| GET | `/` | Información de la API | - |
| **Device Management** |
| POST | `/devices/connect` | Conectar dispositivo | `ip`, `port` (opcional) |
| GET | `/devices` | Listar dispositivos conectados | - |
| GET | `/status` | Estado del dispositivo | `device_ip` |
| POST | `/devices/disconnect` | Desconectar dispositivo | `device_ip` |
| **Device Information** |
| GET | `/device/info` | Información detallada del dispositivo | `device_ip` |
| GET | `/device/current-app` | Aplicación actualmente en pantalla | `device_ip` |
| GET | `/device/installed-apps` | Lista de aplicaciones instaladas | `device_ip`, `limit` (opcional) |
| GET | `/device/logcat` | Logs del sistema | `device_ip`, `lines` (opcional), `filter_text` (opcional) |
| **Volume Control** |
| GET | `/device/volume/current` | Obtener volumen actual | `device_ip` |
| POST | `/device/volume/increase` | Aumentar volumen | `device_ip`, `steps` (1-15) |
| POST | `/device/volume/decrease` | Disminuir volumen | `device_ip`, `steps` (1-15) |
| POST | `/device/volume/set` | Establecer nivel de volumen | `device_ip`, `level` (0-15) |
| POST | `/device/volume/mute` | Silenciar dispositivo | `device_ip` |
| **Video Control** |
| POST | `/play` | Reproducir video | `device_ip`, `video_url` |
| POST | `/stop` | Pausar video | `device_ip` |
| POST | `/exit` | Salir de app | `device_ip` |
| **Device Operations** |
| GET | `/screenshot` | Descargar screenshot | `device_ip` |
| POST | `/command` | Comando personalizado | `device_ip`, `command` |

## Respuestas

### Éxito (200)

```json
{
  "status": "success",
  "message": "Conectado a 192.168.0.161:5555"
}
```

### Error (4xx/5xx)

```json
{
  "detail": "Dispositivo no conectado"
}
```

## Configuración de Dispositivo Android

Para que la API funcione, necesitas:

1. **Habilitar Depuración por USB:**
   - Configuración → Información del dispositivo
   - Build Number (presiona 7 veces)
   - Configuración → Opciones de desarrollador
   - Activar "Depuración por USB"

2. **Habilitar Depuración Inalámbrica:**
   - Opciones de desarrollador → Depuración inalámbrica
   - Aceptar la solicitud de conexión

## Logs

Ver logs del contenedor:

```bash
docker logs -f adb-control-api
```

## Detener la API

```bash
docker-compose down
```

## Solución de problemas

### La API no conecta al dispositivo

1. Verifica que ADB esté habilitado en el dispositivo
2. Verifica que el dispositivo y la PC estén en la misma red
3. Comprueba la IP correcta: `adb devices`
4. Reinicia el contenedor: `docker-compose restart`

### Screenshot no se descarga

1. Verifica que el dispositivo tenga espacio en `/sdcard`
2. Revisa los logs: `docker logs adb-control-api`

## Integración con Home Assistant

Usa los scripts disponibles en `home-assistant/scripts.yaml`

## Licencia

**Licencia de Uso No Comercial**

Este proyecto está bajo una licencia de uso no comercial. Puedes utilizarlo para:
- ✅ Uso personal y educativo
- ✅ Investigación académica
- ✅ Desarrollo y testing interno
- ✅ Proyectos de código abierto no comerciales

**Uso comercial prohibido** sin autorización explícita. Para licencias comerciales, contacta a los autores.

Ver [LICENSE](LICENSE) para más detalles.
