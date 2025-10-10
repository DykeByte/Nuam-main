# NUAM - Sistema de Gestión de Cargas Masivas

Proyecto Django para gestión de cargas masivas y calificaciones tributarias, con soporte de múltiples divisas (USD, CLP, EUR, CAD, COP, PEN).

## 🚀 Instalación rápida

1. Clonar el repositorio:

```bash
git clone https://github.com/tu_usuario/Nuam-main.git

cd Nuam-main

2. Crear y activar entorno virual:

python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

3. Instalar dependencias:

pip install -r requirements.txt

⚙️ Configuración:

1. Crear un archivo .env en la raíz del proyecto:

SECRET_KEY='tu_secret_key_generada' (la secret key que puede generar django)
DEBUG=True
DATABASE_URL='postgres://usuario:contraseña@host:puerto/dbname' (aqui va el link a la DB de railway)

2. Asegúrate de que .env esté incluido en .gitignore.

3. En settings.py ya está configurado para leer las variables con python-decouple y dj-database-url.

🛠️ Migraciones y superusuario:

python manage.py migrate
python manage.py createsuperuser

▶️ Levantar servidor:

python manage.py runserver
Abrir en el navegador: http://127.0.0.1:8000/

📄 Funcionalidades principales:

- Registro de usuarios con aprobación manual

- Cargas masivas de archivos Excel/CSV

- Dashboard con estadísticas de calificaciones y cargas

- Conversión de divisas (para pruebas se usan tasas fijas)

- Reportes de validación de datos

⚠️ Nota: La funcionalidad de procesamiento de archivos aún está en desarrollo.