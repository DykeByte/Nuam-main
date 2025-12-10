# services/currency-service/app/main.py
"""
Currency Service - Microservicio de Divisas para NUAM
Complementa el CurrencyConverter de Django almacenando históricos
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from decimal import Decimal
import requests
import logging
from functools import lru_cache
import os

# ============================================
# CONFIGURACIÓN
# ============================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nuam_user:nuam_password@postgres:5432/nuam_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("currency-service")

# FastAPI App
app = FastAPI(
    title="NUAM Currency Service",
    description="Servicio de divisas con históricos y UF chilena",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# MODELOS DE BASE DE DATOS
# ============================================
class ExchangeRate(Base):
    """Modelo para almacenar histórico de tasas de cambio"""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(10), nullable=False, index=True)
    to_currency = Column(String(10), nullable=False, index=True)
    rate = Column(Numeric(18, 6), nullable=False)
    source = Column(String(50), default="exchangerate-api")  # exchangerate-api, cmf, manual
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_currency_timestamp', 'from_currency', 'to_currency', 'timestamp'),
    )

# Crear tablas
Base.metadata.create_all(bind=engine)

# ============================================
# SCHEMAS PYDANTIC
# ============================================
class RateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: Decimal
    timestamp: datetime
    source: str = "exchangerate-api"

class HistoricalRate(BaseModel):
    date: datetime
    rate: Decimal

class ConversionRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    from_currency: str = Field(..., min_length=3, max_length=10)
    to_currency: str = Field(..., min_length=3, max_length=10)

class ConversionResponse(BaseModel):
    amount: Decimal
    from_currency: str
    to_currency: str
    converted_amount: Decimal
    rate: Decimal
    timestamp: datetime

class UFResponse(BaseModel):
    value: Decimal
    date: str
    source: str = "CMF"

class CurrencyStats(BaseModel):
    currency: str
    current_rate: Decimal
    avg_30d: Decimal
    max_30d: Decimal
    min_30d: Decimal
    change_percent: Decimal

# ============================================
# DEPENDENCIAS
# ============================================
def get_db():
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# SERVICIOS EXTERNOS
# ============================================
class ExchangeRateAPI:
    """Cliente para ExchangeRate-API"""
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_rate(from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Obtiene tasa desde API externa con caché"""
        try:
            url = f"{ExchangeRateAPI.BASE_URL}/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            if to_currency in rates:
                return Decimal(str(rates[to_currency]))
            
            logger.warning(f"Currency {to_currency} not found in API response")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {e}")
            return None

class CMFAPI:
    """Cliente para API CMF (Comisión para el Mercado Financiero) - UF"""
    BASE_URL = "https://api.cmfchile.cl/api-sbifv3/recursos_api"
    API_KEY = os.getenv("CMF_API_KEY", "")  # Opcional, API es pública
    
    @staticmethod
    def get_uf_value(date: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene valor UF desde CMF
        date: formato YYYY-MM-DD, si None obtiene el último valor
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y/%m/%d")
            else:
                # Convertir YYYY-MM-DD a YYYY/MM/DD
                date = date.replace("-", "/")
            
            # Endpoint: /uf/[año]/[mes]/dias/[dia]
            url = f"{CMFAPI.BASE_URL}/uf/{date}"
            
            headers = {}
            if CMFAPI.API_KEY:
                headers['apikey'] = CMFAPI.API_KEY
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'UFs' in data:
                    uf_data = data['UFs'][0]
                    return {
                        'value': Decimal(str(uf_data['Valor']).replace('.', '').replace(',', '.')),
                        'date': uf_data['Fecha']
                    }
            
            logger.warning(f"UF not found for date {date}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching UF from CMF: {e}")
            return None

# ============================================
# FUNCIONES DE NEGOCIO
# ============================================
def save_rate_to_db(
    db: Session,
    from_currency: str,
    to_currency: str,
    rate: Decimal,
    source: str = "exchangerate-api"
):
    """Guarda tasa en base de datos"""
    try:
        db_rate = ExchangeRate(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            rate=rate,
            source=source
        )
        db.add(db_rate)
        db.commit()
        logger.info(f"✅ Rate saved: {from_currency}/{to_currency} = {rate}")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving rate: {e}")

def get_historical_rates(
    db: Session,
    from_currency: str,
    to_currency: str,
    days: int = 30
) -> List[HistoricalRate]:
    """Obtiene histórico de tasas de los últimos N días"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    rates = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency.upper(),
        ExchangeRate.to_currency == to_currency.upper(),
        ExchangeRate.timestamp >= start_date
    ).order_by(ExchangeRate.timestamp).all()
    
    return [
        HistoricalRate(date=r.timestamp, rate=r.rate)
        for r in rates
    ]

def calculate_stats(
    db: Session,
    from_currency: str,
    to_currency: str,
    days: int = 30
) -> Optional[CurrencyStats]:
    """Calcula estadísticas de una divisa"""
    rates = get_historical_rates(db, from_currency, to_currency, days)
    
    if not rates:
        return None
    
    rate_values = [float(r.rate) for r in rates]
    current_rate = Decimal(str(rate_values[-1]))
    avg_rate = Decimal(str(sum(rate_values) / len(rate_values)))
    max_rate = Decimal(str(max(rate_values)))
    min_rate = Decimal(str(min(rate_values)))
    
    # Calcular cambio porcentual respecto al promedio
    change_percent = ((current_rate - avg_rate) / avg_rate) * 100
    
    return CurrencyStats(
        currency=to_currency,
        current_rate=current_rate,
        avg_30d=avg_rate,
        max_30d=max_rate,
        min_30d=min_rate,
        change_percent=change_percent
    )

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Health"])
def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "currency-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health/", tags=["Health"])
def health():
    """Health check detallado"""
    return {
        "status": "ok",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/rates/current", response_model=RateResponse, tags=["Rates"])
async def get_current_rate(
    from_currency: str = Query(..., description="Código de divisa origen (USD, EUR, CLP)"),
    to_currency: str = Query(..., description="Código de divisa destino"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la tasa de cambio actual entre dos divisas.
    Guarda el resultado en la base de datos para históricos.
    """
    logger.info(f"📊 Request: {from_currency} → {to_currency}")
    
    # Obtener de API externa
    rate = ExchangeRateAPI.get_rate(from_currency.upper(), to_currency.upper())
    
    if rate is None:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo obtener tasa para {from_currency}/{to_currency}"
        )
    
    # Guardar en BD para histórico
    save_rate_to_db(db, from_currency, to_currency, rate)
    
    return RateResponse(
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper(),
        rate=rate,
        timestamp=datetime.utcnow(),
        source="exchangerate-api"
    )

@app.get("/api/v1/rates/history/{currency}", response_model=List[HistoricalRate], tags=["Rates"])
async def get_rate_history(
    currency: str,
    base: str = "USD",
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtiene el histórico de tasas de cambio para una divisa.
    Útil para generar gráficos en el dashboard.
    """
    logger.info(f"📈 Historical request: {base}/{currency} - Last {days} days")
    
    rates = get_historical_rates(db, base, currency, days)
    
    if not rates:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron datos históricos para {base}/{currency}"
        )
    
    return rates

@app.post("/api/v1/rates/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert_currency(
    conversion: ConversionRequest,
    db: Session = Depends(get_db)
):
    """
    Convierte un monto de una divisa a otra.
    """
    logger.info(f"💱 Conversion: {conversion.amount} {conversion.from_currency} → {conversion.to_currency}")
    
    # Obtener tasa
    rate = ExchangeRateAPI.get_rate(conversion.from_currency.upper(), conversion.to_currency.upper())
    
    if rate is None:
        raise HTTPException(
            status_code=503,
            detail="No se pudo obtener tasa de cambio"
        )
    
    # Convertir
    converted = conversion.amount * rate
    
    # Guardar en BD
    save_rate_to_db(db, conversion.from_currency, conversion.to_currency, rate)
    
    return ConversionResponse(
        amount=conversion.amount,
        from_currency=conversion.from_currency.upper(),
        to_currency=conversion.to_currency.upper(),
        converted_amount=converted.quantize(Decimal('0.01')),
        rate=rate,
        timestamp=datetime.utcnow()
    )

@app.get("/api/v1/rates/uf", response_model=UFResponse, tags=["Chilean UF"])
async def get_uf_value(
    date: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el valor de la UF (Unidad de Fomento) chilena desde CMF.
    Si no se especifica fecha, obtiene el valor actual.
    """
    logger.info(f"🇨🇱 UF request for date: {date or 'today'}")
    
    uf_data = CMFAPI.get_uf_value(date)
    
    if uf_data is None:
        raise HTTPException(
            status_code=503,
            detail="No se pudo obtener valor UF desde CMF"
        )
    
    # Guardar UF como tasa (UF/CLP)
    save_rate_to_db(db, "UF", "CLP", uf_data['value'], source="CMF")
    
    return UFResponse(
        value=uf_data['value'],
        date=uf_data['date'],
        source="CMF"
    )

@app.get("/api/v1/stats/{currency}", response_model=CurrencyStats, tags=["Statistics"])
async def get_currency_stats(
    currency: str,
    base: str = "USD",
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de una divisa (promedio, máximo, mínimo, cambio %).
    Útil para cards del dashboard.
    """
    logger.info(f"📊 Stats request: {base}/{currency}")
    
    stats = calculate_stats(db, base, currency, days)
    
    if stats is None:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos suficientes para calcular estadísticas de {currency}"
        )
    
    return stats

@app.get("/api/v1/dashboard/summary", tags=["Dashboard"])
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Obtiene resumen de todas las divisas principales para el dashboard.
    Incluye: CLP, COP, PEN (SOL), UF
    """
    logger.info("📊 Dashboard summary request")
    
    currencies = ["CLP", "COP", "PEN", "MXN", "BRL"]
    summary = []
    
    for currency in currencies:
        try:
            stats = calculate_stats(db, "USD", currency, 30)
            if stats:
                summary.append(stats.dict())
        except Exception as e:
            logger.error(f"Error getting stats for {currency}: {e}")
    
    # Agregar UF
    try:
        uf_data = CMFAPI.get_uf_value()
        if uf_data:
            summary.append({
                "currency": "UF",
                "current_rate": float(uf_data['value']),
                "source": "CMF",
                "date": uf_data['date']
            })
    except Exception as e:
        logger.error(f"Error getting UF: {e}")
    
    return {
        "currencies": summary,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================
# TAREA PERIÓDICA (Background)
# ============================================
# Nota: En producción usar APScheduler o Celery
# Por ahora, este endpoint se puede llamar con un cron job

@app.post("/api/v1/admin/update-rates", tags=["Admin"])
async def update_all_rates(db: Session = Depends(get_db)):
    """
    Actualiza todas las tasas principales.
    Este endpoint debería llamarse cada hora con un cron job.
    """
    logger.info("🔄 Updating all rates...")
    
    currencies = ["CLP", "COP", "PEN", "EUR", "MXN", "BRL", "ARS"]
    updated = []
    
    for currency in currencies:
        try:
            rate = ExchangeRateAPI.get_rate("USD", currency)
            if rate:
                save_rate_to_db(db, "USD", currency, rate)
                updated.append(f"USD/{currency}")
        except Exception as e:
            logger.error(f"Error updating {currency}: {e}")
    
    # Actualizar UF
    try:
        uf_data = CMFAPI.get_uf_value()
        if uf_data:
            save_rate_to_db(db, "UF", "CLP", uf_data['value'], source="CMF")
            updated.append("UF/CLP")
    except Exception as e:
        logger.error(f"Error updating UF: {e}")
    
    return {
        "status": "success",
        "updated": updated,
        "count": len(updated),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)