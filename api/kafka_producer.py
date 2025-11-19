# api/kafka_producer.py
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class NuamKafkaProducer:
    """
    Productor de Kafka para publicar eventos del sistema NUAM.
    """
    
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092'])
        self.connect()
    
    def connect(self):
        """Establece conexión con Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Esperar confirmación de todos los brokers
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"✅ Kafka Producer conectado a {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Error conectando a Kafka: {str(e)}", exc_info=True)
            self.producer = None
    
    def publicar_evento(self, topic, evento, key=None):
        """
        Publica un evento en un topic de Kafka.
        
        Args:
            topic (str): Nombre del topic
            evento (dict): Datos del evento
            key (str): Clave del mensaje (opcional)
        """
        if not self.producer:
            logger.warning("⚠️ Kafka Producer no está conectado. Reconectando...")
            self.connect()
            if not self.producer:
                logger.error("❌ No se pudo publicar evento. Kafka no disponible.")
                return False
        
        try:
            future = self.producer.send(topic, value=evento, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"📤 Evento publicado en Kafka:")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Partition: {record_metadata.partition}")
            logger.info(f"   Offset: {record_metadata.offset}")
            logger.info(f"   Evento: {json.dumps(evento, indent=2)}")
            
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Error publicando en Kafka: {str(e)}", exc_info=True)
            return False
    
    def close(self):
        """Cierra la conexión con Kafka"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("🔌 Kafka Producer cerrado")


# Instancia global del productor
kafka_producer = NuamKafkaProducer()


# Funciones helper para eventos específicos
def publicar_evento_carga_iniciada(carga):
    """Publica evento cuando se inicia una carga masiva"""
    evento = {
        'tipo_evento': 'CARGA_INICIADA',
        'carga_id': carga.id,
        'usuario': carga.iniciado_por.username,
        'tipo_carga': carga.tipo_carga,
        'mercado': carga.mercado,
        'archivo': carga.archivo_nombre,
        'timestamp': carga.fecha_inicio.isoformat()
    }
    return kafka_producer.publicar_evento('nuam-cargas', evento, key=f"carga-{carga.id}")


def publicar_evento_carga_completada(carga):
    """Publica evento cuando se completa una carga masiva"""
    evento = {
        'tipo_evento': 'CARGA_COMPLETADA',
        'carga_id': carga.id,
        'usuario': carga.iniciado_por.username,
        'estado': carga.estado,
        'registros_procesados': carga.registros_procesados,
        'registros_exitosos': carga.registros_exitosos,
        'registros_fallidos': carga.registros_fallidos,
        'porcentaje_exito': round((carga.registros_exitosos / carga.registros_procesados * 100), 2) if carga.registros_procesados > 0 else 0,
        'timestamp': carga.fecha_inicio.isoformat()
    }
    return kafka_producer.publicar_evento('nuam-cargas', evento, key=f"carga-{carga.id}")


def publicar_evento_calificacion_creada(calificacion):
    """Publica evento cuando se crea una calificación"""
    evento = {
        'tipo_evento': 'CALIFICACION_CREADA',
        'calificacion_id': calificacion.id,
        'usuario': calificacion.usuario.username,
        'instrumento': calificacion.instrumento,
        'mercado': calificacion.mercado,
        'divisa': calificacion.divisa,
        'valor_historico': str(calificacion.valor_historico) if calificacion.valor_historico else None,
        'timestamp': calificacion.created_at.isoformat()
    }
    return kafka_producer.publicar_evento('nuam-calificaciones', evento, key=f"calif-{calificacion.id}")


def publicar_evento_calificacion_actualizada(calificacion, datos_anteriores):
    """Publica evento cuando se actualiza una calificación"""
    evento = {
        'tipo_evento': 'CALIFICACION_ACTUALIZADA',
        'calificacion_id': calificacion.id,
        'usuario': calificacion.usuario.username,
        'datos_anteriores': datos_anteriores,
        'datos_nuevos': {
            'instrumento': calificacion.instrumento,
            'mercado': calificacion.mercado,
            'valor_historico': str(calificacion.valor_historico) if calificacion.valor_historico else None
        },
        'timestamp': calificacion.updated_at.isoformat()
    }
    return kafka_producer.publicar_evento('nuam-calificaciones', evento, key=f"calif-{calificacion.id}")


def publicar_evento_calificacion_eliminada(calificacion_id, usuario):
    """Publica evento cuando se elimina una calificación"""
    evento = {
        'tipo_evento': 'CALIFICACION_ELIMINADA',
        'calificacion_id': calificacion_id,
        'usuario': usuario,
        'timestamp': timezone.now().isoformat()
    }
    return kafka_producer.publicar_evento('nuam-calificaciones', evento, key=f"calif-{calificacion_id}")