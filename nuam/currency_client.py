"""
nuam/currency_client.py
Cliente para comunicarse con el Currency Service desde Django
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, List
from decimal import Decimal

logger = logging.getLogger('api')

class CurrencyServiceClient:
    """
    Cliente para interactuar con el Currency Service (FastAPI)
    Implementa cache, reintentos y fallback
    """
    
    def __init__(self):
        self.base_url = getattr(
            settings, 
            'CURRENCY_SERVICE_URL', 
            'http://currency-service:8001'
        )
        self.timeout = 10
        self.max_retries = 3
        
    def _make_request(
        self, 
        endpoint: str, 
        method: str = 'GET',
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Realiza request con manejo de errores y reintentos"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == 'GET':
                    response = requests.get(
                        url, 
                        params=params, 
                        timeout=self.timeout
                    )
                elif method == 'POST':
                    response = requests.post(
                        url,
                        json=json_data,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Método HTTP no soportado: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout en intento {attempt + 1} para {url}")
                if attempt == self.max_retries - 1:
                    logger.error(f"❌ Timeout final para {url}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error en request a Currency Service: {e}")
                return None
                
        return None
    
    def get_current_rate(
        self, 
        from_currency: str, 
        to_currency: str,
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Obtiene la tasa actual entre dos monedas
        
        Args:
            from_currency: Código de moneda origen (USD, EUR, CLP)
            to_currency: Código de moneda destino
            use_cache: Si usar caché de Django
            
        Returns:
            Dict con datos de la tasa o None si falla
        """
        cache_key = f"currency_rate_{from_currency}_{to_currency}"
        
        # Intentar obtener de caché
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"💾 Cache hit para {from_currency}/{to_currency}")
                return cached
        
        # Llamar al servicio
        data = self._make_request(
            "/api/v1/rates/current",
            params={
                'from_currency': from_currency,
                'to_currency': to_currency
            }
        )
        
        if data:
            # Guardar en caché por 5 minutos
            cache.set(cache_key, data, 300)
            logger.info(f"✅ Tasa obtenida: {from_currency}/{to_currency} = {data.get('rate')}")
            return data
        
        return None
    
    def get_uf_value(self, date: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene el valor de la UF chilena
        
        Args:
            date: Fecha en formato YYYY-MM-DD (None para valor actual)
            
        Returns:
            Dict con valor UF
        """
        cache_key = f"uf_value_{date or 'current'}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        params = {'date': date} if date else {}
        data = self._make_request("/api/v1/rates/uf", params=params)
        
        if data:
            # Cache más largo para UF (1 hora)
            cache.set(cache_key, data, 3600)
            return data
        
        return None
    
    def get_historical_data(
        self,
        currency: str,
        base: str = 'USD',
        days: int = 30
    ) -> Optional[List[Dict]]:
        """
        Obtiene datos históricos de una moneda
        
        Args:
            currency: Código de moneda
            base: Moneda base (default: USD)
            days: Cantidad de días hacia atrás
            
        Returns:
            Lista de datos históricos
        """
        cache_key = f"currency_history_{base}_{currency}_{days}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request(
            f"/api/v1/rates/history/{currency}",
            params={'base': base, 'days': days}
        )
        
        if data:
            # Cache por 1 hora
            cache.set(cache_key, data, 3600)
            return data
        
        return None
    
    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Optional[Dict]:
        """
        Convierte una cantidad de una moneda a otra
        
        Args:
            amount: Monto a convertir
            from_currency: Moneda origen
            to_currency: Moneda destino
            
        Returns:
            Dict con resultado de conversión
        """
        data = self._make_request(
            "/api/v1/rates/convert",
            method='POST',
            json_data={
                'amount': str(amount),
                'from_currency': from_currency,
                'to_currency': to_currency
            }
        )
        
        return data
    
    def get_currency_stats(
        self,
        currency: str,
        base: str = 'USD',
        days: int = 30
    ) -> Optional[Dict]:
        """
        Obtiene estadísticas de una moneda (promedio, max, min, cambio %)
        
        Args:
            currency: Código de moneda
            base: Moneda base
            days: Período en días
            
        Returns:
            Dict con estadísticas
        """
        cache_key = f"currency_stats_{base}_{currency}_{days}"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request(
            f"/api/v1/stats/{currency}",
            params={'base': base, 'days': days}
        )
        
        if data:
            cache.set(cache_key, data, 600)  # 10 minutos
            return data
        
        return None
    
    def get_dashboard_summary(self) -> Optional[Dict]:
        """
        Obtiene resumen de todas las monedas principales
        Usado por el dashboard frontend
        
        Returns:
            Dict con resumen de monedas
        """
        cache_key = "dashboard_summary"
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request("/api/v1/dashboard/summary")
        
        if data:
            cache.set(cache_key, data, 300)  # 5 minutos
            return data
        
        return None
    
    def health_check(self) -> bool:
        """Verifica si el Currency Service está disponible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/health/",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# ==========================================
# INSTANCIA GLOBAL DEL CLIENTE
# ==========================================
currency_service = CurrencyServiceClient()


# ==========================================
# FUNCIONES DE AYUDA PARA VISTAS
# ==========================================

def get_current_uf() -> Optional[Decimal]:
    """Obtiene el valor actual de la UF"""
    data = currency_service.get_uf_value()
    if data:
        return Decimal(str(data['value']))
    return None


def get_current_rate(from_currency: str, to_currency: str) -> Optional[Decimal]:
    """Obtiene tasa de cambio actual"""
    data = currency_service.get_current_rate(from_currency, to_currency)
    if data:
        return Decimal(str(data['rate']))
    return None


def convert_to_clp(amount: float, currency: str) -> Optional[Decimal]:
    """
    Convierte un monto de cualquier moneda a CLP
    
    Args:
        amount: Monto a convertir
        currency: Moneda origen (USD, EUR, UF, etc.)
        
    Returns:
        Monto en CLP o None si falla
    """
    if currency.upper() == 'CLP':
        return Decimal(str(amount))
    
    result = currency_service.convert_currency(amount, currency, 'CLP')
    if result:
        return Decimal(str(result['converted_amount']))
    return None


def get_all_current_rates() -> Dict[str, Decimal]:
    """
    Obtiene todas las tasas principales en un dict simple
    
    Returns:
        Dict con {moneda: tasa} desde USD
    """
    summary = currency_service.get_dashboard_summary()
    
    if not summary or 'currencies' not in summary:
        return {}
    
    rates = {}
    for currency_data in summary['currencies']:
        currency = currency_data.get('currency')
        rate = currency_data.get('current_rate')
        if currency and rate:
            rates[currency] = Decimal(str(rate))
    
    return rates