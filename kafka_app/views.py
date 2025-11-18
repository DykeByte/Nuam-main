from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient
import json


# -------------------------------
# Producer: envío de mensajes
# -------------------------------

@login_required
def send_kafka_message(request):
    """
    Envía un mensaje al tópico 'nuam-topic' usando KafkaProducer.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            message = data.get("message", "")

            producer = KafkaProducer(
                bootstrap_servers="localhost:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

            producer.send("nuam-topic", {"message": message})
            producer.flush()

            return JsonResponse({"status": "success", "message": "Mensaje enviado"})
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


# -------------------------------
# Dashboard con métricas Kafka
# -------------------------------

@login_required
def kafka_dashboard_view(request):
    """
    Renderiza el dashboard Kafka con métricas básicas del cluster.
    """
    try:
        admin = KafkaAdminClient(
            bootstrap_servers="localhost:9092",
            client_id="nuam-dashboard"
        )

        topics = admin.list_topics()
        cluster_info = admin.describe_cluster()

        brokers_count = len(cluster_info.get("brokers", []))
        cluster_health = "healthy" if brokers_count > 0 else "unhealthy"

        topics_info = [
            {"name": t, "partitions": "?", "lag": "?"} for t in topics
        ]

    except Exception:
        # Kafka caído → Dashboard no se rompe
        brokers_count = 0
        cluster_health = "unhealthy"
        topics_info = []
        topics = []

    context = {
        "cluster_health": cluster_health,
        "brokers_count": brokers_count,
        "topics_count": len(topics),
        "messages_sent": 0,  # Placeholder opcional

        # Tabla
        "topics_info": topics_info,

        # Cards de métricas
        "total_messages": 0,
        "total_errors": 0,
        "dlq_messages": 0,
    }

    return render(request, "kafka/dashboard.html", context)


# -------------------------------
# API healthcheck (por si lo necesitas)
# -------------------------------

def kafka_health_check(request):
    """
    Endpoint simple para revisar si Kafka está disponible.
    """
    try:
        admin = KafkaAdminClient(
            bootstrap_servers="localhost:9092",
            client_id="nuam-health"
        )
        admin.list_topics()
        return JsonResponse({"status": "healthy"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
