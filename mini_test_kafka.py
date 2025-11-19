# mini_test_kafka.py
import time
import json
import requests
from kafka import KafkaProducer
from datetime import datetime

# Configuración
KAFKA_SERVER = 'localhost:9092'
TOPIC = 'nuam-cargas'
BASE_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "CatalinaM"
PASSWORD = "Nuam123!"  # puedes reemplazar con getpass si quieres

def obtener_token(username, password):
    """Obtiene token JWT"""
    response = requests.post(f"{BASE_URL}/auth/token/", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        return data['access']
    else:
        print("❌ Error obteniendo token:", response.json())
        return None

def enviar_mensaje_kafka(mensaje):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(TOPIC, mensaje)
    producer.flush()
    print("✅ Mensaje enviado a Kafka:", mensaje)

def verificar_cargas(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/cargas/", headers=headers)
    if response.status_code == 200:
        cargas = response.json().get('results', [])
        print(f"\n📦 Total cargas registradas: {len(cargas)}")
        for c in cargas[-5:]:  # mostrar las últimas 5
            print(f"  - ID: {c['id']}, Archivo: {c['archivo_nombre']}, Usuario: {c['iniciado_por_nombre']}")
    else:
        print("❌ Error consultando cargas:", response.json())

def main():
    # 1️⃣ Obtener token
    token = obtener_token(USERNAME, PASSWORD)
    if not token:
        return

    # 2️⃣ Enviar mensaje de prueba a Kafka
    mensaje_prueba = {
        "tipo_evento": "CARGA_INICIADA",
        "carga_id": 9999,
        "usuario": USERNAME,
        "tipo_carga": "TEST",
        "mercado": "LOCAL",
        "archivo": "archivo_prueba.xlsx",
        "timestamp": datetime.utcnow().isoformat()
    }
    enviar_mensaje_kafka(mensaje_prueba)

    # 3️⃣ Esperar a que los consumidores procesen (5 segundos)
    print("⏳ Esperando 5 segundos a que los consumidores procesen...")
    time.sleep(5)

    # 4️⃣ Verificar que la carga se registró en la DB
    verificar_cargas(token)

if __name__ == "__main__":
    main()
