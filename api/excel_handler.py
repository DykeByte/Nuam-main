# api/excel_handler.py - VERSIÓN COMPLETA CON KAFKA
import pandas as pd
from datetime import datetime
from django.utils import timezone
from api.models import CalificacionTributaria, CargaMasiva, LogOperacion
from api.kafka_producer import (
    publicar_evento_carga_iniciada, 
    publicar_evento_carga_completada,
    publicar_evento_calificacion_creada
)
import logging


logger = logging.getLogger(__name__)


class ExcelHandler:
    """Manejador para procesar archivos Excel con integración Kafka"""
    
    def __init__(self, archivo, tipo_carga, usuario):
        self.archivo = archivo
        self.tipo_carga = tipo_carga
        self.usuario = usuario
        self.mercado = None  # Se puede asignar después
        self.errores = []
        self.registros_exitosos = 0
        self.registros_fallidos = 0
        
        logger.info(f"📦 ExcelHandler creado:")
        logger.info(f"   - Archivo: {archivo.name}")
        logger.info(f"   - Tipo: {tipo_carga}")
        logger.info(f"   - Usuario: {usuario.username}")
        
    def procesar(self):
        """Procesa el archivo Excel y crea las calificaciones"""
        logger.info("🔄 Iniciando procesamiento de archivo...")
        
        carga = None
        
        try:
            # Leer el archivo Excel - HOJA 1: Datos Principales
            logger.info("📖 Leyendo archivo Excel (Hoja 1: Datos Principales)...")
            df_principales = pd.read_excel(self.archivo, sheet_name='Datos Principales')
            logger.info(f"✅ Hoja 1 leída: {len(df_principales)} filas, {len(df_principales.columns)} columnas")
            logger.info(f"   Columnas encontradas: {list(df_principales.columns)}")
            
            # Limpiar nombres de columnas (quitar espacios)
            df_principales.columns = df_principales.columns.str.strip()
            
            # Leer HOJA 2: Factores (si existe)
            df_factores = None
            try:
                logger.info("📖 Leyendo Hoja 2: Factores...")
                df_factores = pd.read_excel(self.archivo, sheet_name='Factores')
                df_factores.columns = df_factores.columns.str.strip()
                logger.info(f"✅ Hoja 2 leída: {len(df_factores)} filas, {len(df_factores.columns)} columnas")
                
                # Convertir ID_Registro a índice para fácil acceso
                if 'ID_Registro' in df_factores.columns:
                    df_factores = df_factores.set_index('ID_Registro')
                    logger.info(f"✅ Factores indexados por ID_Registro")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo leer hoja de factores: {str(e)}")
                df_factores = None
            
            # Crear el registro de carga masiva
            logger.info("💾 Creando registro de CargaMasiva...")
            carga = CargaMasiva.objects.create(
                iniciado_por=self.usuario,
                tipo_carga=self.tipo_carga,
                mercado=self.mercado or 'LOCAL',
                archivo_nombre=self.archivo.name,
                archivo_path='',
                registros_procesados=len(df_principales),
                estado='PROCESANDO'
            )
            logger.info(f"✅ CargaMasiva creada con ID: {carga.id}")
            
            # 🆕 PUBLICAR EVENTO KAFKA: Carga iniciada
            logger.info("📤 Publicando evento CARGA_INICIADA en Kafka...")
            try:
                publicar_evento_carga_iniciada(carga)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo publicar evento en Kafka: {str(e)}")
            
            # Procesar cada fila
            logger.info(f"🔄 Procesando {len(df_principales)} filas...")
            for index, row in df_principales.iterrows():
                try:
                    # Obtener factores correspondientes si existen
                    row_factores = None
                    if df_factores is not None:
                        id_registro = index + 1  # ID_Registro empieza en 1
                        if id_registro in df_factores.index:
                            row_factores = df_factores.loc[id_registro]
                            logger.debug(f"   Factores encontrados para registro {id_registro}")
                    
                    calificacion = self._procesar_fila(row, carga, index + 2, row_factores)
                    self.registros_exitosos += 1
                    
                    # 🆕 PUBLICAR EVENTO KAFKA: Calificación creada
                    try:
                        publicar_evento_calificacion_creada(calificacion)
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo publicar evento de calificación: {str(e)}")
                    
                    if (index + 1) % 10 == 0:
                        logger.debug(f"   Procesadas {index + 1}/{len(df_principales)} filas...")
                        
                except Exception as e:
                    self.registros_fallidos += 1
                    error_msg = f"Fila {index + 2}: {str(e)}"
                    self.errores.append(error_msg)
                    logger.warning(f"⚠️ {error_msg}")
            
            # Actualizar el registro de carga
            logger.info("💾 Actualizando estadísticas de carga...")
            carga.registros_exitosos = self.registros_exitosos
            carga.registros_fallidos = self.registros_fallidos
            carga.estado = 'COMPLETADO' if self.registros_fallidos == 0 else 'COMPLETADO_CON_ERRORES'
            carga.save()
            
            logger.info(f"✅ Procesamiento completado:")
            logger.info(f"   - Exitosos: {self.registros_exitosos}")
            logger.info(f"   - Fallidos: {self.registros_fallidos}")
            logger.info(f"   - Estado: {carga.estado}")
            
            # 🆕 PUBLICAR EVENTO KAFKA: Carga completada
            logger.info("📤 Publicando evento CARGA_COMPLETADA en Kafka...")
            try:
                publicar_evento_carga_completada(carga)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo publicar evento en Kafka: {str(e)}")
            
            # Crear log de la operación
            logger.debug("📝 Creando log de operación...")
            LogOperacion.objects.create(
                usuario=self.usuario,
                carga_masiva=carga,
                operacion='CARGA',
                datos_nuevos={
                    'archivo': self.archivo.name,
                    'tipo': self.tipo_carga,
                    'mercado': self.mercado or 'LOCAL',
                    'exitosos': self.registros_exitosos,
                    'fallidos': self.registros_fallidos,
                    'errores': self.errores[:10]  # Solo primeros 10 errores
                }
            )
            
            return carga
            
        except Exception as e:
            logger.error(f"❌ Error crítico al procesar archivo: {str(e)}", exc_info=True)
            
            # Si se creó la carga, marcarla como error
            if carga:
                carga.estado = 'ERROR'
                carga.save()
                
                # Publicar evento de error
                try:
                    evento_error = {
                        'tipo_evento': 'CARGA_ERROR',
                        'carga_id': carga.id,
                        'usuario': self.usuario.username,
                        'error': str(e),
                        'timestamp': timezone.now().isoformat()
                    }
                    from api.kafka_producer import kafka_producer
                    kafka_producer.publicar_evento('nuam-cargas', evento_error, key=f"carga-{carga.id}")
                except:
                    pass
            
            raise Exception(f"Error al procesar archivo: {str(e)}")
    
    def _procesar_fila(self, row, carga, num_fila, row_factores=None):
        """Procesa una fila individual del Excel"""
        
        logger.debug(f"   Procesando fila {num_fila}...")
        
        # Crear la calificación tributaria
        calificacion = CalificacionTributaria(
            usuario=self.usuario,
            carga_masiva=carga
        )
        
        # Mapear campos básicos
        calificacion.corredor_dueno = self._get_value(row, 'corredor_dueno', '')
        calificacion.rut_es_el_manual = self._get_value(row, 'rut_es_el_manual', '')
        calificacion.ano_comercial = self._get_value(row, 'ano_comercial', '')
        calificacion.mercado = self._get_value(row, 'mercado', self.mercado or 'LOCAL')
        calificacion.instrumento = self._get_value(row, 'instrumento', '')
        calificacion.descripcion = self._get_value(row, 'descripcion', '')
        calificacion.tipo_sociedad = self._get_value(row, 'tipo_sociedad', '')
        calificacion.divisa = self._get_value(row, 'divisa', 'CLP')
        calificacion.origen = self._get_value(row, 'origen', 'CARGA_MASIVA')
        
        # Campos numéricos
        calificacion.secuencia_evento = self._get_int_value(row, 'secuencia_evento')
        calificacion.numero_dividendo = self._get_int_value(row, 'numero_dividendo')
        calificacion.valor_historico = self._get_decimal_value(row, 'valor_historico')
        calificacion.factor_actualizacion = self._get_decimal_value(row, 'factor_actualizacion')
        calificacion.valor_convertido = self._get_decimal_value(row, 'valor_convertido')
        
        # Fecha
        calificacion.fecha_pago = self._get_date_value(row, 'fecha_pago')
        
        # Booleanos
        calificacion.acopio_lsfxf = self._get_bool_value(row, 'acopio_lsfxf')
        calificacion.es_local = self._get_bool_value(row, 'es_local', default=True)
        
        # Procesar factores (del 8 al 37) desde la hoja de factores
        if row_factores is not None:
            logger.debug(f"   Procesando factores desde hoja Factores...")
            factores_procesados = 0
            for i in range(8, 38):
                factor_name = f'factor_{i}'
                factor_value = self._get_decimal_value(row_factores, factor_name)
                if factor_value is not None:
                    setattr(calificacion, factor_name, factor_value)
                    factores_procesados += 1
            logger.debug(f"   ✅ {factores_procesados} factores asignados")
        else:
            logger.debug(f"   ⚠️ No hay factores para este registro")
        
        # Guardar
        calificacion.save()
        logger.debug(f"   ✅ Calificación guardada: {calificacion.id}")
        
        return calificacion
    
    def _get_value(self, row, column, default=''):
        """Obtiene un valor string de la fila"""
        try:
            value = row.get(column, default)
            if pd.isna(value):
                return default
            return str(value).strip()
        except:
            return default
    
    def _get_int_value(self, row, column, default=None):
        """Obtiene un valor entero de la fila"""
        try:
            value = row.get(column)
            if pd.isna(value):
                return default
            return int(value)
        except:
            return default
    
    def _get_decimal_value(self, row, column, default=None):
        """Obtiene un valor decimal de la fila"""
        try:
            value = row.get(column)
            if pd.isna(value):
                return default
            return float(value)
        except:
            return default
    
    def _get_date_value(self, row, column, default=None):
        """Obtiene un valor de fecha de la fila"""
        try:
            value = row.get(column)
            if pd.isna(value):
                return default
            
            if isinstance(value, datetime):
                return value.date()
            
            if isinstance(value, str):
                # Intentar varios formatos
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
            
            return default
        except:
            return default
    
    def _get_bool_value(self, row, column, default=False):
        """Obtiene un valor booleano de la fila"""
        try:
            value = row.get(column, default)
            if pd.isna(value):
                return default
            
            if isinstance(value, bool):
                return value
            
            value_str = str(value).lower().strip()
            return value_str in ['true', '1', 'sí', 'si', 'yes', 't', 'verdadero', 'verdad']
        except:
            return default


def get_columnas_esperadas(tipo_carga):
    """Retorna las columnas esperadas según el tipo de carga"""
    
    columnas_basicas = [
        'corredor_dueno',
        'rut_es_el_manual',
        'ano_comercial',
        'mercado',
        'instrumento',
        'fecha_pago',
        'secuencia_evento',
        'numero_dividendo',
        'descripcion',
        'tipo_sociedad',
        'divisa',
        'acopio_lsfxf',
        'valor_historico',
        'factor_actualizacion',
        'valor_convertido',
        'origen',
        'es_local',
    ]
    
    # Agregar factores del 8 al 37
    columnas_factores = [f'factor_{i}' for i in range(8, 38)]
    
    if tipo_carga == 'FACTORES':
        return columnas_basicas + columnas_factores
    elif tipo_carga == 'MONITOR':
        return columnas_basicas
    
    return columnas_basicas


def validar_archivo_excel(archivo, tipo_carga):
    """
    Valida que el archivo Excel tenga las columnas correctas.
    
    Returns:
        tuple: (es_valido, mensaje_error, columnas_faltantes)
    """
    try:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        
        columnas_esperadas = get_columnas_esperadas(tipo_carga)
        columnas_encontradas = set(df.columns)
        columnas_requeridas = set(columnas_esperadas)
        
        columnas_faltantes = columnas_requeridas - columnas_encontradas
        
        if columnas_faltantes:
            return False, f"Columnas faltantes: {', '.join(columnas_faltantes)}", list(columnas_faltantes)
        
        return True, "Archivo válido", []
        
    except Exception as e:
        return False, f"Error leyendo archivo: {str(e)}", []
    


