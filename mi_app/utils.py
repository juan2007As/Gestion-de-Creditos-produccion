"""
Utilidades generales del sistema
"""
from decimal import Decimal
import re


def limpiar_numero_entrada(valor_str):
    """
    Convierte entrada de números en cualquier formato a Decimal.
    Acepta: 1000000, 1.000.000, 1,000,000, 1000,00
    
    Args:
        valor_str: String del número a limpiar
    
    Returns:
        Decimal limpio
    """
    if not valor_str:
        return Decimal('0')
    
    try:
        valor_str = str(valor_str).strip()
        
        # Si tiene punto y coma, determinar cuál es separador decimal
        if '.' in valor_str and ',' in valor_str:
            # Formato: 1.000,00 (colombiano)
            valor_str = valor_str.replace('.', '').replace(',', '.')
        elif ',' in valor_str and valor_str.count(',') == 1:
            # Podría ser 1,000.00 o 1,000000
            if valor_str.count(',') == 1 and len(valor_str.split(',')[1]) == 2:
                # Es 1,000.00 (decimal)
                pass
            else:
                # Es separador de miles, reemplazar
                valor_str = valor_str.replace(',', '')
        elif '.' in valor_str and valor_str.count('.') > 1:
            # Múltiples puntos: 1.000.000
            valor_str = valor_str.replace('.', '')
        
        return Decimal(valor_str)
    except (ValueError, TypeError):
        return Decimal('0')


def formatear_numero_colombiano(valor, decimales=2):
    """
    Formatea número al estándar colombiano.
    
    Args:
        valor: Número a formatear
        decimales: Cantidad de decimales (default 2)
    
    Returns:
        String formateado: 1.000.000,00
    """
    try:
        if not valor and valor != 0:
            return "0"
        
        valor_float = float(valor)
        
        # Formato con separador de miles y decimales
        formato = f"{{:,.{decimales}f}}"
        valor_formateado = formato.format(valor_float)
        
        # Cambiar formato: comas → X, puntos → comas, X → puntos
        resultado = valor_formateado.replace(",", "X").replace(".", ",").replace("X", ".")
        return resultado
    except (ValueError, TypeError):
        return str(valor)


def determinar_estado_cuota_al_crear(pagado, fecha_pago_esperada, monto_pagado_principal, monto_original):
    """
    ✅ OPCIÓN C PASO 1: Función centralizada para determinar estado correcto al crear cuota.
    
    Esta función define la lógica de transformación de estado PENDIENTE → VENCIDA/VENCIDA_PARCIAL
    basado en:
    - ¿Está pagada? → PAGADA
    - ¿Está vencida (fecha pasó)? → VENCIDA o VENCIDA_PARCIAL
    - Caso defecto → PENDIENTE
    
    Args:
        pagado (bool): ¿La cuota está completamente pagada?
        fecha_pago_esperada (date): Fecha esperada de pago
        monto_pagado_principal (Decimal): Monto del principal pagado
        monto_original (Decimal): Monto original total del principal
    
    Returns:
        str: Estado correcto ('PAGADA', 'VENCIDA', 'VENCIDA_PARCIAL', 'PENDIENTE')
    """
    from datetime import date
    from decimal import Decimal
    
    hoy = date.today()
    
    # Caso 1: Si está completamente pagada
    if pagado and (Decimal(str(monto_pagado_principal)) >= Decimal(str(monto_original))):
        return 'PAGADA'
    
    # Caso 2: Si está vencida (fecha de pago pasó)
    if fecha_pago_esperada and fecha_pago_esperada < hoy:
        # Si tiene algún monto pagado del principal
        if Decimal(str(monto_pagado_principal)) > 0:
            return 'VENCIDA_PARCIAL'
        else:
            return 'VENCIDA'
    
    # Caso 3: Por defecto, pendiente
    return 'PENDIENTE'
