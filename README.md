# NUAM - Sistema de Gestión de Calificaciones Tributarias

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.8-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Sistema empresarial de gestión de calificaciones tributarias de instrumentos financieros con arquitectura de microservicios, procesamiento asíncrono con Kafka, frontend moderno y seguridad SSL/TLS.**

---

## 🆕 **ACTUALIZACIONES RECIENTES (Diciembre 2024)**

### ✨ **Versión 2.1.0 - Nueva Actualización**

#### **1. Sistema Avanzado de Búsqueda y Filtros** 🔍
- **Búsqueda rápida**: Búsqueda instantánea por corredor, instrumento, mercado o descripción
- **Filtros avanzados**: Filtrado por mercado, divisa, rango de fechas
- **Ordenamiento dinámico**: Click en columnas para ordenar (ID, fecha pago, valor, fecha creación)
- **Paginación inteligente**: 10, 25, 50, 100 resultados por página
- **Preservación de estado**: Filtros y ordenamiento se mantienen entre páginas
- **Interfaz colapsable**: Filtros avanzados se expanden solo cuando se usan

#### **2. Barra de Progreso en Tiempo Real** ⏳
- **Progreso visual**: Barra animada 0-100% durante la carga
- **Actualización en tiempo real**: Polling cada 2 segundos vía AJAX
- **Estadísticas en vivo**: Procesados, Exitosos, Fallidos actualizados en tiempo real
- **Cronómetro integrado**: Tiempo transcurrido del proceso
- **Auto-reload**: Recarga automática al completar el proceso
- **Modal flotante**: Overlay que bloquea interacción hasta completar

#### **3. Reporte Detallado de Errores** ⚠️
- **Tabla de errores**: Información estructurada de cada fallo
- **Fila exacta**: Número de fila de Excel donde ocurrió el error
- **Campo específico**: Campo que causó el error
- **Valor recibido**: Dato que generó el problema
- **Sugerencias inteligentes**: Recomendaciones específicas para corregir
- **Color coding**: Errores resaltados visualmente
- **Exportable**: Información lista para corrección en Excel

#### **4. Apache2 como Reverse Proxy Principal** 🔐
- **Arquitectura dual-layer**: Apache2 (80/443) → Nginx (8080) → Microservices
- **SSL/TLS configurado**: Soporte HTTPS con certificados autofirmados
- **Protocolos modernos**: TLS 1.2 y 1.3, SSLv3/TLS1.0/1.1 deshabilitados
- **ProxyPass configurado**: Redirección transparente a Nginx
- **Configuración segura**: Cipher suites modernos, headers de seguridad

#### **5. Frontend Profesional Modernizado** 🎨
- **CSS renovado**: 310 → 770 líneas (+148% de código profesional)
- **8 animaciones CSS**: fadeIn, scaleUp, pulse, shimmer, float, spin, etc.
- **Glassmorphism**: Efectos de vidrio esmerilado con backdrop-filter
- **Gradientes profesionales**: Texto y fondos con gradientes modernos
- **Tipografía mejorada**: Sistema de jerarquía profesional
- **Responsive design**: Mobile-first, optimizado para todos los dispositivos

#### **6. Dashboard Interactivo con Gráficos** 📊
- **React Dashboard**: Frontend moderno con Vite + Tailwind CSS
- **Gráficos en tiempo real**: Recharts con AreaChart, LineChart, BarChart
- **Divisas soportadas**: CLP, COP, PEN (SOL), MXN, EUR, UF
- **Estadísticas 30d**: Promedio, máximo, mínimo, cambio porcentual
- **Auto-refresh**: Actualización automática cada 5 minutos
- **Comparación de monedas**: Gráficos comparativos interactivos

#### **7. Microservicio de Divisas** 💱
- **FastAPI Currency Service**: Servicio independiente en puerto 8001
- **Histórico de tasas**: Almacenamiento en PostgreSQL
- **UF Chilena**: Integración con API CMF (Comisión para el Mercado Financiero)
- **ExchangeRate-API**: 160+ divisas en tiempo real
- **Endpoints RESTful**: Tasas actuales, históricos, conversión, estadísticas
- **Widget interactivo**: Conversor en tiempo real en el dashboard

---

## 📋 **TABLA DE CONTENIDOS**

1. [Características Principales](#características-principales)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Instalación Rápida](#instalación-rápida)
5. [Acceso a Servicios](#acceso-a-servicios)
6. [API REST - Ejemplos](#api-rest---ejemplos)
7. [Sistema de Logging](#sistema-de-logging-avanzado)
8. [Optimizaciones de Performance](#optimizaciones-de-performance)
9. [Comandos Útiles](#comandos-útiles)
10. [Deployment](#deployment-producción)
11. [Licencia](#licencia-y-contacto)

---

## 🚀 **CARACTERÍSTICAS PRINCIPALES**

### **Core Features**
- ✅ **CRUD completo** de calificaciones tributarias
- ✅ **Cargas masivas** desde archivos Excel (hasta 10,000 registros)
- ✅ **Progreso en tiempo real** con barra de progreso y estadísticas en vivo
- ✅ **Reporte de errores detallado** con sugerencias de corrección
- ✅ **Multi-divisa**: USD, CLP, COP, PEN, EUR, MXN, BRL, ARS + UF chilena
- ✅ **API REST** con autenticación JWT y Swagger documentation
- ✅ **Procesamiento asíncrono** con Apache Kafka
- ✅ **Dashboard en tiempo real** con estadísticas y gráficos
- ✅ **Auditoría completa** de operaciones con logging avanzado
- ✅ **SSL/TLS** con HTTPS configurado

### **Advanced Features**
- 🔍 **Búsqueda y filtros avanzados**: Búsqueda rápida, filtros por mercado/divisa/fecha, ordenamiento
- 📄 **Paginación inteligente**: 10-100 resultados por página con preservación de estado
- 🔐 **Dual reverse proxy**: Apache2 + Nginx para máxima seguridad
- 📊 **React Dashboard**: Gráficos interactivos con Recharts
- 💱 **Currency Service**: Microservicio FastAPI para tasas de cambio
- 🎨 **Frontend moderno**: Glassmorphism, gradientes, animaciones CSS
- ⚡ **Performance optimizada**: ORM optimizations, 7 database indexes, caching
- 📈 **Históricos de divisas**: Almacenamiento y visualización de tendencias
- 🇨🇱 **UF Chilena**: Integración directa con API CMF oficial
- 🔄 **Auto-refresh**: Actualización automática de datos en dashboard

---

## 🛠️ **STACK TECNOLÓGICO**

### **Backend**
- **Django 5.2.8** - Framework principal
- **Django REST Framework 3.16.1** - API REST
- **PostgreSQL 15** - Base de datos principal
- **FastAPI** - Microservicio de divisas
- **Apache Kafka 3.5 + Zookeeper** - Mensajería asíncrona
- **Redis 7** - Cache layer

### **Frontend**
- **React 18 + Vite** - Dashboard moderno
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Biblioteca de gráficos
- **Bootstrap 5** - Framework CSS (Django templates)
- **jQuery** - Interactividad (Django templates)
- **Glassmorphism + CSS Animations** - UI moderna

### **Reverse Proxy & Security**
- **Apache2 (httpd 2.4)** - Reverse proxy principal, SSL termination
- **Nginx Alpine** - Routing interno, serving estáticos
- **SSL/TLS** - HTTPS con certificados autofirmados
- **JWT Authentication** - Autenticación segura
- **CSRF Protection** - Protección contra ataques

### **DevOps**
- **Docker + Docker Compose** - Containerización
- **Prometheus Metrics** - Monitoreo (preparado)
- **Multi-stage logging** - 7 archivos de log rotatorios

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET / USER                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Apache2 (Ports 80/443)     │  ← SSL Termination
        │   - HTTPS/SSL Certificates    │
        │   - ProxyPass Configuration   │
        │   - Security Headers          │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │    Nginx (Port 8080)         │  ← Internal Routing
        │   - Static Files Serving     │
        │   - Load Balancing           │
        └──────────────┬─────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌────────────────┐          ┌──────────────────┐
│  Django Core   │          │ Currency Service │
│  (Port 8000)   │◄────────►│   (Port 8001)    │
│  - API REST    │          │   - FastAPI      │
│  - Templates   │          │   - Forex Data   │
│  - Admin       │          │   - UF Chilena   │
└───────┬────────┘          └────────┬─────────┘
        │                            │
        ▼                            ▼
┌────────────────┐          ┌──────────────────┐
│   PostgreSQL   │          │  React Dashboard │
│   (Port 5432)  │          │   (Port 3000)    │
│  - Main DB     │          │  - Charts        │
│  - Historical  │          │  - Real-time     │
└────────────────┘          └──────────────────┘
        │
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
┌─────────────┐  ┌─────────┐  ┌──────────────┐
│    Kafka    │  │  Redis  │  │ Kafka        │
│ (Port 9092) │  │ (6379)  │  │ Consumer     │
│ + Zookeeper │  │ Cache   │  │              │
└─────────────┘  └─────────┘  └──────────────┘
```

---

## ⚡ **INSTALACIÓN RÁPIDA**

### **Opción 1: Docker (Recomendado)**

```bash
# 1. Clonar repositorio
git clone https://github.com/DykeByte/Nuam-main.git
cd Nuam-main

# 2. Generar certificados SSL
bash generate_ssl_certs.sh

# 3. Configurar variables de entorno (.env ya incluido)
# Opcionalmente, editar .env con tus valores

# 4. Levantar todos los servicios
docker-compose up -d

# 5. Crear superusuario
docker exec -it nuam-django-core python manage.py createsuperuser

# 6. Acceder a la aplicación
# HTTP:  http://localhost/accounts/login/
# HTTPS: https://localhost/accounts/login/
```

### **Opción 2: Instalación Local**

```bash
# 1. Clonar repositorio
git clone https://github.com/DykeByte/Nuam-main.git
cd Nuam-main

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables (.env)
cp .env.example .env
# Editar .env con tus valores

# 5. Levantar servicios de infraestructura (Docker)
docker-compose up -d postgres redis kafka zookeeper

# 6. Configurar base de datos
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 7. Iniciar servicios
# Terminal 1:
python manage.py runserver

# Terminal 2:
python manage.py run_kafka_consumers
```

**Ver `USER_MANUAL.md` para instrucciones paso a paso detalladas.**

---

## 🌐 **ACCESO A SERVICIOS**

### **Arquitectura de Red**
```
Apache2 (80/443) → Nginx (8080) → Services (8000, 8001, 3000)
```

### **Acceso HTTP (Desarrollo)**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **React Dashboard** | http://localhost/ | Dashboard principal con gráficos |
| **Django Home** | http://localhost/accounts/home/ | Panel de control Django |
| **Admin Django** | http://localhost/admin/ | Administración Django |
| **API REST** | http://localhost/api/v1/ | API REST con Swagger |
| **Currency API** | http://localhost/currency-api/v1/ | Microservicio de divisas |
| **Swagger Docs** | http://localhost/swagger/ | Documentación API interactiva |
| **Kafka Dashboard** | http://localhost/kafka/dashboard/ | Monitoreo de Kafka |

### **Acceso HTTPS (Seguro)**

| Servicio | URL | Nota |
|----------|-----|------|
| **React Dashboard** | https://localhost/ | Certificado autofirmado |
| **Django Home** | https://localhost/accounts/home/ | Aceptar advertencia SSL |
| **Admin Django** | https://localhost/admin/ | Usar credenciales superuser |
| **API REST** | https://localhost/api/v1/ | Bearer token requerido |

⚠️ **Nota HTTPS**: El navegador mostrará advertencia de seguridad (certificado autofirmado). Esto es normal en desarrollo. Ver `APACHE2_SETUP.md` para configuración en producción.

### **Acceso Directo (Bypass Apache2)**

| Servicio | URL | Uso |
|----------|-----|-----|
| **Nginx** | http://localhost:8080/ | Testing routing |
| **Django Core** | http://localhost:8000/ | Direct Django access |
| **Currency Service** | http://localhost:8001/ | Direct FastAPI access |
| **React App** | http://localhost:3000/ | Development server |

---

## 📡 **API REST - EJEMPLOS**

### **Autenticación JWT**

```bash
# Obtener token
curl -X POST http://localhost/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu_password"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **Calificaciones Tributarias**

```bash
# Listar calificaciones (requiere token)
curl http://localhost/api/v1/calificaciones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Crear calificación
curl -X POST http://localhost/api/v1/calificaciones/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "corredor_dueno": "Corredor ABC",
    "instrumento": "BONOS-2025",
    "mercado": "LOCAL",
    "divisa": "CLP",
    "valor_historico": 1500000.00,
    "fecha_pago": "2025-12-31"
  }'

# Filtrar y buscar
curl "http://localhost/api/v1/calificaciones/?mercado=LOCAL&divisa=CLP"
curl "http://localhost/api/v1/calificaciones/?search=BONOS"
curl "http://localhost/api/v1/calificaciones/?ordering=-created_at"
curl "http://localhost/api/v1/calificaciones/?page=2&page_size=50"
```

### **Carga Masiva Excel**

```bash
curl -X POST http://localhost/api/v1/cargas/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "archivo=@datos.xlsx" \
  -F "tipo_carga=FACTORES" \
  -F "mercado=LOCAL"
```

### **Conversión de Divisas**

```bash
# Obtener tasa de cambio
curl "http://localhost/api/v1/divisas/tasa/?from=USD&to=CLP"

# Response:
{
  "success": true,
  "from_currency": "USD",
  "to_currency": "CLP",
  "rate": "924.86",
  "timestamp": "2025-12-09T22:31:04Z"
}

# Convertir monto
curl -X POST http://localhost/api/v1/divisas/convertir/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100.00",
    "from_currency": "USD",
    "to_currency": "CLP"
  }'

# Response:
{
  "success": true,
  "amount": "100.00",
  "converted_amount": "92486.00",
  "rate": "924.86"
}

# Obtener todas las tasas
curl "http://localhost/api/v1/divisas/tasas/?base=USD"
```

### **Currency Service (FastAPI)**

```bash
# Tasa actual
curl "http://localhost:8001/api/v1/rates/current?from_currency=USD&to_currency=CLP"

# Histórico (últimos 30 días)
curl "http://localhost:8001/api/v1/rates/history/CLP?base=USD&days=30"

# Estadísticas
curl "http://localhost:8001/api/v1/stats/CLP?base=USD&days=30"

# Valor UF (Unidad de Fomento chilena)
curl "http://localhost:8001/api/v1/rates/uf"

# Dashboard summary (todas las divisas principales)
curl "http://localhost:8001/api/v1/dashboard/summary"
```

---

## 📊 **SISTEMA DE LOGGING AVANZADO**

### **Arquitectura de Logging**

El proyecto cuenta con un sistema de logging robusto que registra todas las operaciones críticas.

**Archivos de Log (rotación automática):**

```
logs/
├── django.log          # Logs generales Django (10MB rotación)
├── api.log            # Peticiones HTTP y API (10MB rotación)
├── kafka.log          # Eventos Kafka (10MB rotación)
├── accounts.log       # Autenticación y usuarios (5MB rotación)
├── carga_excel.log    # Procesamiento Excel (10MB rotación)
├── errors.log         # Todos los errores (10MB rotación)
└── security.log       # Seguridad y auditoría (5MB rotación)
```

### **Niveles de Logging**

- **DEBUG**: Información detallada para debugging
- **INFO**: Eventos normales de la aplicación
- **WARNING**: Eventos inusuales pero manejables
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos del sistema

### **Comandos de Monitoreo**

```bash
# Ver logs en tiempo real
tail -f logs/api.log              # Logs de API
tail -f logs/kafka.log            # Logs de Kafka
tail -f logs/errors.log           # Solo errores
tail -f logs/*.log                # Todos los logs

# Buscar errores específicos
grep "ERROR" logs/errors.log | grep "$(date +%Y-%m-%d)"
grep "User: admin" logs/api.log | grep "ERROR"

# Análisis de performance
grep "duration_ms" logs/api.log | awk '$NF > 1000'  # Requests > 1s
grep "REQUEST" logs/api.log | awk '{print $7}' | sort | uniq -c
```

### **Características del Logging**

✅ **Middleware automático** - Registra todas las peticiones HTTP
✅ **Logging en API views** - Creación, listado, eliminación
✅ **Logging en Kafka** - Productores y consumidores
✅ **Rotación automática** - 5-10 archivos de backup
✅ **Formato compatible** - ELK, Grafana, Splunk, Datadog
✅ **Seguridad** - No registra contraseñas ni tokens

---

## ⚡ **OPTIMIZACIONES DE PERFORMANCE**

### **ORM Optimizations**

**1. SELECT_RELATED (ForeignKeys)**
- Usuario en calificaciones tributarias
- Carga masiva en calificaciones
- **Mejora**: De 100+ queries a 1-2 queries por request (-97%)

**2. PREFETCH_RELATED (Many-to-Many)**
- Logs de operación
- Calificaciones tributarias relacionadas
- **Mejora**: Reducción 50-80% en tiempo de queries

**3. ONLY() / DEFER()**
- Selecciona solo campos necesarios
- **Mejora**: -60% transferencia de datos

### **Database Indexes**

**7 índices compuestos implementados:**

```sql
-- Índices en CalificacionTributaria
cal_trib_user_date_idx      (usuario, created_at)
cal_trib_merc_div_idx       (mercado, divisa)
cal_trib_inst_pago_idx      (instrumento, fecha_pago)
cal_trib_corr_merc_idx      (corredor_dueno, mercado)
cal_trib_pago_div_idx       (fecha_pago, divisa)
cal_trib_soc_loc_idx        (tipo_sociedad, es_local)
cal_trib_carga_idx          (carga_masiva, created_at)
```

**Mejora**: Queries 5-10x más rápidas en tablas grandes

### **Caching System**

- **Cache de listados**: 5 minutos TTL
- **Invalidación automática**: Al crear/actualizar/eliminar
- **Cache key**: Basada en usuario y parámetros de query
- **Backend**: LocMemCache (desarrollo), Redis (producción)

```bash
# Ver cache hit/miss en logs
tail -f logs/api.log | grep "Cache"

# Limpiar caché
docker exec -it nuam-django-core python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### **Performance Metrics**

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Tiempo de respuesta listado** | 2000ms | 150ms | -92% |
| **Queries por request** | 100+ | 2-3 | -97% |
| **Tiempo de filtrado** | 500ms | 50ms | -90% |
| **Transferencia de datos** | - | - | -60% |
| **Cache hit rate** | 0% | ~85% | +85% |

### **Database Constraints**

```sql
-- Validaciones a nivel de base de datos
valor_historico_positivo          CHECK (valor_historico >= 0)
valor_convertido_positivo         CHECK (valor_convertido >= 0)
calificacion_unica_por_entidad_fecha   UNIQUE (entidad, fecha)
```

---

## 🐳 **KAFKA - TOPICS Y EVENTOS**

### **Topics Configurados**

- `nuam.carga-masiva.events` - Eventos de carga masiva
- `nuam.calificacion.events` - Eventos de calificaciones
- `nuam.auditoria.logs` - Logs de auditoría
- `nuam.notificaciones.queue` - Cola de notificaciones
- `nuam.errores.dlq` - Dead Letter Queue

### **Consumidores**

```bash
# Iniciar todos los consumidores
docker exec -it nuam-kafka-consumer python manage.py run_kafka_consumers

# Consumidores específicos
python manage.py run_kafka_consumers --consumer carga
python manage.py run_kafka_consumers --consumer calificacion
python manage.py run_kafka_consumers --consumer auditoria
```

### **Monitoreo**

```bash
# Ver mensajes en tiempo real
docker exec -it nuam-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic nuam.carga-masiva.events \
  --from-beginning

# Dashboard web
open http://localhost/kafka/dashboard/
```

---

## 🔒 **HTTPS/SSL - CERTIFICADOS**

### **Generar Certificados Autofirmados**

```bash
# Método 1: Script bash (Linux/Mac)
bash generate_ssl_certs.sh

# Método 2: Python script
python run_https.py

# Método 3: Script de instalación local
bash install_local_ssl.sh
```

### **Gestionar Certificados**

```bash
# Ver información del certificado
python manage.py cert_info

# Renovar certificado
python manage.py cert_info --renew

# Verificar expiración
python manage.py cert_info --check
```

### **Iniciar Servidor HTTPS**

```bash
python run_https.py
# Acceder: https://localhost:8000
```

---

## 📁 **ESTRUCTURA DEL PROYECTO**

```
Nuam-main/
├── accounts/                   # Autenticación y usuarios
│   ├── management/            # Comandos personalizados
│   ├── static/                # CSS, JS, imágenes
│   └── templates/             # Templates Django
├── api/                       # API REST y lógica de negocio
│   ├── serializers.py        # Serializadores DRF
│   ├── views.py              # API Views
│   └── urls.py               # URL routing
├── kafka_app/                # Integración Kafka
│   ├── consumers/            # Consumidores Kafka
│   ├── producers/            # Productores Kafka
│   └── management/           # Comandos Kafka
├── nuam/                     # Configuración Django
│   ├── settings.py          # Settings principal
│   ├── urls.py              # URL routing principal
│   └── wsgi.py              # WSGI config
├── services/                 # Microservicios
│   ├── currency-service/    # FastAPI - Divisas
│   └── dashboard-frontend/  # React - Dashboard
├── apache/                   # Configuración Apache2
│   ├── httpd.conf           # Config principal
│   ├── conf.d/              # Virtual hosts
│   └── Dockerfile           # Build Apache2
├── nginx/                    # Configuración Nginx
│   ├── nginx.conf           # Config principal
│   └── conf.d/              # Server blocks
├── logs/                     # Sistema de logging
├── certs/                    # Certificados SSL
├── static/                   # Static files recolectados
├── docker-compose.yml        # Orquestación Docker
├── .env                      # Variables de entorno
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── USER_MANUAL.md           # Manual de usuario
├── APACHE2_IMPLEMENTATION_SUMMARY.md
├── FRONTEND_UPGRADE_SUMMARY.md
└── PROJECT_STRUCTURE.md
```

---

## 🧪 **TESTING**

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=api --cov=kafka_app

# Tests específicos
python test_kafka.py
python test_api.py

# Test de integración
pytest tests/integration/

# Test de carga
locust -f tests/load/locustfile.py
```

---

## 📝 **COMANDOS ÚTILES**

### **Django**

```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Verificar sistema
python manage.py check
python manage.py check --deploy  # Para producción

# Static files
python manage.py collectstatic --noinput

# Limpiar base de datos
python manage.py flush
```

### **Docker**

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f django-core
docker-compose logs -f currency-service

# Reiniciar servicio
docker-compose restart django-core

# Reconstruir imagen
docker-compose up -d --build django-core

# Detener todo
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

### **Base de Datos**

```bash
# Acceder a PostgreSQL
docker exec -it nuam-postgres psql -U nuam_user -d nuam_db

# Backup
docker exec nuam-postgres pg_dump -U nuam_user nuam_db > backup.sql

# Restore
docker exec -i nuam-postgres psql -U nuam_user nuam_db < backup.sql
```

---

## 🚀 **DEPLOYMENT (PRODUCCIÓN)**

### **Checklist de Producción**

```bash
# 1. Configurar variables de entorno
cp .env.example .env.production
# Editar .env.production con valores seguros

# 2. Verificar configuración
python manage.py check --deploy

# 3. Migraciones
python manage.py migrate

# 4. Recolectar estáticos
python manage.py collectstatic --noinput

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Iniciar consumidores Kafka (background)
nohup python manage.py run_kafka_consumers &

# 7. Configurar certificados SSL reales
# Usar Let's Encrypt o certificados comerciales

# 8. Configurar firewall
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### **Variables de Entorno de Producción**

```bash
# .env.production
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@db-host:5432/nuam_db
REDIS_URL=redis://redis-host:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka-host:9092
```

### **Servicios Recomendados**

- **Hosting**: AWS, DigitalOcean, Heroku
- **Base de datos**: AWS RDS, DigitalOcean Managed PostgreSQL
- **Cache**: AWS ElastiCache, Redis Cloud
- **Kafka**: Confluent Cloud, AWS MSK
- **CDN**: CloudFlare, AWS CloudFront
- **Monitoring**: Sentry, Datadog, New Relic

---

## 📚 **RECURSOS Y DOCUMENTACIÓN**

### **Documentación Oficial**

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Apache Kafka](https://kafka.apache.org/documentation/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Apache2 Documentation](https://httpd.apache.org/docs/2.4/)

### **Documentación del Proyecto**

- `USER_MANUAL.md` - Manual de usuario paso a paso
- `APACHE2_IMPLEMENTATION_SUMMARY.md` - Detalles de Apache2
- `FRONTEND_UPGRADE_SUMMARY.md` - Detalles del frontend
- `PROJECT_STRUCTURE.md` - Estructura del proyecto
- `CHANGELOG.md` - Historial de cambios
- `QUICK_REFERENCE.md` - Referencia rápida

### **APIs de Terceros**

- [ExchangeRate-API](https://www.exchangerate-api.com/) - Tasas de cambio
- [CMF Chile API](https://www.cmfchile.cl/portal/principal/605/w3-propertyvalue-26178.html) - UF Chilena
- [Swagger Editor](https://editor.swagger.io/) - Editar API docs

---

## 🤝 **CONTRIBUIR**

```bash
# 1. Fork el repositorio
# 2. Crear rama feature
git checkout -b feature/amazing-feature

# 3. Commit cambios
git commit -m 'Add amazing feature'

# 4. Push a la rama
git push origin feature/amazing-feature

# 5. Abrir Pull Request
```

---

## 📄 **LICENCIA Y CONTACTO**

### **Licencia**
MIT License - Ver `LICENSE` para más detalles

### **Autor**
**DykeByte**

### **Enlaces**
- **GitHub**: [https://github.com/DykeByte](https://github.com/DykeByte)
- **Repositorio**: [https://github.com/DykeByte/Nuam-main](https://github.com/DykeByte/Nuam-main)
- **Issues**: [https://github.com/DykeByte/Nuam-main/issues](https://github.com/DykeByte/Nuam-main/issues)

### **Soporte**
Para reportar bugs o solicitar features, abrir un issue en GitHub.

---

## 🎯 **VERSIONES**

### **v2.1.0** (Diciembre 2024) - CURRENT
- ✅ Sistema avanzado de búsqueda y filtros
- ✅ Barra de progreso en tiempo real
- ✅ Reporte detallado de errores con sugerencias
- ✅ Paginación inteligente (10-100 resultados)
- ✅ Ordenamiento dinámico por columnas

### **v2.0.0** (Diciembre 2024)
- ✅ Apache2 dual-layer reverse proxy
- ✅ Frontend modernizado con glassmorphism
- ✅ React Dashboard con gráficos interactivos
- ✅ Currency Service (FastAPI)
- ✅ Seguridad mejorada (.env, SSL/TLS)

### **v1.0.0** (Noviembre 2024)
- ✅ Sistema base Django + DRF
- ✅ Kafka integration
- ✅ Excel bulk loading
- ✅ JWT authentication

---

**Made with ❤️ by DykeByte**

*Sistema empresarial de gestión tributaria - NUAM v2.1.0*
