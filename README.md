================================================================================
                    NUAM - SISTEMA DE GESTIÓN DE 
              CALIFICACIONES TRIBUTARIAS DE INSTRUMENTOS FINANCIEROS
================================================================================

Aplicación web Django para gestión de calificaciones tributarias con soporte 
para cargas masivas Excel, procesamiento asíncrono con Kafka y seguridad SSL.

================================================================================
CARACTERÍSTICAS PRINCIPALES
================================================================================

✓ CRUD completo de calificaciones tributarias
✓ Cargas masivas desde archivos Excel (hasta 10,000 registros)
✓ Soporte multi-divisa (USD, CLP, COP, PEN, EUR)
✓ API REST con autenticación JWT
✓ Procesamiento asíncrono con Apache Kafka
✓ Certificados SSL autofirmados con renovación automática
✓ Dashboard con estadísticas en tiempo real
✓ Auditoría completa de operaciones
✓ Documentación API con Swagger

================================================================================
STACK TECNOLÓGICO
================================================================================

Backend:  Django 5.2.8, Django REST Framework 3.16.1, PostgreSQL
Mensajería:  Apache Kafka 3.5
Frontend:  Bootstrap 5, jQuery, Chart.js
DevOps:  Docker, Docker Compose, Prometheus

================================================================================
INSTALACIÓN RÁPIDA
================================================================================

1. CLONAR REPOSITORIO
   git clone https://github.com/DykeByte/Nuam-main.git
   cd Nuam-main

2. CREAR ENTORNO VIRTUAL
   python -m venv venv
   source venv/bin/activate           # Linux/Mac
   venv\Scripts\activate              # Windows

3. INSTALAR DEPENDENCIAS
   pip install -r requirements.txt

4. CONFIGURAR VARIABLES (.env)
   SECRET_KEY=tu-secret-key-aqui
   DEBUG=True
   DATABASE_URL=postgresql://user:pass@localhost:5432/nuam_db
   KAFKA_BOOTSTRAP_SERVERS=localhost:9092

5. LEVANTAR SERVICIOS DOCKER
   docker-compose up -d

6. CONFIGURAR BASE DE DATOS
   createdb nuam_db
   python manage.py migrate
   python manage.py createsuperuser

7. INICIAR APLICACIÓN
   # Terminal 1: Servidor
   python manage.py runserver
   
   # Terminal 2: Consumidores Kafka
   python manage.py run_kafka_consumers

================================================================================
ACCESO A SERVICIOS
================================================================================

Aplicación Web:        http://localhost:8000
Admin Django:          http://localhost:8000/admin
API REST:              http://localhost:8000/api/v1/
Documentación Swagger: http://localhost:8000/swagger/
Dashboard Kafka:       http://localhost:8000/kafka/dashboard/
Kafka UI:              http://localhost:8080

================================================================================
API REST - EJEMPLOS
================================================================================

>>> AUTENTICACIÓN (Obtener Token JWT)

POST http://localhost:8000/api/v1/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "tu_password"
}

Respuesta:
{
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}


>>> LISTAR CALIFICACIONES (con paginación)

GET http://localhost:8000/api/v1/calificaciones/
Authorization: Bearer tu_token_aqui


>>> CREAR CALIFICACIÓN

POST http://localhost:8000/api/v1/calificaciones/
Authorization: Bearer tu_token_aqui
Content-Type: application/json

{
  "corredor_dueno": "Corredor ABC",
  "instrumento": "BONOS-2025",
  "mercado": "LOCAL",
  "divisa": "CLP",
  "valor_historico": 1500000.00,
  "fecha_pago": "2025-12-31"
}


>>> SUBIR ARCHIVO EXCEL (Carga Masiva)

POST http://localhost:8000/api/v1/cargas/upload/
Authorization: Bearer tu_token_aqui
Content-Type: multipart/form-data

archivo: datos.xlsx
tipo_carga: FACTORES
mercado: LOCAL


>>> FILTRAR Y BUSCAR

GET /api/v1/calificaciones/?mercado=LOCAL&divisa=CLP
GET /api/v1/calificaciones/?search=BONOS
GET /api/v1/calificaciones/?ordering=-created_at
GET /api/v1/calificaciones/?page=2&page_size=50

================================================================================
KAFKA - TOPICS Y EVENTOS
================================================================================

TOPICS CONFIGURADOS:

nuam.carga-masiva.events     -> Eventos de cargas masivas
nuam.calificacion.events     -> Creación/actualización/eliminación
nuam.auditoria.logs          -> Logs de auditoría
nuam.notificaciones.queue    -> Notificaciones a usuarios
nuam.errores.dlq             -> Dead Letter Queue (mensajes fallidos)


CONSUMIDORES:

# Todos los consumidores
python manage.py run_kafka_consumers

# Consumidor específico
python manage.py run_kafka_consumers --consumer carga
python manage.py run_kafka_consumers --consumer calificacion
python manage.py run_kafka_consumers --consumer auditoria


MONITOREO:

# Ver mensajes en tiempo real
docker exec -it nuam-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic nuam.carga-masiva.events \
  --from-beginning

# Dashboard web
http://localhost:8000/kafka/dashboard/

================================================================================
HTTPS/SSL - CERTIFICADOS
================================================================================

GENERAR CERTIFICADOS AUTOFIRMADOS:

# Automático (recomendado)
python run_https.py

# O con script bash
chmod +x install_local_ssl.sh
./install_local_ssl.sh


GESTIONAR CERTIFICADOS:

# Ver información
python manage.py cert_info

# Renovar certificado
python manage.py cert_info --renew

# Verificar expiración
python manage.py cert_info --check


INICIAR SERVIDOR HTTPS:

python run_https.py
# Acceder a: https://localhost:8000

================================================================================
ESTRUCTURA DEL PROYECTO
================================================================================

Nuam-main/
├── accounts/              Autenticación y usuarios
├── api/                   API REST y lógica de negocio
│   ├── models.py         Modelos de datos
│   ├── views.py          ViewSets y endpoints
│   ├── serializers.py    Serialización DRF
│   ├── services/         Lógica de negocio
│   └── certificates.py   Gestión SSL
├── kafka_app/            Integración Kafka
│   ├── producers.py      Productores de eventos
│   ├── consumers.py      Consumidores
│   └── monitoring.py     Métricas
├── nuam/                 Configuración Django
├── logs/                 Logs del sistema
├── certs/                Certificados SSL
└── docker-compose.yml    Servicios Docker

================================================================================
TESTING
================================================================================

# Todos los tests
pytest

# Con coverage
pytest --cov=api --cov=kafka_app

# Tests de integración
python test_kafka.py
python test_api.py

================================================================================
LOGS Y MONITOREO
================================================================================

VER LOGS:

tail -f logs/django.log          # Logs generales
tail -f logs/api.log             # Logs de API
tail -f logs/carga_excel.log     # Logs de cargas masivas


DASHBOARDS:

Kafka:       http://localhost:8000/kafka/dashboard/
Métricas:    http://localhost:8000/kafka/metrics/
Kafka UI:    http://localhost:8080

================================================================================
COMANDOS ÚTILES
================================================================================

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell

# Verificar configuración
python manage.py check

# Colectar estáticos
python manage.py collectstatic

# Limpiar base de datos
python manage.py flush

================================================================================
DEPLOYMENT (PRODUCCIÓN)
================================================================================

CONFIGURACIÓN:

# .env.production
SECRET_KEY=secret-key-production
DEBUG=False
ALLOWED_HOSTS=tudominio.com
DATABASE_URL=postgresql://user:pass@db:5432/nuam_prod
KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092


COMANDOS POST-DEPLOYMENT:

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
nohup python manage.py run_kafka_consumers &

================================================================================
CONTRIBUCIÓN
================================================================================

1. Fork el repositorio
2. Crea rama: git checkout -b feature/mi-mejora
3. Commit: git commit -m 'feat: nueva funcionalidad'
4. Push: git push origin feature/mi-mejora
5. Abre Pull Request

================================================================================
RECURSOS Y DOCUMENTACIÓN
================================================================================

Django:              https://docs.djangoproject.com/
Django REST:         https://www.django-rest-framework.org/
Apache Kafka:        https://kafka.apache.org/documentation/
Swagger/OpenAPI:     https://swagger.io/specification/

================================================================================
LICENCIA Y CONTACTO
================================================================================

Licencia: MIT License
GitHub:   https://github.com/DykeByte
Issues:   https://github.com/DykeByte/Nuam-main/issues

Made with ❤️ by DykeByte

================================================================================