# Integración con Home Assistant

Esta guía muestra cómo integrar la **ADB Control API** con **Home Assistant** para automatizar dispositivos Android.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación Rápida](#instalación-rápida)
- [Configuración Detallada](#configuración-detallada)
- [Ejemplos de Automatizaciones](#ejemplos-de-automatizaciones)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos Previos

1. **Home Assistant** instalado y corriendo
2. **ADB Control API** corriendo en la misma red (en Docker o localmente)
3. **curl** disponible en el sistema (para shell_command)
4. Un **dispositivo Android** con depuración ADB habilitada

### Verificar que curl está disponible

En Home Assistant, desde Developer Tools > Template, ejecuta:

```
{{ range(1, 2) | list }}
```

Si ves `[1]`, template está OK. Luego prueba shell_command con:

```yaml
shell_command:
  test_curl: "curl --version"
```

## 🚀 Instalación Rápida

### 1. Copiar el archivo de configuración

```bash
# Copia el archivo de ejemplo a tu instalación de Home Assistant
cp config/home-assistant.example.yaml /path/to/home-assistant/config/adb_integration.yaml
```

### 2. Incluir en configuration.yaml

Abre tu `configuration.yaml` y agrega al final:

```yaml
# Incluir configuración de ADB Control API
shell_command: !include adb_integration.yaml
```

O incluso más simple, si solo quieres shell_commands:

```yaml
shell_command:
  adb_device_info: 'curl -s "http://localhost:8000/device/info?device_ip=192.168.0.161"'
  adb_volume_up: 'curl -s -X POST "http://localhost:8000/device/volume/increase?device_ip=192.168.0.161&steps=1"'
  adb_volume_down: 'curl -s -X POST "http://localhost:8000/device/volume/decrease?device_ip=192.168.0.161&steps=1"'
  adb_play_video: 'curl -s -X POST "http://localhost:8000/play?device_ip=192.168.0.161&video_url={{ video_url }}"'
```

### 3. Reiniciar Home Assistant

```bash
# En la UI: Developer Tools > YAML > Restart Home Assistant
# O desde terminal:
sudo systemctl restart home-assistant@homeassistant
```

## 📝 Configuración Detallada

### Shell Commands Parametrizados

**⚠️ IMPORTANTE**: Home Assistant tiene limitaciones con caracteres especiales (`&`, `?`, etc) en shell_commands cuando usas templates. Por eso el archivo de ejemplo usa **comandos específicos** en lugar de genéricos.

#### ❌ Esto NO funciona bien (evitar):

```yaml
shell_command:
  adb_api_post: 'curl -s -X POST "http://localhost:8000{{ endpoint }}" | jq .'
```

Problemas:
- `&` en query parameters puede romper el comando
- `jq` podría no estar instalado
- Dificultad para pasar datos en el body

#### ✅ Esto SÍ funciona (recomendado):

```yaml
shell_command:
  adb_volume_up: 'curl -s -X POST "http://localhost:8000/device/volume/increase?device_ip={{ device_ip }}&steps={{ steps | default(1) }}"'
  adb_volume_down: 'curl -s -X POST "http://localhost:8000/device/volume/decrease?device_ip={{ device_ip }}&steps={{ steps | default(1) }}"'
```

Ventajas:
- Los parámetros son específicos y bien definidos
- Funciona directamente sin dependencias externas (no necesita jq)
- Fácil de debuguear

### Input Helpers para Parametrización

Los input helpers permiten que los usuarios controlen parámetros sin editar YAML:

```yaml
input_text:
  adb_device_ip:
    name: "IP del Dispositivo ADB"
    initial: "192.168.0.161"

input_number:
  adb_volume_level:
    name: "Nivel de Volumen"
    min: 0
    max: 15
    step: 1
```

En una automatización, accede con:

```yaml
device_ip: "{{ states('input_text.adb_device_ip') }}"
```

## 🔄 Ejemplos de Automatizaciones

### 1. Reproducir Video Cuando Alguien Llega

```yaml
automation:
  - alias: "Reproducir Video al Llegar"
    trigger:
      platform: state
      entity_id: person.usuario
      to: home
    action:
      service: shell_command.adb_play_video
      data:
        device_ip: "192.168.0.161"
        video_url: "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Silenciar a Cierta Hora

```yaml
automation:
  - alias: "Silenciar a las 22:00"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: shell_command.adb_volume_mute
      data:
        device_ip: "192.168.0.161"
```

### 3. Aumentar Volumen Condicionalmente

```yaml
automation:
  - alias: "Aumentar Volumen si está Activo"
    trigger:
      platform: state
      entity_id: light.living_room
      to: "on"
    action:
      - service: shell_command.adb_volume_up
        data:
          device_ip: "192.168.0.161"
          steps: 3
```

### 4. Ejecutar Script Complejo

```yaml
script:
  reproducir_video_completo:
    description: "Reproduce video con confirmación"
    fields:
      device_ip:
        description: "IP del dispositivo"
      video_url:
        description: "URL de YouTube"
    sequence:
      - service: shell_command.adb_play_video
        data:
          device_ip: "{{ device_ip }}"
          video_url: "{{ video_url }}"
      - delay: 2
      - service: notify.notify
        data:
          message: "Video iniciado en {{ device_ip }}"
```

## 🧪 Pruebas desde Home Assistant

### Usando Developer Tools

1. Ve a **Developer Tools** > **Services**
2. Selecciona el servicio: `shell_command.adb_volume_up`
3. En "Service Data" ingresa:
   ```json
   {
     "device_ip": "192.168.0.161",
     "steps": 2
   }
   ```
4. Haz clic en "CALL SERVICE"

### Usando REST Sensor para Monitoreo

```yaml
rest:
  - resource: http://localhost:8000/
    name: adb_health
    scan_interval: 30
    json_attributes:
      - status
      - connected_devices
    value_template: "{{ value_json.status }}"
```

Esto te permite monitorear la salud de la API desde Home Assistant.

## 🔐 Seguridad

### Usar !secret para IPs Sensibles

En `configuration.yaml`:

```yaml
shell_command:
  adb_volume_up: !secret adb_volume_up_command
```

En `secrets.yaml`:

```yaml
adb_volume_up_command: "curl -s -X POST 'http://192.168.0.161:8000/device/volume/increase?device_ip=192.168.0.161&steps=1'"
```

### Restringir Acceso

Si la API está en Internet, usa:

1. **Autenticación**: Proxy con básica auth
2. **Firewall**: Limita IP de origen a Home Assistant solo
3. **HTTPS**: Con certificado autofirmado mínimo

## 🐛 Solución de Problemas

### Problema: "shell_command not found"

**Causa**: El comando no está bien escrito o curl no está disponible

**Solución**:
```bash
# Verifica que curl está instalado
docker exec -it home-assistant curl --version

# O instálalo
docker exec -it home-assistant apt-get update && apt-get install -y curl
```

### Problema: "curl: command not found"

**Causa**: curl no está en el contenedor de Home Assistant

**Solución**: Agrega a tu `Dockerfile`:

```dockerfile
FROM homeassistant/home-assistant:latest
RUN apt-get update && apt-get install -y curl
```

### Problema: "Connection refused"

**Causa**: La API no es accesible desde Home Assistant

**Solución**:
1. Verifica que la API está corriendo: `docker ps | grep adb`
2. Verifica que están en la misma red: `docker network ls`
3. Usa IP correcta (no localhost si es otro contenedor)

Desde Home Assistant, prueba:
```bash
docker exec -it home-assistant curl http://adb-control-api:8000/
```

### Problema: "Template variable not found"

**Causa**: Variable no pasada correctamente en service call

**Solución**: Verifica que pasas los datos en formato correcto:

```yaml
# ❌ Incorrecto
service: shell_command.adb_volume_up
data: device_ip="192.168.0.161"

# ✅ Correcto
service: shell_command.adb_volume_up
data:
  device_ip: "192.168.0.161"
```

## 📚 Referencias

- [Home Assistant Shell Command](https://www.home-assistant.io/integrations/shell_command/)
- [Home Assistant Scripts](https://www.home-assistant.io/docs/scripts/)
- [Home Assistant Automations](https://www.home-assistant.io/docs/automation/)
- [ADB Control API Documentation](../docs/TESTING_GUIDE.md)

## ✅ Checklist de Configuración

- [ ] ADB Control API está corriendo
- [ ] curl está disponible en Home Assistant
- [ ] Configuración YAML está incluida en configuration.yaml
- [ ] Home Assistant reiniciado
- [ ] Shell command funciona desde Developer Tools
- [ ] Automatización creada y activa
- [ ] Logs sin errores

## 📞 Soporte

Para más información sobre los endpoints disponibles, consulta:
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)
- [README.md](../README.md)
