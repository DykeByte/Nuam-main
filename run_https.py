#!/usr/bin/env python
"""
Script para ejecutar el servidor Django con HTTPS
Genera certificados SSL automáticamente si no existen

Uso:
    python run_https.py
    python run_https.py --port 8443
"""
import os
import sys
import argparse
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam.settings')

import django
django.setup()

from api.certificates import CertificateManager
from django.core.management import execute_from_command_line


def main():
    parser = argparse.ArgumentParser(description='Ejecutar servidor Django con HTTPS')
    parser.add_argument('--port', type=int, default=8000, help='Puerto (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host (default: 0.0.0.0)')
    args = parser.parse_args()
    
    # Generar/verificar certificados
    cert_manager = CertificateManager()
    cert_file, key_file = cert_manager.ensure_certificate()
    
    # Mostrar info del certificado
    cert_info = cert_manager.get_certificate_info()
    if cert_info:
        print("=" * 60)
        print("🔐 CERTIFICADO SSL")
        print("=" * 60)
        print(f"📄 Certificado: {cert_file}")
        print(f"🔑 Clave privada: {key_file}")
        print(f"👤 Subject: {cert_info['subject']}")
        print(f"📅 Válido hasta: {cert_info['not_valid_after']}")
        print(f"✅ Estado: {'Válido' if cert_info['is_valid'] else '⚠️ Vencido'}")
        print("=" * 60)
    
    # Iniciar servidor
    print(f"\n🚀 Iniciando servidor HTTPS en https://{args.host}:{args.port}")
    print("   Presiona Ctrl+C para detener\n")
    
    sys.argv = [
        'manage.py',
        'runserver_plus',
        '--cert-file', cert_file,
        '--key-file', key_file,
        f'{args.host}:{args.port}'
    ]
    
    try:
               execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("\n⛔ Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de tener instalado django-extensions:")
        print("   pip install django-extensions Werkzeug pyOpenSSL")
        sys.exit(1)


if __name__ == '__main__':
    main()