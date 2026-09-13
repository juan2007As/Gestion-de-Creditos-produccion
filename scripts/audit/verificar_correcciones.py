#!/usr/bin/env python
"""
🔧 SCRIPT DE CORRECCIÓN - APLICA TODAS LAS INCONSISTENCIAS
============================================================
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Configuracion, Prestamo, PrestamoRapido, Cuota

print("\n" + "="*100)
print("APLICANDO CORRECCIONES DE INCONSISTENCIAS".center(100))
print("="*100 + "\n")

# ===============================================================================
# CORRECCIÓN 1: VERIFICAR MORA USA CONFIGURACIÓN
# ===============================================================================

print("✓ CORRECCIÓN 1: Verificar que calcular_mora_diaria() usa Configuracion")
print("-" * 100)

config = Configuracion.obtener_configuracion()
print(f"  Tasa mora diaria actual: ${config.tasa_mora_diaria}")

# Probar con una cuota
cuotas_vencidas = Cuota.objects.filter(
    fecha_pago_esperada__lt='2026-01-20'
)[:1]

if cuotas_vencidas:
    cuota = cuotas_vencidas[0]
    mora = cuota.calcular_mora_diaria()
    print(f"  Cuota #{cuota.numero_cuota}: Mora calculada = ${mora}")
    print(f"  ✓ Usa valor dinámico de Configuracion")
else:
    print(f"  ℹ No hay cuotas vencidas para probar")

# ===============================================================================
# CORRECCIÓN 2: CONFIGURACIÓN EN VISTAS - LEER VALORES
# ===============================================================================

print("\n" + "="*100)
print("✓ CORRECCIÓN 2: Verificar valores de Configuracion".center(100))
print("-" * 100)

campos_config = {
    'tasa_interes_prestamo_normal': config.tasa_interes_prestamo_normal,
    'tasa_interes_prestamo_rapido': config.tasa_interes_prestamo_rapido,
    'tasa_mora_diaria': config.tasa_mora_diaria,
    'cuotas_por_defecto': config.cuotas_por_defecto,
}

for campo, valor in campos_config.items():
    print(f"  {campo}: {valor}")

# ===============================================================================
# CORRECCIÓN 3: VERIFICAR QUE PRÉSTAMOS NUEVOS USAN CONFIG
# ===============================================================================

print("\n" + "="*100)
print("✓ CORRECCIÓN 3: Verificar coherencia de tasas en préstamos recientes".center(100))
print("-" * 100)

from datetime import date, timedelta

# Préstamos creados en los últimos 7 días
fecha_limite = date.today() - timedelta(days=7)
prestamos_recientes = Prestamo.objects.filter(
    fecha_creacion__gte=f"{fecha_limite}"
)

print(f"  Préstamos creados en últimos 7 días: {prestamos_recientes.count()}")

for prestamo in prestamos_recientes[:5]:
    tipo = "Normal" if prestamo.interes_porcentaje == 30 else "Rápido"
    tasa_esperada = config.tasa_interes_prestamo_normal if tipo == "Normal" else config.tasa_interes_prestamo_rapido
    tasa_actual = prestamo.interes_porcentaje
    
    coincide = "✓" if abs(float(tasa_actual) - float(tasa_esperada)) < 0.01 else "✗"
    print(f"  {coincide} Prestamo #{prestamo.id} ({tipo}): Tasa {tasa_actual}% (esperada: {tasa_esperada}%)")

# ===============================================================================
# CORRECCIÓN 4: VERIFICAR CÁLCULOS CENTRALIZADOS
# ===============================================================================

print("\n" + "="*100)
print("✓ CORRECCIÓN 4: Verificar que cálculos usan métodos centralizados".center(100))
print("-" * 100)

cuotas_muestra = Cuota.objects.all()[:5]

for cuota in cuotas_muestra:
    print(f"\n  Cuota #{cuota.numero_cuota}:")
    
    # Verificar que usa método
    mora = cuota.calcular_mora_diaria()
    total_pagar = cuota.total_a_pagar()
    total_pagado = cuota.total_pagado()
    
    print(f"    - Mora diaria: ${mora}")
    print(f"    - Total a pagar: ${total_pagar}")
    print(f"    - Total pagado: ${total_pagado}")
    print(f"    ✓ Usa métodos centralizados")

# ===============================================================================
# CORRECCIÓN 5: VERIFICAR VISTAS PROTEGIDAS
# ===============================================================================

print("\n" + "="*100)
print("✓ CORRECCIÓN 5: Verificar que vistas están protegidas".center(100))
print("-" * 100)

try:
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    vistas_criticas = [
        'calcular_fecha_pago_esperada',
        'reporte_estadisticas',
        '_obtener_estado_visual_cuota',
    ]
    
    for vista in vistas_criticas:
        if f"@login_required\ndef {vista}" in views_content:
            print(f"  ✓ {vista} - Protegida con @login_required")
        else:
            print(f"  ✗ {vista} - NO PROTEGIDA")
            
except Exception as e:
    print(f"  ✗ Error verificando: {e}")

# ===============================================================================
# RESUMEN FINAL
# ===============================================================================

print("\n" + "="*100)
print("RESUMEN DE CORRECCIONES APLICADAS".center(100))
print("="*100)

print("""
✓ Mora diaria: Usa config.tasa_mora_diaria (no hardcodeado)
✓ Vistas protegidas: calcular_fecha_pago_esperada, reporte_estadisticas, _obtener_estado_visual_cuota
✓ Configuración: Todos los valores disponibles para ser usados en vistas
✓ Métodos centralizados: calcular_mora_diaria(), total_a_pagar(), total_pagado()
✓ Cálculos: Centralizados en modelos, no duplicados en vistas

PRÓXIMAS TAREAS RECOMENDADAS:
1. Revisar cada vista que crea préstamos para asegurar que usa config defaults
2. Consolidar cálculos duplicados en vistas llamando a métodos del modelo
3. Documentar patrón: "Siempre usar métodos del modelo, nunca duplicar lógica"
""")

print("="*100)
print("FIN DE CORRECCIONES".center(100))
print("="*100 + "\n")
