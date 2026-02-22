#!/usr/bin/env python
"""
Script para validar las 3 correcciones realizadas:
1. Alertas overlay global
2. Búsqueda con dropdown fijo
3. Fechas de cuotas con 15+ días entre cada una
"""

import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import calcular_fechas_pago

print("\n" + "="*80)
print("PRUEBA #3: VALIDACIÓN DE FECHAS DE CUOTAS CON 15+ DÍAS ENTRE CADA UNA")
print("="*80)

# Prueba 1: QUINCENAL
print("\n✓ PRUEBA QUINCENAL (5, 15, 20, 30):")
print("-" * 60)
fecha_inicio_q = date(2026, 1, 25)  # Sábado 25 de enero
fechas_q = calcular_fechas_pago('QUINCENAL', 6, fecha_inicio_q)

print(f"Fecha inicio: {fecha_inicio_q.strftime('%A, %d de %B de %Y')}")
print(f"Cuotas generadas: {len(fechas_q)}\n")

for i, fecha in enumerate(fechas_q, 1):
    print(f"Cuota {i}: {fecha.strftime('%A, %d de %B de %Y')} (Día {fecha.day})")
    if i > 1:
        dias_diff = (fecha - fechas_q[i-2]).days
        print(f"         ↳ Diferencia con anterior: {dias_diff} días", end="")
        if dias_diff >= 15:
            print(" ✓")
        else:
            print(" ✗ ERROR: MENOS DE 15 DÍAS")

# Prueba 2: MENSUAL
print("\n\n✓ PRUEBA MENSUAL (día 1):")
print("-" * 60)
fecha_inicio_m = date(2026, 1, 25)  # Sábado 25 de enero
fechas_m = calcular_fechas_pago('MENSUAL', 4, fecha_inicio_m)

print(f"Fecha inicio: {fecha_inicio_m.strftime('%A, %d de %B de %Y')}")
print(f"Cuotas generadas: {len(fechas_m)}\n")

for i, fecha in enumerate(fechas_m, 1):
    print(f"Cuota {i}: {fecha.strftime('%A, %d de %B de %Y')} (Día {fecha.day})")
    if i > 1:
        dias_diff = (fecha - fechas_m[i-2]).days
        print(f"         ↳ Diferencia con anterior: {dias_diff} días", end="")
        if dias_diff >= 15:
            print(" ✓")
        else:
            print(" ✗ ERROR: MENOS DE 15 DÍAS")

# Prueba 3: Caso especial - Comenzar en fecha que lleva a febrero
print("\n\n✓ PRUEBA ESPECIAL (Transición enero→febrero):")
print("-" * 60)
fecha_inicio_esp = date(2026, 1, 28)  # 28 de enero
fechas_esp = calcular_fechas_pago('QUINCENAL', 5, fecha_inicio_esp)

print(f"Fecha inicio: {fecha_inicio_esp.strftime('%A, %d de %B de %Y')}")
print(f"Cuotas generadas: {len(fechas_esp)}\n")

for i, fecha in enumerate(fechas_esp, 1):
    print(f"Cuota {i}: {fecha.strftime('%A, %d de %B de %Y')} (Día {fecha.day})")
    if i > 1:
        dias_diff = (fecha - fechas_esp[i-2]).days
        print(f"         ↳ Diferencia con anterior: {dias_diff} días", end="")
        if dias_diff >= 15:
            print(" ✓")
        else:
            print(" ✗ ERROR: MENOS DE 15 DÍAS")

print("\n" + "="*80)
print("PRUEBAS COMPLETADAS")
print("="*80)
print("\nNOTA: Las otras 2 correcciones (#5 Alertas y #6 Búsqueda) se validan")
print("      manualmente en el navegador.")
print("="*80 + "\n")
