"""
Sistema de recuperación automática de errores
"""
import logging
import functools
import time
from typing import Callable, Any, Optional
from django.db import transaction

logger = logging.getLogger(__name__)


def auto_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentar automáticamente operaciones fallidas
    
    Args:
        max_attempts: Número máximo de intentos
        delay_seconds: Delay inicial entre intentos
        backoff_multiplier: Multiplicador para backoff exponencial
        exceptions: Tupla de excepciones que provocan retry
    
    Example:
        @auto_retry(max_attempts=3, delay_seconds=1.0)
        def operacion_critica():
            # código que puede fallar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = delay_seconds
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"⚠️ Intento {attempt}/{max_attempts} falló para {func.__name__}: {e}. "
                            f"Reintentando en {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"❌ Todos los intentos fallaron para {func.__name__}: {e}",
                            exc_info=True
                        )
            
            # Si llegamos aquí, todos los intentos fallaron
            raise last_exception
        
        return wrapper
    return decorator


def with_transaction_rollback(savepoint_name: Optional[str] = None):
    """
    Decorador para operaciones con rollback automático en caso de error
    
    Args:
        savepoint_name: Nombre del savepoint (opcional)
    
    Example:
        @with_transaction_rollback()
        def crear_calificacion_con_logs(data):
            # Si algo falla, todo hace rollback
            calificacion = CalificacionTributaria.objects.create(**data)
            LogOperacion.objects.create(...)
            return calificacion
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with transaction.atomic():
                savepoint = transaction.savepoint()
                
                try:
                    result = func(*args, **kwargs)
                    transaction.savepoint_commit(savepoint)
                    logger.debug(f"✅ Transacción confirmada para {func.__name__}")
                    return result
                    
                except Exception as e:
                    transaction.savepoint_rollback(savepoint)
                    logger.error(
                        f"🔄 Rollback ejecutado en {func.__name__}: {e}",
                        exc_info=True
                    )
                    raise
        
        return wrapper
    return decorator


class ErrorRecoveryManager:
    """
    Gestor centralizado de recuperación de errores
    """
    
    @staticmethod
    def safe_kafka_publish(producer_method: Callable, *args, **kwargs) -> bool:
        """
        Publica en Kafka de forma segura sin fallar la operación principal
        
        Args:
            producer_method: Método del productor a llamar
            *args, **kwargs: Argumentos para el método
        
        Returns:
            bool: True si publicó exitosamente, False en caso contrario
        """
        try:
            return producer_method(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"⚠️ Error publicando en Kafka (no crítico): {e}",
                extra={'producer_method': producer_method.__name__}
            )
            return False
    
    @staticmethod
    @auto_retry(max_attempts=3, delay_seconds=0.5)
    def safe_database_operation(operation: Callable) -> Any:
        """
        Ejecuta operación de base de datos con retry automático
        
        Args:
            operation: Función que realiza la operación
        
        Returns:
            Any: Resultado de la operación
        """
        return operation()