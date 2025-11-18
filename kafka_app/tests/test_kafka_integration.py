"""
Tests para la integración de Kafka
python manage.py test kafka_app.tests
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from faker import Faker

from kafka_app.producers import (
    CargaMasivaProducer,
    CalificacionProducer,
    AuditoriaProducer,
    NotificacionProducer
)
from kafka_app.consumers import (
    CargaMasivaConsumer,
    CalificacionConsumer,
    AuditoriaConsumer
)

fake = Faker()


class ProducerTestCase(TestCase):
    """Tests para productores Kafka"""
    
    def setUp(self):
        """Setup para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    @patch('kafka_app.producers.KafkaProducer')
    def test_carga_masiva_producer_success(self, mock_kafka_producer):
        """Test: Productor de carga masiva envía mensaje exitosamente"""
        # Configurar mock
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test-topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 123
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        # Ejecutar
        producer = CargaMasivaProducer()
        result = producer.publish_carga_iniciada(
            carga_id=1,
            usuario='testuser',
            filename='test.xlsx'
        )
        
        # Verificar
        self.assertTrue(result)
        mock_producer_instance.send.assert_called_once()
        
        # Verificar estructura del mensaje
        call_args = mock_producer_instance.send.call_args
        message = call_args[1]['value']
        self.assertEqual(message['event_type'], 'CARGA_INICIADA')
        self.assertEqual(message['carga_id'], 1)
        self.assertEqual(message['usuario'], 'testuser')
        self.assertEqual(message['filename'], 'test.xlsx')
        self.assertIn('timestamp', message)
        self.assertIn('source', message)
    
    @patch('kafka_app.producers.KafkaProducer')
    def test_carga_masiva_producer_retry_on_failure(self, mock_kafka_producer):
        """Test: Productor reintenta en caso de fallo temporal"""
        mock_producer_instance = Mock()
        
        # Primer intento falla, segundo tiene éxito
        mock_future_fail = Mock()
        mock_future_fail.get.side_effect = Exception("Connection timeout")
        
        mock_future_success = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test-topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 456
        mock_future_success.get.return_value = mock_metadata
        
        mock_producer_instance.send.side_effect = [
            mock_future_fail,
            mock_future_success
        ]
        mock_kafka_producer.return_value = mock_producer_instance
        
        # Ejecutar
        producer = CargaMasivaProducer()
        result = producer.publish_carga_iniciada(
            carga_id=2,
            usuario='testuser',
            filename='test2.xlsx'
        )
        
        # Verificar que reintentó
        self.assertEqual(mock_producer_instance.send.call_count, 2)
    
    @patch('kafka_app.producers.KafkaProducer')
    def test_notificacion_producer_different_types(self, mock_kafka_producer):
        """Test: Productor de notificaciones maneja diferentes tipos"""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'notifications'
        mock_metadata.partition = 0
        mock_metadata.offset = 789
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        producer = NotificacionProducer()
        
        # Test EMAIL
        result = producer.publish_notificacion(
            usuario_id=1,
            tipo='EMAIL',
            mensaje='Test email',
            prioridad='high'
        )
        self.assertTrue(result)
        
        # Test SMS
        result = producer.publish_notificacion(
            usuario_id=1,
            tipo='SMS',
            mensaje='Test SMS',
            prioridad='normal'
        )
        self.assertTrue(result)
        
        # Verificar que se llamó 2 veces
        self.assertEqual(mock_producer_instance.send.call_count, 2)


class ConsumerTestCase(TestCase):
    """Tests para consumidores Kafka"""
    
    def setUp(self):
        """Setup para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    @patch('kafka_app.consumers.KafkaConsumer')
    def test_carga_masiva_consumer_handles_iniciada(self, mock_kafka_consumer):
        """Test: Consumidor procesa evento CARGA_INICIADA correctamente"""
        # Preparar mensaje mock
        mock_message = Mock()
        mock_message.topic = 'nuam.carga-masiva.events'
        mock_message.partition = 0
        mock_message.offset = 100
        mock_message.key = '1'
        mock_message.value = {
            'event_type': 'CARGA_INICIADA',
            'carga_id': 1,
            'usuario': 'testuser',
            'filename': 'test.xlsx',
            'timestamp': '2024-01-01T10:00:00'
        }
        
        # Configurar consumer mock
        mock_consumer_instance = Mock()
        mock_consumer_instance.__iter__ = Mock(return_value=iter([mock_message]))
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        # Ejecutar
        consumer = CargaMasivaConsumer()
        result = consumer.handle_message(mock_message.value, mock_message.topic)
        
        # Verificar
        self.assertTrue(result)
    
    @patch('kafka_app.consumers.KafkaConsumer')
    def test_consumer_commits_on_success(self, mock_kafka_consumer):
        """Test: Consumidor hace commit solo cuando el procesamiento es exitoso"""
        mock_message = Mock()
        mock_message.topic = 'test-topic'
        mock_message.partition = 0
        mock_message.offset = 200
        mock_message.key = '2'
        mock_message.value = {
            'event_type': 'CARGA_COMPLETADA',
            'carga_id': 2,
            'exitosos': 100,
            'fallidos': 5,
            'timestamp': '2024-01-01T11:00:00'
        }
        
        mock_consumer_instance = Mock()
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        consumer = CargaMasivaConsumer()
        consumer.consumer = mock_consumer_instance
        
        # Procesar mensaje
        consumer._process_message(mock_message)
        
        # Verificar que se hizo commit
        mock_consumer_instance.commit.assert_called_once()
    
    def test_auditoria_consumer_saves_log(self):
        """Test: Consumidor de auditoría guarda log en base de datos"""
        from api.models import LogOperacion
        
        consumer = AuditoriaConsumer()
        message = {
            'usuario': 'testuser',
            'accion': 'TEST_ACTION',
            'recurso': '/api/test',
            'timestamp': '2024-01-01T12:00:00',
            'detalles': {'test': 'data'}
        }
        
        # Ejecutar
        result = consumer.handle_message(message, 'auditoria-topic')
        
        # Verificar
        self.assertTrue(result)
        
        # Verificar que se guardó en base de datos
        log = LogOperacion.objects.filter(
            usuario='testuser',
            accion='TEST_ACTION'
        ).first()
        
        self.assertIsNotNone(log)
        self.assertEqual(log.recurso, '/api/test')


class IntegrationTestCase(TestCase):
    """Tests de integración end-to-end"""
    
    @patch('kafka_app.producers.KafkaProducer')
    @patch('kafka_app.consumers.KafkaConsumer')
    def test_full_carga_masiva_flow(self, mock_consumer, mock_producer):
        """Test: Flujo completo de carga masiva con Kafka"""
        # Configurar mocks
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'carga-masiva'
        mock_metadata.partition = 0
        mock_metadata.offset = 1
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_producer.return_value = mock_producer_instance
        
        # 1. Publicar evento de inicio
        producer = CargaMasivaProducer()
        result = producer.publish_carga_iniciada(
            carga_id=10,
            usuario='testuser',
            filename='integration_test.xlsx'
        )
        self.assertTrue(result)
        
        # 2. Simular procesamiento
        # ... (tu lógica de procesamiento)
        
        # 3. Publicar evento de completado
        result = producer.publish_carga_completada(
            carga_id=10,
            total_registros=500,
            exitosos=495,
            fallidos=5,
            duracion_segundos=12.5
        )
        self.assertTrue(result)
        
        # Verificar que se enviaron 2 mensajes
        self.assertEqual(mock_producer_instance.send.call_count, 2)


@pytest.mark.django_db
class AsyncProducerTestCase:
    """Tests asíncronos con pytest"""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='asyncuser',
            password='testpass123'
        )
    
    @patch('kafka_app.producers.KafkaProducer')
    def test_concurrent_messages(self, mock_producer, user):
        """Test: Múltiples mensajes concurrentes"""
        import concurrent.futures
        
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test'
        mock_metadata.partition = 0
        mock_metadata.offset = 1
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_producer.return_value = mock_producer_instance
        
        producer = CargaMasivaProducer()
        
        def send_message(i):
            return producer.publish_carga_iniciada(
                carga_id=i,
                usuario='asyncuser',
                filename=f'test_{i}.xlsx'
            )
        
        # Enviar 10 mensajes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_message, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Verificar que todos tuvieron éxito
        assert all(results)
        assert mock_producer_instance.send.call_count == 10


# ============================================
# HELPER FUNCTIONS PARA TESTS
# ============================================

def create_mock_kafka_message(event_type: str, **kwargs):
    """Crea un mensaje mock de Kafka para testing"""
    message = Mock()
    message.topic = kwargs.get('topic', 'test-topic')
    message.partition = kwargs.get('partition', 0)
    message.offset = kwargs.get('offset', 1)
    message.key = kwargs.get('key', '1')
    message.value = {
        'event_type': event_type,
        'timestamp': '2024-01-01T10:00:00',
        **kwargs.get('extra_data', {})
    }
    return message


def assert_kafka_message_structure(message: dict, required_fields: list):
    """Verifica que un mensaje tenga todos los campos requeridos"""
    for field in required_fields:
        assert field in message, f"Campo requerido '{field}' no encontrado en mensaje"