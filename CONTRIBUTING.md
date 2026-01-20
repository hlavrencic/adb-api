# Guía de Contribución

## Desarrollo Local

### Requisitos
- Python 3.11+
- Docker & Docker Compose
- Git

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/hn8888/docker-adb-api.git
cd docker-adb-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r config/requirements.txt
```

### Ejecutar localmente

**Con Docker Compose:**
```bash
docker compose -f config/docker-compose.yml up
```

**Sin Docker (desarrollo):**
```bash
cd src
python main.py
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Estructura del Proyecto

```
docker-adb-api/
├── config/
│   ├── Dockerfile           # Configuración del contenedor
│   ├── docker-compose.yml   # Orquestación de contenedores
│   └── requirements.txt      # Dependencias Python
├── src/
│   └── main.py              # Aplicación FastAPI principal
├── tests/
│   └── test_api.py          # Suite de pruebas
├── docs/                    # Documentación
├── collections/             # Colecciones de Postman
└── scripts/                 # Scripts de utilidad
```

### Endpoints Principales

- `POST /devices/connect` - Conectar a dispositivo ADB
- `GET /devices` - Listar dispositivos conectados
- `GET /screenshot` - Obtener captura de pantalla
- `POST /play` - Reproducir video de YouTube
- `POST /stop` - Pausar reproducción
- `POST /exit` - Cerrar aplicación
- `POST /command` - Ejecutar comando ADB personalizado
- `POST /devices/disconnect` - Desconectar dispositivo

### Pruebas

```bash
python tests/test_api.py
```

O con pytest:
```bash
pytest tests/
```

### Commits

Seguimos convenciones estándar:
- `feat:` Nuevas características
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `refactor:` Cambios de estructura sin funcionalidad nueva
- `test:` Cambios en tests
- `ci:` Cambios en CI/CD

### Publicación

Los cambios en `main` se publican automáticamente a Docker Hub mediante GitHub Actions.

### Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.
