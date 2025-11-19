# test_kafka.py
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import time

print("🔍 Probando Kafka...")

# Crear topics
admin = KafkaAdminClient(bootstrap_servers=['localhost:9092'])

topics = [
    NewTopic('nuam-cargas', num_partitions=3, replication_factor=1),
    NewTopic('nuam-calificaciones', num_partitions=3, replication_factor=1),
]

try:
    admin.create_topics(topics)
    print("✅ Topics creados")
except Exception as e:
    print(f"⚠️ Topics ya existen: {e}")

time.sleep(2)

# Producir mensaje
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

mensaje = {
    'tipo': 'TEST',
    'mensaje': 'Hola desde Python',
    'timestamp': time.time()
}

future = producer.send('nuam-cargas', value=mensaje)
record = future.get(timeout=10)

print(f"✅ Mensaje enviado a partition {record.partition}, offset {record.offset}")

producer.close()

# Consumir mensaje
consumer = KafkaConsumer(
    'nuam-cargas',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
)

print("\n📨 Mensajes:")
for msg in consumer:
    print(f"  {msg.value}")

consumer.close()
print("\n✅ Kafka funcionando perfectamente!")