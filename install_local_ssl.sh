#!/bin/bash

echo "🔐 Generando certificado SSL para localhost…"

CERT_DIR="certs"
KEY_FILE="$CERT_DIR/key.pem"
CERT_FILE="$CERT_DIR/cert.pem"

mkdir -p $CERT_DIR

# Generar clave privada
openssl genrsa -out $KEY_FILE 2048

# Generar certificado autofirmado válido por 1 año
openssl req -new -x509 \
  -key $KEY_FILE \
  -out $CERT_FILE \
  -days 365 \
  -subj "/C=CL/ST=Santiago/L=RM/O=Nuam App/OU=Dev/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "📄 Certificado generado en $CERT_FILE"
echo "🔐 Instalando certificado en el llavero del sistema…"

# Instalar en el llavero del sistema con confianza total
sudo security add-trusted-cert \
  -d \
  -r trustRoot \
  -k /Library/Keychains/System.keychain \
  $CERT_FILE

echo "✅ Certificado instalado y confiado correctamente."
echo "👉 Ahora puedes ejecutar:"
echo "   python manage.py runserver_plus --cert-file certs/cert.pem --key-file certs/key.pem"
