"""Filtros y etiquetas (tags) personalizados de TechDrop.

Se usan en las plantillas con:  {% load tienda_extras %}
"""
from django import template

from tienda.models import Producto

register = template.Library()


@register.filter
def soles(valor):
    """Formatea un número como moneda peruana: 1399 → 'S/ 1,399.00'."""
    try:
        return f'S/ {float(valor):,.2f}'
    except (TypeError, ValueError):
        return valor


@register.filter
def estado_stock(producto):
    """Texto corto del estado del inventario de un producto."""
    if producto.agotado:
        return 'Agotado'
    if producto.pocas_unidades:
        return f'Últimas {producto.stock}'
    return 'En stock'


@register.inclusion_tag('tienda/_menu_categorias.html', takes_context=True)
def menu_categorias(context):
    """Enlaces del menú generados desde la base de datos (no hardcodeados)."""
    return {
        'categorias': Producto.objects.resumen_categorias(),
        'categoria_activa': context.get('categoria_activa', ''),
    }


@register.simple_tag(takes_context=True)
def url_con(context, **kwargs):
    """Query string actual cambiando/agregando parámetros. Sirve para paginar sin perder los filtros.

    Uso:  <a href="?{% url_con page=2 %}">
    """
    params = context['request'].GET.copy()
    for clave, valor in kwargs.items():
        params[clave] = valor
    return params.urlencode()
