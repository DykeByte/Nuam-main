# api/excel_handler.py - VERSIÓN FINAL CORREGIDA (FACTORES + KAFKA + MERGE SEGURO)

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
        self.mercado = None
        self.errores = []
        self.registros_exitosos = 0
        self.registros_fallidos = 0
        
        logger.info(f"📦 ExcelHandler creado para archivo {archivo.name}")

    # ----------------------------------------------------------
    # NORMALIZACIÓN DE COLUMNAS DE FACTORES
    # ----------------------------------------------------------

    def _normalizar_columnas_factores(self, df):
        """
        Normaliza nombres de columnas:
        - minusculas
        - reemplaza espacios y guiones
        - convierte "factor8", "factor 8", "Factor-8" → "factor_8"
        """
        nuevas_columnas = {}

        for col in df.columns:
            original = col
            c = col.lower().strip()
            c = c.replace(" ", "_").replace("-", "_")

            # factor8 → factor_8
            if c.startswith("factor") and not c.startswith("factor_"):
                c = c.replace("factor", "factor_")

            # factor_08 → factor_8
            if c.startswith("factor_") and c[7:].isdigit():
                numero = str(int(c[7:]))  # elimina ceros a la izquierda
                c = f"factor_{numero}"

            nuevas_columnas[original] = c

        logger.info(f"🔧 Columnas normalizadas: {list(nuevas_columnas.values())}")
        return df.rename(columns=nuevas_columnas)

    # ----------------------------------------------------------
    # PROCESAMIENTO PRINCIPAL
    # ----------------------------------------------------------

    def procesar(self):
        logger.info("🔄 Iniciando procesamiento de archivo Excel...")

        carga = None

        try:
            # -------------------- HOJA 1 --------------------
            logger.info("📄 Leyendo Hoja 'Datos Principales'...")
            df_principales = pd.read_excel(self.archivo, sheet_name='Datos Principales')
            df_principales.columns = df_principales.columns.str.strip()

            logger.info(f"   Columnas encontradas en hoja principal: {list(df_principales.columns)}")

            # -------------------- HOJA 2 --------------------
            df_factores = None
            try:
                logger.info("📄 Leyendo Hoja 'Factores'...")
                df_factores = pd.read_excel(self.archivo, sheet_name='Factores')
                df_factores.columns = df_factores.columns.str.strip()

                # normalizar nombres
                df_factores = self._normalizar_columnas_factores(df_factores)

                # Indexar por ID_Registro si existe
                if "id_registro" in df_factores.columns:
                    df_factores = df_factores.set_index("id_registro")
                    logger.info("   Factores indexados por ID_Registro.")
                else:
                    raise ValueError("Falta columna ID_Registro en la hoja Factores")

            except Exception as e:
                logger.warning(f"⚠ No se pudo leer la hoja Factores: {e}")
                df_factores = None

            # Crear registro de carga masiva
            carga = CargaMasiva.objects.create(
                iniciado_por=self.usuario,
                tipo_carga=self.tipo_carga,
                mercado=self.mercado or "LOCAL",
                archivo_nombre=self.archivo.name,
                archivo_path="",
                registros_procesados=len(df_principales),
                estado="PROCESANDO"
            )

            try:
                publicar_evento_carga_iniciada(carga)
            except Exception as e:
                logger.warning(f"Kafka error: {e}")

            # -------------------------------------------------------
            # CREAR ID_REGISTRO Y FUSIONAR PRIMERA HOJA + FACTORES
            # -------------------------------------------------------

            df_principales["id_registro"] = df_principales.index + 1

            if df_factores is not None:
                logger.info("🔗 Fusionando datos principales con factores...")
                df_merged = df_principales.merge(
                    df_factores,
                    left_on="id_registro",
                    right_index=True,
                    how="left"
                )
            else:
                df_merged = df_principales.copy()

            # -------------------------------------------------------
            # PROCESAR FILAS
            # -------------------------------------------------------

            logger.info(f"🔄 Procesando {len(df_merged)} filas...")

            for index, row in df_merged.iterrows():
                try:
                    calificacion = self._procesar_fila(row, carga, index + 2)
                    self.registros_exitosos += 1

                    try:
                        publicar_evento_calificacion_creada(calificacion)
                    except Exception:
                        pass

                except Exception as e:
                    self.registros_fallidos += 1
                    msg = f"Fila {index+2}: {e}"
                    self.errores.append(msg)
                    logger.warning(msg)

            # -------------------------------------------------------
            # FINALIZAR
            # -------------------------------------------------------

            carga.registros_exitosos = self.registros_exitosos
            carga.registros_fallidos = self.registros_fallidos
            carga.estado = "COMPLETADO" if self.registros_fallidos == 0 else "COMPLETADO_CON_ERRORES"
            carga.save()

            try:
                publicar_evento_carga_completada(carga)
            except Exception:
                pass

            LogOperacion.objects.create(
                usuario=self.usuario,
                carga_masiva=carga,
                operacion="CARGA",
                datos_nuevos={
                    "archivo": self.archivo.name,
                    "tipo": self.tipo_carga,
                    "mercado": self.mercado or 'LOCAL',
                    "exitosos": self.registros_exitosos,
                    "fallidos": self.registros_fallidos,
                    "errores": self.errores[:10]
                }
            )

            return carga

        except Exception as e:
            logger.error(f"❌ Error crítico: {e}", exc_info=True)

            if carga:
                carga.estado = "ERROR"
                carga.save()

            raise

    # ----------------------------------------------------------
    # PROCESAR UNA FILA
    # ----------------------------------------------------------

    def _procesar_fila(self, row, carga, num_fila):
        logger.debug(f"Procesando fila {num_fila}...")

        calificacion = CalificacionTributaria(
            usuario=self.usuario,
            carga_masiva=carga
        )

        # -------------------- CAMPOS BÁSICOS --------------------
        campos = [
            ('corredor_dueno', ''),
            ('rut_es_el_manual', ''),
            ('ano_comercial', ''),
            ('mercado', self.mercado or 'LOCAL'),
            ('instrumento', ''),
            ('descripcion', ''),
            ('tipo_sociedad', ''),
            ('divisa', 'CLP'),
            ('origen', 'CARGA_MASIVA'),
        ]

        for campo, default in campos:
            setattr(calificacion, campo, self._get_value(row, campo, default))

        # numéricos
        calificacion.secuencia_evento = self._get_int_value(row, 'secuencia_evento')
        calificacion.numero_dividendo = self._get_int_value(row, 'numero_dividendo')
        calificacion.valor_historico = self._get_decimal_value(row, 'valor_historico')
        calificacion.factor_actualizacion = self._get_decimal_value(row, 'factor_actualizacion')
        calificacion.valor_convertido = self._get_decimal_value(row, 'valor_convertido')

        # fechas
        calificacion.fecha_pago = self._get_date_value(row, 'fecha_pago')

        # booleanos
        calificacion.acopio_lsfxf = self._get_bool_value(row, 'acopio_lsfxf')
        calificacion.es_local = self._get_bool_value(row, 'es_local', True)

        # -------------------- FACTORES 8–37 --------------------
        asignados = 0
        for i in range(8, 38):
            col = f"factor_{i}"
            valor = self._get_decimal_value(row, col)
            if valor is not None:
                setattr(calificacion, col, valor)
                asignados += 1

        logger.debug(f"   Factores asignados: {asignados}")

        # guardar en base de datos
        calificacion.save()
        return calificacion

    # ----------------------------------------------------------
    # MÉTODOS AUXILIARES
    # ----------------------------------------------------------

    def _get_value(self, row, column, default=''):
        try:
            value = row.get(column, default)
            return default if pd.isna(value) else str(value).strip()
        except:
            return default

    def _get_int_value(self, row, column, default=None):
        try:
            value = row.get(column)
            return default if pd.isna(value) else int(value)
        except:
            return default

    def _get_decimal_value(self, row, column, default=None):
        try:
            value = row.get(column)
            return default if pd.isna(value) else float(value)
        except:
            return default

    def _get_date_value(self, row, column, default=None):
        try:
            value = row.get(column)
            if pd.isna(value): return default
            if isinstance(value, datetime): return value.date()
            if isinstance(value, str):
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try: return datetime.strptime(value, fmt).date()
                    except: pass
            return default
        except:
            return default

    def _get_bool_value(self, row, column, default=False):
        try:
            value = row.get(column, default)
            if pd.isna(value): return default
            if isinstance(value, bool): return value
            return str(value).lower().strip() in ['true', '1', 'sí', 'si', 'yes', 't', 'verdadero']
        except:
            return default


# ----------------------------------------------------------
# VALIDACIÓN DE ARCHIVO
# ----------------------------------------------------------

def get_columnas_esperadas(tipo_carga):
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

    columnas_factores = [f'factor_{i}' for i in range(8, 38)]

    if tipo_carga == 'FACTORES':
        return columnas_basicas + columnas_factores
    return columnas_basicas


def validar_archivo_excel(archivo, tipo_carga):
    try:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()

        columnas_esperadas = get_columnas_esperadas(tipo_carga)
        faltantes = set(columnas_esperadas) - set(df.columns)

        if faltantes:
            return False, f"Columnas faltantes: {', '.join(faltantes)}", list(faltantes)

        return True, "Archivo válido", []
        
    except Exception as e:
        return False, f"Error leyendo archivo: {e}", []
