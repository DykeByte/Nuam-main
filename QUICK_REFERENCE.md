# NUAM - Quick Reference Guide

## 🏗️ Architecture
```
Client → Apache2 (80/443) → Nginx (8080) → Services
         SSL Termination     Routing        Django/FastAPI/React
```

## 🚀 URLs (Through Apache2 → Nginx)

### HTTP Access
| Service | URL | Description |
|---------|-----|-------------|
| **React Dashboard** | http://localhost/ | Modern React SPA for monitoring |
| **Django Home** | http://localhost/accounts/home/ | Django template dashboard |
| **Login** | http://localhost/accounts/login/ | User authentication |
| **Django Admin** | http://localhost/admin/ | Django admin panel |
| **API** | http://localhost/api/v1/ | REST API endpoints |
| **Swagger Docs** | http://localhost/swagger/ | API documentation |
| **Currency API** | http://localhost/currency-api/v1/ | Currency service API |
| **Kafka Dashboard** | http://localhost/kafka/dashboard/ | Kafka monitoring |
| **Static Files** | http://localhost/static/ | CSS, JS, images |

### HTTPS Access (Self-Signed Certificate)
| Service | URL | Notes |
|---------|-----|-------|
| **React Dashboard** | https://localhost/ | Will show security warning |
| **Django Home** | https://localhost/accounts/home/ | Accept certificate in browser |
| **API** | https://localhost/api/v1/ | Use `-k` flag with curl |
| **Admin** | https://localhost/admin/ | Encrypted connection |

### Direct Access (Bypassing Apache2)
| Service | URL | Purpose |
|---------|-----|---------|
| **Nginx** | http://localhost:8080/ | Direct nginx access |
| **Django** | http://localhost:8000/ | Development/debugging |
| **Currency Service** | http://localhost:8001/ | Direct service access |

## 🐳 Docker Commands

```bash
# Start all services (including Apache2)
docker-compose up -d --build

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart django-core
docker-compose restart nginx
docker-compose restart apache2

# View logs
docker logs nuam-django-core --tail 50 -f
docker logs nuam-nginx --tail 50 -f
docker logs nuam-apache2 --tail 50 -f

# Check container status
docker ps --filter "name=nuam"

# Execute commands in container
docker exec nuam-django-core python manage.py shell
docker exec nuam-postgres psql -U nuam_user -d nuam_db
```

## 🔒 Apache2 Specific Commands

```bash
# Test Apache2 configuration
docker exec nuam-apache2 httpd -t

# Show virtual hosts
docker exec nuam-apache2 httpd -S

# Reload Apache2 (graceful restart)
docker exec nuam-apache2 httpd -k graceful

# Check Apache2 modules
docker exec nuam-apache2 httpd -M | grep proxy

# View Apache2 status
curl http://localhost/server-status

# Test HTTPS connection
curl -k -I https://localhost/

# Check SSL certificate
openssl s_client -connect localhost:443 -servername localhost

# View SSL certificate details
openssl x509 -in ./certs/nuam.crt -text -noout
```

## 📦 Static Files Workflow

```bash
# After modifying CSS/JS files
docker exec nuam-django-core python manage.py collectstatic --noinput

# Restart nginx (optional)
docker-compose restart nginx

# Hard refresh browser
# Mac: Cmd + Shift + R
# Windows: Ctrl + Shift + R
```

## 🗂️ File Locations

```
# Frontend
accounts/static/css/main.css              # Main stylesheet
accounts/static/js/main.js                # Core JavaScript
accounts/static/js/currency-converter.js  # Currency widget
accounts/templates/base.html              # Base template
accounts/templates/home.html              # Dashboard page

# Apache2 Configuration
apache/Dockerfile                         # Apache2 container
apache/httpd.conf                         # Main Apache config
apache/conf.d/nuam.conf                   # Virtual host config

# Nginx Configuration
nginx/nginx.conf                          # Main Nginx config
nginx/conf.d/nuam.conf                    # Nginx routing config

# Security & Environment
.env                                      # Environment variables (DO NOT COMMIT!)
certs/nuam.crt                            # SSL certificate
certs/nuam.key                            # SSL private key
generate_ssl_certs.sh                     # Certificate generator

# Django
nuam/settings.py                          # Django settings
staticfiles/                              # Collected static files (auto-generated)

# Documentation
APACHE2_SETUP.md                          # Apache2 implementation guide
README.md                                 # Main documentation
CHANGELOG.md                              # Version history
QUICK_REFERENCE.md                        # This file
```

## 🔧 Common Tasks

### Create Django superuser
```bash
docker exec -it nuam-django-core python manage.py createsuperuser
```

### Run migrations
```bash
docker exec nuam-django-core python manage.py migrate
```

### Access Django shell
```bash
docker exec -it nuam-django-core python manage.py shell
```

### Access PostgreSQL
```bash
docker exec -it nuam-postgres psql -U nuam_user -d nuam_db
```

### Check Django logs
```bash
docker exec nuam-django-core tail -f /app/logs/django.log
```

## 🎨 Adding Custom Styles

### Option 1: Modify main.css
```bash
# Edit the file
nano accounts/static/css/main.css

# Collect static files
docker exec nuam-django-core python manage.py collectstatic --noinput
```

### Option 2: Page-specific styles
```django
{% block extra_css %}
<style>
    .my-custom-class {
        color: #667eea;
    }
</style>
{% endblock %}
```

## 📝 Adding Custom JavaScript

### Option 1: Modify main.js
```bash
# Edit the file
nano accounts/static/js/main.js

# Collect static files
docker exec nuam-django-core python manage.py collectstatic --noinput
```

### Option 2: Page-specific scripts
```django
{% block extra_js %}
<script src="{% static 'js/my-script.js' %}"></script>
{% endblock %}
```

## 🔍 Debugging

### Check if static files are accessible
```bash
curl http://localhost/static/css/main.css
curl http://localhost/static/js/main.js
```

### Verify nginx can access staticfiles
```bash
docker exec nuam-nginx ls -la /var/www/static/
```

### Test API endpoints
```bash
# Django API
curl http://localhost/api/v1/health/

# Currency API
curl http://localhost/currency-api/v1/dashboard/summary
```

### Browser Developer Tools
- **Chrome/Edge**: Press F12
- **Firefox**: Press F12
- **Console Tab**: Check for JavaScript errors
- **Network Tab**: Monitor API calls and static file loading

## 📊 Health Checks

```bash
# Overall health
curl http://localhost/health

# Django health
curl http://localhost/api/v1/health/

# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 🔑 Environment Variables

Located in `docker-compose.yml`:

```yaml
# Django
DATABASE_NAME: nuam_db
DATABASE_USER: nuam_user
DATABASE_PASSWORD: nuam_password
DATABASE_HOST: postgres
KAFKA_BOOTSTRAP_SERVERS: kafka:29092

# Currency Service
CURRENCY_SERVICE_URL: http://currency-service:8001
```

## 🌐 API Examples

### Get currency rate
```bash
curl "http://localhost/api/v1/divisas/tasa-ajax/?from=USD&to=CLP"
```

### Get dashboard stats
```bash
curl "http://localhost/api/v1/dashboard/stats/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Login (get JWT token)
```bash
curl -X POST "http://localhost/api/v1/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Apache2 won't start** | Check logs: `docker logs nuam-apache2`<br>Test config: `docker exec nuam-apache2 httpd -t` |
| **SSL certificate error** | Browser security warning is normal for self-signed cert<br>Click "Advanced" → "Proceed to localhost" |
| **Certificate expired** | Regenerate: `./generate_ssl_certs.sh && docker-compose restart apache2` |
| **502 Bad Gateway** | Check if services are up: `docker ps`<br>Restart: `docker-compose restart apache2 nginx django-core` |
| **Static files not loading** | Run `collectstatic`, restart services, hard refresh browser |
| **Database connection error** | Check postgres: `docker logs nuam-postgres` |
| **CSS changes not showing** | Hard refresh browser (Cmd+Shift+R) or clear cache |
| **API not responding** | Check logs: `docker logs nuam-django-core` |
| **HTTPS not working** | Verify certificate exists: `ls -la certs/`<br>Check Apache logs: `docker logs nuam-apache2` |
| **Port 80/443 in use** | Find process: `lsof -i :80` or `lsof -i :443`<br>Stop conflicting service |

## 📚 Additional Resources

- **Apache HTTP Server**: https://httpd.apache.org/docs/2.4/
- **Django Docs**: https://docs.djangoproject.com/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **SSL/TLS Testing**: https://www.ssllabs.com/ssltest/
- **Project Documentation**:
  - `APACHE2_SETUP.md` - Apache2 implementation guide
  - `README.md` - Main documentation
  - `CHANGELOG.md` - Version history
  - `PROJECT_STRUCTURE.md` - Project organization

## 🎯 Quick Start Checklist

- [ ] All containers running: `docker ps --filter "name=nuam"`
  ```
  Should show 9 containers:
  - nuam-apache2 (HEALTHY)
  - nuam-nginx (HEALTHY)
  - nuam-django-core (HEALTHY)
  - nuam-currency-service (HEALTHY)
  - nuam-dashboard-frontend (Running)
  - nuam-kafka-consumer (Running)
  - nuam-postgres (HEALTHY)
  - nuam-redis (HEALTHY)
  - nuam-kafka (HEALTHY)
  - nuam-zookeeper (HEALTHY)
  ```
- [ ] Apache2 configuration valid: `docker exec nuam-apache2 httpd -t`
- [ ] Static files collected: `docker exec nuam-django-core python manage.py collectstatic --noinput`
- [ ] Can access login page: http://localhost/accounts/login/
- [ ] HTTPS working (with warning): https://localhost/
- [ ] Static files loading: Check browser Network tab
- [ ] APIs responding: `curl http://localhost/api/v1/health/`
- [ ] Dashboard visible: http://localhost/
- [ ] SSL certificate valid: `openssl x509 -in ./certs/nuam.crt -noout -dates`

## 🔐 Security Checklist

- [ ] `.env` file exists and has `SECRET_KEY` set
- [ ] `.env` is in `.gitignore` (DO NOT COMMIT SECRETS!)
- [ ] SSL certificates generated: `ls -la certs/`
- [ ] HTTPS accessible (even with self-signed warning)
- [ ] For production: Replace self-signed cert with trusted CA certificate
- [ ] For production: Set `DEBUG=False` in `.env`
- [ ] For production: Update `ALLOWED_HOSTS` in `.env`

---

**Need help?**
- Apache2 logs: `docker logs nuam-apache2 --tail 50`
- Django logs: `docker logs nuam-django-core --tail 50`
- Full documentation: See `APACHE2_SETUP.md`
