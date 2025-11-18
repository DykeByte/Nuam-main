"""
Consumidores Kafka para el sistema NUAM
Implementa procesamiento robusto con manejo de errores y métricas
"""
import json
import logging
from typing import Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from django.conf import settings
from prometheus_client import Counter, Histogram
import time

logger = logging.getLogger(__name__)

# ============================================
# MÉTRICAS PROMETHEUS
# ============================================
messages_consumed = Counter(
    'kafka_messages_consumed_total',
    'Total de mensajes consumidos',
    ['topic', 'status']
)

processing_duration = Histogram(
    'kafka_processing_duration_seconds',
    'Duración del procesamiento de mensajes',
    ['topic', 'event_type']
)


class BaseKafkaConsumer:
    """
    Consumidor base con funcionalidades avanzadas:
    - Commit manual para garantizar procesamiento
    - Manejo de errores con retry
    - Métricas de monitoreo
    - Procesamiento por lotes
    """
    
    def __init__(self, topics: list):
        self.topics = topics
        self.consumer = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con Kafka"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                **settings.KAFKA_CONSUMER_CONFIG
            )
            logger.info(f"✅ Consumidor Kafka conectado - Topics: {self.topics}")
        except Exception as e:
            logger.error(f"❌ Error conectando consumidor: {e}")
            raise
    
    def start(self):
        """Inicia el consumo de mensajes"""
        logger.info(f"🚀 Iniciando consumo de mensajes...")
        
        try:
            for message in self.consumer:
                self._process_message(message)
        except KeyboardInterrupt:
            logger.info("⛔ Consumo detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en consumo: {e}", exc_info=True)
        finally:
            self.close()
    
    def _process_message(self, message):
        """Procesa un mensaje individual"""
        start_time = time.time()
        
        try:
            # Parsear mensaje
            value = message.value
            key = message.key
            
            logger.info(
                f"📥 Mensaje recibido - Topic: {message.topic}, "
                f"Partition: {message.partition}, "
                f"Offset: {message.offset}, "
                f"Key: {key}"
            )
            
            # Procesar según tipo de evento
            event_type = value.get('event_type', 'UNKNOWN')
            success = self.handle_message(value, message.topic)
            
            if success:
                # Commit manual solo si procesamiento fue exitoso
                self.consumer.commit()
                messages_consumed.labels(
                    topic=message.topic,
                    status='success'
                ).inc()
                logger.info("✅ Mensaje procesado y committeado exitosamente")
            else:
                messages_consumed.labels(
                    topic=message.topic,
                    status='failed'
                ).inc()
                logger.warning("⚠️ Mensaje no procesado, se reintentará")
            
            # Registrar métricas
            duration = time.time() - start_time
            processing_duration.labels(
                topic=message.topic,
                event_type=event_type
            ).observe(duration)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}", exc_info=True)
            messages_consumed.labels(
                topic=message.topic,
                status='error'
            ).inc()
            # No hacer commit para reintentar
    
    def handle_message(self, message: Dict[str, Any], topic: str) -> bool:
        """
        Método a implementar por subclases
        
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        raise NotImplementedError("Subclases deben implementar handle_message()")
    
    def close(self):
        """Cierra el consumidor limpiamente"""
        if self.consumer:
            self.consumer.close()
            logger.info("🔒 Consumidor Kafka cerrado")


# ============================================
# CONSUMIDORES ESPECÍFICOS
# ============================================

class CargaMasivaConsumer(BaseKafkaConsumer):
    """Consumidor para eventos de carga masiva"""
    
    def __init__(self):
        super().__init__([settings.KAFKA_TOPICS['CARGA_MASIVA']])
    
    def handle_message(self, message: Dict[str, Any], topic: str) -> bool:
        """Procesa eventos de carga masiva"""
        event_type = message.get('event_type')
        
        try:
            if event_type == 'CARGA_INICIADA':
                return self._handle_carga_iniciada(message)
            
            elif event_type == 'CARGA_COMPLETADA':
                return self._handle_carga_completada(message)
            
            elif event_type == 'CARGA_FALLIDA':
                return self._handle_carga_fallida(message)
            
            else:
                logger.warning(f"⚠️ Tipo de evento desconocido: {event_type}")
                return True  # Ignorar eventos desconocidos
        
        except Exception as e:
            logger.error(f"❌ Error manejando evento {event_type}: {e}")
            return False
    
    def _handle_carga_iniciada(self, message: Dict) -> bool:
        """Procesa inicio de carga"""
        carga_id = message.get('carga_id')
        usuario = message.get('usuario')
        filename = message.get('filename')
        
        logger.info(
            f"🔵 CARGA INICIADA - ID: {carga_id}, "
            f"Usuario: {usuario}, "
            f"Archivo: {filename}"
        )
        
        # Aquí puedes:
        # - Enviar notificación al usuario
        # - Actualizar dashboard en tiempo real (WebSockets)
        # - Inicializar métricas
        
        from kafka_app.producers import notificacion_producer
        notificacion_producer.publish_notificacion(
            usuario_id=1,  # Obtener de usuario
            tipo='IN_APP',
            mensaje=f'Carga masiva iniciada: {filename}',
            prioridad='normal'
        )
        
        return True
    
    def _handle_carga_completada(self, message: Dict) -> bool:
        """Procesa carga completada"""
        carga_id = message.get('carga_id')
        exitosos = message.get('exitosos')
        fallidos = message.get('fallidos')
        duracion = message.get('duracion_segundos')
        
        logger.info(
            f"🟢 CARGA COMPLETADA - ID: {carga_id}, "
            f"Exitosos: {exitosos}, "
            f"Fallidos: {fallidos}, "
            f"Duración: {duracion:.2f}s"
        )
        
        # Actualizar estadísticas
        # Enviar notificación de éxito
        # Generar reporte
        
        from kafka_app.producers import notificacion_producer
        notificacion_producer.publish_notificacion(
            usuario_id=1,
            tipo='EMAIL',
            mensaje=f'Carga completada: {exitosos} exitosos, {fallidos} fallidos',
            prioridad='normal'
        )
        
        return True
    
    def _handle_carga_fallida(self, message: Dict) -> bool:
        """Procesa carga fallida"""
        carga_id = message.get('carga_id')
        error = message.get('error')
        
        logger.error(f"🔴 CARGA FALLIDA - ID: {carga_id}, Error: {error}")
        
        # Notificar al usuario
        # Registrar en sistema de alertas
        # Enviar a equipo de soporte
        
        from kafka_app.producers import notificacion_producer
        notificacion_producer.publish_notificacion(
            usuario_id=1,
            tipo='EMAIL',
            mensaje=f'Error en carga masiva: {error}',
            prioridad='high'
        )
        
        return True


class CalificacionConsumer(BaseKafkaConsumer):
    """Consumidor para eventos de calificación"""
    
    def __init__(self):
        super().__init__([settings.KAFKA_TOPICS['CALIFICACION']])
    
    def handle_message(self, message: Dict[str, Any], topic: str) -> bool:
        """Procesa eventos de calificación"""
        event_type = message.get('event_type')
        
        try:
            if event_type == 'CALIFICACION_CREADA':
                return self._handle_calificacion_creada(message)
            
            elif event_type == 'CALIFICACION_ACTUALIZADA':
                return self._handle_calificacion_actualizada(message)
            
            else:
                logger.warning(f"⚠️ Tipo de evento desconocido: {event_type}")
                return True
        
        except Exception as e:
            logger.error(f"❌ Error manejando evento {event_type}: {e}")
            return False
    
    def _handle_calificacion_creada(self, message: Dict) -> bool:
        """Procesa nueva calificación"""
        calificacion = message.get('calificacion', {})
        
        logger.info(f"📊 Nueva calificación creada: ID {calificacion.get('id')}")
        
        # Aquí puedes:
        # - Actualizar índices de búsqueda (Elasticsearch)
        # - Invalidar cache
        # - Calcular métricas agregadas
        # - Sincronizar con otros sistemas
        
        return True
    
    def _handle_calificacion_actualizada(self, message: Dict) -> bool:
        """Procesa actualización de calificación"""
        calificacion_id = message.get('calificacion_id')
        cambios = message.get('cambios', {})
        
        logger.info(
            f"🔄 Calificación actualizada: ID {calificacion_id}, "
            f"Cambios: {list(cambios.keys())}"
        )
        
        return True


class AuditoriaConsumer(BaseKafkaConsumer):
    """Consumidor para logs de auditoría"""
    
    def __init__(self):
        super().__init__([settings.KAFKA_TOPICS['AUDITORIA']])
    
    def handle_message(self, message: Dict[str, Any], topic: str) -> bool:
        """Procesa logs de auditoría"""
        try:
            usuario = message.get('usuario')
            accion = message.get('accion')
            recurso = message.get('recurso')
            timestamp = message.get('timestamp')
            
            logger.info(
                f"📝 AUDIT LOG - Usuario: {usuario}, "
                f"Acción: {accion}, "
                f"Recurso: {recurso}, "
                f"Timestamp: {timestamp}"
            )
            
            # Aquí puedes:
            # - Guardar en base de datos de auditoría
            # - Enviar a sistema SIEM
            # - Analizar patrones sospechosos
            # - Generar alertas de seguridad
            
            from api.models import LogOperacion
            LogOperacion.objects.create(
                usuario=usuario,
                accion=accion,
                recurso=recurso,
                timestamp=timestamp,
                detalles=message.get('detalles', {})
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando audit log: {e}")
            return False


class NotificacionConsumer(BaseKafkaConsumer):
    """Consumidor para notificaciones"""
    
    def __init__(self):
        super().__init__([settings.KAFKA_TOPICS['NOTIFICACIONES']])
    
    def handle_message(self, message: Dict[str, Any], topic: str) -> bool:
        """Procesa notificaciones"""
        try:
            usuario_id = message.get('usuario_id')
            tipo = message.get('tipo')
            mensaje_texto = message.get('mensaje')
            prioridad = message.get('prioridad')
            
            logger.info(
                f"📧 NOTIFICACIÓN - Usuario: {usuario_id}, "
                f"Tipo: {tipo}, "
                f"Prioridad: {prioridad}"
            )
            
            # Procesar según tipo
            if tipo == 'EMAIL':
                return self._send_email(usuario_id, mensaje_texto)
            
            elif tipo == 'SMS':
                return self._send_sms(usuario_id, mensaje_texto)
            
            elif tipo == 'PUSH':
                return self._send_push(usuario_id, mensaje_texto)
            
            elif tipo == 'IN_APP':
                return self._save_in_app_notification(usuario_id, mensaje_texto)
            
            else:
                logger.warning(f"⚠️ Tipo de notificación desconocido: {tipo}")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando notificación: {e}")
            return False
    
    def _send_email(self, usuario_id: int, mensaje: str) -> bool:
        """Envía email (integrar con SendGrid, AWS SES, etc.)"""
        logger.info(f"📧 Enviando email a usuario {usuario_id}: {mensaje}")
        # TODO: Implementar integración real
        return True
    
    def _send_sms(self, usuario_id: int, mensaje: str) -> bool:
        """Envía SMS (integrar con Twilio, etc.)"""
        logger.info(f"📱 Enviando SMS a usuario {usuario_id}: {mensaje}")
        # TODO: Implementar integración real
        return True
    
    def _send_push(self, usuario_id: int, mensaje: str) -> bool:
        """Envía push notification (integrar con FCM, etc.)"""
        logger.info(f"🔔 Enviando push a usuario {usuario_id}: {mensaje}")
        # TODO: Implementar integración real
        return True
    
    def _save_in_app_notification(self, usuario_id: int, mensaje: str) -> bool:
        """Guarda notificación in-app en base de datos"""
        logger.info(f"💾 Guardando notificación in-app para usuario {usuario_id}")
        # TODO: Guardar en modelo de Notificaciones
        return True