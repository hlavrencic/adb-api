"""
Script de prueba para la ADB Control API
Prueba todos los endpoints de la API
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
TEST_DEVICE_IP = "192.168.0.161"  # Cambiar por IP real del dispositivo
TEST_PORT = 5555
YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log de mensajes"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     params: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """Prueba un endpoint y retorna el resultado"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"Probando: {name}", "TEST")
            self.log(f"  Método: {method} {url}", "DEBUG")
            
            if params:
                self.log(f"  Parámetros: {params}", "DEBUG")
            if json_data:
                self.log(f"  Datos: {json_data}", "DEBUG")
            
            if method == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method == "POST":
                response = self.session.post(url, params=params, json=json_data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response": response.text[:500]  # Primeros 500 caracteres
            }
            
            if result["success"]:
                self.log(f"  ✓ PASÓ (Status: {response.status_code})", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"  ✗ FALLÓ (Status: {response.status_code})", "ERROR")
                self.failed += 1
            
            self.results.append(result)
            return result
            
        except requests.exceptions.ConnectionError:
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": 0,
                "success": False,
                "response": "Error de conexión - ¿La API está corriendo?"
            }
            self.log(f"  ✗ ERROR: No se pudo conectar a {self.base_url}", "ERROR")
            self.failed += 1
            self.results.append(result)
            return result
        
        except Exception as e:
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": 0,
                "success": False,
                "response": str(e)
            }
            self.log(f"  ✗ ERROR: {str(e)}", "ERROR")
            self.failed += 1
            self.results.append(result)
            return result
    
    def run_basic_tests(self):
        """Ejecuta pruebas básicas sin dispositivo"""
        self.log("=" * 60)
        self.log("INICIANDO PRUEBAS BÁSICAS DE API", "INFO")
        self.log("=" * 60)
        
        # Test 1: Raíz
        self.test_endpoint(
            "Obtener información de la API (GET /)",
            "GET",
            "/"
        )
        
        # Test 2: Listar dispositivos (debería estar vacío inicialmente)
        self.test_endpoint(
            "Listar dispositivos (GET /devices)",
            "GET",
            "/devices"
        )
        
        # Test 3: Obtener estado sin dispositivo
        self.test_endpoint(
            "Obtener estado sin dispositivo (GET /status)",
            "GET",
            "/status",
            params={"device_ip": TEST_DEVICE_IP}
        )
    
    def run_device_tests(self):
        """Ejecuta pruebas que requieren dispositivo conectado"""
        self.log("")
        self.log("=" * 60)
        self.log("INICIANDO PRUEBAS CON DISPOSITIVO", "INFO")
        self.log("=" * 60)
        self.log(f"Dispositivo de prueba: {TEST_DEVICE_IP}:{TEST_PORT}")
        
        # Test 1: Conectar dispositivo
        self.test_endpoint(
            "Conectar dispositivo (POST /devices/connect)",
            "POST",
            "/devices/connect",
            params={"ip": TEST_DEVICE_IP, "port": TEST_PORT}
        )
        
        # Esperar un poco
        time.sleep(2)
        
        # Test 2: Listar dispositivos conectados
        self.test_endpoint(
            "Listar dispositivos conectados (GET /devices)",
            "GET",
            "/devices"
        )
        
        # Test 3: Obtener estado del dispositivo
        self.test_endpoint(
            "Obtener estado del dispositivo (GET /status)",
            "GET",
            "/status",
            params={"device_ip": TEST_DEVICE_IP}
        )
        
        # Test 4: Enviar comando personalizado
        self.test_endpoint(
            "Enviar comando personalizado (POST /command)",
            "POST",
            "/command",
            params={"device_ip": TEST_DEVICE_IP, "command": "getprop ro.product.model"}
        )
        
        # Test 5: Reproducir video
        self.test_endpoint(
            "Reproducir video de YouTube (POST /play)",
            "POST",
            "/play",
            params={"device_ip": TEST_DEVICE_IP, "video_url": YOUTUBE_URL}
        )
        
        # Esperar un poco
        time.sleep(3)
        
        # Test 6: Pausar video
        self.test_endpoint(
            "Pausar video (POST /stop)",
            "POST",
            "/stop",
            params={"device_ip": TEST_DEVICE_IP}
        )
        
        # Test 7: Descargar captura de pantalla
        self.test_endpoint(
            "Descargar captura de pantalla (GET /screenshot)",
            "GET",
            "/screenshot",
            params={"device_ip": TEST_DEVICE_IP}
        )
        
        # Test 8: Salir de la aplicación
        self.test_endpoint(
            "Salir de la aplicación (POST /exit)",
            "POST",
            "/exit",
            params={"device_ip": TEST_DEVICE_IP}
        )
        
        # Test 9: Desconectar dispositivo
        self.test_endpoint(
            "Desconectar dispositivo (POST /devices/disconnect)",
            "POST",
            "/devices/disconnect",
            params={"device_ip": TEST_DEVICE_IP}
        )
        
        # Test 10: Verificar que se desconectó
        self.test_endpoint(
            "Listar dispositivos después de desconectar (GET /devices)",
            "GET",
            "/devices"
        )
    
    def run_error_tests(self):
        """Ejecuta pruebas de manejo de errores"""
        self.log("")
        self.log("=" * 60)
        self.log("INICIANDO PRUEBAS DE MANEJO DE ERRORES", "INFO")
        self.log("=" * 60)
        
        # Test 1: URL de YouTube inválida
        self.test_endpoint(
            "Reproducir URL no YouTube (debería fallar)",
            "POST",
            "/play",
            params={"device_ip": TEST_DEVICE_IP, "video_url": "https://www.google.com"}
        )
        
        # Test 2: Desconectar dispositivo inexistente
        self.test_endpoint(
            "Desconectar dispositivo inexistente (debería fallar)",
            "POST",
            "/devices/disconnect",
            params={"device_ip": "192.168.1.999"}
        )
        
        # Test 3: Enviar comando en dispositivo desconectado
        self.test_endpoint(
            "Enviar comando sin dispositivo (debería fallar)",
            "POST",
            "/command",
            params={"device_ip": "192.168.1.999", "command": "echo test"}
        )
    
    def print_summary(self):
        """Imprime resumen de pruebas"""
        self.log("")
        self.log("=" * 60)
        self.log("RESUMEN DE PRUEBAS", "INFO")
        self.log("=" * 60)
        self.log(f"Total de pruebas: {self.passed + self.failed}")
        self.log(f"✓ Pasaron: {self.passed}")
        self.log(f"✗ Fallaron: {self.failed}")
        
        if self.failed == 0:
            self.log("¡Todas las pruebas pasaron!", "SUCCESS")
        else:
            self.log(f"Se encontraron {self.failed} fallos", "ERROR")
        
        self.log("")
        self.log("Detalles de pruebas:")
        for result in self.results:
            status = "✓" if result["success"] else "✗"
            self.log(f"  {status} {result['name']}")
            if not result["success"]:
                self.log(f"     Status: {result['status_code']}", "DEBUG")
                self.log(f"     Response: {result['response'][:100]}", "DEBUG")

def main():
    """Función principal"""
    print("")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  ADB CONTROL API - SUITE DE PRUEBAS".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("")
    
    tester = APITester(BASE_URL)
    
    # Ejecutar pruebas básicas
    tester.run_basic_tests()
    
    # Preguntar si continuar con pruebas de dispositivo
    print("")
    print("Las pruebas básicas completadas.")
    print(f"Nota: Las pruebas con dispositivo requieren un Android conectado en {TEST_DEVICE_IP}")
    print("")
    response = input("¿Ejecutar pruebas con dispositivo? (s/n): ").lower().strip()
    
    if response in ['s', 'si', 'yes']:
        tester.run_device_tests()
    
    # Ejecutar pruebas de errores
    print("")
    response = input("¿Ejecutar pruebas de manejo de errores? (s/n): ").lower().strip()
    
    if response in ['s', 'si', 'yes']:
        tester.run_error_tests()
    
    # Imprimir resumen
    tester.print_summary()
    
    print("")
    print("=" * 60)
    sys.exit(0 if tester.failed == 0 else 1)

if __name__ == "__main__":
    main()
