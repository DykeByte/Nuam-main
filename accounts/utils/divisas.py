# accounts/utils/divisas.py
from forex_python.converter import CurrencyRates

def obtener_tipo_cambio():
    cr = CurrencyRates()
    monedas = ['USD', 'EUR', 'CAD', 'COP', 'PEN']  # CLP lo dejamos como base
    tasas = {}
    for m in monedas:
        try:
            tasas[m] = round(cr.get_rate(m, 'CLP'), 2)
        except:
            tasas[m] = None
    return tasas
