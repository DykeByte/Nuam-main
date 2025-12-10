#!/bin/bash

echo "🚀 Iniciando proyecto NUAM con microservicios"
echo "=============================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Verificar que Docker esté corriendo
echo ""
print_status "Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# 2. Limpiar contenedores anteriores (opcional)
echo ""
read -p "¿Deseas limpiar contenedores anteriores? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deteniendo y eliminando contenedores anteriores..."
    docker-compose down -v
    print_status "Limpieza completada"
fi

# 3. Crear estructura de directorios necesaria
echo ""
print_status "Creando estructura de directorios..."
mkdir -p accounts/management/commands
mkdir -p api/management/commands
mkdir -p logs
touch accounts/management/__init__.py
touch accounts/management/commands/__init__.py
touch api/management/__init__.py
touch api/management/commands/__init__.py

# 4. Verificar que existe el archivo .env
echo ""
if [ ! -f .env ]; then
    print_warning "Archivo .env no encontrado, creando uno por defecto..."
    cat > .env << 'EOF'
DB_USER=nuam
DB_PASSWORD=nuam123
DB_NAME=nuam_user
DB_HOST=postgres
DB_PORT=5432
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_TOPIC_NAME=nuam-operations
EOF
    print_status "Archivo .env creado"
else
    print_status "Archivo .env encontrado"
fi

# 5. Construir imágenes
echo ""
print_status "Construyendo imágenes Docker..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    print_error "Error al construir las imágenes"
    exit 1
fi

# 6. Iniciar servicios base primero (PostgreSQL, Zookeeper, Kafka)
echo ""
print_status "Iniciando servicios base (PostgreSQL, Zookeeper, Kafka)..."
docker-compose up -d postgres zookeeper kafka

# 7. Esperar a que los servicios estén listos
echo ""
print_status "Esperando a que los servicios estén listos..."
echo "   - Esto puede tomar 30-60 segundos..."

# Esperar PostgreSQL
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U nuam > /dev/null 2>&1; then
        print_status "PostgreSQL está listo"
        break
    fi
    echo -n "."
    sleep 2
done

# Esperar Kafka
echo ""
print_status "Esperando a Kafka (puede tomar hasta 60 segundos)..."
sleep 30

# Verificar que Kafka está listo
for i in {1..20}; do
    if docker-compose exec -T kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
        print_status "Kafka está listo"
        break
    fi
    echo -n "."
    sleep 3
done

# 8. Iniciar servicios de aplicación
echo ""
print_status "Iniciando servicios de aplicación..."
docker-compose up -d currency-service web

# 9. Aplicar migraciones
echo ""
print_status "Aplicando migraciones de Django..."
sleep 10
docker-compose exec web python manage.py migrate

# 10. Crear superusuario (opcional)
echo ""
read -p "¿Deseas crear un superusuario de Django? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

# 11. Iniciar consumer de Kafka
echo ""
print_status "Iniciando Kafka consumer..."
docker-compose up -d kafka-consumer

# 12. Mostrar estado de servicios
echo ""
print_status "Estado de los servicios:"
docker-compose ps

# 13. Mostrar logs en tiempo real
echo ""
echo "=============================================="
print_status "¡Servicios iniciados exitosamente!"
echo ""
echo "URLs disponibles:"
echo "  - Django Admin: http://localhost:8000/admin/"
echo "  - API: http://localhost:8000/api/"
echo "  - Currency Service: http://localhost:8001/"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f [servicio]"
echo "  - Detener: docker-compose down"
echo "  - Reiniciar: docker-compose restart [servicio]"
echo ""
read -p "¿Deseas ver los logs en tiempo real? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi

