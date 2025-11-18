"""
Management command para ejecutar todos los consumidores Kafka
Uso: python manage.py run_kafka_consumers
"""
import threading
import logging
from django.core.management.base import BaseCommand
from kafka_app.consumers import (
    CargaMasivaConsumer,
    CalificacionConsumer,
    AuditoriaConsumer,
    NotificacionConsumer
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicia todos los consumidores Kafka en threads separados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--consumer',
            type=str,
            help='Nombre del consumidor específico a ejecutar (carga, calificacion, auditoria, notificacion)',
        )

    def handle(self, *args, **options):
        consumer_name = options.get('consumer')
        
        if consumer_name:
            # Ejecutar consumidor específico
            self._run_specific_consumer(consumer_name)
        else:
            # Ejecutar todos los consumidores
            self._run_all_consumers()

    def _run_specific_consumer(self, name: str):
        """Ejecuta un consumidor específico"""
        consumers = {
            'carga': CargaMasivaConsumer,
            'calificacion': CalificacionConsumer,
            'auditoria': AuditoriaConsumer,
            'notificacion': NotificacionConsumer,
        }
        
        consumer_class = consumers.get(name.lower())
        if not consumer_class:
            self.stdout.write(
                self.style.ERROR(f'❌ Consumidor "{name}" no encontrado')
            )
            self.stdout.write(f'Opciones válidas: {", ".join(consumers.keys())}')
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando consumidor: {name}')
        )
        
        try:
            consumer = consumer_class()
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING(f'⛔ Consumidor {name} detenido')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error en consumidor {name}: {e}')
            )

    def _run_all_consumers(self):
        """Ejecuta todos los consumidores en threads separados"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando todos los consumidores Kafka...')
        )
        
        consumers = [
            ('Carga Masiva', CargaMasivaConsumer),
            ('Calificación', CalificacionConsumer),
            ('Auditoría', AuditoriaConsumer),
            ('Notificación', NotificacionConsumer),
        ]
        
        threads = []
        
        for name, consumer_class in consumers:
            thread = threading.Thread(
                target=self._run_consumer_thread,
                args=(name, consumer_class),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Thread iniciado para: {name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Todos los consumidores están corriendo\n'
                'Presiona Ctrl+C para detener\n'
            )
        )
        
        try:
            # Mantener el proceso principal vivo
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⛔ Deteniendo todos los consumidores...')
            )

    def _run_consumer_thread(self, name: str, consumer_class):
        """Ejecuta un consumidor en un thread"""
        try:
            consumer = consumer_class()
            logger.info(f'Thread {name} iniciado')
            consumer.start()
        except Exception as e:
            logger.error(f'Error en thread {name}: {e}', exc_info=True)