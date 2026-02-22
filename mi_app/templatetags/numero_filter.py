from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def formato_colombiano(valor):
    """
    Convierte número a formato colombiano: 1.000.000
    Acepta: int, float, Decimal, str
    """
    if not valor and valor != 0:
        return "0"
    
    try:
        # Convertir a float si no lo es
        if isinstance(valor, Decimal):
            valor_float = float(valor)
        elif isinstance(valor, str):
            # Limpiar formato anterior si existe
            valor_str = str(valor).replace(".", "").replace(",", ".")
            valor_float = float(valor_str)
        else:
            valor_float = float(valor)
        
        # Formatear con 2 decimales
        valor_formateado = f"{valor_float:,.2f}"
        
        # Reemplazar comas por X, puntos por comas, X por puntos (formato colombiano)
        resultado = valor_formateado.replace(",", "X").replace(".", ",").replace("X", ".")
        return resultado
    except (ValueError, TypeError):
        return str(valor)


@register.filter
def formato_moneda_colombiana(valor):
    """
    Convierte número a formato moneda colombiana: $1.000.000
    """
    return f"${formato_colombiano(valor)}"
