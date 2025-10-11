from django import template

register = template.Library()

# Filtro de ejemplo para tu template
@register.filter
def attr(obj, attr_name):
    """Permite acceder a atributos dinámicos del objeto"""
    return getattr(obj, attr_name, None)
