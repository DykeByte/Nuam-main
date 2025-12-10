import requests
import logging
from datetime import datetime, timedelta
from functools import wraps
import os

logger = logging.getLogger('service_client')


class CircuitBreaker:
    """Implementación del patrón Circuit Breaker"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, name="service"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.name = name
    
    def call(self, func, *args, **kwargs):
        """Ejecutar función con circuit breaker"""
        if self.state == 'OPEN':
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = 'HALF_OPEN'
                logger.info(f"🔄 Circuit Breaker [{self.name}]: Intentando recuperación (HALF_OPEN)")
            else:
                logger.error(f"⛔ Circuit Breaker [{self.name}]: OPEN - Rechazando petición")
                raise Exception(f"Circuit breaker [{self.name}] is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info(f"✅ Circuit Breaker [{self.name}]: Recuperado (CLOSED)")
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"❌ Circuit Breaker [{self.name}]: Abierto por {self.failure_count} fallos - {e}")
            
            raise


class ServiceClient:
    """Cliente para comunicación entre microservicios"""
    
    def __init__(self, service_name, base_url=None, timeout=5):
        self.service_name = service_name
        self.base_url = base_url or os.getenv(f'{service_name.upper()}_URL', f'http://{service_name}:8000')
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker(name=service_name)
        self.logger = logging.getLogger(f'service_client.{service_name}')
    
    def get(self, endpoint, headers=None, params=None):
        """GET request con circuit breaker y retry"""
        return self.circuit_breaker.call(
            self._do_request, 'GET', endpoint, headers, params
        )
    
    def post(self, endpoint, data=None, headers=None):
        """POST request con circuit breaker y retry"""
        return self.circuit_breaker.call(
            self._do_request, 'POST', endpoint, headers, None, data
        )
    
    def put(self, endpoint, data=None, headers=None):
        """PUT request con circuit breaker"""
        return self.circuit_breaker.call(
            self._do_request, 'PUT', endpoint, headers, None, data
        )
    
    def delete(self, endpoint, headers=None):
        """DELETE request con circuit breaker"""
        return self.circuit_breaker.call(
            self._do_request, 'DELETE', endpoint, headers
        )
    
    def _do_request(self, method, endpoint, headers=None, params=None, data=None):
        """Ejecutar request HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        self.logger.info(f"➡️ {method} {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            self.logger.info(f"✅ Response {response.status_code} from {self.service_name}")
            
            # Intentar parsear JSON, sino devolver texto
            try:
                return response.json()
            except ValueError:
                return response.text
        
        except requests.Timeout:
            self.logger.error(f"⏱️ Timeout calling {self.service_name} at {url}")
            raise
        except requests.HTTPError as e:
            self.logger.error(f"❌ HTTP Error {e.response.status_code} from {self.service_name}: {e}")
            raise
        except requests.RequestException as e:
            self.logger.error(f"❌ Error calling {self.service_name}: {e}")
            raise
    
    def health_check(self):
        """Verificar salud del servicio"""
        try:
            response = self.get('/api/health/')
            return response.get('status') == 'healthy'
        except Exception:
            return False


# ========================================
# INSTANCIAS DE CLIENTES PRE-CONFIGURADAS
# ========================================

# Cliente para servicio de autenticación
auth_service = ServiceClient(
    'auth-service',
    base_url=os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8001')
)

# Cliente para servicio de calificaciones
calificaciones_service = ServiceClient(
    'calificaciones-service',
    base_url=os.getenv('CALIFICACIONES_SERVICE_URL', 'http://calificaciones-service:8002')
)

# Cliente para servicio de conversión
conversion_service = ServiceClient(
    'conversion-service',
    base_url=os.getenv('CONVERSION_SERVICE_URL', 'http://conversion-service:8003')
)

# Cliente para servicio de dashboard
dashboard_service = ServiceClient(
    'dashboard-service',
    base_url=os.getenv('DASHBOARD_SERVICE_URL', 'http://dashboard-service:8004')
)


# ========================================
# DECORADOR PARA VALIDAR TOKENS JWT
# ========================================

def validate_jwt_with_auth_service(func):
    """Decorador para validar JWT usando el servicio de autenticación"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            from django.http import JsonResponse
            return JsonResponse({'error': 'No authorization token provided'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # Validar token con el servicio de autenticación
            response = auth_service.post('/api/auth/validate/', {
                'token': token
            })
            
            if response.get('valid'):
                # Agregar usuario al request
                request.user_data = response.get('user')
                return func(request, *args, **kwargs)
            else:
                from django.http import JsonResponse
                return JsonResponse({'error': 'Invalid token'}, status=401)
        
        except Exception as e:
            logger.error(f"Error validando token: {e}")
            from django.http import JsonResponse
            return JsonResponse({'error': 'Token validation failed'}, status=401)
    
    return wrapper