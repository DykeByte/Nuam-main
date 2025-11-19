# api/management/commands/generate_cert.py
from django.core.management.base import BaseCommand
from django.conf import settings
from api.certificates import CertificateManager


class Command(BaseCommand):
    help = 'Genera certificado SSL autofirmado para desarrollo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Días de validez del certificado (default: 365)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar regeneración aunque ya exista uno válido'
        )

    def handle(self, *args, **options):
        days = options['days']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('🔐 Generador de Certificados SSL - NUAM'))
        self.stdout.write('=' * 60)
        
        manager = CertificateManager(settings.BASE_DIR)
        
        if manager.certificate_exists() and not force:
            info = manager.get_certificate_info()
            if info and info['is_valid']:
                self.stdout.write(
                    self.style.WARNING('⚠️  Ya existe un certificado válido')
                )
                self.stdout.write(f"   Válido hasta: {info['not_valid_after']}")
                self.stdout.write('')
                self.stdout.write('   Usa --force para regenerar')
                return
        
        cert_path, key_path = manager.generate_self_signed_cert(days)
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Certificado generado exitosamente'))
        self.stdout.write('')
        self.stdout.write(f"📄 Certificado: {cert_path}")
        self.stdout.write(f"🔑 Clave privada: {key_path}")
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANTE:'))
        self.stdout.write('   Este es un certificado autofirmado para DESARROLLO.')
        self.stdout.write('   NO usar en producción.')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🚀 Para iniciar con HTTPS:'))
        self.stdout.write('   python manage.py runserver_plus --cert-file certs/nuam_cert.crt')
        self.stdout.write('')