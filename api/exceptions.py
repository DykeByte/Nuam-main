# api/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para la API REST.
    Proporciona respuestas consistentes y logging detallado.
    """
    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)
    
    # Obtener información del contexto
    view = context.get('view', None)
    request = context.get('request', None)
    
    # Log del error con contexto
    logger.error(
        f"API Error: {exc.__class__.__name__} - {str(exc)}",
        extra={
            'exception': str(exc),
            'view': str(view) if view else 'Unknown',
            'method': request.method if request else 'Unknown',
            'path': request.path if request else 'Unknown',
            'user': request.user.username if request and request.user.is_authenticated else 'Anonymous',
        },
        exc_info=True
    )
    
    # Si el manejador por defecto no pudo manejar la excepción
    if response is None:
        return Response(
            {
                'error': 'Error interno del servidor',
                'detail': str(exc),
                'status_code': 500,
                'success': False
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Personalizar la respuesta para que sea consistente
    custom_response_data = {
        'success': False,
        'error': response.data.get('detail', 'Error en la solicitud'),
        'status_code': response.status_code,
    }
    
    # Agregar errores de validación si existen
    if isinstance(response.data, dict):
        errors = {k: v for k, v in response.data.items() if k != 'detail'}
        if errors:
            custom_response_data['errors'] = errors
    
    response.data = custom_response_data
    
    return response