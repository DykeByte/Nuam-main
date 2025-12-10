# api/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from accounts.models import Perfil
import pandas as pd
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from api.services import registrar_log
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from kafka_app.producers import calificacion_producer
# from api.utils import obtener_estadisticas_dashboard
from api.currency_converter import CurrencyConverter, convert_currency

from nuam.service_client import (
    calificaciones_service,
    conversion_service,
    dashboard_service,
    validate_jwt_with_auth_service
)

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from api.models import CargaMasiva


import logging

# Configurar logger
logger = logging.getLogger('api')


from api.utils.error_recovery import (
    auto_retry,
    with_transaction_rollback,
    ErrorRecoveryManager
)

from api.models import (
    CalificacionTributaria, 
    CargaMasiva, 
    LogOperacion,
    Calificacion,
    Divisa,
    LogAuditoria
)
from api.serializers import (
    CalificacionTributariaSerializer,
    CalificacionTributariaListSerializer,
    CalificacionTributariaCreateSerializer,
    CargaMasivaSerializer,
    CargaMasivaDetailSerializer,
    CargaMasivaUploadSerializer,
    LogOperacionSerializer,
    LogAuditoriaSerializer,
    CalificacionSerializer,
    DivisaSerializer,
    PerfilSerializer,
    RegistroSerializer,
    UserSerializer,
    UserDetailSerializer,
    EstadisticasSerializer,
)

from api.excel_handler import ExcelHandler

# ===============================
# Paginación Personalizada
# ===============================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===============================
# ViewSets
# ===============================

class PerfilViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar perfiles de usuario.
    
    list: Obtener lista de perfiles
    retrieve: Obtener un perfil específico
    create: Crear un nuevo perfil
    update: Actualizar un perfil
    delete: Eliminar un perfil
    """
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        logger.debug(f"📋 API: Obteniendo perfiles - Usuario: {self.request.user.username}")
        return Perfil.objects.all()


class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar calificaciones tributarias.
    
    Permite operaciones CRUD completas sobre calificaciones tributarias.
    Soporta filtrado, búsqueda y ordenamiento.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mercado', 'divisa', 'es_local', 'tipo_sociedad']
    search_fields = ['corredor_dueno', 'instrumento', 'descripcion', 'rut_es_el_manual']
    ordering_fields = ['created_at', 'fecha_pago', 'valor_historico']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Queryset optimizado con select_related y prefetch_related
        para reducir queries a la base de datos.
        """
        user = self.request.user
        
        # Optimización con select_related para ForeignKeys
        queryset = CalificacionTributaria.objects.filter(usuario=user).select_related(
            'usuario',           # Traer datos del usuario en el mismo query
            'carga_masiva',      # Traer datos de carga masiva si existe
        ).prefetch_related(
            'logs_operacion',    # Precarga logs de operación relacionados
        ).only(
            # Seleccionar solo campos necesarios para listado
            'id', 'corredor_dueno', 'instrumento', 'mercado', 
            'divisa', 'valor_historico', 'fecha_pago', 'created_at',
            'usuario__username', 'carga_masiva__id', 'carga_masiva__tipo_carga'
        )
        
        logger.debug(f"📋 API: Calificaciones para {user.username} - Total: {queryset.count()}")
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Listado con caché para mejorar performance en consultas frecuentes
        """
        # Generar cache key basada en parámetros de query
        query_params = request.GET.urlencode()
        cache_key = f'calificaciones_list_{request.user.id}_{query_params}'
        
        # Intentar obtener del cache
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"💾 Cache HIT: {cache_key}")
            return Response(cached_data)
        
        # Si no está en cache, ejecutar query normal
        logger.debug(f"🔍 Cache MISS: {cache_key}")
        response = super().list(request, *args, **kwargs)
        
        # Guardar en cache por 5 minutos
        if response.status_code == 200:
            cache.set(cache_key, response.data, 300)
            logger.debug(f"💾 Guardado en cache: {cache_key}")
        
        return response
    
    def create(self, request, *args, **kwargs):
        """
        Crear y limpiar cache relacionado
        """
        response = super().create(request, *args, **kwargs)
        
        # Invalidar cache después de crear
        if response.status_code == 201:
            cache_pattern = f'calificaciones_list_{request.user.id}_*'
            # Limpiar todo el cache del usuario
            cache.delete_many(cache.keys(cache_pattern))
            logger.info(f"🧹 Cache limpiado: {cache_pattern}")
        
        return response
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar y limpiar cache relacionado
        """
        response = super().update(request, *args, **kwargs)
        
        # Invalidar cache después de actualizar
        if response.status_code == 200:
            cache_pattern = f'calificaciones_list_{request.user.id}_*'
            cache.delete_many(cache.keys(cache_pattern))
            logger.info(f"🧹 Cache limpiado: {cache_pattern}")
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar y limpiar cache relacionado
        """
        response = super().destroy(request, *args, **kwargs)
        
        # Invalidar cache después de eliminar
        if response.status_code == 204:
            cache_pattern = f'calificaciones_list_{request.user.id}_*'
            cache.delete_many(cache.keys(cache.keys(cache_pattern)))
            logger.info(f"🧹 Cache limpiado: {cache_pattern}")
        
        return response



    def get_serializer_class(self):
        if self.action == 'list':
            return CalificacionTributariaListSerializer
        elif self.action == 'create':
            return CalificacionTributariaCreateSerializer
        return CalificacionTributariaSerializer

    def perform_create(self, serializer):
        logger.info(f"➕ API: Creando calificación - Usuario: {self.request.user.username}")
        try:
            obj = serializer.save(usuario=self.request.user)
            registrar_log(self.request.user, "CREATE", obj)
            logger.info(f"✅ API: Calificación creada - ID: {obj.id}")
        except Exception as e:
            logger.error(f"❌ API: Error creando calificación: {str(e)}", exc_info=True)
            raise

    def perform_update(self, serializer):
        instance = self.get_object()
        logger.info(f"✏️ API: Actualizando calificación {instance.id}")
        try:
            antes = self.get_serializer(instance).data
            obj = serializer.save()
            despues = self.get_serializer(obj).data
            registrar_log(self.request.user, "UPDATE", obj, antes, despues)
            logger.info(f"✅ API: Calificación {obj.id} actualizada")
        except Exception as e:
            logger.error(f"❌ API: Error actualizando calificación: {str(e)}", exc_info=True)
            raise

    def perform_destroy(self, instance):
        logger.info(f"🗑️ API: Eliminando calificación {instance.id}")
        try:
            registrar_log(self.request.user, "DELETE", instance)
            instance.delete()
            logger.info(f"✅ API: Calificación eliminada")
        except Exception as e:
            logger.error(f"❌ API: Error eliminando calificación: {str(e)}", exc_info=True)
            raise
    
    @action(detail=False, methods=['get'])
    def por_mercado(self, request):
        """Agrupa calificaciones por mercado"""
        logger.info(f"📊 API: Agrupación por mercado - Usuario: {request.user.username}")
        queryset = self.get_queryset()
        data = queryset.values('mercado').annotate(
            total=Count('id'),
            valor_total=Sum('valor_historico')
        ).order_by('-total')
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def por_divisa(self, request):
        """Agrupa calificaciones por divisa"""
        logger.info(f"📊 API: Agrupación por divisa - Usuario: {request.user.username}")
        queryset = self.get_queryset()
        data = queryset.values('divisa').annotate(
            total=Count('id'),
            valor_total=Sum('valor_historico')
        ).order_by('-total')
        return Response(data)
    
    @with_transaction_rollback()
    def perform_create(self, serializer):
        """Crear con rollback automático si falla"""
        logger.info(f"➕ API: Creando calificación - Usuario: {self.request.user.username}")
        
        try:
            # Guardar en BD
            obj = serializer.save(usuario=self.request.user)
            
            # Kafka de forma segura (no crítico)
            ErrorRecoveryManager.safe_kafka_publish(
                calificacion_producer.publish_calificacion_creada,
                {
                    'id': obj.id,
                    'instrumento': obj.instrumento,
                    'mercado': obj.mercado,
                    'divisa': obj.divisa,
                    'valor_historico': str(obj.valor_historico) if obj.valor_historico else None,
                    'usuario': self.request.user.username
                }
            )
            
            ErrorRecoveryManager.safe_kafka_publish(
                auditoria_producer.publish_log,
                usuario=self.request.user.username,
                accion='CALIFICACION_CREADA',
                recurso=f'calificacion/{obj.id}',
                detalles={'instrumento': obj.instrumento}
            )
            
            # Log tradicional
            registrar_log(self.request.user, "CREATE", obj)
            logger.info(f"✅ API: Calificación creada - ID: {obj.id}")
            
        except Exception as e:
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(
                f"❌ API: Error crítico creando calificación:\n"
                f"Tipo: {exc_type.__name__}\n"
                f"Mensaje: {str(e)}\n"
                f"Traceback:\n{''.join(traceback.format_tb(exc_traceback))}"
            )
            raise


class CargaMasivaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cargas masivas.
    
    Incluye endpoint especial para subir archivos Excel.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_carga', 'mercado', 'estado']
    ordering_fields = ['fecha_inicio', 'registros_procesados']
    ordering = ['-fecha_inicio']

    def get_queryset(self):
        """
        Queryset optimizado con select_related y annotations
        """
        user = self.request.user
        
        # Optimización con select_related y anotaciones
        queryset = CargaMasiva.objects.filter(iniciado_por=user).select_related(
            'iniciado_por'  # Traer datos del usuario en mismo query
        ).prefetch_related(
            'calificaciones_tributarias',  # Precarga calificaciones relacionadas
            'logs_operacion',              # Precarga logs
        ).annotate(
            total_calificaciones=models.Count('calificaciones_tributarias')
        )
        
        logger.debug(f"📋 API: Cargas para {user.username} - Total: {queryset.count()}")
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CargaMasivaDetailSerializer
        elif self.action == 'upload':
            return CargaMasivaUploadSerializer
        return CargaMasivaSerializer

    def perform_create(self, serializer):
        logger.info(f"➕ API: Creando carga masiva - Usuario: {self.request.user.username}")
        try:
            obj = serializer.save(iniciado_por=self.request.user)
            registrar_log(self.request.user, "CREATE", None, datos_nuevos={"carga_id": obj.id})
            logger.info(f"✅ API: Carga masiva creada - ID: {obj.id}")
        except Exception as e:
            logger.error(f"❌ API: Error creando carga masiva: {str(e)}", exc_info=True)
            raise
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Endpoint para subir archivos Excel y procesarlos.
        
        POST /api/v1/cargas/upload/
        Body: multipart/form-data
          - archivo: File
          - tipo_carga: FACTORES | MONITOR
          - mercado: LOCAL | INTERNACIONAL
        """
        logger.info(f"📤 API: Upload de archivo - Usuario: {request.user.username}")
        
        serializer = CargaMasivaUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"❌ API: Validación fallida - {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            archivo = serializer.validated_data['archivo']
            tipo_carga = serializer.validated_data['tipo_carga']
            mercado = serializer.validated_data['mercado']
            
            logger.info(f"✅ Archivo válido: {archivo.name}")
            
            # Procesar con ExcelHandler
            handler = ExcelHandler(archivo, tipo_carga, request.user)
            handler.mercado = mercado
            
            carga = handler.procesar()
            
            logger.info(f"✅ Carga procesada - ID: {carga.id}")
            
            return Response({
                'success': True,
                'message': 'Archivo procesado correctamente',
                'data': CargaMasivaDetailSerializer(carga).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de cargas"""
        logger.info(f"📊 API: Estadísticas de cargas - Usuario: {request.user.username}")
        queryset = self.get_queryset()
        
        data = {
            'total_cargas': queryset.count(),
            'completadas': queryset.filter(estado='COMPLETADO').count(),
            'con_errores': queryset.filter(estado='COMPLETADO_CON_ERRORES').count(),
            'procesando': queryset.filter(estado='PROCESANDO').count(),
            'total_registros_procesados': queryset.aggregate(Sum('registros_procesados'))['registros_procesados__sum'] or 0,
            'total_exitosos': queryset.aggregate(Sum('registros_exitosos'))['registros_exitosos__sum'] or 0,
            'total_fallidos': queryset.aggregate(Sum('registros_fallidos'))['registros_fallidos__sum'] or 0,
        }
        
        return Response(data)


class LogOperacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para logs de operaciones.
    """
    serializer_class = LogOperacionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['operacion']
    ordering = ['-fecha_hora']

    def get_queryset(self):
        return LogOperacion.objects.filter(usuario=self.request.user)


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para logs de auditoría.
    """
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['accion', 'modelo']
    ordering = ['-timestamp']

    def get_queryset(self):
        return LogAuditoria.objects.filter(usuario=self.request.user)


class CalificacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para calificaciones generales (crediticias).
    """
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_calificacion', 'activo']
    search_fields = ['entidad', 'agencia_calificadora']
    ordering = ['-fecha_calificacion']


class DivisaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar divisas.
    """
    queryset = Divisa.objects.filter(activo=True)
    serializer_class = DivisaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']


# ===============================
# API Views (Function-Based)
# ===============================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Obtiene estadísticas generales del dashboard.
    
    GET /api/v1/dashboard/stats/
    """
    logger.info(f"📊 API: Dashboard stats - Usuario: {request.user.username}")
    try:
        stats = obtener_estadisticas_dashboard(request.user)
        serializer = EstadisticasSerializer(stats)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"❌ API: Error obteniendo stats: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def registro_api(request):
    """
    Registro de nuevos usuarios vía API.
    
    POST /api/v1/auth/registro/
    Body: {
        "username": "string",
        "email": "string",
        "password": "string",
        "password_confirm": "string",
        "first_name": "string",
        "last_name": "string"
    }
    """
    logger.info(f"➕ API: Registro de usuario vía API")
    
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        logger.info(f"✅ API: Usuario registrado: {user.username}")
        return Response({
            'success': True,
            'message': 'Usuario creado correctamente',
            'data': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    else:
        logger.warning(f"❌ API: Registro fallido - Errores: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    """
    Obtiene el perfil del usuario autenticado.
    
    GET /api/v1/auth/me/
    """
    logger.info(f"👤 API: Perfil de usuario - {request.user.username}")
    serializer = UserDetailSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(["GET"])
def health_check(request):
    """
    Health check del API.
    
    GET /api/v1/health/
    """
    logger.debug("🏥 API: Health check ejecutado")
    return Response({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })


@login_required
def nueva_carga_masiva(request):
    """
    Vista para procesar carga masiva de datos
    MODIFICA VISTA EXISTENTE PARA AÑADIR KAFKA
    """
    if request.method == 'POST':
        archivo = request.FILES.get('archivo_excel')
        
        if not archivo:
            return JsonResponse({'error': 'No se proporcionó archivo'}, status=400)
        
        # Crear registro de carga
        carga = CargaMasiva.objects.create(
            usuario=request.user,
            nombre_archivo=archivo.name,
            estado='PROCESANDO'
        )
        
        # 🔥 KAFKA: Publicar evento de inicio
        carga_masiva_producer.publish_carga_iniciada(
            carga_id=carga.id,
            usuario=request.user.username,
            filename=archivo.name
        )
        
        # 🔥 KAFKA: Registrar auditoría
        auditoria_producer.publish_log(
            usuario=request.user.username,
            accion='CARGA_MASIVA_INICIADA',
            recurso=f'carga_masiva/{carga.id}',
            detalles={'filename': archivo.name}
        )
        
        try:
            # Medir tiempo de procesamiento
            start_time = time.time()
            
            # Procesar archivo Excel (tu lógica existente)
            df = pd.read_excel(archivo)
            
            total_registros = len(df)
            exitosos = 0
            fallidos = 0
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Crear calificación (tu lógica existente)
                    calificacion = CalificacionTributaria.objects.create(
                        nemotecnico=row['nemotecnico'],
                        fecha_valor=row['fecha_valor'],
                        divisa=row['divisa'],
                        valor_nominal_usd=row['valor_nominal_usd'],
                        # ... otros campos
                    )
                    
                    # 🔥 KAFKA: Publicar evento de calificación creada
                    calificacion_producer.publish_calificacion_creada({
                        'id': calificacion.id,
                        'nemotecnico': calificacion.nemotecnico,
                        'divisa': calificacion.divisa,
                        'valor_nominal_usd': float(calificacion.valor_nominal_usd),
                        'carga_masiva_id': carga.id
                    })
                    
                    exitosos += 1
                    
                except Exception as e:
                    fallidos += 1
                    print(f"Error en fila {index}: {e}")
            
            # Calcular duración
            duracion = time.time() - start_time
            
            # Actualizar registro de carga
            carga.total_registros = total_registros
            carga.exitosos = exitosos
            carga.fallidos = fallidos
            carga.estado = 'COMPLETADO'
            carga.save()
            
            # 🔥 KAFKA: Publicar evento de carga completada
            carga_masiva_producer.publish_carga_completada(
                carga_id=carga.id,
                total_registros=total_registros,
                exitosos=exitosos,
                fallidos=fallidos,
                duracion_segundos=duracion
            )
            
            # 🔥 KAFKA: Enviar notificación de éxito
            notificacion_producer.publish_notificacion(
                usuario_id=request.user.id,
                tipo='IN_APP',
                mensaje=f'Carga masiva completada: {exitosos} exitosos, {fallidos} fallidos',
                prioridad='normal'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Carga completada: {exitosos} exitosos, {fallidos} fallidos',
                'carga_id': carga.id,
                'duracion_segundos': round(duracion, 2)
            })
            
        except Exception as e:
            # Actualizar estado de carga
            carga.estado = 'FALLIDO'
            carga.save()
            
            # 🔥 KAFKA: Publicar evento de carga fallida
            carga_masiva_producer.publish_carga_fallida(
                carga_id=carga.id,
                error=str(e)
            )
            
            # 🔥 KAFKA: Notificación de error
            notificacion_producer.publish_notificacion(
                usuario_id=request.user.id,
                tipo='EMAIL',
                mensaje=f'Error en carga masiva: {str(e)}',
                prioridad='high'
            )
            
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return render(request, 'api/nueva_carga.html')




@login_required
def actualizar_calificacion(request, calificacion_id):
    """
    Vista para actualizar calificación
    EJEMPLO DE INTEGRACIÓN CON KAFKA
    """
    if request.method == 'POST':
        try:
            calificacion = CalificacionTributaria.objects.get(id=calificacion_id)
            
            # Guardar valores anteriores para cambios
            cambios = {}
            
            # Actualizar campos (ejemplo)
            if 'valor_nominal_usd' in request.POST:
                old_value = calificacion.valor_nominal_usd
                new_value = request.POST['valor_nominal_usd']
                if old_value != new_value:
                    cambios['valor_nominal_usd'] = {
                        'old': float(old_value),
                        'new': float(new_value)
                    }
                    calificacion.valor_nominal_usd = new_value
            
            calificacion.save()
            
            # 🔥 KAFKA: Publicar evento de actualización
            if cambios:
                calificacion_producer.publish_calificacion_actualizada(
                    calificacion_id=calificacion.id,
                    cambios=cambios
                )
                
                # 🔥 KAFKA: Registrar auditoría
                auditoria_producer.publish_log(
                    usuario=request.user.username,
                    accion='CALIFICACION_ACTUALIZADA',
                    recurso=f'calificacion/{calificacion.id}',
                    detalles={'cambios': cambios}
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Calificación actualizada'
            })
            
        except CalificacionTributaria.DoesNotExist:
            return JsonResponse({
                'error': 'Calificación no encontrada'
            }, status=404)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ===============================
# API de Conversión de Divisas
# ===============================



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_tasa_cambio(request):
    """
    Obtiene la tasa de cambio entre dos divisas.
    
    GET /api/v1/divisas/tasa/?from=USD&to=CLP
    
    Response:
    {
        "success": true,
        "from_currency": "USD",
        "to_currency": "CLP",
        "rate": "950.50",
        "timestamp": "2025-11-19T18:30:00Z"
    }
    """
    from_currency = request.GET.get('from', 'USD')
    to_currency = request.GET.get('to', 'CLP')
    
    logger.info(f"📊 API: Solicitud de tasa {from_currency}/{to_currency} - Usuario: {request.user.username}")
    
    try:
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            return Response({
                'success': False,
                'error': f'No se pudo obtener tasa de cambio para {from_currency}/{to_currency}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            'success': True,
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'rate': str(rate),
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo tasa: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convertir_monto(request):
    """
    Convierte un monto de una divisa a otra.
    
    POST /api/v1/divisas/convertir/
    Body:
    {
        "amount": "100.00",
        "from_currency": "USD",
        "to_currency": "CLP"
    }
    
    Response:
    {
        "success": true,
        "amount": "100.00",
        "from_currency": "USD",
        "to_currency": "CLP",
        "converted_amount": "95050.00",
        "rate": "950.50",
        "timestamp": "2025-11-19T18:30:00Z"
    }
    """
    logger.info(f"💱 API: Solicitud de conversión - Usuario: {request.user.username}")
    
    try:
        amount = Decimal(request.data.get('amount', '0'))
        from_currency = request.data.get('from_currency', 'USD')
        to_currency = request.data.get('to_currency', 'CLP')
        
        if amount <= 0:
            return Response({
                'success': False,
                'error': 'El monto debe ser mayor a cero'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener tasa
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)
        if rate is None:
            return Response({
                'success': False,
                'error': f'No se pudo obtener tasa de cambio'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Convertir
        converted_amount = CurrencyConverter.convert(amount, from_currency, to_currency)
        
        if converted_amount is None:
            return Response({
                'success': False,
                'error': 'Error en la conversión'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"✅ Conversión exitosa: {amount} {from_currency} = {converted_amount} {to_currency}")
        
        return Response({
            'success': True,
            'amount': str(amount),
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'converted_amount': str(converted_amount),
            'rate': str(rate),
            'timestamp': timezone.now().isoformat()
        })
        
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Error en datos de conversión: {e}")
        return Response({
            'success': False,
            'error': 'Datos inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"❌ Error convirtiendo monto: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_todas_tasas(request):
    """
    Obtiene todas las tasas de cambio para una divisa base.
    
    GET /api/v1/divisas/tasas/?base=USD
    
    Response:
    {
        "success": true,
        "base_currency": "USD",
        "rates": {
            "CLP": "950.50",
            "EUR": "0.92",
            "COP": "4100.00",
            ...
        },
        "timestamp": "2025-11-19T18:30:00Z"
    }
    """
    base_currency = request.GET.get('base', 'USD')
    
    logger.info(f"📊 API: Solicitud de todas las tasas para {base_currency} - Usuario: {request.user.username}")
    
    try:
        rates = CurrencyConverter.get_all_rates(base_currency)
        
        # Convertir a string para JSON
        rates_str = {k: str(v) for k, v in rates.items()}
        
        return Response({
            'success': True,
            'base_currency': base_currency.upper(),
            'rates': rates_str,
            'count': len(rates_str),
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo todas las tasas: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# AJAX widget

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def obtener_tasa_ajax(request):
    """
    Endpoint para AJAX sin JWT (usa sesión de Django).
    GET /api/v1/divisas/tasa-ajax/?from=USD&to=CLP
    """
    from_currency = request.GET.get('from', 'USD')
    to_currency = request.GET.get('to', 'CLP')
    
    try:
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            return Response({
                'success': False,
                'error': 'No se pudo obtener tasa'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            'success': True,
            'from': from_currency.upper(),
            'to': to_currency.upper(),
            'rate': float(rate),
            'formatted_rate': f"{rate:,.2f}",
        })
        
    except Exception as e:
        logger.error(f"❌ Error en tasa AJAX: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# api/views.py (agregar al final)
import requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_historico_divisa(request, currency):
    """
    Obtiene histórico desde Currency Service
    """
    try:
        response = requests.get(
            f'http://currency-service:8001/api/v1/rates/history/{currency}',
            params={'days': 30},
            timeout=10
        )
        response.raise_for_status()
        return Response(response.json())
    except Exception as e:
        logger.error(f"Error consultando currency service: {e}")
        return Response(
            {'error': 'Currency service no disponible'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    

# ==============================================
# API VIEW
# ==============================================

@api_view(['GET'])
@permission_classes([AllowAny])
def system_stats(request):
    """
    Endpoint para obtener estadísticas del sistema
    VERSIÓN SIN LogOperacion
    """
    try:
        # Fecha actual
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=7)
        inicio_mes = hoy - timedelta(days=30)
        
        # Estadísticas de archivos (CargaMasiva)
        archivos_procesados = CargaMasiva.objects.filter(
            estado='completado'
        ).count()
        archivos_pendientes = CargaMasiva.objects.filter(
            estado='pendiente'
        ).count()
        archivos_con_error = CargaMasiva.objects.filter(
            estado='error'
        ).count()
        
        # Total de archivos como proxy de operaciones
        total_operaciones = CargaMasiva.objects.count()
        operaciones_hoy = CargaMasiva.objects.filter(
            fecha_creacion__date=hoy
        ).count()
        operaciones_semana = CargaMasiva.objects.filter(
            fecha_creacion__date__gte=inicio_semana
        ).count()
        operaciones_mes = CargaMasiva.objects.filter(
            fecha_creacion__date__gte=inicio_mes
        ).count()
        
        # Estadísticas de usuarios
        usuarios_activos = User.objects.filter(is_active=True).count()
        usuarios_registrados = User.objects.count()
        
        stats = {
            # Operaciones (basadas en CargaMasiva)
            'total_operaciones': total_operaciones,
            'operaciones_hoy': operaciones_hoy,
            'operaciones_semana': operaciones_semana,
            'operaciones_mes': operaciones_mes,
            
            # Usuarios
            'usuarios_activos': usuarios_activos,
            'usuarios_registrados': usuarios_registrados,
            
            # Archivos
            'archivos_procesados': archivos_procesados,
            'archivos_pendientes': archivos_pendientes,
            'archivos_con_error': archivos_con_error,
            
            # Timestamp
            'timestamp': timezone.now().isoformat(),
        }
        
        logger.info(f"📊 Stats solicitadas: {stats}")
        return Response(stats, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return Response(
            {'error': 'Error obteniendo estadísticas del sistema'},
            status=500
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    try:
        from nuam.currency_client import currency_service
        currency_service_ok = currency_service.health_check()
    except:
        currency_service_ok = False
    
    try:
        User.objects.count()
        db_ok = True
    except:
        db_ok = False
    
    status_code = 200 if (currency_service_ok and db_ok) else 503
    
    return Response({
        'status': 'healthy' if status_code == 200 else 'unhealthy',
        'database': 'ok' if db_ok else 'error',
        'currency_service': 'ok' if currency_service_ok else 'error',
        'timestamp': timezone.now().isoformat()
    }, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def currency_proxy(request):
    """Proxy para Currency Service"""
    try:
        from nuam.currency_client import currency_service
        
        from_currency = request.GET.get('from', 'USD')
        to_currency = request.GET.get('to', 'CLP')
        
        data = currency_service.get_current_rate(from_currency, to_currency)
        
        if data:
            return Response(data, status=200)
        else:
            return Response(
                {'error': 'No se pudo obtener tasa de cambio'},
                status=503
            )
    except Exception as e:
        logger.error(f"Error en currency_proxy: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_data(request):
    """Endpoint completo para el dashboard"""
    try:
        from nuam.currency_client import currency_service
        
        # Stats del sistema
        stats_response = system_stats(request)
        stats = stats_response.data
        
        # Datos de monedas
        currency_summary = currency_service.get_dashboard_summary()
        
        return Response({
            'system_stats': stats,
            'currency_data': currency_summary,
            'timestamp': timezone.now().isoformat()
        }, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error en dashboard_data: {e}")
        return Response(
            {'error': 'Error obteniendo datos del dashboard'},
            status=500
        )