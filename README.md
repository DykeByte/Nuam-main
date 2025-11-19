NUAM - Sistema de Gestión de Calificaciones Tributarias de Instrumentos Financieros
----------------------------------------------------------------------------------

Aplicación web Django para gestión de calificaciones tributarias con soporte 
para cargas masivas Excel, procesamiento asíncrono con Kafka y seguridad SSL.

CARACTERÍSTICAS PRINCIPALES
---------------------------
- CRUD completo de calificaciones tributarias
- Cargas masivas desde archivos Excel (hasta 10,000 registros)
- Soporte multi-divisa (USD, CLP, COP, PEN, EUR)
- API REST con autenticación JWT
- Procesamiento asíncrono con Apache Kafka
- Certificados SSL autofirmados con renovación automática
- Dashboard con estadísticas en tiempo real
- Auditoría completa de operaciones
- Documentación API con Swagger

STACK TECNOLÓGICO
-----------------
- Backend: Django 5.2.8, Django REST Framework 3.16.1, PostgreSQL
- Mensajería: Apache Kafka 3.5
- Frontend: Bootstrap 5, jQuery, Chart.js
- DevOps: Docker, Docker Compose, Prometheus

INSTALACIÓN RÁPIDA
------------------
1. Clonar repositorio:
   git clone https://github.com/DykeByte/Nuam-main.git
   cd Nuam-main

2. Crear entorno virtual:
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

3. Instalar dependencias:
   pip install -r requirements.txt

4. Configurar variables (.env):
   SECRET_KEY=tu-secret-key
   DEBUG=True
   DATABASE_URL=postgresql://user:pass@localhost:5432/nuam_db
   KAFKA_BOOTSTRAP_SERVERS=localhost:9092

5. Levantar servicios Docker:
   docker-compose up -d

6. Configurar base de datos:
   createdb nuam_db
   python manage.py migrate
   python manage.py createsuperuser

7. Iniciar aplicación:
   - Servidor: python manage.py runserver
   - Consumidores Kafka: python manage.py run_kafka_consumers

ACCESO A SERVICIOS
------------------
- Aplicación Web: http://localhost:8000
- Admin Django:   http://localhost:8000/admin
- API REST:       http://localhost:8000/api/v1/
- Swagger:        http://localhost:8000/swagger/
- Dashboard Kafka: http://localhost:8000/kafka/dashboard/
- Kafka UI:       http://localhost:8080

API REST - EJEMPLOS
-------------------
Autenticación (Obtener Token JWT):
POST /api/v1/auth/token/
{
  "username": "admin",
  "password": "tu_password"
}

Listar calificaciones:
GET /api/v1/calificaciones/  (Authorization: Bearer tu_token)

Crear calificación:
POST /api/v1/calificaciones/
{
  "corredor_dueno": "Corredor ABC",
  "instrumento": "BONOS-2025",
  "mercado": "LOCAL",
  "divisa": "CLP",
  "valor_historico": 1500000.00,
  "fecha_pago": "2025-12-31"
}

Subir archivo Excel (Carga Masiva):
POST /api/v1/cargas/upload/ (multipart/form-data)
archivo: datos.xlsx
tipo_carga: FACTORES
mercado: LOCAL

Filtrar y buscar:
GET /api/v1/calificaciones/?mercado=LOCAL&divisa=CLP
GET /api/v1/calificaciones/?search=BONOS
GET /api/v1/calificaciones/?ordering=-created_at
GET /api/v1/calificaciones/?page=2&page_size=50

KAFKA - TOPICS Y EVENTOS
------------------------
Topics configurados:
- nuam.carga-masiva.events
- nuam.calificacion.events
- nuam.auditoria.logs
- nuam.notificaciones.queue
- nuam.errores.dlq

Consumidores:
- Todos: python manage.py run_kafka_consumers
- Específicos: 
  --consumer carga
  --consumer calificacion
  --consumer auditoria

Monitoreo:
- Ver mensajes: 
  docker exec -it nuam-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic nuam.carga-masiva.events --from-beginning
- Dashboard web: http://localhost:8000/kafka/dashboard/

HTTPS/SSL - CERTIFICADOS
------------------------
Generar certificados autofirmados:
- python run_https.py
- O con script bash: ./install_local_ssl.sh

Gestionar certificados:
- Ver info: python manage.py cert_info
- Renovar: python manage.py cert_info --renew
- Verificar expiración: python manage.py cert_info --check

Iniciar servidor HTTPS:
- python run_https.py
- Acceder: https://localhost:8000

ESTRUCTURA DEL PROYECTO
-----------------------
Nuam-main/
├── accounts/           Autenticación y usuarios
├── api/                API REST y lógica
├── kafka_app/          Integración Kafka
├── nuam/               Configuración Django
├── logs/               Logs del sistema
├── certs/              Certificados SSL
└── docker-compose.yml  Servicios Docker

TESTING
-------
- pytest
- pytest --cov=api --cov=kafka_app
- python test_kafka.py
- python test_api.py

LOGS Y MONITOREO
----------------
- tail -f logs/django.log
- tail -f logs/api.log
- tail -f logs/carga_excel.log

COMANDOS ÚTILES
---------------
- python manage.py makemigrations
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py shell
- python manage.py check
- python manage.py collectstatic
- python manage.py flush

DEPLOYMENT (PRODUCCIÓN)
-----------------------
- Configurar .env.production
- Ejecutar: migrate, collectstatic --noinput, check --deploy
- Consumidores Kafka: nohup python manage.py run_kafka_consumers &

RECURSOS
--------
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Kafka: https://kafka.apache.org/documentation/
- Swagger: https://swagger.io/specification/

LICENCIA Y CONTACTO
------------------
MIT License  
GitHub: https://github.com/DykeByte  
Issues: https://github.com/DykeByte/Nuam-main/issues  

Made with ❤️ by DykeByte
