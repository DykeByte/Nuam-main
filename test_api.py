# test_api.py
import requests
import json
from getpass import getpass
import urllib3
import os

# Ignorar warnings de certificado autofirmado (solo desarrollo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Detecta si estamos en DEBUG (desarrollo) para usar HTTPS
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1"]
SCHEME = "https" if DEBUG else "http"
BASE_URL = f"{SCHEME}://127.0.0.1:8000/api/v1"

def obtener_token(username, password):
    """Obtiene un token JWT"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token/",
            json={"username": username, "password": password},
            verify=False  # Ignora certificado autofirmado
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token obtenido exitosamente")
            print(f"   Access Token: {data['access'][:50]}...")
            print(f"   Refresh Token: {data['refresh'][:50]}...")
            return data['access'], data['refresh']
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None, None

def test_endpoint(url, headers, method='GET', data=None):
    """Prueba un endpoint"""
    print(f"\n{'='*60}")
    print(f"🔍 Probando: {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, verify=False)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, verify=False)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ ÉXITO")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ ERROR")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Excepción de conexión: {e}")
        return None

def main():
    print("🚀 NUAM API - Script de Pruebas")
    print("="*60)
    
    # Credenciales
    username = input("Usuario: ") or "CatalinaM"
    password = getpass("Contraseña: ")
    
    # Obtener token
    access_token, refresh_token = obtener_token(username, password)
    
    if not access_token:
        print("❌ No se pudo obtener el token. Verifica tus credenciales.")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Health Check
    test_endpoint(f"{BASE_URL}/health/", headers)
    
    # Mi perfil
    test_endpoint(f"{BASE_URL}/auth/me/", headers)
    
    # Dashboard stats
    test_endpoint(f"{BASE_URL}/dashboard/stats/", headers)
    
    # Lista de calificaciones
    result = test_endpoint(f"{BASE_URL}/calificaciones/", headers)
    if result:
        print(f"\n📊 Total de calificaciones: {result.get('count', 0)}")
    
    # Lista de cargas
    result = test_endpoint(f"{BASE_URL}/cargas/", headers)
    if result:
        print(f"\n📦 Total de cargas: {result.get('count', 0)}")
    
    # Estadísticas de cargas
    test_endpoint(f"{BASE_URL}/cargas/estadisticas/", headers)
    
    # Logs de operaciones
    result = test_endpoint(f"{BASE_URL}/logs-operacion/", headers)
    if result:
        print(f"\n📝 Total de logs: {result.get('count', 0)}")
    
    print(f"\n{'='*60}")
    print("✅ Pruebas completadas")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
