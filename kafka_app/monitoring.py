"""
Sistema de monitoreo y métricas para Kafka
Integración con Prometheus
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    REGISTRY
)
from django.core.cache import cache
from kafka import KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType
from kafka.errors import KafkaError
from django.conf import settings

logger = logging.getLogger(__name__)

# ============================================
# MÉTRICAS PROMETHEUS
# ============================================

# Contadores
kafka_messages_total = Counter(
    'kafka_messages_total',
    'Total de mensajes procesados',
    ['topic', 'operation', 'status']
)

kafka_errors_total = Counter(
    'kafka_errors_total',
    'Total de errores en Kafka',
    ['topic', 'error_type']
)

kafka_dlq_messages_total = Counter(
    'kafka_dlq_messages_total',
    'Mensajes enviados a Dead Letter Queue',
    ['original_topic']
)

# Histogramas (para latencias)
kafka_producer_latency = Histogram(
    'kafka_producer_latency_seconds',
    'Latencia de productor Kafka',
    ['topic'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

kafka_consumer_latency = Histogram(
    'kafka_consumer_processing_latency_seconds',
    'Latencia de procesamiento de consumidor',
    ['topic', 'event_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Gauges (para valores actuales)
kafka_consumer_lag = Gauge(
    'kafka_consumer_lag',
    'Lag del consumidor (mensajes pendientes)',
    ['topic', 'partition', 'consumer_group']
)

kafka_topic_partitions = Gauge(
    'kafka_topic_partitions',
    'Número de particiones por topic',
    ['topic']
)

kafka_broker_count = Gauge(
    'kafka_broker_count',
    'Número de brokers activos'
)

# Info
kafka_cluster_info = Info(
    'kafka_cluster',
    'Información del cluster Kafka'
)


# ============================================
# CLASE DE MONITOREO
# ============================================

class KafkaMonitor:
    """
    Monitor para métricas de Kafka
    Recolecta información sobre topics, consumidores, lag, etc.
    """
    
    def __init__(self):
        self.admin_client = None
        self._connect_admin()
    
    def _connect_admin(self):
        """Conecta al AdminClient de Kafka"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='nuam-monitor'
            )
            logger.info("✅ Kafka AdminClient conectado")
        except Exception as e:
            logger.error(f"❌ Error conectando AdminClient: {e}")
    
    def get_cluster_info(self) -> Dict:
        """Obtiene información del cluster"""
        if not self.admin_client:
            return {}
        
        try:
            # Obtener información de brokers
            cluster_metadata = self.admin_client._client.cluster
            
            brokers = []
            for broker in cluster_metadata.brokers():
                brokers.append({
                    'id': broker.nodeId,
                    'host': broker.host,
                    'port': broker.port
                })
            
            # Actualizar métricas
            kafka_broker_count.set(len(brokers))
            
            info = {
                'brokers': brokers,
                'controller_id': cluster_metadata.controller().nodeId if cluster_metadata.controller() else None,
                'cluster_id': str(cluster_metadata.cluster_id())
            }
            
            kafka_cluster_info.info({
                'broker_count': str(len(brokers)),
                'cluster_id': info['cluster_id']
            })
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del cluster: {e}")
            return {}
    
    def get_topics_info(self) -> List[Dict]:
        """Obtiene información de todos los topics"""
        if not self.admin_client:
            return []
        
        try:
            topics = self.admin_client.list_topics()
            topics_info = []
            
            for topic in topics:
                metadata = self.admin_client._client.cluster.partitions_for_topic(topic)
                
                if metadata:
                    partition_count = len(metadata)
                    
                    # Actualizar métrica
                    kafka_topic_partitions.labels(topic=topic).set(partition_count)
                    
                    topics_info.append({
                        'name': topic,
                        'partitions': partition_count
                    })
            
            return topics_info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo topics: {e}")
            return []
    
    def get_consumer_lag(self, group_id: str, topic: str) -> Dict:
        """
        Calcula el lag del consumidor
        (diferencia entre último offset y offset actual del consumidor)
        """
        try:
            from kafka import KafkaConsumer
            
            # Crear consumidor temporal para consultar offsets
            consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id,
                enable_auto_commit=False
            )
            
            # Obtener particiones del topic
            partitions = consumer.partitions_for_topic(topic)
            
            if not partitions:
                return {}
            
            lag_info = {}
            
            for partition in partitions:
                from kafka import TopicPartition
                tp = TopicPartition(topic, partition)
                
                # Último offset disponible
                consumer.assign([tp])
                consumer.seek_to_end(tp)
                last_offset = consumer.position(tp)
                
                # Offset actual del consumidor
                committed = consumer.committed(tp)
                current_offset = committed if committed is not None else 0
                
                # Calcular lag
                lag = last_offset - current_offset
                
                # Actualizar métrica
                kafka_consumer_lag.labels(
                    topic=topic,
                    partition=partition,
                    consumer_group=group_id
                ).set(lag)
                
                lag_info[f'partition_{partition}'] = {
                    'current_offset': current_offset,
                    'last_offset': last_offset,
                    'lag': lag
                }
            
            consumer.close()
            return lag_info
            
        except Exception as e:
            logger.error(f"❌ Error calculando lag: {e}")
            return {}
    
    def get_health_status(self) -> Dict:
        """Obtiene estado de salud del sistema Kafka"""
        try:
            cluster_info = self.get_cluster_info()
            topics_info = self.get_topics_info()
            
            # Calcular lag para topics principales
            lags = {}
            for topic_key in settings.KAFKA_TOPICS.keys():
                topic = settings.KAFKA_TOPICS[topic_key]
                lag = self.get_consumer_lag('nuam-consumer-group', topic)
                if lag:
                    lags[topic] = lag
            
            health = {
                'status': 'healthy' if cluster_info else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'cluster': cluster_info,
                'topics': topics_info,
                'consumer_lags': lags,
                'metrics': {
                    'total_messages_sent': self._get_metric_value('kafka_messages_total'),
                    'total_errors': self._get_metric_value('kafka_errors_total'),
                    'dlq_messages': self._get_metric_value('kafka_dlq_messages_total'),
                }
            }
            
            # Cachear por 30 segundos
            cache.set('kafka_health_status', health, 30)
            
            return health
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo health status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_metric_value(self, metric_name: str) -> float:
        """Obtiene el valor actual de una métrica"""
        try:
            for metric in REGISTRY.collect():
                if metric.name == metric_name:
                    for sample in metric.samples:
                        if sample.name == metric_name + '_total':
                            return sample.value
            return 0.0
        except:
            return 0.0


# ============================================
# DECORADOR PARA MONITOREO AUTOMÁTICO
# ============================================

def monitor_kafka_operation(operation: str):
    """
    Decorador para monitorear operaciones de Kafka automáticamente
    
    Uso:
        @monitor_kafka_operation('send')
        def my_producer_method(self, topic, message):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            topic = kwargs.get('topic', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                
                # Registrar éxito
                kafka_messages_total.labels(
                    topic=topic,
                    operation=operation,
                    status='success'
                ).inc()
                
                # Registrar latencia
                duration = time.time() - start_time
                if operation == 'send':
                    kafka_producer_latency.labels(topic=topic).observe(duration)
                
                return result
                
            except Exception as e:
                # Registrar error
                kafka_messages_total.labels(
                    topic=topic,
                    operation=operation,
                    status='error'
                ).inc()
                
                kafka_errors_total.labels(
                    topic=topic,
                    error_type=type(e).__name__
                ).inc()
                
                raise
        
        return wrapper
    return decorator


# ============================================
# ALERTAS
# ============================================

class KafkaAlertManager:
    """Gestor de alertas para Kafka"""
    
    ALERT_THRESHOLDS = {
        'high_lag': 1000,  # Alerta si lag > 1000 mensajes
        'high_error_rate': 0.05,  # Alerta si error rate > 5%
        'dlq_messages': 10,  # Alerta si hay más de 10 mensajes en DLQ
    }
    
    @staticmethod
    def check_high_lag(monitor: KafkaMonitor) -> List[Dict]:
        """Verifica si hay lag alto en algún consumidor"""
        alerts = []
        
        for topic_key in settings.KAFKA_TOPICS.keys():
            topic = settings.KAFKA_TOPICS[topic_key]
            lag = monitor.get_consumer_lag('nuam-consumer-group', topic)
            
            for partition, info in lag.items():
                if info['lag'] > KafkaAlertManager.ALERT_THRESHOLDS['high_lag']:
                    alerts.append({
                        'severity': 'warning',
                        'type': 'high_lag',
                        'topic': topic,
                        'partition': partition,
                        'lag': info['lag'],
                        'message': f"Alto lag detectado en {topic}:{partition} - {info['lag']} mensajes"
                    })
        
        return alerts
    
    @staticmethod
    def send_alert(alert: Dict):
        """Envía una alerta (email, Slack, PagerDuty, etc.)"""
        logger.warning(f"🚨 ALERTA KAFKA: {alert['message']}")
        
        # TODO: Implementar envío real de alertas
        # - Email
        # - Slack webhook
        # - PagerDuty
        # - etc.


# Instancia global del monitor
kafka_monitor = KafkaMonitor()