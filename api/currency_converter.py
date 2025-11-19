"""
Servicio de conversión de divisas usando API externa
API: ExchangeRate-API (gratuita, sin registro)
Documentación: https://www.exchangerate-api.com/
"""
import requests
import logging
from decimal import Decimal
from typing import Dict, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('api')


class CurrencyConverter:
    """
    Servicio de conversión de divisas con:
    - API externa (ExchangeRate-API)
    - Caché de tasas (1 hora)
    - Fallback a tasas locales
    - Logging completo
    """
    
    # API gratuita sin necesidad de key
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    # Fallback: tasas aproximadas si la API falla
    FALLBACK_RATES = {
        'USD': 1.0,
        'CLP': 950.0,
        'EUR': 0.92,
        'COP': 4100.0,
        'PEN': 3.75,
        'MXN': 17.5,
        'BRL': 5.0,
        'ARS': 350.0,
    }
    
    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Obtiene la tasa de cambio entre dos divisas.
        
        Args:
            from_currency: Código ISO de divisa origen (USD, EUR, CLP, etc.)
            to_currency: Código ISO de divisa destino
            
        Returns:
            Decimal con la tasa de cambio o None si falla
            
        Example:
            >>> rate = CurrencyConverter.get_exchange_rate('USD', 'CLP')
            >>> print(rate)  # 950.50
        """
        # Normalizar códigos
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()
        
        # Si son iguales, retornar 1
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Intentar obtener del caché
        cache_key = f'exchange_rate_{from_currency}_{to_currency}'
        cached_rate = cache.get(cache_key)
        
        if cached_rate:
            logger.debug(f"💾 Tasa de cambio desde caché: {from_currency}/{to_currency} = {cached_rate}")
            return Decimal(str(cached_rate))
        
        # Intentar obtener de API externa
        try:
            rate = cls._fetch_from_api(from_currency, to_currency)
            if rate:
                # Guardar en caché por 1 hora
                cache.set(cache_key, float(rate), 3600)
                logger.info(f"✅ Tasa obtenida de API: {from_currency}/{to_currency} = {rate}")
                return rate
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo tasa de API: {e}")
        
        # Fallback a tasas locales
        rate = cls._get_fallback_rate(from_currency, to_currency)
        if rate:
            logger.warning(f"⚠️ Usando tasa fallback: {from_currency}/{to_currency} = {rate}")
            return rate
        
        logger.error(f"❌ No se pudo obtener tasa: {from_currency}/{to_currency}")
        return None
    
    @classmethod
    def _fetch_from_api(cls, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Obtiene la tasa desde la API externa.
        """
        try:
            # Request a la API
            url = f"{cls.BASE_URL}/{from_currency}"
            logger.debug(f"🌐 Consultando API: {url}")
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            if to_currency in rates:
                rate = Decimal(str(rates[to_currency]))
                return rate
            
            logger.warning(f"⚠️ Divisa {to_currency} no encontrada en respuesta API")
            return None
            
        except requests.RequestException as e:
            logger.error(f"❌ Error de red en API: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"❌ Error parseando respuesta API: {e}")
            return None
    
    @classmethod
    def _get_fallback_rate(cls, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Obtiene tasa de cambio desde valores de fallback.
        Convierte todo a USD primero, luego a la moneda destino.
        """
        try:
            if from_currency not in cls.FALLBACK_RATES or to_currency not in cls.FALLBACK_RATES:
                return None
            
            # Convertir a USD primero
            from_to_usd = Decimal('1.0') / Decimal(str(cls.FALLBACK_RATES[from_currency]))
            # Luego de USD a moneda destino
            usd_to_target = Decimal(str(cls.FALLBACK_RATES[to_currency]))
            
            rate = from_to_usd * usd_to_target
            return rate
            
        except (KeyError, ZeroDivisionError, ValueError) as e:
            logger.error(f"❌ Error calculando tasa fallback: {e}")
            return None
    
    @classmethod
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Convierte un monto de una divisa a otra.
        
        Args:
            amount: Monto a convertir
            from_currency: Divisa origen
            to_currency: Divisa destino
            
        Returns:
            Monto convertido o None si falla
            
        Example:
            >>> converted = CurrencyConverter.convert(Decimal('100'), 'USD', 'CLP')
            >>> print(converted)  # 95050.00
        """
        logger.info(f"💱 Conversión: {amount} {from_currency} → {to_currency}")
        
        try:
            amount = Decimal(str(amount))
            
            if amount < 0:
                logger.error(f"❌ Monto negativo: {amount}")
                return None
            
            rate = cls.get_exchange_rate(from_currency, to_currency)
            
            if rate is None:
                return None
            
            result = amount * rate
            logger.info(f"✅ Conversión exitosa: {amount} {from_currency} = {result:.2f} {to_currency}")
            
            return result.quantize(Decimal('0.01'))  # Redondear a 2 decimales
            
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Error en conversión: {e}")
            return None
    
    @classmethod
    def get_all_rates(cls, base_currency: str = 'USD') -> Dict[str, Decimal]:
        """
        Obtiene todas las tasas de cambio para una divisa base.
        
        Args:
            base_currency: Divisa base (default: USD)
            
        Returns:
            Diccionario con códigos de divisa y sus tasas
        """
        logger.info(f"📊 Obteniendo todas las tasas para: {base_currency}")
        
        # Intentar desde caché
        cache_key = f'all_rates_{base_currency}'
        cached_rates = cache.get(cache_key)
        
        if cached_rates:
            logger.debug(f"💾 Tasas desde caché para {base_currency}")
            return cached_rates
        
        try:
            url = f"{cls.BASE_URL}/{base_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            # Convertir a Decimal
            decimal_rates = {k: Decimal(str(v)) for k, v in rates.items()}
            
            # Guardar en caché por 1 hora
            cache.set(cache_key, decimal_rates, 3600)
            
            logger.info(f"✅ Obtenidas {len(decimal_rates)} tasas para {base_currency}")
            return decimal_rates
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo todas las tasas: {e}")
            return cls.FALLBACK_RATES


# Funciones de utilidad para uso directo
def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Optional[Decimal]:
    """Función de conveniencia para conversión rápida"""
    return CurrencyConverter.convert(amount, from_currency, to_currency)


def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[Decimal]:
    """Función de conveniencia para obtener tasa"""
    return CurrencyConverter.get_exchange_rate(from_currency, to_currency)