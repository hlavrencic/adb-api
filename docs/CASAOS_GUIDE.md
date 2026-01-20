# Docker Compose para CasaOS

Este archivo `docker-compose.yml` está optimizado para funcionar con **CasaOS**, un sistema operativo NAS/hogar moderno basado en Docker.

## Características para CasaOS

✅ **Labels de integración** - Aparece automáticamente en App Store de CasaOS  
✅ **Volúmenes persistentes locales** - Los datos se guardan en la máquina  
✅ **Health checks** - Monitoreo automático de salud del contenedor  
✅ **Límites de recursos** - Configuración de CPU y memoria  
✅ **Iconos y descripciones** - Información legible en UI de CasaOS  

## Instalación en CasaOS

### Opción 1: Desde la interfaz web

1. Abre CasaOS en tu navegador (`http://ip-del-nas:80`)
2. Ve a **App Store** → **Custom App**
3. Copia el contenido de `docker-compose.yml`
4. Pega en el editor de CasaOS
5. Haz clic en **Install**

### Opción 2: Desde la línea de comandos

```bash
ssh user@ip-del-nas
cd /data/docker-compose/adb-api  # O donde guardes tus compose files
docker-compose -f docker-compose.yml up -d
```

## Variables de Entorno

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `TZ` | `America/Argentina/Buenos_Aires` | Zona horaria |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

Puedes modificarlas directamente en CasaOS desde la UI.

## Puertos

| Puerto | Protocolo | Uso |
|--------|-----------|-----|
| `8000` | TCP | API REST y Swagger UI |

Accede a la documentación interactiva en: `http://ip-del-nas:8000/docs`

## Volúmenes

| Volumen | Path | Descripción |
|---------|------|-------------|
| `adb-keys` | `/app/.android` | Claves RSA persistentes |
| `adb-screenshots` | `/tmp/screenshots` | Screenshots guardados |

Los datos se guardan en:
- `/var/lib/docker/volumes/adb_api_adb-keys/_data`
- `/var/lib/docker/volumes/adb_api_adb-screenshots/_data`

## Límites de Recursos

- **CPU**: Máximo 2 cores, mínimo 0.5 cores
- **Memoria**: Máximo 512 MB, mínimo 256 MB

Estos límites pueden ajustarse en CasaOS si necesitas más recursos.

## Health Check

El contenedor incluye un health check que verifica:
- Cada 30 segundos
- Timeout: 10 segundos
- Reintentos: 3 intentos
- Inicio: 10 segundos después de levantar

Puedes ver el estado en: **CasaOS → Containers → adb-control-api → Health**

## Funcionalidades

### API Endpoints

```bash
# Conectar a dispositivo
curl -X POST "http://localhost:8000/devices/connect?ip=192.168.0.213&port=5555"

# Listar dispositivos
curl -X GET "http://localhost:8000/devices"

# Captura de pantalla
curl -X GET "http://localhost:8000/screenshot?device_ip=192.168.0.213" -o screenshot.png

# Reproducir video de YouTube
curl -X POST "http://localhost:8000/play?device_ip=192.168.0.213&video_url=https://youtu.be/dQw4w9WgXcQ"

# Pausar video
curl -X POST "http://localhost:8000/stop?device_ip=192.168.0.213"

# Salir de aplicación
curl -X POST "http://localhost:8000/exit?device_ip=192.168.0.213"

# Ejecutar comando personalizado
curl -X POST "http://localhost:8000/command?device_ip=192.168.0.213&command=pm+list+packages"

# Desconectar
curl -X POST "http://localhost:8000/devices/disconnect?device_ip=192.168.0.213"
```

## Troubleshooting en CasaOS

### El contenedor no inicia

```bash
# Ver logs
docker logs adb-control-api

# Reiniciar contenedor
docker restart adb-control-api

# Reconstruir imagen
docker-compose -f docker-compose.yml up -d --build
```

### Dispositivo no se conecta

1. Verifica que ADB está habilitado en el dispositivo
2. Autoriza la conexión cuando aparezca el diálogo
3. Revisa los logs: `docker logs adb-control-api`
4. Intenta reconectar: `curl -X POST "http://localhost:8000/devices/connect?ip=IP_DISPOSITIVO"`

### Screenshots no se descarga

1. Verifica espacio en `/sdcard` del dispositivo
2. Revisa permisos del contenedor
3. Consulta logs detallados

## Integración con Home Assistant

Si tienes Home Assistant en CasaOS:

```yaml
# configuration.yaml
shell_command:
  play_video: 'curl -X POST "http://adb-api:8000/play?device_ip={{ ip }}&video_url={{ url }}"'
  take_screenshot: 'curl -X GET "http://adb-api:8000/screenshot?device_ip={{ ip }}" -o /config/www/screenshot.png'
```

## Notas de Seguridad

⚠️ **Importante:**
- La API no tiene autenticación. Usa en red local confiable
- Las claves RSA se almacenan sin cifrado
- No expongas el puerto 8000 a Internet

Para producción comercial, contacta a los autores para opciones de seguridad.

## Soporte

- 📖 Documentación: [README.md](../README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/hn8888/docker-adb-api/issues)
- 💬 Contacto: [GitHub Discussions](https://github.com/hn8888/docker-adb-api/discussions)

## Licencia

**Uso No Comercial** - Consulta [LICENSE](../LICENSE) para más detalles.
