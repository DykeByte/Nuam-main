"""
Management command para esperar a que la base de datos esté disponible
Guardar en: accounts/management/commands/wait_for_db.py
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Espera a que la base de datos esté disponible'

    def handle(self, *args, **options):
        self.stdout.write('Esperando a que la base de datos esté disponible...')
        db_conn = None
        max_retries = 30
        retry_count = 0
        
        while not db_conn and retry_count < max_retries:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('✓ Base de datos disponible!'))
                return
            except OperationalError:
                retry_count += 1
                self.stdout.write(
                    f'Base de datos no disponible, esperando... ({retry_count}/{max_retries})'
                )
                time.sleep(2)
        
        if retry_count >= max_retries:
            self.stdout.write(
                self.style.ERROR('✗ No se pudo conectar a la base de datos')
            )
            raise Exception('No se pudo conectar a la base de datos después de múltiples intentos')