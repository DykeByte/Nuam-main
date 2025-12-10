FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el proyecto
COPY . .

# Crear directorio de logs
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Exponer puerto
EXPOSE 8000

# El comando se define en docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]