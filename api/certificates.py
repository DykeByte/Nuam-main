import os
import logging
from datetime import datetime, timedelta, timezone as tz

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import json
from typing import Optional, Literal

logger = logging.getLogger(__name__)


class CertificateManager:
    def __init__(self, base_dir="certs"):
        self.base_dir = base_dir
        self.key_file = os.path.join(base_dir, "key.pem")
        self.cert_file = os.path.join(base_dir, "cert.pem")

        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)

    # =========================================================
    def certificate_exists(self):
        return os.path.exists(self.key_file) and os.path.exists(self.cert_file)

    # =========================================================
    def create_self_signed_cert(self):
        try:
            logger.info("🔐 Generando nuevo certificado autofirmado...")

            # Generar clave privada
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            # Guardar clave privada
            with open(self.key_file, "wb") as f:
                f.write(
                    key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"CL"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Santiago"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"RM"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Nuam App"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])

            valid_from = datetime.now(tz.utc)
            valid_to = valid_from + timedelta(days=365)

            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(valid_from)
                .not_valid_after(valid_to)
                .add_extension(
                    x509.SubjectAlternativeName([
                        x509.DNSName(u"localhost"),
                        x509.DNSName(u"127.0.0.1"),
                    ]),
                    critical=False,
                )
                .sign(key, hashes.SHA256(), default_backend())
            )

            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            logger.info("✅ Certificado generado correctamente.")

        except Exception as e:
            logger.error(f"❌ Error generando certificado: {e}")

    # =========================================================
    def get_certificate_info(self):
        if not self.certificate_exists():
            return None

        try:
            with open(self.cert_file, "rb") as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())

            # cryptography pide usar *_utc
            not_valid_before = cert.not_valid_before_utc
            not_valid_after = cert.not_valid_after_utc

            now = datetime.now(tz.utc)

            return {
                "subject": cert.subject.rfc4514_string(),
                "issuer": cert.issuer.rfc4514_string(),
                "not_valid_before": not_valid_before,
                "not_valid_after": not_valid_after,
                "serial_number": cert.serial_number,
                "is_valid": now < not_valid_after,
            }

        except Exception as e:
            logger.error(f"Error leyendo certificado: {e}")
            return None

    # =========================================================
    def ensure_certificate(self):
        """
        Devuelve siempre (cert_file, key_file)
        """
        info = None

        if self.certificate_exists():
            info = self.get_certificate_info()
            if info and info["is_valid"]:
                logger.info("🔏 Certificado válido encontrado.")
                return self.cert_file, self.key_file

            logger.warning("⚠️ Certificado vencido o inválido. Regenerando...")

        # Regenerar
        self.create_self_signed_cert()

        # Retornar rutas correctas
        return self.cert_file, self.key_file

    def export_certificate_info(self, output_format: Literal['json', 'text', 'dict'] = 'json') -> str:
        """
        Exporta información del certificado en diferentes formatos
        
        Args:
            output_format: Formato de salida ('json', 'text', 'dict')
        
        Returns:
            str: Información formateada
        
        Example:
            >>> manager = CertificateManager()
            >>> info_json = manager.export_certificate_info('json')
            >>> print(info_json)
        """
        info = self.get_certificate_info()
        
        if not info:
            return "No hay certificado disponible"
        
        if output_format == 'json':
            return json.dumps({
                'subject': info['subject'],
                'issuer': info['issuer'],
                'valid_from': info['not_valid_before'].isoformat(),
                'valid_until': info['not_valid_after'].isoformat(),
                'serial_number': str(info['serial_number']),
                'is_valid': info['is_valid'],
                'files': {
                    'certificate': self.cert_file,
                    'key': self.key_file
                }
            }, indent=2, default=str)
        
        elif output_format == 'text':
            status_icon = '✅' if info['is_valid'] else '❌'
            return f"""
        ╔════════════════════════════════════════════════════════════╗
        ║              CERTIFICADO SSL - NUAM                        ║
        ╚════════════════════════════════════════════════════════════╝

        📄 Archivos:
            Certificado: {self.cert_file}
            Clave:       {self.key_file}

        👤 Subject:
        {info['subject']}

🏢 Issuer:
   {info['issuer']}

📅 Validez:
   Desde: {info['not_valid_before']}
   Hasta: {info['not_valid_after']}

🔢 Serial:
   {info['serial_number']}

{status_icon} Estado:
   {'VÁLIDO' if info['is_valid'] else 'VENCIDO'}

{'─' * 60}
"""
        
        elif output_format == 'dict':
            return info
        
        else:
            raise ValueError(f"Formato no soportado: {output_format}")
    
    def get_days_until_expiry(self) -> Optional[int]:
        """
        Calcula días hasta que expire el certificado
        
        Returns:
            int: Días hasta expiración (negativo si ya expiró)
            None: Si no hay certificado
        """
        info = self.get_certificate_info()
        if not info:
            return None
        
        from datetime import datetime, timezone as tz
        now = datetime.now(tz.utc)
        delta = info['not_valid_after'] - now
        return delta.days
    
    def needs_renewal(self, days_threshold: int = 30) -> bool:
        """
        Verifica si el certificado necesita renovación
        
        Args:
            days_threshold: Días antes de expiración para renovar (default: 30)
        
        Returns:
            bool: True si necesita renovación
        """
        days_left = self.get_days_until_expiry()
        if days_left is None:
            return True
        return days_left <= days_threshold