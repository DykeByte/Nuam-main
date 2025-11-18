NUAM – Sistema de Gestión de Cargas Masivas

Descripción:
Nuam es una aplicación web desarrollada en Django destinada a la gestión de calificaciones tributarias de instrumentos financieros. La plataforma soporta múltiples divisas (USD, CLP, COP, PEN) y permite la carga masiva de datos mediante archivos Excel, asegurando un control eficiente y seguro de la información.

Características principales:
- Registro y autenticación de usuarios con roles diferenciados.
- Módulo de cargas masivas que permite subir archivos Excel (.xlsx/.xls) para insertar datos en el sistema.
- Panel de estadísticas que incluye número de cargas, calificaciones por mercado y por divisa.
- Gestión de modelos clave: CalificacionTributaria, CargaMasiva y LogOperacion.
- Conversión automática de valores históricos a moneda local según la divisa indicada.
- Interfaz web que permite consultar, editar y eliminar calificaciones.
- API REST desarrollada con Django REST Framework para la exposición de datos.
- Arquitectura modular organizada en apps: accounts y api.

Tecnologías utilizadas:
- Django 5.2.x
- Django REST Framework
- pandas y openpyxl para procesamiento de archivos Excel
- django-decouple y dj-database-url para gestión de configuración mediante variables de entorno
- PostgreSQL como base de datos
- Bootstrap 5 para el frontend
- GitHub para control de versiones

Instalación rápida:
1. Clonar el repositorio:
   git clone https://github.com/DykeByte/Nuam-main.git
   cd Nuam-main

2. Crear y activar un entorno virtual:
   python3 -m venv venv
   source venv/bin/activate      (macOS/Linux)
   venv\Scripts\activate.bat     (Windows)

3. Instalar dependencias:
   pip install -r requirements.txt

4. Crear un archivo .env en la raíz del proyecto con las variables mínimas:
   SECRET_KEY = 'tu_secret_key_generada'
   DEBUG = True
   DATABASE_URL = 'postgres://usuario:contraseña@host:puerto/dbname'

5. Aplicar migraciones y crear un superusuario:
   python manage.py migrate
   python manage.py createsuperuser

6. Levantar el servidor de desarrollo:
   python manage.py runserver
   Acceder luego a: http://127.0.0.1:8000/

Estructura del proyecto:

Nuam-main/
│ manage.py
│ requirements.txt
│ .env              ← archivo con variables sensibles (no subir al repositorio)
│ accounts/         ← app de autenticación y vistas web
│ api/              ← app de lógica de negocio, servicios y API REST
│ nuam/             ← carpeta de configuración de Django
│ templates/        ← plantillas HTML
│ static/           ← archivos estáticos (CSS, JS, imágenes)
└─ ...

Flujo de carga masiva:
- El usuario autenticado accede al módulo “Nueva Carga”.
- Se sube un archivo Excel con las columnas requeridas (ver plantilla de ejemplo).
- La información se procesa mediante pandas y se insertan registros en CalificacionTributaria.
- Se registra la operación en CargaMasiva y LogOperacion.
- El dashboard presenta el estado de la carga: éxitos, fallidos y progreso.

Dependencias (extracto de requirements.txt):
- Django==5.2.6
- djangorestframework
- pandas
- openpyxl
- django-decouple
- dj-database-url
- ... (ver requirements.txt para lista completa con versiones)

Contribuciones:
Para colaborar con el proyecto:
1. Realizar un fork del repositorio.
2. Crear una rama de feature: git checkout -b feature-mi-mejora
3. Realizar commits y push a la rama.
4. Abrir un Pull Request describiendo los cambios realizados.

Licencia:
El proyecto se encuentra bajo licencia MIT. Consultar el archivo LICENSE para más información.

Contacto:
Para consultas o sugerencias, contactar a DykeByte a través de GitHub.
