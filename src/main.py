from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from adb_shell.adb_device import AdbDeviceTcp
import os
import json
import re
from typing import Optional
from datetime import datetime
import logging
from pathlib import Path
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ADB Control API", version="1.2.0")

# Diccionario para almacenar conexiones
devices = {}

def validate_ip_address(ip: str) -> bool:
    """Validar que el formato de IP sea válido"""
    if not ip or not isinstance(ip, str):
        return False
    # Patrón para IPv4
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    # Permitir también hostnames/dominios
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(hostname_pattern, ip))

def validate_required_params(**params):
    """
    Validar parámetros requeridos
    Lanza HTTPException si algún parámetro es inválido
    """
    for param_name, param_value in params.items():
        if param_value is None or (isinstance(param_value, str) and param_value.strip() == ""):
            raise HTTPException(
                status_code=400, 
                detail=f"El parámetro '{param_name}' es requerido y no puede estar vacío"
            )
    return True

def validate_device_ip(device_ip: str) -> bool:
    """Validar que device_ip sea un parámetro válido"""
    if not device_ip or not isinstance(device_ip, str):
        raise HTTPException(
            status_code=400,
            detail="device_ip es requerido y debe ser una cadena válida"
        )
    
    device_ip = device_ip.strip()
    if not device_ip:
        raise HTTPException(
            status_code=400,
            detail="device_ip no puede estar vacío"
        )
    
    if not validate_ip_address(device_ip):
        raise HTTPException(
            status_code=400,
            detail=f"device_ip '{device_ip}' no es una dirección IP o hostname válido"
        )
    
    return True

def ensure_device_connection(func):
    """
    Decorador que asegura que el dispositivo esté conectado.
    Si no está conectado, intenta conectar automáticamente.
    
    El parámetro device_ip debe estar presente en los argumentos de la función.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        device_ip = kwargs.get('device_ip') or (args[0] if args else None)
        port = kwargs.get('port', 5555)
        
        # Validar device_ip
        validate_device_ip(device_ip)
        
        # Verificar si el dispositivo existe en el diccionario
        if device_ip not in devices:
            logger.info(f"Dispositivo {device_ip} no encontrado en conexiones, conectando automáticamente...")
            # Intentar conectar automáticamente
            result = await connect_device(device_ip, port)
            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=f"No se pudo conectar al dispositivo: {result.get('message')}")
        
        # Si el dispositivo existe pero no está conectado, reconectar
        if not devices[device_ip].connected:
            logger.info(f"Dispositivo {device_ip} desconectado, reconectando...")
            reconnect_result = devices[device_ip].connect()
            if reconnect_result["status"] == "error":
                raise HTTPException(status_code=400, detail=f"No se pudo reconectar al dispositivo: {reconnect_result.get('message')}")
        
        # Llamar a la función original
        return await func(*args, **kwargs)
    
    return wrapper

def generate_adb_keys():
    """Generar claves RSA para ADB si no existen"""
    try:
        # Directorio para almacenar claves
        keys_dir = Path("/app/.android")
        keys_dir.mkdir(parents=True, exist_ok=True)
        
        adbkey_path = keys_dir / "adbkey"
        
        # Si las claves no existen, generarlas
        if not adbkey_path.exists():
            logger.info(f"Generando nuevas claves RSA en {adbkey_path}")
            try:
                from adb_shell.auth.keygen import keygen
                keygen(str(adbkey_path))
                logger.info("Claves RSA generadas exitosamente")
            except Exception as e:
                logger.error(f"Error al generar claves: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return []
        else:
            logger.info(f"Claves ADB encontradas en {adbkey_path}")
        
        # Cargar las claves
        try:
            from adb_shell.auth.sign_pythonrsa import PythonRSASigner
            signer = PythonRSASigner.FromRSAKeyPath(str(adbkey_path))
            logger.info("Claves ADB cargadas exitosamente")
            return [signer]
        except Exception as e:
            logger.error(f"Error al cargar claves: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    except Exception as e:
        logger.error(f"Error al generar/cargar claves ADB: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

class DeviceConnection:
    def __init__(self, ip: str, port: int = 5555):
        self.ip = ip
        self.port = port
        self.device = None
        self.connected = False
        self.rsa_keys = None  # Se cargarán al conectar
    
    def _ensure_keys_loaded(self):
        """Cargar o generar claves si es necesario"""
        if self.rsa_keys is not None:
            logger.info(f"Claves ya cargadas: {len(self.rsa_keys)} clave(s)")
            return  # Ya están cargadas
        
        logger.info("Cargando/generando claves...")
        self.rsa_keys = generate_adb_keys()
        logger.info(f"Claves cargadas: {len(self.rsa_keys)} clave(s) disponibles")
    
    def connect(self) -> dict:
        """Conectar al dispositivo"""
        try:
            # Asegurar que las claves estén cargadas/generadas
            self._ensure_keys_loaded()
            
            logger.info(f"Intentando conectar a {self.ip}:{self.port}")
            # Crear dispositivo
            self.device = AdbDeviceTcp(self.ip, self.port)
            # Conectar
            self.device.connect(rsa_keys=self.rsa_keys)
            self.connected = True
            logger.info(f"Conectado exitosamente a {self.ip}:{self.port}")
            return {"status": "success", "message": f"Conectado a {self.ip}:{self.port}"}
        except Exception as e:
            self.connected = False
            logger.error(f"Error al conectar: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def disconnect(self):
        """Desconectar del dispositivo"""
        try:
            if self.device:
                self.device.close()
            self.connected = False
            logger.info(f"Desconectado de {self.ip}:{self.port}")
            return {"status": "success", "message": "Desconectado"}
        except Exception as e:
            logger.error(f"Error al desconectar: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def execute_command(self, cmd: str) -> dict:
        """Ejecutar comando ADB"""
        if not self.connected:
            logger.info(f"Dispositivo no conectado, intentando reconectar")
            connect_result = self.connect()
            if connect_result["status"] == "error":
                return connect_result
        
        try:
            logger.info(f"Ejecutando comando en {self.ip}: {cmd}")
            result = self.device.shell(cmd)
            logger.info(f"Comando ejecutado exitosamente")
            return {"status": "success", "output": result}
        except Exception as e:
            self.connected = False
            logger.error(f"Error al ejecutar comando: {str(e)}")
            return {"status": "error", "message": str(e)}

# Inicializar claves al arrancar la aplicación
@app.on_event("startup")
async def startup_event():
    """Generar/cargar claves RSA al iniciar la aplicación"""
    logger.info("Inicializando claves RSA...")
    keys = generate_adb_keys()
    if keys:
        logger.info(f"Claves RSA disponibles: {len(keys)} clave(s) cargada(s)")
    else:
        logger.warning("No se pudieron cargar las claves RSA")

# Endpoints

@app.get("/")
async def root():
    """Healthcheck - verifica que la API está corriendo y operacional"""
    try:
        return {
            "name": "ADB Control API",
            "version": "1.2.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "connected_devices": len(devices),
            "uptime_seconds": int((datetime.now() - datetime.now()).total_seconds())
        }
    except Exception as e:
        logger.error(f"Error en healthcheck: {str(e)}")
        return {
            "name": "ADB Control API",
            "version": "1.2.0",
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }, 503

@app.post("/devices/connect")
async def connect_device(ip: str, port: int = 5555):
    """Conectar a un dispositivo Android"""
    try:
        # Validar parámetros
        validate_device_ip(ip)
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise HTTPException(status_code=400, detail="port debe ser un número entre 1 y 65535")
        
        if ip in devices:
            if devices[ip].connected:
                return {"status": "warning", "message": "Dispositivo ya conectado"}
            devices[ip].disconnect()
        
        device = DeviceConnection(ip, port)
        result = device.connect()
        
        if result["status"] == "success":
            devices[ip] = device
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /devices/connect: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/devices")
async def list_devices():
    """Listar dispositivos conectados"""
    device_list = []
    for ip, device in devices.items():
        try:
            if device.connected:
                device_list.append({
                    "ip": ip,
                    "port": device.port,
                    "status": "connected"
                })
            else:
                # Intentar reconectar
                device.connect()
                device_list.append({
                    "ip": ip,
                    "port": device.port,
                    "status": "reconnected" if device.connected else "disconnected"
                })
        except Exception as e:
            logger.error(f"Error al listar dispositivos: {str(e)}")
            device_list.append({
                "ip": ip,
                "port": device.port,
                "status": "error",
                "error": str(e)
            })
    
    return {"devices": device_list, "count": len(device_list)}

@app.post("/play")
@ensure_device_connection
async def play_video(device_ip: str, video_url: str):
    """Reproducir video de YouTube"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip, video_url=video_url)
        
        # Validar URL
        if "youtube.com" not in video_url and "youtu.be" not in video_url:
            raise HTTPException(status_code=400, detail="video_url debe ser una URL válida de YouTube")
        
        device = devices[device_ip]
        cmd = f'am start -a android.intent.action.VIEW -d "{video_url}"'
        result = device.execute_command(cmd)
        
        return {
            "device": device_ip,
            "action": "play",
            "video_url": video_url,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /play: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.post("/stop")
@ensure_device_connection
async def stop_video(device_ip: str):
    """Pausar video (espacio)"""
    try:
        device = devices[device_ip]
        cmd = "input keyevent KEYCODE_SPACE"
        result = device.execute_command(cmd)
        
        return {
            "device": device_ip,
            "action": "pause",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /stop: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.post("/exit")
@ensure_device_connection
async def exit_app(device_ip: str):
    """Salir de la aplicación (Back)"""
    try:
        device = devices[device_ip]
        cmd = "input keyevent KEYCODE_BACK"
        result = device.execute_command(cmd)
        
        return {
            "device": device_ip,
            "action": "exit",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /exit: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.get("/screenshot")
@ensure_device_connection
async def get_screenshot(device_ip: str):
    """Descargar captura de pantalla"""
    try:
        device = devices[device_ip]
        
        # Crear directorio temporal si no existe
        os.makedirs("/tmp/screenshots", exist_ok=True)
        
        # Tomar screenshot
        device.execute_command("screencap -p /sdcard/screenshot.png")
        
        # Descargar archivo
        timestamp = int(datetime.now().timestamp())
        local_path = f"/tmp/screenshots/screenshot_{device_ip}_{timestamp}.png"
        device.device.pull("/sdcard/screenshot.png", local_path)
        
        logger.info(f"Screenshot descargado de {device_ip}")
        
        return FileResponse(
            local_path, 
            media_type="image/png", 
            filename=f"screenshot_{device_ip}.png"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al descargar screenshot: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando ADB: {str(e)}")

@app.get("/status")
@ensure_device_connection
async def get_status(device_ip: str):
    """Obtener estado del dispositivo"""
    try:
        device = devices[device_ip]
        
        # Intentar ejecutar comando simple para verificar conexión
        test_result = device.execute_command("echo 'test'")
        
        if test_result["status"] == "success":
            device.connected = True
        else:
            device.connected = False
        
        return {
            "device": device_ip,
            "port": device.port,
            "status": "connected" if device.connected else "disconnected",
            "connected": device.connected
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /status: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.post("/devices/disconnect")
async def disconnect_device(device_ip: str):
    """Desconectar de un dispositivo"""
    try:
        # Validar parámetros
        validate_device_ip(device_ip)
        
        if device_ip not in devices:
            raise HTTPException(status_code=400, detail=f"Dispositivo '{device_ip}' no encontrado")
        
        result = devices[device_ip].disconnect()
        del devices[device_ip]
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /devices/disconnect: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al desconectar: {str(e)}")

@app.post("/command")
@ensure_device_connection
async def send_custom_command(device_ip: str, command: str):
    """Enviar comando personalizado ADB shell"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip, command=command)
        
        device = devices[device_ip]
        result = device.execute_command(command)
        
        return {
            "device": device_ip,
            "command": command,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /command: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.get("/device/info")
@ensure_device_connection
async def get_device_info(device_ip: str):
    """Obtener información detallada del dispositivo (modelo, versión, RAM, etc.)"""
    try:
        device = devices[device_ip]
        
        # Obtener información del dispositivo
        info = {}
        
        # Modelo del dispositivo
        model_result = device.execute_command("getprop ro.product.model")
        if model_result["status"] == "success":
            info["model"] = model_result["output"].strip()
        
        # Fabricante
        manufacturer_result = device.execute_command("getprop ro.product.manufacturer")
        if manufacturer_result["status"] == "success":
            info["manufacturer"] = manufacturer_result["output"].strip()
        
        # Versión de Android
        android_version_result = device.execute_command("getprop ro.build.version.release")
        if android_version_result["status"] == "success":
            info["android_version"] = android_version_result["output"].strip()
        
        # Nivel de API
        api_level_result = device.execute_command("getprop ro.build.version.sdk")
        if api_level_result["status"] == "success":
            info["api_level"] = api_level_result["output"].strip()
        
        # RAM total
        ram_result = device.execute_command("cat /proc/meminfo | grep MemTotal")
        if ram_result["status"] == "success":
            info["total_ram"] = ram_result["output"].strip()
        
        # Almacenamiento
        storage_result = device.execute_command("df /data")
        if storage_result["status"] == "success":
            info["storage_info"] = storage_result["output"].strip()
        
        # Identificador único del dispositivo
        device_id_result = device.execute_command("getprop ro.serialno")
        if device_id_result["status"] == "success":
            info["serial_number"] = device_id_result["output"].strip()
        
        # Battery level
        battery_result = device.execute_command("dumpsys battery | grep 'level'")
        if battery_result["status"] == "success":
            info["battery_info"] = battery_result["output"].strip()
        
        return {
            "device": device_ip,
            "info": info,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/info: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al ejecutar comando: {str(e)}")

@app.get("/device/current-app")
@ensure_device_connection
async def get_current_app(device_ip: str):
    """Obtener la aplicación actualmente en pantalla"""
    try:
        device = devices[device_ip]
        
        # Obtener la ventana enfocada
        focusedwindow_result = device.execute_command("dumpsys window windows | grep 'mCurrentFocus'")
        
        current_app = None
        package_name = None
        
        if focusedwindow_result["status"] == "success":
            output = focusedwindow_result["output"].strip()
            # Parsear el resultado para extraer el nombre del package
            if output:
                # Ejemplo: mCurrentFocus=Window{123456 u0 com.google.android.youtube/com.google.android.youtube.MainActivity}
                import re
                match = re.search(r'(\S+)/(\S+)\}', output)
                if match:
                    package_name = match.group(1)
                    current_app = match.group(2)
        
        # Obtener información de la aplicación (si existe el package)
        app_info = {}
        if package_name:
            label_result = device.execute_command(f"dumpsys package {package_name} | grep 'versionCode'")
            if label_result["status"] == "success":
                app_info["version_info"] = label_result["output"].strip()
        
        return {
            "device": device_ip,
            "current_app": {
                "package": package_name,
                "activity": current_app,
                "info": app_info
            },
            "raw_output": focusedwindow_result.get("output", ""),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/current-app: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al obtener aplicación actual: {str(e)}")

@app.get("/device/installed-apps")
@ensure_device_connection
async def get_installed_apps(device_ip: str, limit: int = 20):
    """Obtener lista de aplicaciones instaladas en el dispositivo"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip)
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise HTTPException(status_code=400, detail="limit debe ser un número entre 1 y 500")
        
        device = devices[device_ip]
        
        # Obtener lista de paquetes
        packages_result = device.execute_command("pm list packages")
        
        apps = []
        if packages_result["status"] == "success":
            lines = packages_result["output"].strip().split('\n')
            # Limitar a los últimos 'limit' paquetes
            selected_packages = lines[-limit:] if len(lines) > limit else lines
            
            for line in selected_packages:
                if line.startswith("package:"):
                    package_name = line.replace("package:", "").strip()
                    apps.append({
                        "package_name": package_name
                    })
        
        # Obtener lista de aplicaciones del sistema
        system_apps_result = device.execute_command("pm list packages -s")
        system_packages = set()
        if system_apps_result["status"] == "success":
            for line in system_apps_result["output"].strip().split('\n'):
                if line.startswith("package:"):
                    system_packages.add(line.replace("package:", "").strip())
        
        # Marcar cuáles son del sistema
        for app in apps:
            app["is_system_app"] = app["package_name"] in system_packages
        
        return {
            "device": device_ip,
            "total_apps": len(apps),
            "apps": apps,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/installed-apps: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al obtener lista de aplicaciones: {str(e)}")

@app.get("/device/logcat")
@ensure_device_connection
async def get_device_logcat(device_ip: str, lines: int = 50, filter_text: Optional[str] = None):
    """Obtener últimas líneas del logcat del dispositivo"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip)
        if not isinstance(lines, int) or lines < 1 or lines > 1000:
            raise HTTPException(status_code=400, detail="lines debe ser un número entre 1 y 1000")
        
        device = devices[device_ip]
        
        # Obtener logcat
        cmd = f"logcat -t {lines}"
        if filter_text:
            cmd += f" | grep '{filter_text}'"
        
        logcat_result = device.execute_command(cmd)
        
        logs = []
        if logcat_result["status"] == "success":
            lines_list = logcat_result["output"].strip().split('\n')
            for line in lines_list:
                if line.strip():
                    logs.append(line)
        
        return {
            "device": device_ip,
            "filter": filter_text,
            "total_lines": len(logs),
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/logcat: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al obtener información del dispositivo: {str(e)}")

@app.get("/device/volume/current")
@ensure_device_connection
async def get_current_volume(device_ip: str):
    """Obtener el nivel de volumen actual del dispositivo"""
    try:
        device = devices[device_ip]
        
        # Obtener información de volumen actual
        volume_result = device.execute_command("dumpsys audio_service | grep -i 'speaker.*volume'")
        
        volume_info = {}
        if volume_result["status"] == "success":
            volume_info["raw_output"] = volume_result["output"].strip()
        
        return {
            "device": device_ip,
            "volume_info": volume_info,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/volume/current: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al obtener volumen: {str(e)}")

@app.post("/device/volume/increase")
@ensure_device_connection
async def increase_volume(device_ip: str, steps: int = 1):
    """Aumentar el volumen del dispositivo"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip)
        if not isinstance(steps, int) or steps < 1 or steps > 15:
            raise HTTPException(status_code=400, detail="steps debe ser un número entero entre 1 y 15")
        
        device = devices[device_ip]
        
        # Aumentar volumen usando VOLUME_UP keyevent
        results = []
        for _ in range(steps):
            cmd = "input keyevent KEYCODE_VOLUME_UP"
            result = device.execute_command(cmd)
            results.append(result)
        
        return {
            "device": device_ip,
            "action": "increase_volume",
            "steps": steps,
            "status": "success" if all(r["status"] == "success" for r in results) else "partial",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/volume/increase: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al aumentar volumen: {str(e)}")

@app.post("/device/volume/decrease")
@ensure_device_connection
async def decrease_volume(device_ip: str, steps: int = 1):
    """Disminuir el volumen del dispositivo"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip)
        if not isinstance(steps, int) or steps < 1 or steps > 15:
            raise HTTPException(status_code=400, detail="steps debe ser un número entero entre 1 y 15")
        
        device = devices[device_ip]
        
        # Disminuir volumen usando VOLUME_DOWN keyevent
        results = []
        for _ in range(steps):
            cmd = "input keyevent KEYCODE_VOLUME_DOWN"
            result = device.execute_command(cmd)
            results.append(result)
        
        return {
            "device": device_ip,
            "action": "decrease_volume",
            "steps": steps,
            "status": "success" if all(r["status"] == "success" for r in results) else "partial",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/volume/decrease: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al disminuir volumen: {str(e)}")

@app.post("/device/volume/mute")
@ensure_device_connection
async def mute_device(device_ip: str):
    """Silenciar el dispositivo"""
    try:
        device = devices[device_ip]
        
        # Silenciar usando MUTE keyevent
        cmd = "input keyevent KEYCODE_MUTE"
        result = device.execute_command(cmd)
        
        return {
            "device": device_ip,
            "action": "mute",
            "status": result["status"],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/volume/mute: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al silenciar dispositivo: {str(e)}")

@app.post("/device/volume/set")
@ensure_device_connection
async def set_volume(device_ip: str, level: int):
    """Establecer el volumen a un nivel específico (0-15)"""
    try:
        # Validar parámetros
        validate_required_params(device_ip=device_ip)
        if not isinstance(level, int) or level < 0 or level > 15:
            raise HTTPException(status_code=400, detail="level debe ser un número entero entre 0 y 15")
        
        device = devices[device_ip]
        
        # Primero obtener el volumen actual (0 pasos = mute, 15 pasos = máximo)
        # Usar cmds para establecer volumen directamente si es posible
        # Alternativamente, usar múltiples pulsaciones de volume up/down
        
        # Approach: Bajar volumen al mínimo primero, luego subir al nivel deseado
        cmd = "input keyevent KEYCODE_VOLUME_MUTE"
        device.execute_command(cmd)
        
        # Ahora subir al nivel deseado
        results = []
        for _ in range(level):
            cmd = "input keyevent KEYCODE_VOLUME_UP"
            result = device.execute_command(cmd)
            results.append(result)
        
        return {
            "device": device_ip,
            "action": "set_volume",
            "level": level,
            "status": "success" if all(r["status"] == "success" for r in results) else "partial",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /device/volume/set: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error al establecer volumen: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 9123))
    uvicorn.run(app, host="0.0.0.0", port=port)
