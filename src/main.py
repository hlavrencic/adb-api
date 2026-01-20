from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from adb_shell.adb_device import AdbDeviceTcp
import os
import json
from typing import Optional
from datetime import datetime
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ADB Control API", version="1.0.0")

# Diccionario para almacenar conexiones
devices = {}

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
            # Conectar con timeout de 60 segundos
            self.device.connect(rsa_keys=self.rsa_keys, timeout=60.0)
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
    """Raíz - información de la API"""
    return {
        "name": "ADB Control API",
        "version": "1.0.0",
        "description": "API para controlar dispositivos Android mediante ADB",
        "endpoints": {
            "POST /devices/connect": "Conectar a un dispositivo",
            "GET /devices": "Listar dispositivos conectados",
            "POST /play": "Reproducir video de YouTube",
            "POST /stop": "Pausar video",
            "POST /exit": "Salir de la aplicación",
            "GET /screenshot": "Descargar captura de pantalla",
            "GET /status": "Obtener estado del dispositivo",
            "POST /devices/disconnect": "Desconectar dispositivo",
            "GET /docs": "Documentación Swagger"
        }
    }

@app.post("/devices/connect")
async def connect_device(ip: str, port: int = 5555):
    """Conectar a un dispositivo Android"""
    try:
        if ip in devices:
            if devices[ip].connected:
                return {"status": "warning", "message": "Dispositivo ya conectado"}
            devices[ip].disconnect()
        
        device = DeviceConnection(ip, port)
        result = device.connect()
        
        if result["status"] == "success":
            devices[ip] = device
        
        return result
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
async def play_video(device_ip: str, video_url: str):
    """Reproducir video de YouTube"""
    try:
        # Validar URL
        if "youtube.com" not in video_url and "youtu.be" not in video_url:
            raise HTTPException(status_code=400, detail="URL debe ser de YouTube")
        
        if device_ip not in devices or not devices[device_ip].connected:
            connect_result = await connect_device(device_ip)
            if connect_result["status"] == "error":
                raise HTTPException(status_code=400, detail=connect_result)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
async def stop_video(device_ip: str):
    """Pausar video (espacio)"""
    try:
        if device_ip not in devices or not devices[device_ip].connected:
            raise HTTPException(status_code=400, detail="Dispositivo no conectado")
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/exit")
async def exit_app(device_ip: str):
    """Salir de la aplicación (Back)"""
    try:
        if device_ip not in devices or not devices[device_ip].connected:
            raise HTTPException(status_code=400, detail="Dispositivo no conectado")
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/screenshot")
async def get_screenshot(device_ip: str):
    """Descargar captura de pantalla"""
    try:
        if device_ip not in devices or not devices[device_ip].connected:
            raise HTTPException(status_code=400, detail="Dispositivo no conectado")
        
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
        raise HTTPException(status_code=500, detail=f"Error al descargar screenshot: {str(e)}")

@app.get("/status")
async def get_status(device_ip: str):
    """Obtener estado del dispositivo"""
    try:
        if device_ip not in devices:
            return {
                "device": device_ip,
                "status": "not_connected",
                "connected": False
            }
        
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
    except Exception as e:
        logger.error(f"Error en /status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/disconnect")
async def disconnect_device(device_ip: str):
    """Desconectar de un dispositivo"""
    try:
        if device_ip not in devices:
            raise HTTPException(status_code=400, detail="Dispositivo no encontrado")
        
        result = devices[device_ip].disconnect()
        del devices[device_ip]
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /devices/disconnect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def send_custom_command(device_ip: str, command: str):
    """Enviar comando personalizado ADB shell"""
    try:
        if device_ip not in devices or not devices[device_ip].connected:
            raise HTTPException(status_code=400, detail="Dispositivo no conectado")
        
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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 9123))
    uvicorn.run(app, host="0.0.0.0", port=port)
