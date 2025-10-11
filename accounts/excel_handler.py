# accounts/excel_handler.py
import pandas as pd
from datetime import datetime
from .models import CalificacionTributaria, CargaMasiva, LogOperacion


class ExcelHandler:
    """Manejador para procesar archivos Excel"""
    
    def __init__(self, archivo, tipo_carga, usuario):
        self.archivo = archivo
        self.tipo_carga = tipo_carga
        self.usuario = usuario
        self.errores = []
        self.registros_exitosos = 0
        self.registros_fallidos = 0
        
    def procesar(self):
        """Procesa el archivo Excel y crea las calificaciones"""
        try:
            # Leer el archivo Excel
            df = pd.read_excel(self.archivo)
            
            # Limpiar nombres de columnas (quitar espacios)
            df.columns = df.columns.str.strip()
            
            # Crear el registro de carga masiva
            carga = CargaMasiva.objects.create(
                usuario=self.usuario,
                tipo_carga=self.tipo_carga,
                nombre_archivo=self.archivo.name,
                registros_procesados=len(df)
            )
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    self._procesar_fila(row, carga, index + 2)  # +2 porque Excel empieza en 1 y tiene header
                    self.registros_exitosos += 1
                except Exception as e:
                    self.registros_fallidos += 1
                    self.errores.append(f"Fila {index + 2}: {str(e)}")
            
            # Actualizar el registro de carga
            carga.registros_exitosos = self.registros_exitosos
            carga.registros_fallidos = self.registros_fallidos
            carga.errores_detalle = "\n".join(self.errores) if self.errores else ""
            carga.save()
            
            # Crear log de la operación
            LogOperacion.objects.create(
                usuario=self.usuario,
                carga_masiva=carga,
                operacion='CARGA',
                datos_nuevos={
                    'archivo': self.archivo.name,
                    'tipo': self.tipo_carga,
                    'exitosos': self.registros_exitosos,
                    'fallidos': self.registros_fallidos
                }
            )
            
            return carga
            
        except Exception as e:
            raise Exception(f"Error al procesar archivo: {str(e)}")
    
    def _procesar_fila(self, row, carga, num_fila):
        """Procesa una fila individual del Excel"""
        
        # Crear la calificación tributaria
        calificacion = CalificacionTributaria(
            usuario=self.usuario,
            carga_masiva=carga
        )
        
        # Mapear campos básicos (con valores por defecto si no existen)
        calificacion.corredor_dueno = self._get_value(row, 'corredor_dueno', '')
        calificacion.rut_es_el_manual = self._get_value(row, 'rut', '')
        calificacion.ano_comercial = self._get_value(row, 'ano_comercial', '')
        calificacion.mercado = self._get_value(row, 'mercado', '')
        calificacion.instrumento = self._get_value(row, 'instrumento', '')
        calificacion.descripcion = self._get_value(row, 'descripcion', '')
        calificacion.tipo_sociedad = self._get_value(row, 'tipo_sociedad', '')
        
        # Campos numéricos
        calificacion.secuencia_evento = self._get_int_value(row, 'secuencia_evento')
        calificacion.numero_dividendo = self._get_int_value(row, 'numero_dividendo')
        calificacion.valor_historico = self._get_decimal_value(row, 'valor_historico')
        calificacion.factor_actualizacion = self._get_decimal_value(row, 'factor_actualizacion')
        
        # Fecha
        calificacion.fecha_pago = self._get_date_value(row, 'fecha_pago')
        
        # Boolean
        calificacion.acopio_lsfxf = self._get_bool_value(row, 'acopio_lsfxf')
        calificacion.es_local = self._get_bool_value(row, 'es_local', default=True)
        
        # Procesar factores (del 8 al 37)
        for i in range(8, 38):
            factor_name = f'factor_{i}'
            setattr(calificacion, factor_name, self._get_decimal_value(row, factor_name))
        
        # Otros campos
        calificacion.divisa = self._get_value(row, 'divisa', 'CLP')
        calificacion.origen = self._get_value(row, 'origen', 'CARGA_MASIVA')
        
        # Guardar
        calificacion.save()
        
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
            
            # Si ya es datetime
            if isinstance(value, datetime):
                return value.date()
            
            # Si es string, intentar parsear
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
            
            # Convertir diferentes formatos a bool
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
        'rut',
        'ano_comercial',
        'mercado',
        'instrumento',
        'fecha_pago',
        'secuencia_evento',
        'numero_dividendo',
        'descripcion',
        'tipo_sociedad',
        'acopio_lsfxf',
        'valor_historico',
        'factor_actualizacion',
    ]
    
    # Agregar factores del 8 al 37
    columnas_factores = [f'factor_{i}' for i in range(8, 38)]
    
    if tipo_carga == 'FACTORES':
        return columnas_basicas + columnas_factores
    elif tipo_carga == 'MONITOR':
        return columnas_basicas
    
    return columnas_basicas