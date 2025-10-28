# NUAM - Sistema de Gestión de Cargas Masivas

Proyecto Django para gestión de cargas masivas y calificaciones tributarias, con soporte de múltiples divisas (USD, CLP, COP, PEN).

## 🚀 Instalación rápida

1. Clonar el repositorio:

```bash
git clone https://github.com/DykeByte/Nuam-main.git

cd Nuam-main

2. Crear y activar entorno virual:

python3 -m venv venv   
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

3. Instalar dependencias:

pip install -r requirements.txt

⚙️ Configuración:

1. Crear un archivo .env en la raíz del proyecto:

SECRET_KEY='tu_secret_key_generada' 
DEBUG=True
DATABASE_URL='postgres://usuario:contraseña@host:puerto/dbname'

(se debe revisar documentación adjunta para obtener las credenciales correspondientes)** 

2. Asegúrate de que .env esté incluido en .gitignore.

3. En settings.py ya está configurado para leer las variables con python-decouple y dj-database-url.

🛠️ Migraciones y superusuario:

python manage.py migrate
python manage.py createsuperuser

▶️ Levantar servidor:

python manage.py runserver
Abrir en el navegador: http://127.0.0.1:8000/

Sugerencia de uso del sistema:

Una vez iniciado el servidor, se recomienda realizar la siguiente verificación funcional:

1. Registro de usuario:
En la página principal, realice un registro como usuario nuevo para observar el flujo de autenticación.

2. Validación por administrador:
Los usuarios recién registrados deben ser validados por el administrador antes de poder acceder al sistema.
Para ello, cree un superusuario (como se indica más arriba) y acceda al panel de administración de Django desde:
👉 http://127.0.0.1:8000/admin

3. Autorización del usuario:
Dentro del panel de administración, ubique al usuario registrado y márquelo como activo o autorizado.

4. Acceso al sistema:
Una vez autorizado, el usuario podrá ingresar utilizando las credenciales creadas durante el registro.


📄 Funcionalidades principales:

- Registro de usuarios con aprobación manual y factores de seguridad

- Cargas masivas de archivos Excel/CSV

- Dashboard con estadísticas de calificaciones y cargas

- Conversión de divisas (para pruebas se usan tasas fijas)**

- Reportes de validación de datos

⚠️ Nota: La funcionalidad de conversión de divisas se encuentra en desarrollo.
