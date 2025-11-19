import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging detallado de todas las requests HTTP.
    Registra: método, path, usuario, IP, tiempo de respuesta y status code.
    """
    
    def process_request(self, request):
        """Se ejecuta ANTES de procesar la request"""
        request.start_time = time.time()
        
        # Log de entrada
        logger.info(
            f"⬇️ REQUEST | {request.method} {request.path} | "
            f"User: {request.user} | IP: {self.get_client_ip(request)}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Se ejecuta DESPUÉS de procesar la request"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Datos del log
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': str(request.user),
                'ip': self.get_client_ip(request),
            }
            
            # Log diferente según status code
            if response.status_code >= 500:
                logger.error(f"❌ RESPONSE | {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"⚠️ RESPONSE | {json.dumps(log_data)}")
            else:
                logger.info(f"⬆️ RESPONSE | {json.dumps(log_data)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Se ejecuta cuando hay una EXCEPCIÓN"""
        logger.error(
            f"💥 EXCEPTION | {request.method} {request.path} | "
            f"Error: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': str(request.user),
                'ip': self.get_client_ip(request),
            }
        )
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip