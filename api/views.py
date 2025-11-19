# api/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from accounts.models import Perfil
import pandas as pd
from django.contrib.auth.decorators import login_required
from api.services import registrar_log
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from kafka_app.producers import calificacion_producer
# from api.utils import obtener_estadisticas_dashboard



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
    MODIFICAR TU VISTA EXISTENTE PARA AÑADIR KAFKA
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


