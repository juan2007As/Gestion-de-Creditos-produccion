from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def abs_value(value):
    """Devuelve el valor absoluto de un número"""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value


@register.filter
def formato_colombiano(valor):
    """
    Formatea números al estilo colombiano: 1.000,00
    Usa punto como separador de miles y coma para decimales
    """
    if valor is None or valor == '':
        return '-'
    
    try:
        valor = float(valor)
        # Convertir a string con 2 decimales y usar separador de miles
        formateado = f"{valor:,.2f}"
        # Reemplazar comas por X (temporal), puntos por comas, X por puntos
        formateado = formateado.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formateado
    except (ValueError, TypeError):
        return str(valor)


@register.filter
def formato_moneda_co(valor):
    """
    Formato moneda colombiana con símbolo: $1.000,00
    """
    if valor is None:
        return '$0,00'
    
    try:
        valor = float(valor)
        formateado = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"${formateado}"
    except (ValueError, TypeError):
        return '$0,00'


@register.filter
def dictsumby(lista_dicts, key):
    """
    Suma los valores de una clave en una lista de diccionarios
    Uso: {{ datos|dictsumby:"monto_prestamo" }}
    """
    if not lista_dicts:
        return 0
    
    total = 0
    try:
        for item in lista_dicts:
            if isinstance(item, dict) and key in item:
                total += float(item[key])
    except (ValueError, TypeError):
        return 0
    
    return total

@register.filter
def formato_porcentaje(valor):
    """Formato porcentaje: 15,5%"""
    if valor is None:
        return '0%'
    try:
        valor = float(valor)
        # Usar coma como separador decimal
        return f"{valor:.1f}%".replace('.', ',')
    except (ValueError, TypeError):
        return '0%'
