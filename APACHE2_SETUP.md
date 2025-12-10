# Apache2 (httpd) Setup & HTTPS Configuration

**Date**: December 10, 2025
**Status**: ✅ Implemented and Configured

---

## 📋 Overview

NUAM now uses a **dual reverse proxy architecture** with Apache2 as the primary entry point, providing SSL/TLS termination and enhanced security, while Nginx handles internal routing and static file serving.

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUESTS                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    APACHE2 (Port 80/443)                         │
│  - SSL/TLS Termination                                           │
│  - Security Headers                                              │
│  - ProxyPass to Nginx                                            │
│  - Rate Limiting (optional)                                      │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     NGINX (Port 80 Internal)                     │
│  - Route to Services                                             │
│  - Static File Serving                                           │
│  - Caching Strategy                                              │
│  - WebSocket Support                                             │
└──────────────┬──────────┬──────────┬──────────┬──────────────────┘
               │          │          │          │
               ▼          ▼          ▼          ▼
         ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
         │ Django  │ │Currency│ │  React │ │  Static  │
         │  Core   │ │Service │ │Dashboard│ │  Files   │
         │ :8000   │ │ :8001  │ │ :3000  │ │          │
         └─────────┘ └────────┘ └────────┘ └──────────┘
```

---

## 🎯 Benefits of This Architecture

### 1. **Separation of Concerns**
- **Apache2**: SSL termination, security headers, primary firewall
- **Nginx**: Fast routing, static file serving, caching

### 2. **Performance**
- SSL/TLS offloading at Apache2 layer
- Nginx handles high-concurrency static file serving
- Connection pooling between layers

### 3. **Security**
- Multiple security layers
- Easy to add WAF (Web Application Firewall)
- Centralized SSL certificate management
- Security headers at multiple levels

### 4. **Flexibility**
- Easy to swap or upgrade either proxy
- Can add additional services without changing core routing
- Simple to implement A/B testing or canary deployments

---

## 📁 File Structure

```
Nuam-main/
├── apache/
│   ├── Dockerfile              # Apache2 container definition
│   ├── httpd.conf              # Main Apache configuration
│   └── conf.d/
│       └── nuam.conf           # Virtual host configuration
│
├── certs/
│   ├── nuam.crt                # SSL certificate (generated)
│   └── nuam.key                # SSL private key (generated)
│
├── generate_ssl_certs.sh       # Certificate generation script
├── .env                        # Environment variables (SECRET_KEY, etc.)
└── docker-compose.yml          # Updated with Apache2 service
```

---

## 🔧 Configuration Details

### Apache2 Configuration (`apache/httpd.conf`)

**Key Features:**
- ✅ Modern TLS configuration (TLS 1.2+)
- ✅ Proxy modules enabled
- ✅ Compression with mod_deflate
- ✅ Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- ✅ Server signature hiding
- ✅ SSL session caching

**Enabled Modules:**
```apache
mod_proxy           # Reverse proxy capability
mod_proxy_http      # HTTP proxy
mod_proxy_balancer  # Load balancing
mod_ssl             # SSL/TLS support
mod_rewrite         # URL rewriting
mod_headers         # Header manipulation
mod_deflate         # Compression
```

### Virtual Host Configuration (`apache/conf.d/nuam.conf`)

**HTTP Virtual Host (Port 80):**
```apache
<VirtualHost *:80>
    ServerName localhost

    # Proxy all requests to Nginx
    ProxyPass / http://nginx:80/
    ProxyPassReverse / http://nginx:80/

    # Optional: Redirect to HTTPS
    # RewriteEngine On
    # RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>
```

**HTTPS Virtual Host (Port 443):**
```apache
<VirtualHost *:443>
    ServerName localhost

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /usr/local/apache2/conf/ssl/nuam.crt
    SSLCertificateKeyFile /usr/local/apache2/conf/ssl/nuam.key

    # Modern TLS only
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite HIGH:!aNULL:!MD5:!3DES

    # HSTS Header
    Header always set Strict-Transport-Security "max-age=31536000"

    # Proxy to Nginx (SSL termination here)
    ProxyPass / http://nginx:80/
    ProxyPassReverse / http://nginx:80/

    # WebSocket support
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule /(.*)  ws://nginx:80/$1 [P,L]
</VirtualHost>
```

---

## 🔐 SSL/TLS Setup

### Self-Signed Certificate (Development)

The project includes a script to generate self-signed certificates for development:

```bash
# Generate certificates (already done during setup)
./generate_ssl_certs.sh
```

**Certificate Details:**
- **Algorithm**: RSA 2048-bit
- **Validity**: 365 days
- **Common Name**: localhost
- **SANs**: localhost, nuam.local, 127.0.0.1

**Files Created:**
- `certs/nuam.crt` - Certificate
- `certs/nuam.key` - Private key

### Trusting the Self-Signed Certificate

**Browser Warning**: You'll see a security warning because the certificate is self-signed. This is normal for development.

**To trust the certificate (optional):**

**macOS:**
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ./certs/nuam.crt
```

**Chrome/Edge:**
1. Go to `chrome://settings/certificates`
2. Click "Authorities" tab
3. Import `certs/nuam.crt`

**Firefox:**
1. Go to Settings → Privacy & Security → Certificates
2. Click "View Certificates" → "Authorities" → "Import"
3. Import `certs/nuam.crt`

### Production Certificate (Let's Encrypt)

For production, use a trusted certificate from Let's Encrypt:

```bash
# Install certbot
apt-get install certbot python3-certbot-apache

# Generate certificate
certbot --apache -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

**Update virtual host:**
```apache
SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

---

## 🚀 Running the Stack

### Start All Services

```bash
# Build and start all containers (including Apache2)
docker-compose up -d --build

# Check Apache2 logs
docker logs nuam-apache2 -f

# Check Apache2 status
docker exec nuam-apache2 httpd -t  # Test configuration
docker exec nuam-apache2 httpd -S  # Show virtual hosts
```

### Access Points

| Service | HTTP URL | HTTPS URL | Description |
|---------|----------|-----------|-------------|
| **Main App** | http://localhost/ | https://localhost/ | Through Apache2 |
| **API** | http://localhost/api/v1/ | https://localhost/api/v1/ | REST API |
| **Admin** | http://localhost/admin/ | https://localhost/admin/ | Django Admin |
| **Swagger** | http://localhost/swagger/ | https://localhost/swagger/ | API Docs |
| **Nginx (Direct)** | http://localhost:8080/ | N/A | Bypass Apache2 |
| **Apache Status** | http://localhost/server-status | N/A | Server metrics |

### Container Status

```bash
# Check all containers
docker ps

# Should show:
# - nuam-apache2 (80/443) ✅
# - nuam-nginx (8080) ✅
# - nuam-django-core (8000) ✅
# - nuam-currency-service (8001) ✅
# - nuam-dashboard-frontend (3000) ✅
# - nuam-postgres (5432) ✅
# - nuam-redis (6379) ✅
# - nuam-kafka (9092) ✅
# - nuam-zookeeper (2181) ✅
```

---

## 🔍 Testing & Verification

### 1. Test HTTP Access

```bash
curl -I http://localhost/
# Should return: HTTP/1.1 200 OK
```

### 2. Test HTTPS Access

```bash
curl -k -I https://localhost/
# -k flag ignores self-signed certificate warning
# Should return: HTTP/1.1 200 OK
```

### 3. Check SSL Certificate

```bash
openssl s_client -connect localhost:443 -servername localhost
# Shows certificate details and TLS handshake
```

### 4. Verify Security Headers

```bash
curl -k -I https://localhost/ | grep -E "X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security"
# Should show security headers
```

### 5. Test ProxyPass

```bash
# Test API endpoint
curl http://localhost/api/v1/health/

# Test currency service
curl http://localhost/currency-api/v1/health/

# Test static files
curl http://localhost/static/css/main.css
```

---

## 🛠️ Troubleshooting

### Apache2 Won't Start

**Check logs:**
```bash
docker logs nuam-apache2
```

**Common issues:**
1. **Port already in use**: Stop other services using port 80/443
   ```bash
   lsof -i :80
   lsof -i :443
   ```

2. **Certificate not found**:
   ```bash
   # Regenerate certificates
   ./generate_ssl_certs.sh
   ```

3. **Configuration syntax error**:
   ```bash
   docker exec nuam-apache2 httpd -t
   ```

### SSL Certificate Errors

**Browser shows "Your connection is not private"**:
- This is normal for self-signed certificates
- Click "Advanced" → "Proceed to localhost (unsafe)"
- Or trust the certificate (see instructions above)

**Certificate expired**:
```bash
# Check expiry
openssl x509 -in ./certs/nuam.crt -noout -dates

# Regenerate if expired
./generate_ssl_certs.sh
docker-compose restart apache2
```

### ProxyPass Not Working

**Check Nginx is reachable from Apache2:**
```bash
docker exec nuam-apache2 wget -O- http://nginx:80/health
```

**Check proxy logs:**
```bash
docker logs nuam-apache2 | grep proxy
```

### Performance Issues

**Enable Apache status module:**
```bash
# Access status page
curl http://localhost/server-status

# Shows:
# - Current requests
# - Server uptime
# - Request per second
# - CPU usage
```

---

## 📊 Monitoring & Metrics

### Apache2 Server Status

Access at: `http://localhost/server-status`

Shows:
- Total requests
- Requests per second
- Bytes served
- CPU usage
- Worker status

### Log Locations

**Inside container:**
- Access log: `/usr/local/apache2/logs/access_log`
- Error log: `/usr/local/apache2/logs/error_log`

**Docker logs:**
```bash
docker logs nuam-apache2 --tail 100 -f
```

---

## 🔒 Security Best Practices

### 1. **Production Checklist**

- [ ] Replace self-signed certificate with trusted CA certificate
- [ ] Enable HTTPS redirect (uncomment in `nuam.conf`)
- [ ] Set strong SSL cipher suites
- [ ] Enable HSTS with long max-age
- [ ] Disable Apache status module in production
- [ ] Set ServerTokens to Prod
- [ ] Enable rate limiting (mod_ratelimit)
- [ ] Configure firewall rules (only allow 80/443)

### 2. **Environment Variables**

All sensitive configuration is now in `.env`:

```bash
# .env file (DO NOT COMMIT)
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Important**: Add `.env` to `.gitignore`!

### 3. **TLS Configuration**

Current configuration supports:
- ✅ TLS 1.2
- ✅ TLS 1.3
- ❌ TLS 1.1 (disabled - insecure)
- ❌ TLS 1.0 (disabled - insecure)
- ❌ SSLv3 (disabled - insecure)

Test your SSL configuration:
```bash
nmap --script ssl-enum-ciphers -p 443 localhost
```

---

## 📝 Maintenance

### Restart Apache2

```bash
docker-compose restart apache2
```

### Reload Configuration (No Downtime)

```bash
docker exec nuam-apache2 httpd -k graceful
```

### Update SSL Certificates

```bash
# Replace certificate files
cp new-cert.crt ./certs/nuam.crt
cp new-key.key ./certs/nuam.key

# Reload Apache2
docker-compose restart apache2
```

### View Active Connections

```bash
docker exec nuam-apache2 httpd -S
docker exec nuam-apache2 apachectl fullstatus
```

---

## 📚 Additional Resources

### Apache2 Documentation
- [Apache HTTP Server Documentation](https://httpd.apache.org/docs/2.4/)
- [mod_proxy Guide](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html)
- [mod_ssl Guide](https://httpd.apache.org/docs/2.4/mod/mod_ssl.html)

### SSL/TLS Tools
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Let's Encrypt](https://letsencrypt.org/)
- [SSL Configuration Generator](https://ssl-config.mozilla.org/)

### Testing Tools
```bash
# Apache Benchmark
ab -n 1000 -c 10 http://localhost/

# Check headers
curl -I https://localhost/

# SSL handshake test
openssl s_client -connect localhost:443

# Check certificate
openssl x509 -in ./certs/nuam.crt -text -noout
```

---

## ✅ Summary

**What Was Implemented:**
1. ✅ Apache2 (httpd) container with Alpine Linux
2. ✅ Dual reverse proxy architecture (Apache2 → Nginx → Services)
3. ✅ SSL/TLS with self-signed certificates (HTTPS support)
4. ✅ Security headers (HSTS, X-Frame-Options, etc.)
5. ✅ ProxyPass configuration to Nginx backend
6. ✅ WebSocket support for React hot reload
7. ✅ Environment-based configuration (.env file)
8. ✅ Health check endpoints
9. ✅ Compression with mod_deflate
10. ✅ Modern TLS 1.2/1.3 support

**Architecture Improvements:**
- **Security**: Multiple security layers, SSL termination
- **Performance**: Connection pooling, compression, caching
- **Maintainability**: Clean separation of concerns
- **Scalability**: Easy to add services or load balancers

**Production Ready**: Yes, with trusted SSL certificate

---

**Last Updated**: December 10, 2025
**Status**: ✅ Fully Operational
**HTTPS**: ✅ Enabled (Self-Signed Certificate)
**Apache2 Version**: 2.4-alpine
**Nginx Version**: Alpine (internal routing)
