# ADB Control API

API Docker para controlar dispositivos Android mediante ADB (Android Debug Bridge).

## Características

- ✅ Conectar/desconectar dispositivos Android
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

#### 3. Reproducir video de YouTube

```bash
curl -X POST "http://localhost:8000/play?device_ip=192.168.0.161&video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### 4. Pausar video

```bash
curl -X POST "http://localhost:8000/stop?device_ip=192.168.0.161"
```

#### 5. Salir de la app

```bash
curl -X POST "http://localhost:8000/exit?device_ip=192.168.0.161"
```

#### 6. Descargar screenshot

```bash
curl "http://localhost:8000/screenshot?device_ip=192.168.0.161" -o screenshot.png
```

#### 7. Obtener estado

```bash
curl "http://localhost:8000/status?device_ip=192.168.0.161"
```

#### 8. Enviar comando personalizado

```bash
curl -X POST "http://localhost:8000/command?device_ip=192.168.0.161&command=input%20keyevent%20KEYCODE_HOME"
```

#### 9. Desconectar dispositivo

```bash
curl -X POST "http://localhost:8000/devices/disconnect?device_ip=192.168.0.161"
```

## Endpoints

| Método | Ruta | Descripción | Parámetros |
|--------|------|-------------|-----------|
| GET | `/` | Información de la API | - |
| POST | `/devices/connect` | Conectar dispositivo | `ip`, `port` (opcional) |
| GET | `/devices` | Listar dispositivos | - |
| POST | `/play` | Reproducir video | `device_ip`, `video_url` |
| POST | `/stop` | Pausar video | `device_ip` |
| POST | `/exit` | Salir de app | `device_ip` |
| GET | `/screenshot` | Descargar screenshot | `device_ip` |
| GET | `/status` | Estado del dispositivo | `device_ip` |
| POST | `/command` | Comando personalizado | `device_ip`, `command` |
| POST | `/devices/disconnect` | Desconectar | `device_ip` |

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

MIT
