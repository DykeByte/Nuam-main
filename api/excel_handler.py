# api/excel_handler.py - VERSIÓN CORREGIDA
import pandas as pd
from datetime import datetime
from api.models import CalificacionTributaria, CargaMasiva, LogOperacion
import logging

logger = logging.getLogger(__name__)


class ExcelHandler:
    """Manejador para procesar archivos Excel"""
    
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
        
        try:
            # Leer el archivo Excel
            logger.info("📖 Leyendo archivo Excel...")
            df = pd.read_excel(self.archivo)
            logger.info(f"✅ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"   Columnas encontradas: {list(df.columns)}")
            
            # Limpiar nombres de columnas (quitar espacios)
            df.columns = df.columns.str.strip()
            
            # Crear el registro de carga masiva
            logger.info("💾 Creando registro de CargaMasiva...")
            carga = CargaMasiva.objects.create(
                iniciado_por=self.usuario,  # ← CORREGIDO: era 'usuario'
                tipo_carga=self.tipo_carga,
                mercado=self.mercado or 'LOCAL',  # ← AGREGADO
                archivo_nombre=self.archivo.name,  # ← CORREGIDO: era 'nombre_archivo'
                archivo_path='',  # Por ahora vacío
                registros_procesados=len(df),
                estado='PROCESANDO'  # ← AGREGADO
            )
            logger.info(f"✅ CargaMasiva creada con ID: {carga.id}")
            
            # Procesar cada fila
            logger.info(f"🔄 Procesando {len(df)} filas...")
            for index, row in df.iterrows():
                try:
                    self._procesar_fila(row, carga, index + 2)
                    self.registros_exitosos += 1
                    
                    if (index + 1) % 10 == 0:
                        logger.debug(f"   Procesadas {index + 1}/{len(df)} filas...")
                        
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
            raise Exception(f"Error al procesar archivo: {str(e)}")
    
    def _procesar_fila(self, row, carga, num_fila):
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
        
        # Procesar factores (del 8 al 37)
        if self.tipo_carga == 'FACTORES':
            for i in range(8, 38):
                factor_name = f'factor_{i}'
                setattr(calificacion, factor_name, self._get_decimal_value(row, factor_name))
        
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
                return datetime.strptime(value, '%Y-%m-%d').date()
            
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
            return value_str in ['true', '1', 'sí', 'si', 'yes', 't', 'verdadero']
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