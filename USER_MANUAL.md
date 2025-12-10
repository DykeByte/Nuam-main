# NUAM - Manual de Usuario

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)

**Guía completa paso a paso para usar el Sistema de Gestión de Calificaciones Tributarias NUAM**

---

## 📋 **TABLA DE CONTENIDOS**

1. [Primeros Pasos](#primeros-pasos)
2. [Panel de Control](#panel-de-control)
3. [Búsqueda y Filtros Avanzados](#búsqueda-y-filtros-avanzados)
4. [Carga Masiva de Excel](#carga-masiva-de-excel)
5. [Progreso en Tiempo Real](#progreso-en-tiempo-real)
6. [Reporte de Errores](#reporte-de-errores)
7. [Gestión de Calificaciones](#gestión-de-calificaciones)
8. [Conversor de Divisas](#conversor-de-divisas)
9. [API REST](#api-rest)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 **PRIMEROS PASOS**

### **1. Acceder al Sistema**

1. Abrir navegador web (Chrome, Firefox, Safari, Edge)
2. Ir a: **http://localhost:8000** (o la URL de tu servidor)
3. Ver la página de login

### **2. Iniciar Sesión**

**Credenciales por defecto:**
- **Usuario**: `admin`
- **Contraseña**: `admin123`

**¿Olvidaste tu contraseña?**
- Contactar al administrador del sistema
- O usar el comando: `python manage.py changepassword usuario`

### **3. Primera Vista - Dashboard**

Después de iniciar sesión verás:
- **Estadísticas generales**: Calificaciones totales, cargas realizadas
- **Conversor de divisas**: Widget interactivo en tiempo real
- **Acciones rápidas**: Botones para nueva carga, ver calificaciones
- **Últimas cargas**: Historial reciente

---

## 🏠 **PANEL DE CONTROL**

### **Menú de Navegación**

```
┌─────────────────────────────────────┐
│  🏠 Home  📊 Calificaciones  📤 Cargas  📋 Logs  👤 Perfil
└─────────────────────────────────────┘
```

**🏠 Home**
- Dashboard con resumen general
- Conversor de divisas en tiempo real
- Acceso rápido a funciones principales

**📊 Calificaciones**
- Lista completa de calificaciones
- Búsqueda, filtros y ordenamiento
- CRUD (Crear, Leer, Actualizar, Eliminar)

**📤 Cargas**
- Historial de cargas masivas
- Estado de cada carga (Exitosas, Con errores, Fallidas)
- Detalles y reportes de errores

**📋 Logs**
- Auditoría de operaciones
- Historial de acciones del usuario
- Registro de cambios

**👤 Perfil**
- Información del usuario
- Cambio de contraseña
- Cerrar sesión

---

## 🔍 **BÚSQUEDA Y FILTROS AVANZADOS**

### **Paso 1: Acceder a Calificaciones**

Click en **"📊 Calificaciones"** en el menú superior

### **Paso 2: Búsqueda Rápida**

```
🔍 Buscar: [_____________] [🔍 Buscar]
```

**Puedes buscar por:**
- Corredor dueño
- Instrumento
- Mercado
- Cualquier texto en las notas o descripción

**Ejemplo:**
- Buscar `"BONOS"` → Encuentra todos los instrumentos con la palabra "bonos"
- Buscar `"JP Morgan"` → Encuentra todas las calificaciones de JP Morgan
- Buscar `"2025"` → Encuentra registros del año 2025

### **Paso 3: Filtros Avanzados**

Click en **"📊 Filtros Avanzados"** para expandir el panel:

```
┌────────────────────────────────────────┐
│ Mercado:  [ LOCAL ▼ ]                  │
│ Divisa:   [ CLP ▼ ]                    │
│ Fecha desde: [__/__/____]              │
│ Fecha hasta: [__/__/____]              │
│ [Aplicar Filtros] [Limpiar]           │
└────────────────────────────────────────┘
```

**Filtros disponibles:**
- **Mercado**: LOCAL, INTERNACIONAL
- **Divisa**: USD, CLP, EUR, COP, PEN, MXN, BRL, ARS
- **Rango de fechas**: Desde/Hasta fecha de pago

**Acciones:**
- **Aplicar Filtros**: Ejecuta la búsqueda con los filtros seleccionados
- **Limpiar**: Elimina todos los filtros y vuelve a mostrar todo

### **Paso 4: Ordenar Columnas**

Click en los encabezados de columna para ordenar:

| Columna | Acción | Resultado |
|---------|--------|-----------|
| **ID** | Click → ↑ | Orden ascendente (1, 2, 3...) |
| **ID** | Click nuevamente → ↓ | Orden descendente (100, 99, 98...) |
| **Fecha Pago** | Click → ↑ | Más antiguas primero |
| **Fecha Pago** | Click → ↓ | Más recientes primero |
| **Valor** | Click → ↑ | Menor a mayor |
| **Valor** | Click → ↓ | Mayor a menor |
| **Fecha Creación** | Click → ↑ | Más antiguas primero |
| **Fecha Creación** | Click → ↓ | Más recientes primero (Default) |

**Indicadores visuales:**
- ⇅ Columna ordenable
- ↑ Orden ascendente activo
- ↓ Orden descendente activo

### **Paso 5: Paginación**

En la parte inferior de la lista:

```
← Anterior | Página 1 de 10 | Siguiente →
Mostrando 1-50 de 500 resultados
```

**Cambiar resultados por página:**
```
Mostrar: [50 ▼] resultados por página
```

**Opciones disponibles:** 10, 25, 50, 100

**Navegación:**
- **← Anterior**: Ir a la página anterior
- **Números**: Click directo en número de página
- **Siguiente →**: Ir a la siguiente página

---

## 📤 **CARGA MASIVA DE EXCEL**

### **Paso 1: Preparar el Archivo Excel**

#### **Descargar Plantilla**

1. Ir a **"📤 Nueva Carga"**
2. Click en **"📥 Descargar Plantilla Excel"**
3. Se descarga un archivo `.xlsx` con dos hojas

#### **Estructura del Archivo**

**HOJA 1: Datos Principales**

| Columna | Tipo | Obligatorio | Ejemplo |
|---------|------|-------------|---------|
| corredor_dueno | Texto | ✅ | JP Morgan |
| instrumento | Texto | ✅ | BONOS-2025 |
| mercado | LOCAL/INTERNACIONAL | ✅ | LOCAL |
| divisa | Texto | ✅ | CLP |
| fecha_pago | Fecha | ❌ | 2025-12-31 |
| valor_historico | Decimal | ❌ | 1500000.50 |

**HOJA 2: Factores**

| Columna | Ejemplo |
|---------|---------|
| ID_Registro | 1 |
| Factor_8 | 0.123456 |
| Factor_9 | 0.234567 |
| ... | ... |
| Factor_37 | 0.987654 |

**⚠️ Reglas Importantes:**
- Fechas en formato: YYYY-MM-DD (ej: 2025-12-31)
- Valores decimales con punto (no coma): 1500000.50
- Divisas válidas: USD, CLP, EUR, COP, PEN, MXN, BRL, ARS

### **Paso 2: Subir el Archivo**

1. Ir a **"📤 Nueva Carga"**
2. Seleccionar archivo Excel
3. Elegir tipo de carga y mercado
4. Click en **"🚀 Procesar Carga"**

---

## ⏳ **PROGRESO EN TIEMPO REAL**

Después de subir el archivo, aparece un modal de progreso:

```
┌────────────────────────────────────────┐
│   ⏳ Procesando Carga...                │
│                                        │
│  [████████████░░░░░░░░] 65%            │
│                                        │
│   📝 Procesados: 650                   │
│   ✅ Exitosos:   645                   │
│   ❌ Fallidos:   5                     │
│                                        │
│   ⏱️ Tiempo transcurrido: 12s          │
└────────────────────────────────────────┘
```

**Características:**
- **Actualización automática**: Cada 2 segundos
- **Progreso visual**: Barra animada 0-100%
- **Estadísticas en vivo**: Actualizadas en tiempo real
- **Auto-reload**: Se recarga al completar

---

## ⚠️ **REPORTE DE ERRORES**

Si hay errores, verás una tabla detallada:

| Fila | Campo | Error | Valor Recibido | Sugerencia |
|------|-------|-------|----------------|------------|
| 15 | fecha_pago | Invalid date | 31/12/2025 | 💡 Formato esperado: YYYY-MM-DD |
| 23 | divisa | Invalid | PES | 💡 Divisas válidas: USD, CLP, EUR... |
| 47 | valor_historico | Not decimal | 1.500.000 | 💡 Debe ser número decimal válido |

### **Cómo Corregir Errores**

1. Abrir tu archivo Excel original
2. Ir a cada fila indicada
3. Corregir según la sugerencia
4. Guardar y volver a subir

---

## 📊 **GESTIÓN DE CALIFICACIONES**

### **Ver Calificación**
- Click en **"👁️ Ver"** para ver detalles completos

### **Crear Calificación**
- Click en **"+ Nueva Calificación"**
- Completar formulario
- Guardar

### **Editar Calificación**
- Click en **"✏️ Editar"**
- Modificar campos
- Guardar cambios

### **Eliminar Calificación**
- Click en **"🗑️ Eliminar"**
- Confirmar (no se puede deshacer)

---

## 💱 **CONVERSOR DE DIVISAS**

Widget en tiempo real en la página principal:

```
Amount: [100.00] USD → CLP
Result: 100.00 USD = 92,486.00 CLP
Rate: 1 USD = 924.86 CLP
```

**Divisas disponibles:** USD, EUR, CLP, COP, PEN, MXN, BRL, ARS, UF

---

## 🔌 **API REST**

### **Autenticación**

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### **Endpoints**

- `GET /api/v1/calificaciones/` - Listar
- `POST /api/v1/calificaciones/` - Crear
- `GET /accounts/cargas/{id}/progress/` - Ver progreso

**Documentación:** http://localhost:8000/swagger/

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **No puedo iniciar sesión**
```bash
python manage.py changepassword admin
```

### **La carga se queda en "Procesando"**
1. Esperar 5 minutos
2. Refrescar página (F5)
3. Revisar logs

### **Errores en Excel**
1. Descargar plantilla nueva
2. Verificar formato de fechas (YYYY-MM-DD)
3. Verificar decimales (punto, no coma)

### **Conversor no funciona**
```bash
curl http://localhost:8001/api/health/
docker-compose restart currency-service
```

---

## 📞 **SOPORTE**

- **GitHub**: [DykeByte/Nuam-main](https://github.com/DykeByte/Nuam-main)
- **Issues**: [Reportar problema](https://github.com/DykeByte/Nuam-main/issues)
- **README.md**: Documentación técnica completa

---

**NUAM v2.1.0** - Sistema de Gestión de Calificaciones Tributarias

*Made with ❤️ by DykeByte*
