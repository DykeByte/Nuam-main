# NUAM - Manual de Usuario Completo

**Guía paso a paso para instalar, configurar y usar el Sistema de Gestión de Calificaciones Tributarias**

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)

---

## 📚 **TABLA DE CONTENIDOS**

1. [Introducción](#1-introducción)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [Instalación desde GitHub](#3-instalación-desde-github)
4. [Configuración Inicial](#4-configuración-inicial)
5. [Primer Inicio del Sistema](#5-primer-inicio-del-sistema)
6. [Acceso al Sistema](#6-acceso-al-sistema)
7. [Navegación por la Interfaz](#7-navegación-por-la-interfaz)
8. [Gestión de Calificaciones](#8-gestión-de-calificaciones)
9. [Cargas Masivas Excel](#9-cargas-masivas-excel)
10. [Uso del Dashboard](#10-uso-del-dashboard)
11. [API REST - Guía Práctica](#11-api-rest---guía-práctica)
12. [Conversor de Divisas](#12-conversor-de-divisas)
13. [Resolución de Problemas](#13-resolución-de-problemas)
14. [Mantenimiento del Sistema](#14-mantenimiento-del-sistema)
15. [Preguntas Frecuentes (FAQ)](#15-preguntas-frecuentes-faq)

---

## 1. **INTRODUCCIÓN**

### **¿Qué es NUAM?**

NUAM es un sistema empresarial completo para la gestión de calificaciones tributarias de instrumentos financieros. Permite:

- ✅ Crear, editar y eliminar calificaciones tributarias
- ✅ Cargar miles de registros desde archivos Excel
- ✅ Visualizar estadísticas en tiempo real
- ✅ Convertir entre diferentes divisas (USD, CLP, COP, PEN, EUR, etc.)
- ✅ Consultar históricos de tasas de cambio con gráficos
- ✅ Acceder a través de API REST para integraciones
- ✅ Trabajar de forma segura con HTTPS

### **¿Para quién es este sistema?**

- Analistas financieros
- Contadores y auditores
- Equipos de tesorería
- Desarrolladores que necesitan integrar sistemas financieros

### **Arquitectura del Sistema**

```
Usuario → Apache2 (HTTPS) → Nginx → Django + FastAPI + React
                                       ↓
                            PostgreSQL + Redis + Kafka
```

---

## 2. **REQUISITOS DEL SISTEMA**

### **Software Necesario**

#### **Opción A: Instalación con Docker (RECOMENDADA)**

| Software | Versión Mínima | Descargar |
|----------|----------------|-----------|
| **Docker Desktop** | 20.10+ | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| **Git** | 2.30+ | [git-scm.com/downloads](https://git-scm.com/downloads) |

#### **Opción B: Instalación Local**

| Software | Versión Mínima | Descargar |
|----------|----------------|-----------|
| **Python** | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) |
| **PostgreSQL** | 15+ | [postgresql.org/download](https://www.postgresql.org/download/) |
| **Redis** | 7+ | [redis.io/download](https://redis.io/download) |
| **Apache Kafka** | 3.5+ | [kafka.apache.org/downloads](https://kafka.apache.org/downloads) |
| **Node.js** | 18+ | [nodejs.org/download](https://nodejs.org/download) |
| **Git** | 2.30+ | [git-scm.com/downloads](https://git-scm.com/downloads) |

### **Requisitos de Hardware**

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **Procesador** | 2 núcleos | 4 núcleos |
| **RAM** | 4 GB | 8 GB o más |
| **Disco Duro** | 10 GB libres | 20 GB libres |
| **Red** | Conexión a Internet | Banda ancha |

### **Sistemas Operativos Soportados**

- ✅ Windows 10/11 (64-bit)
- ✅ macOS 11+ (Big Sur o superior)
- ✅ Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)

---

## 3. **INSTALACIÓN DESDE GITHUB**

### **Paso 1: Instalar Git**

#### **Windows:**
1. Descargar Git desde: https://git-scm.com/download/win
2. Ejecutar el instalador
3. Mantener opciones por defecto
4. Hacer clic en "Next" hasta finalizar

#### **macOS:**
```bash
# Opción 1: Homebrew (recomendado)
brew install git

# Opción 2: Descargar instalador
# Visitar: https://git-scm.com/download/mac
```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git -y
```

**Verificar instalación:**
```bash
git --version
# Debería mostrar: git version 2.x.x
```

---

### **Paso 2: Instalar Docker Desktop**

#### **Windows:**
1. Descargar Docker Desktop: https://www.docker.com/products/docker-desktop
2. Ejecutar el instalador `Docker Desktop Installer.exe`
3. Seguir el asistente de instalación
4. Reiniciar el computador cuando se solicite
5. Iniciar Docker Desktop desde el menú inicio
6. Esperar a que el icono de Docker en la bandeja del sistema diga "Docker Desktop is running"

#### **macOS:**
1. Descargar Docker Desktop para Mac
2. Arrastrar Docker.app a la carpeta Aplicaciones
3. Abrir Docker desde Aplicaciones
4. Autorizar cuando se solicite
5. Esperar a que el icono de la ballena deje de animarse

#### **Linux (Ubuntu/Debian):**
```bash
# Actualizar repositorios
sudo apt update

# Instalar dependencias
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio de Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Agregar usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Cerrar sesión y volver a iniciarla para aplicar cambios
```

**Verificar instalación de Docker:**
```bash
docker --version
# Debería mostrar: Docker version 20.x.x

docker-compose --version
# Debería mostrar: Docker Compose version v2.x.x
```

---

### **Paso 3: Clonar el Repositorio**

Abrir una terminal/símbolo del sistema:

#### **Windows:**
- Presionar `Win + R`
- Escribir `cmd` y presionar Enter
- O abrir "PowerShell" desde el menú inicio

#### **macOS:**
- Presionar `Cmd + Espacio`
- Escribir "Terminal" y presionar Enter

#### **Linux:**
- Presionar `Ctrl + Alt + T`

**Comandos para clonar:**

```bash
# Navegar a la carpeta donde quieres descargar el proyecto
# Por ejemplo, en Windows:
cd C:\Users\TuUsuario\Documents

# En macOS/Linux:
cd ~/Documents

# Clonar el repositorio
git clone https://github.com/DykeByte/Nuam-main.git

# Entrar a la carpeta del proyecto
cd Nuam-main
```

**¿Qué hace este comando?**
- Descarga todos los archivos del proyecto desde GitHub
- Crea una carpeta llamada `Nuam-main` con todo el código fuente
- Incluye todo el historial de cambios (commits)

---

### **Paso 4: Verificar Archivos Descargados**

```bash
# Listar archivos en la carpeta
# Windows:
dir

# macOS/Linux:
ls -la
```

**Deberías ver:**
```
accounts/
api/
apache/
kafka_app/
nginx/
nuam/
services/
docker-compose.yml
requirements.txt
README.md
.env
...
```

---

## 4. **CONFIGURACIÓN INICIAL**

### **Paso 1: Generar Certificados SSL**

Los certificados SSL permiten que el sistema funcione con HTTPS (conexión segura).

#### **Linux/macOS:**
```bash
# Dar permisos de ejecución al script
chmod +x generate_ssl_certs.sh

# Ejecutar script
bash generate_ssl_certs.sh
```

#### **Windows:**
```bash
# Opción 1: Git Bash (incluido con Git para Windows)
bash generate_ssl_certs.sh

# Opción 2: Usar OpenSSL manualmente
# Descargar OpenSSL: https://slproweb.com/products/Win32OpenSSL.html
# Luego ejecutar:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
  -keyout certs/nuam.key ^
  -out certs/nuam.crt ^
  -subj "/C=CL/ST=Santiago/L=Santiago/O=NUAM/OU=IT/CN=localhost"
```

**¿Qué hace esto?**
- Crea un certificado SSL autofirmado válido por 365 días
- Genera dos archivos:
  - `certs/nuam.crt` - Certificado público
  - `certs/nuam.key` - Clave privada

**Nota:** Para uso en desarrollo local. En producción, usar certificados de Let's Encrypt o un proveedor comercial.

---

### **Paso 2: Revisar Archivo .env**

El archivo `.env` contiene todas las configuraciones del sistema.

```bash
# Ver contenido del archivo (ya viene incluido en el repositorio)
# Windows:
type .env

# macOS/Linux:
cat .env
```

**Contenido del archivo `.env`:**

```bash
# Configuración Django
SECRET_KEY=django-insecure-vdxx7x-a+h#*)5==$7$3o338!)zsu*+m(dqjf!gi=1i!l)-36s
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,nuam.local
CSRF_TRUSTED_ORIGINS=http://localhost,https://localhost,http://127.0.0.1,https://127.0.0.1

# Base de Datos PostgreSQL
DATABASE_NAME=nuam_db
DATABASE_USER=nuam_user
DATABASE_PASSWORD=nuam_password
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_URL=postgresql://nuam_user:nuam_password@postgres:5432/nuam_db

# Redis
REDIS_URL=redis://redis:6379/1

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Currency Service
CURRENCY_SERVICE_URL=http://currency-service:8001
```

**⚠️ IMPORTANTE:**
- **Para desarrollo local**: Dejar todo como está
- **Para producción**: Cambiar `SECRET_KEY`, `DEBUG=False`, y usar contraseñas seguras

**Generar nuevo SECRET_KEY (Opcional):**
```bash
# Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# O usar generador online: https://djecrety.ir/
```

---

### **Paso 3: Configuración de Docker Desktop**

#### **Ajustar Recursos de Docker (Recomendado):**

**Windows/macOS:**
1. Abrir Docker Desktop
2. Click en el icono de engranaje (Settings)
3. Ir a "Resources"
4. Ajustar:
   - **CPUs**: 2-4 núcleos
   - **Memory**: 4-6 GB
   - **Disk**: 20 GB
5. Click "Apply & Restart"

**Linux:**
No requiere ajustes, usa los recursos del sistema directamente.

---

## 5. **PRIMER INICIO DEL SISTEMA**

### **Método 1: Inicio Completo con Docker (RECOMENDADO)**

Este método levanta todos los servicios automáticamente.

```bash
# Asegurarse de estar en la carpeta del proyecto
cd Nuam-main

# Levantar todos los servicios
docker-compose up -d
```

**¿Qué significa `-d`?**
- `-d` = "detached mode" (modo separado)
- Los contenedores se ejecutan en segundo plano
- Puedes seguir usando la terminal

**Primera vez (puede tomar 10-15 minutos):**
- Descarga imágenes de Docker (PostgreSQL, Redis, Kafka, etc.)
- Construye las imágenes personalizadas (Django, FastAPI, React)
- Crea las redes y volúmenes
- Inicia todos los servicios

**Ver progreso:**
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Presionar Ctrl+C para salir (los servicios siguen corriendo)

# Ver logs de un servicio específico
docker-compose logs -f django-core
docker-compose logs -f currency-service
```

**Verificar que todo está corriendo:**
```bash
docker-compose ps
```

**Deberías ver:**
```
NAME                  STATUS    PORTS
nuam-apache2          Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
nuam-nginx            Up        0.0.0.0:8080->80/tcp
nuam-django-core      Up        0.0.0.0:8000->8000/tcp
nuam-currency-service Up        0.0.0.0:8001->8001/tcp
nuam-dashboard-frontend Up      0.0.0.0:3000->3000/tcp
nuam-postgres         Up        0.0.0.0:5432->5432/tcp
nuam-redis            Up        0.0.0.0:6379->6379/tcp
nuam-kafka            Up        0.0.0.0:9092->9092/tcp
nuam-zookeeper        Up        2181/tcp
nuam-kafka-consumer   Up
```

**Todos deben decir `Up` (Arriba) o `Up (healthy)` (Arriba y saludable).**

---

### **Paso 2: Aplicar Migraciones de Base de Datos**

Las migraciones crean las tablas necesarias en PostgreSQL.

```bash
# Ejecutar migraciones
docker exec -it nuam-django-core python manage.py migrate
```

**Salida esperada:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

### **Paso 3: Crear Superusuario (Administrador)**

El superusuario puede acceder a todo el sistema.

```bash
docker exec -it nuam-django-core python manage.py createsuperuser
```

**El sistema te preguntará:**
```
Username: admin
Email address: admin@nuam.com
Password: [escribir contraseña, no se verá]
Password (again): [repetir contraseña]
```

**Recomendaciones:**
- Username: `admin` o tu nombre
- Email: Tu correo real
- Password: Mínimo 8 caracteres, combinar letras, números y símbolos

**⚠️ IMPORTANTE:** Guardar estas credenciales en un lugar seguro. Las necesitarás para acceder al sistema.

---

### **Paso 4: Recolectar Archivos Estáticos**

Los archivos estáticos incluyen CSS, JavaScript e imágenes.

```bash
docker exec -it nuam-django-core python manage.py collectstatic --noinput
```

**Salida esperada:**
```
205 static files copied to '/app/staticfiles'
```

---

### **Paso 5: Verificar Servicios Activos**

```bash
# Verificar estado de servicios
docker-compose ps

# Verificar logs si hay algún problema
docker-compose logs -f
```

**Health Checks Automáticos:**

El sistema verifica automáticamente cada 30 segundos que los servicios estén funcionando correctamente.

---

## 6. **ACCESO AL SISTEMA**

### **URLs de Acceso**

Una vez que todos los servicios estén corriendo, puedes acceder a:

#### **Acceso Principal (HTTPS - Recomendado):**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **🏠 Dashboard Principal** | https://localhost/ | React Dashboard con gráficos |
| **📊 Panel Django** | https://localhost/accounts/home/ | Panel de control |
| **🔐 Login** | https://localhost/accounts/login/ | Página de inicio de sesión |
| **⚙️ Admin Django** | https://localhost/admin/ | Administración completa |

⚠️ **Advertencia SSL:** Tu navegador mostrará una advertencia de seguridad porque el certificado es autofirmado.

**Cómo Proceder:**

**Google Chrome / Microsoft Edge:**
1. Verás "Tu conexión no es privada"
2. Click en "Avanzado"
3. Click en "Ir a localhost (no seguro)"

**Mozilla Firefox:**
1. Verás "Advertencia: Riesgo potencial de seguridad a continuación"
2. Click en "Avanzado"
3. Click en "Aceptar el riesgo y continuar"

**Safari:**
1. Click en "Mostrar detalles"
2. Click en "visitar este sitio web"
3. Confirmar

#### **Acceso HTTP (Sin SSL):**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **🏠 Dashboard Principal** | http://localhost/ | React Dashboard |
| **📊 Panel Django** | http://localhost/accounts/home/ | Panel de control |
| **🔐 Login** | http://localhost/accounts/login/ | Inicio de sesión |
| **⚙️ Admin Django** | http://localhost/admin/ | Administración |

#### **Acceso Directo a Servicios (Desarrollo):**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Django Core** | http://localhost:8000/ | Backend principal |
| **Currency API** | http://localhost:8001/ | Microservicio de divisas |
| **React Dev** | http://localhost:3000/ | Frontend React |
| **Nginx** | http://localhost:8080/ | Proxy interno |

#### **Documentación API:**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Swagger UI** | http://localhost/swagger/ | Documentación interactiva |
| **ReDoc** | http://localhost/redoc/ | Documentación alternativa |
| **Currency API Docs** | http://localhost:8001/docs | FastAPI Swagger |

---

### **Primera Prueba de Acceso**

#### **Paso 1: Abrir Navegador**

Abrir Google Chrome, Firefox, Edge o Safari.

#### **Paso 2: Acceder a la Página de Login**

```
https://localhost/accounts/login/
```

o

```
http://localhost/accounts/login/
```

#### **Paso 3: Iniciar Sesión**

- **Usuario:** El username que creaste (ej: `admin`)
- **Contraseña:** La contraseña que configuraste

Hacer click en "Ingresar".

#### **Paso 4: Ver Dashboard**

Serás redirigido automáticamente a:
```
https://localhost/accounts/home/
```

**Deberías ver:**
- Tarjetas de estadísticas (Calificaciones, Cargas, Sistema)
- Widget de conversión de divisas
- Acciones rápidas
- Información del sistema

---

## 7. **NAVEGACIÓN POR LA INTERFAZ**

### **Barra de Navegación**

La barra superior contiene los siguientes menús:

```
NUAM | Inicio | Calificaciones ▼ | Cargas ▼ | Logs ▼ | Admin | 👤 Usuario ▼
```

#### **1. Inicio**
- Regresa al dashboard principal
- Muestra estadísticas generales

#### **2. Calificaciones ▼**
- **📝 Nueva Calificación**: Crear una calificación manualmente
- **📋 Lista de Calificaciones**: Ver todas las calificaciones
- **🔍 Buscar**: Buscar calificaciones por criterios

#### **3. Cargas ▼**
- **📤 Nueva Carga Masiva**: Subir archivo Excel con miles de registros
- **📋 Historial de Cargas**: Ver todas las cargas realizadas
- **📊 Estadísticas de Cargas**: Métricas de éxito/fallo

#### **4. Logs ▼**
- **📝 Historial de Operaciones**: Ver todas las acciones realizadas
- **⚠️ Errores del Sistema**: Ver logs de errores
- **👤 Accesos de Usuarios**: Auditoría de sesiones

#### **5. Admin**
- Acceso al panel de administración de Django
- Control total del sistema

#### **6. 👤 Usuario ▼**
- **👤 Mi Perfil**: Ver y editar información personal
- **🔑 Cambiar Contraseña**: Actualizar contraseña
- **🚪 Cerrar Sesión**: Salir del sistema

---

### **Dashboard Principal**

El dashboard muestra información en tiempo real:

#### **Sección 1: Estadísticas**

Tres tarjetas principales:

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ 📊 Calificaciones   │  │ 📤 Cargas           │  │ ✨ Sistema          │
│                     │  │                     │  │                     │
│     150             │  │     25              │  │     100%            │
│ Tributarias         │  │ Realizadas          │  │ Operativo           │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

#### **Sección 2: Conversor de Divisas**

Widget interactivo que permite:
- Ingresar un monto
- Seleccionar divisa origen
- Seleccionar divisa destino
- Ver resultado en tiempo real

```
💱 Conversor de Divisas en Tiempo Real
┌──────────────────────────────────────────────┐
│ Monto: [100] | De: [USD ▼] | A: [CLP ▼]     │
│                                               │
│ Resultado: $100 USD = $92,486 CLP            │
│ Tasa: 1 USD = 924.86 CLP                     │
│ Actualizado: 09/12/2024 15:30                │
└──────────────────────────────────────────────┘
```

#### **Sección 3: Acciones Rápidas**

Botones para operaciones frecuentes:
- **📤 Nueva Carga Masiva**: Subir archivo Excel
- **📋 Ver Calificaciones**: Ir al listado
- **📊 Historial de Operaciones**: Ver logs

#### **Sección 4: Últimas Cargas**

Muestra las últimas 5 cargas masivas realizadas:
```
🕒 Últimas Cargas
┌──────────────────────────────────────────┐
│ FACTORES                                  │
│ 🗓️ 09/12/2024 14:25                     │
│ ✓ 500 exitosos                            │
└──────────────────────────────────────────┘
```

#### **Sección 5: Información del Sistema**

Tarjetas con información del usuario:
- 👤 Usuario: admin
- 📧 Email: admin@nuam.com
- ✅ Estado: Activo
- 🕐 Última sesión: 09/12/2024 15:30

---

## 8. **GESTIÓN DE CALIFICACIONES**

### **Crear Nueva Calificación Manualmente**

#### **Paso 1: Navegar a Nueva Calificación**

Menú superior → Calificaciones → Nueva Calificación

#### **Paso 2: Llenar Formulario**

**Campos obligatorios:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Corredor Dueño** | Nombre del corredor | Corredor ABC |
| **Instrumento** | Código del instrumento | BONOS-2025 |
| **Mercado** | LOCAL o EXTERNO | LOCAL |
| **Divisa** | Moneda del valor | CLP |
| **Valor Histórico** | Monto en la divisa indicada | 1500000.00 |
| **Fecha de Pago** | Fecha en formato DD/MM/AAAA | 31/12/2025 |

**Campos opcionales:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Tipo de Sociedad** | Clasificación | S.A. |
| **Es Local** | Checkbox si es local | ☑ |
| **Notas** | Comentarios adicionales | Instrumento de largo plazo |

#### **Paso 3: Guardar**

Click en botón **"Guardar"** (azul).

**Resultado:**
- Mensaje de confirmación verde: "Calificación creada exitosamente"
- Redirección automática al listado de calificaciones
- La nueva calificación aparece en la primera posición

---

### **Ver Lista de Calificaciones**

#### **Paso 1: Acceder al Listado**

Menú superior → Calificaciones → Lista de Calificaciones

#### **Paso 2: Entender la Tabla**

La tabla muestra:

```
┌─────┬─────────────┬──────────────┬─────────┬─────────┬──────────────┬──────────┐
│ ID  │ Corredor    │ Instrumento  │ Mercado │ Divisa  │ Valor        │ Acciones │
├─────┼─────────────┼──────────────┼─────────┼─────────┼──────────────┼──────────┤
│ 150 │ Corredor A  │ BONOS-2025   │ LOCAL   │ CLP     │ 1,500,000.00 │ 👁️ ✏️ 🗑️  │
│ 149 │ Corredor B  │ ACCIONES-24  │ EXTERNO │ USD     │    25,000.00 │ 👁️ ✏️ 🗑️  │
└─────┴─────────────┴──────────────┴─────────┴─────────┴──────────────┴──────────┘
```

**Acciones disponibles:**
- 👁️ **Ver Detalle**: Muestra toda la información
- ✏️ **Editar**: Modificar la calificación
- 🗑️ **Eliminar**: Borrar (pide confirmación)

#### **Paso 3: Filtrar y Buscar**

**Buscador rápido:**
```
🔍 Buscar: [_____________] [🔍 Buscar]
```

Puedes buscar por:
- Corredor dueño
- Instrumento
- Mercado
- Cualquier texto en las notas

**Filtros avanzados:**
```
📊 Filtros:
┌────────────────────────────────────────┐
│ Mercado:  [ LOCAL ▼ ]                  │
│ Divisa:   [ CLP ▼ ]                    │
│ Fecha desde: [__/__/____]              │
│ Fecha hasta: [__/__/____]              │
│ [Aplicar Filtros] [Limpiar]           │
└────────────────────────────────────────┘
```

#### **Paso 4: Ordenar**

Click en los encabezados de columna para ordenar:
- **ID**: ↑ Ascendente / ↓ Descendente
- **Fecha**: Más reciente primero / Más antiguo primero
- **Valor**: Menor a mayor / Mayor a menor

#### **Paso 5: Paginación**

En la parte inferior:
```
← Anterior | Página 1 de 10 | Siguiente →
Mostrando 1-50 de 500 resultados
```

**Cambiar resultados por página:**
```
Mostrar: [50 ▼] resultados por página
```

Opciones: 10, 25, 50, 100

---

### **Editar Calificación Existente**

#### **Paso 1: Ir al Listado**

Calificaciones → Lista de Calificaciones

#### **Paso 2: Click en Editar**

Click en el ícono ✏️ de la calificación que deseas modificar.

#### **Paso 3: Modificar Campos**

Cambiar los valores que necesites actualizar.

#### **Paso 4: Guardar Cambios**

Click en **"Guardar Cambios"** (azul).

**Resultado:**
- Mensaje verde: "Calificación actualizada exitosamente"
- Registro del cambio en el log de auditoría
- Valores actualizados visibles en el listado

---

### **Eliminar Calificación**

#### **Paso 1: Click en Eliminar**

En el listado, click en el ícono 🗑️.

#### **Paso 2: Confirmar**

Aparece modal de confirmación:
```
⚠️ Confirmar Eliminación
¿Estás seguro de eliminar esta calificación?

Corredor: Corredor ABC
Instrumento: BONOS-2025
Valor: $1,500,000.00 CLP

Esta acción no se puede deshacer.

[Cancelar]  [Eliminar]
```

#### **Paso 3: Eliminar**

Click en **"Eliminar"** (rojo).

**Resultado:**
- Mensaje verde: "Calificación eliminada exitosamente"
- La calificación desaparece del listado
- Se guarda registro de eliminación en logs de auditoría

---

## 9. **CARGAS MASIVAS EXCEL**

Las cargas masivas permiten subir miles de calificaciones desde un archivo Excel en segundos.

### **Preparar Archivo Excel**

#### **Plantilla Requerida:**

El archivo Excel debe tener estas columnas (exactamente con estos nombres):

| Columna | Tipo | Obligatorio | Ejemplo |
|---------|------|-------------|---------|
| **corredor_dueno** | Texto | ✅ | Corredor ABC |
| **instrumento** | Texto | ✅ | BONOS-2025 |
| **mercado** | Texto (LOCAL/EXTERNO) | ✅ | LOCAL |
| **divisa** | Texto (CLP/USD/EUR/etc) | ✅ | CLP |
| **valor_historico** | Número | ✅ | 1500000.00 |
| **fecha_pago** | Fecha | ✅ | 31/12/2025 |
| **tipo_sociedad** | Texto | ❌ | S.A. |
| **es_local** | Sí/No | ❌ | Sí |
| **notas** | Texto | ❌ | Comentarios |

**Ejemplo de archivo Excel:**

```
| corredor_dueno | instrumento | mercado | divisa | valor_historico | fecha_pago |
|----------------|-------------|---------|--------|-----------------|------------|
| Corredor A     | BONOS-001   | LOCAL   | CLP    | 1000000         | 31/12/2025 |
| Corredor B     | ACCIONES-01 | EXTERNO | USD    | 50000           | 15/06/2025 |
| Corredor C     | DERIVADOS-1 | LOCAL   | CLP    | 750000          | 20/08/2025 |
```

#### **Descargar Plantilla:**

1. Ir a: Cargas → Nueva Carga Masiva
2. Click en **"Descargar Plantilla Excel"**
3. Abrir el archivo descargado
4. Llenar con tus datos (puedes agregar hasta 10,000 filas)
5. Guardar como `.xlsx`

---

### **Realizar Carga Masiva**

#### **Paso 1: Navegar a Nueva Carga**

Menú superior → Cargas → Nueva Carga Masiva

#### **Paso 2: Seleccionar Archivo**

```
📤 Nueva Carga Masiva
┌────────────────────────────────────────┐
│ Tipo de Carga: [FACTORES ▼]           │
│                                         │
│ Mercado: [LOCAL ▼]                     │
│                                         │
│ Archivo Excel:                          │
│ [Seleccionar Archivo...]               │
│ Sin archivo seleccionado               │
│                                         │
│ [Subir y Procesar]                     │
└────────────────────────────────────────┘
```

1. **Tipo de Carga**: Seleccionar categoría (FACTORES, BONOS, ACCIONES, etc.)
2. **Mercado**: LOCAL o EXTERNO
3. **Archivo Excel**: Click en "Seleccionar Archivo..." y elegir tu archivo `.xlsx`

#### **Paso 3: Subir y Procesar**

Click en **"Subir y Procesar"** (azul).

**Proceso automático:**

1. **Validación inicial** (1-2 segundos)
   - Verifica que el archivo sea `.xlsx`
   - Verifica columnas requeridas
   - Verifica que no esté vacío

2. **Procesamiento** (depende del tamaño)
   - 100 registros: ~5 segundos
   - 1,000 registros: ~30 segundos
   - 10,000 registros: ~2-3 minutos

**Barra de progreso:**
```
⏳ Procesando...
████████████████░░░░░░░░░░ 67%
Procesados: 670 / 1000
```

3. **Resultado**

Pantalla de resumen:
```
✅ Carga Masiva Completada

📊 Resumen:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total de registros: 1,000
✅ Exitosos: 950
❌ Fallidos: 50

⏱️ Tiempo de procesamiento: 28 segundos

📋 Errores Encontrados:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fila 15: Divisa inválida 'XXX'
Fila 28: Fecha en formato incorrecto
Fila 103: Valor histórico negativo
...

[Descargar Reporte de Errores] [Volver al Listado]
```

#### **Paso 4: Revisar Errores (Si los hay)**

Click en **"Descargar Reporte de Errores"** para obtener un Excel con:
- Filas que fallaron
- Motivo del error
- Sugerencia de corrección

Corregir el archivo y volver a subirlo.

---

### **Ver Historial de Cargas**

#### **Acceder al Historial**

Menú superior → Cargas → Historial de Cargas

**Tabla de cargas:**

```
┌────┬────────────┬──────────┬─────────┬─────────┬──────────┬──────────┬──────────┐
│ ID │ Fecha      │ Usuario  │ Tipo    │ Mercado │ Total   │ Exitosos │ Fallidos │
├────┼────────────┼──────────┼─────────┼─────────┼──────────┼──────────┼──────────┤
│ 25 │ 09/12/2024 │ admin    │ FACTORES│ LOCAL   │ 1,000   │ 950      │ 50       │
│ 24 │ 08/12/2024 │ admin    │ BONOS   │ EXTERNO │ 500     │ 500      │ 0        │
└────┴────────────┴──────────┴─────────┴─────────┴──────────┴──────────┴──────────┘
```

**Acciones disponibles:**
- 👁️ **Ver Detalle**: Información completa de la carga
- 📊 **Ver Registros**: Ver calificaciones creadas por esta carga
- 📥 **Descargar Reporte**: Excel con resultados

---

### **Recomendaciones para Cargas Masivas**

✅ **Hacer:**
- Usar la plantilla proporcionada
- Validar datos antes de subir
- Probar con archivo pequeño primero (100 filas)
- Revisar formato de fechas (DD/MM/AAAA)
- Usar divisas válidas (CLP, USD, EUR, COP, PEN)

❌ **Evitar:**
- Archivos con más de 10,000 filas (dividir en múltiples archivos)
- Cambiar nombres de columnas
- Dejar celdas vacías en columnas obligatorias
- Usar formato de fecha incorrecto
- Divisas inventadas

---

## 10. **USO DEL DASHBOARD**

El Dashboard React ofrece visualización avanzada con gráficos interactivos.

### **Acceder al Dashboard**

```
https://localhost/
```

o

```
http://localhost:3000/
```

---

### **Componentes del Dashboard**

#### **1. Tarjetas de Divisas**

Muestra valores actuales de las principales divisas latinoamericanas:

```
┌─────────────────────────────┐
│ USD/CLP                      │
│                              │
│ 924.86                ↗️ +2.5%│
│                              │
│ Promedio 30d: 920.15        │
│ Máximo: 935.20              │
│ Mínimo: 910.45              │
│ Cambio 30d: +2.5%           │
└─────────────────────────────┘
```

**Divisas mostradas:**
- 🇨🇱 CLP - Peso Chileno
- 🇨🇴 COP - Peso Colombiano
- 🇵🇪 PEN - Sol Peruano
- 🇲🇽 MXN - Peso Mexicano
- 🇨🇱 UF - Unidad de Fomento

**Indicadores:**
- ↗️ Verde: Moneda se está apreciando
- ↘️ Rojo: Moneda se está depreciando

---

#### **2. Gráfico Histórico**

Gráfico de área interactivo con histórico de tasas de cambio.

**Controles:**

```
📈 Histórico USD/CLP                [CLP ▼]  [7d] [30d] [90d] [180d]
```

**Interacción:**
- **Hover**: Pasar el mouse sobre el gráfico para ver valores exactos
- **Selector de moneda**: Cambiar entre CLP, COP, PEN, MXN, EUR
- **Rango de tiempo**: 7, 30, 90 o 180 días

**Tooltip al pasar el mouse:**
```
┌─────────────────┐
│ 5 de Dic        │
│ Tasa: 924.86    │
└─────────────────┘
```

---

#### **3. Gráfico Comparativo**

Compara múltiples monedas latinoamericanas en un solo gráfico.

```
Comparación de Monedas Latinoamericanas

        CLP —— COP —— PEN
```

**Leyenda:**
- Azul: CLP (Peso Chileno)
- Verde: COP (Peso Colombiano)
- Naranja: PEN (Sol Peruano)

**Uso:**
- Identificar tendencias simultáneas
- Comparar volatilidad entre monedas
- Análisis de correlaciones

---

#### **4. Tarjetas de Estadísticas**

Tres tarjetas en la parte inferior:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Operaciones Hoy │  │ Total           │  │ Usuarios        │
│                 │  │ Operaciones     │  │ Activos         │
│     45          │  │     1,250       │  │     12          │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

#### **5. Actualización Automática**

El dashboard se actualiza automáticamente cada 5 minutos.

**Indicador de actualización:**
```
Última actualización: 15:30:45
```

**Actualizar manualmente:**
- Refrescar la página (F5)
- El sistema descarga nuevos datos automáticamente

---

## 11. **API REST - GUÍA PRÁCTICA**

La API REST permite integrar NUAM con otros sistemas.

### **Autenticación**

Todos los endpoints (excepto login) requieren un token JWT.

#### **Paso 1: Obtener Token**

**Usando curl (Terminal):**

```bash
curl -X POST http://localhost/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu_password"}'
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Usando Postman:**

1. Crear nueva request POST
2. URL: `http://localhost/api/v1/auth/token/`
3. Body → raw → JSON:
```json
{
  "username": "admin",
  "password": "tu_password"
}
```
4. Click "Send"
5. Copiar el valor de `access`

**Guardar el token** para usarlo en las siguientes peticiones.

---

### **Listar Calificaciones**

```bash
curl http://localhost/api/v1/calificaciones/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

**Respuesta:**
```json
{
  "count": 150,
  "next": "http://localhost/api/v1/calificaciones/?page=2",
  "previous": null,
  "results": [
    {
      "id": 150,
      "corredor_dueno": "Corredor ABC",
      "instrumento": "BONOS-2025",
      "mercado": "LOCAL",
      "divisa": "CLP",
      "valor_historico": "1500000.00",
      "fecha_pago": "2025-12-31",
      "created_at": "2024-12-09T15:30:00Z"
    }
  ]
}
```

---

### **Crear Calificación**

```bash
curl -X POST http://localhost/api/v1/calificaciones/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "corredor_dueno": "Corredor XYZ",
    "instrumento": "ACCIONES-2025",
    "mercado": "EXTERNO",
    "divisa": "USD",
    "valor_historico": 50000.00,
    "fecha_pago": "2025-06-15"
  }'
```

---

### **Convertir Divisas**

```bash
curl "http://localhost/api/v1/divisas/tasa/?from=USD&to=CLP"
```

**Respuesta:**
```json
{
  "success": true,
  "from_currency": "USD",
  "to_currency": "CLP",
  "rate": "924.86",
  "timestamp": "2024-12-09T15:30:00Z"
}
```

---

### **Documentación Swagger**

Acceder a la documentación interactiva:

```
http://localhost/swagger/
```

**Características:**
- Ver todos los endpoints disponibles
- Probar endpoints directamente desde el navegador
- Ver ejemplos de request/response
- Generar código para diferentes lenguajes

---

## 12. **CONVERSOR DE DIVISAS**

El conversor de divisas usa tasas en tiempo real de ExchangeRate-API.

### **Usar el Widget en Dashboard**

#### **Paso 1: Acceder al Dashboard**

```
https://localhost/accounts/home/
```

#### **Paso 2: Ubicar el Widget**

Scroll hacia abajo hasta ver:

```
💱 Conversor de Divisas en Tiempo Real
```

#### **Paso 3: Ingresar Datos**

1. **Monto**: Escribir cantidad (ej: 100)
2. **De**: Seleccionar divisa origen (ej: USD)
3. **A**: Seleccionar divisa destino (ej: CLP)

**Conversión automática:**
El resultado se actualiza mientras escribes (sin necesidad de botón).

#### **Paso 4: Ver Resultado**

```
Resultado: $100.00 USD = $92,486.00 CLP
Tasa: 1 USD = 924.86 CLP
Actualizado: 09/12/2024 15:30:45
```

---

### **Divisas Disponibles**

| Código | Nombre | Símbolo |
|--------|--------|---------|
| **USD** | Dólar Estadounidense | $ |
| **EUR** | Euro | € |
| **CLP** | Peso Chileno | $ |
| **COP** | Peso Colombiano | $ |
| **PEN** | Sol Peruano | S/ |
| **MXN** | Peso Mexicano | $ |
| **BRL** | Real Brasileño | R$ |
| **ARS** | Peso Argentino | $ |
| **GBP** | Libra Esterlina | £ |
| **JPY** | Yen Japonés | ¥ |
| **CNY** | Yuan Chino | ¥ |
| **CAD** | Dólar Canadiense | $ |

**Más de 160 divisas adicionales disponibles vía API.**

---

### **UF (Unidad de Fomento) Chilena**

Integración con API oficial de CMF (Comisión para el Mercado Financiero).

**Ver valor UF actual:**

```bash
curl "http://localhost:8001/api/v1/rates/uf"
```

**Respuesta:**
```json
{
  "value": "36,890.45",
  "date": "2024-12-09",
  "source": "CMF"
}
```

**Valor actualizado diariamente** por la CMF.

---

## 13. **RESOLUCIÓN DE PROBLEMAS**

### **Problema 1: Docker no se inicia**

**Síntoma:**
```
ERROR: Cannot connect to the Docker daemon
```

**Solución:**

**Windows/macOS:**
1. Abrir Docker Desktop
2. Esperar a que el ícono deje de animarse
3. Verificar que diga "Docker Desktop is running"

**Linux:**
```bash
# Iniciar servicio Docker
sudo systemctl start docker

# Verificar estado
sudo systemctl status docker

# Habilitar inicio automático
sudo systemctl enable docker
```

---

### **Problema 2: Puerto ya en uso**

**Síntoma:**
```
ERROR: for nuam-apache2  Cannot start service apache2:
Ports are not available: port is already allocated
```

**Solución:**

**Opción 1: Detener servicio que usa el puerto**

```bash
# Windows
netstat -ano | findstr :80
# Anotar el PID (última columna)
taskkill /PID [PID] /F

# macOS/Linux
lsof -i :80
# Anotar el PID
sudo kill [PID]
```

**Opción 2: Cambiar puerto en docker-compose.yml**

```yaml
apache2:
  ports:
    - "8888:80"   # Cambiar 80 por 8888
    - "4443:443"  # Cambiar 443 por 4443
```

Luego acceder en: `http://localhost:8888/`

---

### **Problema 3: Contenedor en estado "Restarting"**

**Síntoma:**
```bash
docker-compose ps
# Muestra: nuam-django-core  Restarting (1) 10 seconds ago
```

**Solución:**

```bash
# Ver logs del contenedor
docker logs nuam-django-core --tail 50

# Buscar errores en logs
# Errores comunes:
# - Missing import os
# - Database connection failed
# - Secret key not set
```

**Corregir según el error:**

1. **Import missing:**
```python
# nuam/settings.py
import os  # Agregar al inicio
```

2. **Database error:**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres
# Debe mostrar "Up"
```

3. **Secret key:**
```bash
# Verificar archivo .env
cat .env | grep SECRET_KEY
# Debe tener un valor
```

**Reconstruir contenedor:**
```bash
docker-compose up -d --build django-core
```

---

### **Problema 4: Error al crear superusuario**

**Síntoma:**
```
django.db.utils.OperationalError: FATAL: database "nuam_db" does not exist
```

**Solución:**

```bash
# Aplicar migraciones primero
docker exec -it nuam-django-core python manage.py migrate

# Luego crear superusuario
docker exec -it nuam-django-core python manage.py createsuperuser
```

---

### **Problema 5: Advertencia SSL persistente**

**Síntoma:**
El navegador siempre muestra advertencia de certificado.

**Solución:**

**Opción 1: Usar HTTP (sin SSL)**
```
http://localhost/
```

**Opción 2: Instalar certificado en sistema (Avanzado)**

**Windows:**
1. Abrir `certs/nuam.crt` con doble click
2. Click "Instalar Certificado..."
3. Seleccionar "Usuario actual"
4. Seleccionar "Colocar todos los certificados en el siguiente almacén"
5. Click "Examinar" → Seleccionar "Entidades de certificación raíz de confianza"
6. Click "Siguiente" → "Finalizar"
7. Reiniciar navegador

**macOS:**
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/nuam.crt
```

**Linux:**
```bash
sudo cp certs/nuam.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

---

### **Problema 6: Carga masiva falla**

**Síntoma:**
Todos los registros aparecen como fallidos.

**Soluciones:**

1. **Verificar columnas:**
```
Las columnas deben llamarse exactamente:
- corredor_dueno (no "Corredor Dueño" ni "corredor-dueno")
- instrumento
- mercado
- divisa
- valor_historico
- fecha_pago
```

2. **Verificar formato de fecha:**
```
✅ Correcto: 31/12/2025
❌ Incorrecto: 12/31/2025 (formato US)
❌ Incorrecto: 2025-12-31 (formato ISO)
```

3. **Verificar divisa:**
```
✅ Válidas: CLP, USD, EUR, COP, PEN, MXN, BRL, ARS
❌ Inválidas: PESOS, DOLARES, xxx
```

4. **Descargar plantilla:**
Usar la plantilla oficial del sistema para asegurar formato correcto.

---

### **Problema 7: Dashboard React no carga**

**Síntoma:**
Página en blanco en `http://localhost:3000/`

**Solución:**

```bash
# Verificar que el contenedor esté corriendo
docker-compose ps dashboard-frontend

# Ver logs
docker-compose logs -f dashboard-frontend

# Reiniciar contenedor
docker-compose restart dashboard-frontend

# Si persiste, reconstruir
docker-compose up -d --build dashboard-frontend
```

---

### **Problema 8: Conversor de divisas no funciona**

**Síntoma:**
Widget muestra "Error al obtener la tasa"

**Causas posibles:**

1. **Sin conexión a Internet:**
El widget necesita conexión a ExchangeRate-API.

2. **API externa caída:**
Esperar unos minutos y recargar página.

3. **Currency Service no está corriendo:**
```bash
docker-compose ps currency-service
# Debe mostrar "Up"

# Si no está corriendo:
docker-compose up -d currency-service
```

---

## 14. **MANTENIMIENTO DEL SISTEMA**

### **Detener el Sistema**

```bash
# Detener todos los servicios
docker-compose down

# Los datos se mantienen en volúmenes
```

### **Reiniciar el Sistema**

```bash
# Levantar nuevamente
docker-compose up -d
```

### **Ver Uso de Recursos**

```bash
# Ver uso de CPU, RAM de cada contenedor
docker stats
```

### **Limpiar Sistema**

#### **Opción 1: Limpiar solo contenedores detenidos**
```bash
docker container prune
```

#### **Opción 2: Limpiar imágenes no usadas**
```bash
docker image prune
```

#### **Opción 3: Limpiar TODO (cuidado: borra volúmenes)**
```bash
# ⚠️ ADVERTENCIA: Borra TODOS los datos
docker-compose down -v
```

### **Backup de Base de Datos**

```bash
# Crear backup
docker exec nuam-postgres pg_dump -U nuam_user nuam_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i nuam-postgres psql -U nuam_user nuam_db < backup_20241209.sql
```

### **Ver Logs**

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f django-core

# Últimas 100 líneas
docker-compose logs --tail=100 django-core
```

### **Actualizar el Sistema**

```bash
# Obtener últimos cambios desde GitHub
git pull origin main

# Reconstruir imágenes
docker-compose up -d --build

# Aplicar migraciones
docker exec -it nuam-django-core python manage.py migrate

# Recolectar estáticos
docker exec -it nuam-django-core python manage.py collectstatic --noinput
```

---

## 15. **PREGUNTAS FRECUENTES (FAQ)**

### **¿Puedo usar el sistema en producción?**

Sí, pero debes:
1. Cambiar `DEBUG=False` en `.env`
2. Usar un `SECRET_KEY` seguro
3. Configurar certificados SSL reales (Let's Encrypt)
4. Usar contraseñas fuertes para PostgreSQL
5. Configurar firewall
6. Usar un servidor WSGI (Gunicorn) en lugar de `runserver`

### **¿Cuántas calificaciones puedo cargar?**

- **Manualmente**: Ilimitadas
- **Carga masiva**: Hasta 10,000 por archivo
- **Base de datos**: Millones (limitado por espacio en disco)

### **¿Qué navegadores son compatibles?**

✅ **Recomendados:**
- Google Chrome 90+
- Microsoft Edge 90+
- Firefox 88+
- Safari 14+

❌ **No soportados:**
- Internet Explorer (cualquier versión)
- Navegadores antiguos (>2 años)

### **¿Necesito conexión a Internet?**

- **Sí**, para:
  - Conversión de divisas (ExchangeRate-API)
  - Valor UF (API CMF)
  - Gráficos del Dashboard React

- **No**, para:
  - Crear/editar calificaciones
  - Cargas masivas
  - Administración
  - API REST local

### **¿Puedo cambiar el puerto?**

Sí, editar `docker-compose.yml`:

```yaml
apache2:
  ports:
    - "8080:80"   # Cambiar primer número
    - "8443:443"
```

Luego acceder en: `http://localhost:8080/`

### **¿Cómo agrego más usuarios?**

**Opción 1: Admin Django**
1. Ir a http://localhost/admin/
2. Login con superusuario
3. Usuarios → Agregar usuario
4. Completar formulario

**Opción 2: Terminal**
```bash
docker exec -it nuam-django-core python manage.py createsuperuser
```

### **¿Los datos se pierden al detener Docker?**

No. Los datos se guardan en **volúmenes** de Docker que persisten.

Solo se pierden si ejecutas:
```bash
docker-compose down -v  # ⚠️ El -v borra volúmenes
```

### **¿Puedo cambiar el idioma?**

El sistema está en español. Para agregar otro idioma:

1. Editar `nuam/settings.py`:
```python
LANGUAGE_CODE = 'en-us'  # Para inglés
```

2. Reiniciar contenedor:
```bash
docker-compose restart django-core
```

### **¿Cómo reporto un bug?**

1. Ir a: https://github.com/DykeByte/Nuam-main/issues
2. Click en "New Issue"
3. Describir el problema
4. Incluir logs si es posible

### **¿Dónde encuentro más ayuda?**

- **README.md**: Referencia técnica completa
- **FRONTEND_UPGRADE_SUMMARY.md**: Detalles del frontend
- **APACHE2_IMPLEMENTATION_SUMMARY.md**: Detalles de Apache2
- **GitHub Issues**: Reportar problemas
- **Documentación oficial Django**: https://docs.djangoproject.com/

---

## 🎓 **CONCLUSIÓN**

¡Felicitaciones! Ahora sabes cómo:

✅ Instalar NUAM desde GitHub
✅ Configurar el sistema con Docker
✅ Navegar por la interfaz
✅ Crear y gestionar calificaciones
✅ Realizar cargas masivas desde Excel
✅ Usar el dashboard con gráficos
✅ Integrar vía API REST
✅ Convertir divisas en tiempo real
✅ Resolver problemas comunes
✅ Mantener el sistema

---

## 📞 **SOPORTE**

**GitHub**: [https://github.com/DykeByte/Nuam-main](https://github.com/DykeByte/Nuam-main)
**Issues**: [https://github.com/DykeByte/Nuam-main/issues](https://github.com/DykeByte/Nuam-main/issues)

---

**Made with ❤️ by DykeByte**

*Manual de Usuario NUAM v2.0.0 - Última actualización: Diciembre 2024*
