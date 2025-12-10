#!/bin/bash
# ========================================
# Generate Self-Signed SSL Certificates
# NUAM Project - HTTPS Configuration
# ========================================

echo "========================================="
echo "NUAM - SSL Certificate Generator"
echo "========================================="
echo ""

# Create certs directory if it doesn't exist
mkdir -p ./certs

# Certificate details
COUNTRY="CL"
STATE="Santiago"
CITY="Santiago"
ORGANIZATION="NUAM"
ORGANIZATIONAL_UNIT="IT"
COMMON_NAME="localhost"
EMAIL="admin@nuam.local"

echo "Generating self-signed SSL certificate..."
echo "Common Name: $COMMON_NAME"
echo ""

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./certs/nuam.key \
    -out ./certs/nuam.crt \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL" \
    -addext "subjectAltName=DNS:localhost,DNS:nuam.local,DNS:127.0.0.1,IP:127.0.0.1"

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSL certificate generated successfully!"
    echo ""
    echo "Certificate files created:"
    echo "  - Private Key: ./certs/nuam.key"
    echo "  - Certificate:  ./certs/nuam.crt"
    echo ""
    echo "Certificate details:"
    openssl x509 -in ./certs/nuam.crt -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:"
    echo ""
    echo "========================================="
    echo "IMPORTANT: Self-Signed Certificate Notes"
    echo "========================================="
    echo ""
    echo "1. This is a SELF-SIGNED certificate for DEVELOPMENT only"
    echo "2. Browsers will show a security warning (this is normal)"
    echo "3. For PRODUCTION, use a certificate from a trusted CA like:"
    echo "   - Let's Encrypt (free, automated)"
    echo "   - DigiCert, Comodo, etc. (paid)"
    echo ""
    echo "4. To trust this certificate in your browser:"
    echo "   - Chrome/Edge: Import ./certs/nuam.crt to Trusted Root Certificates"
    echo "   - Firefox: Import in Settings → Privacy & Security → Certificates"
    echo "   - macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ./certs/nuam.crt"
    echo ""
    echo "5. To access via HTTPS:"
    echo "   - https://localhost/"
    echo "   - Accept the security warning (if certificate not trusted)"
    echo ""
    echo "========================================="
else
    echo ""
    echo "✗ Error generating SSL certificate"
    echo "Please ensure OpenSSL is installed:"
    echo "  - macOS: brew install openssl"
    echo "  - Ubuntu: sudo apt-get install openssl"
    echo "  - Alpine: apk add openssl"
    exit 1
fi
