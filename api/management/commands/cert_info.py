"""
Management command para gestionar certificados SSL
Uso: python manage.py cert_info [--format json|text] [--renew]
"""
from django.core.management.base import BaseCommand
from api.certificates import CertificateManager


class Command(BaseCommand):
    help = 'Muestra información del certificado SSL o lo renueva'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['json', 'text'],
            help='Formato de salida'
        )
        parser.add_argument(
            '--renew',
            action='store_true',
            help='Forzar renovación del certificado'
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Solo verificar si necesita renovación'
        )
    
    def handle(self, *args, **options):
        cert_manager = CertificateManager()
        
        if options['renew']:
            self.stdout.write(self.style.WARNING('🔄 Renovando certificado...'))
            cert_manager.create_self_signed_cert()
            self.stdout.write(self.style.SUCCESS('✅ Certificado renovado exitosamente'))
            return
        
        if options['check']:
            if cert_manager.needs_renewal():
                days_left = cert_manager.get_days_until_expiry()
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ Certificado necesita renovación (expira en {days_left} días)'
                    )
                )
            else:
                days_left = cert_manager.get_days_until_expiry()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Certificado válido ({days_left} días restantes)'
                    )
                )
            return
        
        # Mostrar información
        output = cert_manager.export_certificate_info(options['format'])
        self.stdout.write(output)