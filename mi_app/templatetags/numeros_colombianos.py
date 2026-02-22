"""
Filtros de template para formato colombiano de números
"""
from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def formato_colombiano(valor, decimales=2):
    """
    Formatea número al estándar colombiano.
    Uso: {{ monto|formato_colombiano }} o {{ monto|formato_colombiano:0 }}
    
    Args:
        valor: Número a formatear (int, float, Decimal, string)
        decimales: Cantidad de decimales (default 2)
    
    Returns:
        String formateado: "1.234.567,89"
    """
    try:
        # Si es None o vacío, retornar 0
        if valor is None or valor == '':
            valor = 0
        
        # Convertir a Decimal si es string
        if isinstance(valor, str):
            # Limpiar el string: remover $, espacios, etc.
            valor_limpio = valor.replace('$', '').replace(' ', '').strip()
            # Si está vacío después de limpiar, usar 0
            if not valor_limpio:
                valor = 0
            else:
                # Convertir formato colombiano a formato decimal standard
                valor_limpio = valor_limpio.replace('.', '').replace(',', '.')
                valor = Decimal(valor_limpio)
        else:
            valor = Decimal(str(valor))
        
        # Convertir decimales a int si es string
        decimales = int(decimales)
        
        # Redondear a los decimales especificados
        formato = f'0.{decimales}f' if decimales > 0 else '0'
        valor_formateado = format(valor, formato)
        
        # Separar parte entera y decimal
        if '.' in valor_formateado:
            parte_entera, parte_decimal = valor_formateado.split('.')
        else:
            parte_entera = valor_formateado
            parte_decimal = ''
        
        # Agregar puntos cada 3 dígitos (de derecha a izquierda)
        parte_entera_formateada = ''
        for i, digito in enumerate(reversed(parte_entera)):
            if i > 0 and i % 3 == 0:
                parte_entera_formateada = '.' + parte_entera_formateada
            parte_entera_formateada = digito + parte_entera_formateada
        
        # Resultado final
        if decimales > 0 and parte_decimal:
            return f'{parte_entera_formateada},{parte_decimal}'
        else:
            return parte_entera_formateada
    
    except (ValueError, TypeError, AttributeError):
        return str(valor)


@register.filter
def formato_dinero_colombiano(valor):
    """
    Formatea número con símbolo de dinero colombiano.
    Uso: {{ monto|formato_dinero_colombiano }}
    
    Args:
        valor: Número a formatear
    
    Returns:
        String formateado: "$1.234.567"
    """
    try:
        # Usar el filtro anterior sin decimales
        valor_formateado = formato_colombiano(valor, 0)
        return f'${valor_formateado}'
    except:
        return f'${valor}'


@register.filter
def formato_porcentaje_colombiano(valor):
    """
    Formatea número como porcentaje colombiano.
    Uso: {{ tasa|formato_porcentaje_colombiano }}
    
    Args:
        valor: Número a formatear
    
    Returns:
        String formateado: "15,50%"
    """
    try:
        valor_formateado = formato_colombiano(valor, 2)
        return f'{valor_formateado}%'
    except:
        return f'{valor}%'
