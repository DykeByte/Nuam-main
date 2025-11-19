"""
Productores Kafka para el sistema NUAM
Implementa patrones avanzados: retry, circuit breaker, dead letter queue
"""
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
from django.conf import settings
from prometheus_client import Counter, Histogram

logger = logging.getLogger('kafka_app.producers')

# ============================================
# MÉTRICAS PROMETHEUS
# ============================================
messages_sent = Counter(
    'kafka_messages_sent_total',
    'Total de mensajes enviados a Kafka',
    ['topic', 'status']
)

send_duration = Histogram(
    'kafka_send_duration_seconds',
    'Duración del envío de mensajes',
    ['topic']
)


class BaseKafkaProducer:
    """
    Productor base con funcionalidades avanzadas:
    - Retry automático con backoff exponencial
    - Dead Letter Queue para mensajes fallidos
    - Métricas de monitoreo
    - Manejo robusto de errores
    """
    
    def __init__(self):
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con Kafka"""
        try:
            self.producer = KafkaProducer(**settings.KAFKA_PRODUCER_CONFIG)
            logger.info("✅ Productor Kafka conectado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error conectando a Kafka: {e}")
            raise
    
    def send_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Envía un mensaje a Kafka con retry y manejo de errores
        
        Args:
            topic: Nombre del topic
            message: Diccionario con el mensaje
            key: Clave para particionamiento
            headers: Headers adicionales
        
        Returns:
            bool: True si el envío fue exitoso
        """
        if not self.producer:
            self._connect()
        
        # Añadir metadata
        enriched_message = {
            **message,
            'timestamp': datetime.now().isoformat(),
            'source': 'nuam-api',
            'version': '1.0'
        }
        
        # Preparar headers
        kafka_headers = []
        if headers:
            kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
        
        # Intentar envío con retry
        retry_config = settings.KAFKA_RETRY_CONFIG
        max_retries = retry_config['max_retries']
        backoff = retry_config['initial_backoff_seconds']
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Envío asíncrono
                future = self.producer.send(
                    topic,
                    value=enriched_message,
                    key=key,
                    headers=kafka_headers
                )
                
                # Esperar confirmación
                record_metadata = future.get(timeout=10)
                
                # Métricas
                duration = time.time() - start_time
                send_duration.labels(topic=topic).observe(duration)
                messages_sent.labels(topic=topic, status='success').inc()
                
                logger.info(
                    f"✅ Mensaje enviado - Topic: {topic}, "
                    f"Partition: {record_metadata.partition}, "
                    f"Offset: {record_metadata.offset}, "
                    f"Key: {key}"
                )
                return True
                
            except KafkaTimeoutError as e:
                logger.warning(f"⏱️ Timeout enviando mensaje (intento {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    time.sleep(backoff)
                    backoff *= retry_config['backoff_multiplier']
                else:
                    self._send_to_dlq(topic, enriched_message, str(e))
                    messages_sent.labels(topic=topic, status='failed').inc()
                    return False
                    
            except KafkaError as e:
                logger.error(f"❌ Error de Kafka: {e}")
                self._send_to_dlq(topic, enriched_message, str(e))
                messages_sent.labels(topic=topic, status='error').inc()
                return False
                
            except Exception as e:
                logger.error(f"❌ Error inesperado: {e}", exc_info=True)
                self._send_to_dlq(topic, enriched_message, str(e))
                messages_sent.labels(topic=topic, status='error').inc()
                return False
        
        return False
    
    def _send_to_dlq(self, original_topic: str, message: Dict, error: str):
        """Envía mensaje fallido a Dead Letter Queue"""
        dlq_topic = settings.KAFKA_TOPICS['ERRORES']
        dlq_message = {
            'original_topic': original_topic,
            'original_message': message,
            'error': error,
            'failed_at': datetime.now().isoformat()
        }
        
        try:
            self.producer.send(dlq_topic, value=dlq_message)
            logger.info(f"📮 Mensaje enviado a DLQ: {dlq_topic}")
        except Exception as e:
            logger.error(f"❌ Error enviando a DLQ: {e}")
    
    def close(self):
        """Cierra el productor limpiamente"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("🔒 Productor Kafka cerrado")


# ============================================
# PRODUCTORES ESPECÍFICOS
# ============================================

class CargaMasivaProducer(BaseKafkaProducer):
    """Productor para eventos de carga masiva"""
    
    def publish_carga_iniciada(self, carga_id: int, usuario: str, filename: str):
        """Publica evento de inicio de carga"""
        message = {
            'event_type': 'CARGA_INICIADA',
            'carga_id': carga_id,
            'usuario': usuario,
            'filename': filename,
            'estado': 'PROCESANDO'
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['CARGA_MASIVA'],
            message=message,
            key=str(carga_id),
            headers={'event': 'carga_iniciada'}
        )
    
    def publish_carga_completada(
        self,
        carga_id: int,
        total_registros: int,
        exitosos: int,
        fallidos: int,
        duracion_segundos: float
    ):
        """Publica evento de carga completada"""
        message = {
            'event_type': 'CARGA_COMPLETADA',
            'carga_id': carga_id,
            'total_registros': total_registros,
            'exitosos': exitosos,
            'fallidos': fallidos,
            'duracion_segundos': duracion_segundos,
            'estado': 'COMPLETADO'
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['CARGA_MASIVA'],
            message=message,
            key=str(carga_id),
            headers={'event': 'carga_completada'}
        )
    
    def publish_carga_fallida(self, carga_id: int, error: str):
        """Publica evento de carga fallida"""
        message = {
            'event_type': 'CARGA_FALLIDA',
            'carga_id': carga_id,
            'error': error,
            'estado': 'FALLIDO'
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['CARGA_MASIVA'],
            message=message,
            key=str(carga_id),
            headers={'event': 'carga_fallida'}
        )


class CalificacionProducer(BaseKafkaProducer):
    """Productor para eventos de calificación tributaria"""
    
    def publish_calificacion_creada(self, calificacion_data: Dict):
        """Publica nueva calificación"""
        message = {
            'event_type': 'CALIFICACION_CREADA',
            'calificacion': calificacion_data
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['CALIFICACION'],
            message=message,
            key=str(calificacion_data.get('id')),
            headers={'event': 'calificacion_creada'}
        )
    
    def publish_calificacion_actualizada(self, calificacion_id: int, cambios: Dict):
        """Publica actualización de calificación"""
        message = {
            'event_type': 'CALIFICACION_ACTUALIZADA',
            'calificacion_id': calificacion_id,
            'cambios': cambios
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['CALIFICACION'],
            message=message,
            key=str(calificacion_id),
            headers={'event': 'calificacion_actualizada'}
        )


class AuditoriaProducer(BaseKafkaProducer):
    """Productor para logs de auditoría"""
    
    def publish_log(
        self,
        usuario: str,
        accion: str,
        recurso: str,
        detalles: Optional[Dict] = None
    ):
        """Publica log de auditoría"""
        message = {
            'usuario': usuario,
            'accion': accion,
            'recurso': recurso,
            'detalles': detalles or {},
            'ip_address': None,  # Se puede obtener del request
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['AUDITORIA'],
            message=message,
            key=usuario,
            headers={'type': 'audit_log'}
        )


class NotificacionProducer(BaseKafkaProducer):
    """Productor para notificaciones"""
    
    def publish_notificacion(
        self,
        usuario_id: int,
        tipo: str,
        mensaje: str,
        prioridad: str = 'normal'
    ):
        """Publica notificación para usuario"""
        message = {
            'usuario_id': usuario_id,
            'tipo': tipo,  # EMAIL, SMS, PUSH, IN_APP
            'mensaje': mensaje,
            'prioridad': prioridad,  # low, normal, high, urgent
            'leido': False
        }
        
        return self.send_message(
            topic=settings.KAFKA_TOPICS['NOTIFICACIONES'],
            message=message,
            key=str(usuario_id),
            headers={'priority': prioridad}
        )


# ============================================
# INSTANCIAS SINGLETON
# ============================================
carga_masiva_producer = CargaMasivaProducer()
calificacion_producer = CalificacionProducer()
auditoria_producer = AuditoriaProducer()
notificacion_producer = NotificacionProducer()