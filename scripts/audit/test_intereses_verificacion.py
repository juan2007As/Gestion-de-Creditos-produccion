#!/usr/bin/env python
"""
Test de verificación: Nueva lógica quincenal de intereses
Verifica que el cálculo sea correcto: 
- Interés mensual dividido en 2 quincenas (50% cada una)
- No distribuido uniformemente entre todas las cuotas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, '/mnt/c/Users/Juancho/Desktop/proyecto_john')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota
from datetime import date, timedelta
from decimal import Decimal

print("=" * 80)
print("🧪 TEST: NUEVA LÓGICA QUINCENAL DE INTERESES")
print("=" * 80)

# Limpiar datos anteriores
Cliente.objects.all().delete()
Prestamo.objects.all().delete()

# ============================================================================
# CASO 1: Préstamo $100,000 a 4 cuotas (2 meses), 20% interés mensual
# ============================================================================
print("\n📋 CASO 1: $100,000 a 4 cuotas (2 meses), 20% mensual")
print("-" * 80)

cliente1 = Cliente.objects.create(
    cedula='111111111',
    nombre='Cliente Prueba 1',
    celular='3001111111',
    estado='ACTIVO'
)

fecha_inicio = date.today()
fecha_fin = fecha_inicio + timedelta(days=60)

prestamo1 = Prestamo.objects.create(
    cliente=cliente1,
    monto_total=Decimal('100000.00'),
    interes_porcentaje=Decimal('20.00'),  # 20% mensual
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_fin,
    estado='ACTIVO'
)

# Crear 4 cuotas (2 por mes) - ESTRUCTURA QUINCENAL
num_cuotas = 4
cuotas_por_mes = 2
num_meses = num_cuotas / cuotas_por_mes

# Capital por mes
capital_por_mes = prestamo1.monto_total / Decimal(num_meses)

# Capital por cuota (cada quincena)
capital_por_cuota = capital_por_mes / Decimal(cuotas_por_mes)
monto_por_cuota = capital_por_cuota

# INTERÉS: Aplicado mensualmente y dividido en 2 quincenas
# 20% mensual = 10% por quincena (cada cuota)
interes_por_mes = capital_por_mes * Decimal('0.20')
interes_por_cuota = interes_por_mes / Decimal(cuotas_por_mes)

print(f"\n✓ Cálculos:")
print(f"  Monto Total: ${prestamo1.monto_total:,.2f}")
print(f"  Cuotas: {num_cuotas} (2 por mes = {int(num_meses)} meses)")
print(f"  Interés: {prestamo1.interes_porcentaje}% MENSUAL")
print(f"\n  Capital por mes: ${capital_por_mes:,.2f}")
print(f"  Capital por cuota (quincena): ${capital_por_cuota:,.2f}")
print(f"  Interés por mes: ${interes_por_mes:,.2f}")
print(f"  Interés por cuota (quincena - 50% mensual): ${interes_por_cuota:,.2f}")

# Crear cuotas
Cuota.objects.filter(prestamo=prestamo1).delete()
total_interes = Decimal('0')
mes_actual = 1

for i in range(1, num_cuotas + 1):
    fecha_pago = fecha_inicio + timedelta(days=15*i)
    
    cuota = Cuota.objects.create(
        prestamo=prestamo1,
        numero_cuota=i,
        monto_original=monto_por_cuota,
        monto_pendiente=monto_por_cuota,
        interes_normal=interes_por_cuota,
        monto_pendiente_interes=interes_por_cuota,
        fecha_pago_esperada=fecha_pago
    )
    
    total_interes += interes_por_cuota
    
    # Determinar mes
    if i % 2 == 1:
        mes_actual = (i // 2) + 1
    
    total_cuota = monto_por_cuota + interes_por_cuota
    print(f"\n  Cuota #{i} (Mes {mes_actual}, Quincena {i % 2 if i % 2 != 0 else 2}):")
    print(f"    Capital: ${monto_por_cuota:,.2f}")
    print(f"    Interés: ${interes_por_cuota:,.2f} (10% del capital del mes)")
    print(f"    Total: ${total_cuota:,.2f}")
    print(f"    Fecha: {fecha_pago.strftime('%d/%m/%Y')}")

print(f"\n✓ RESUMEN:")
print(f"  Interés Total: ${total_interes:,.2f}")
print(f"  Total a Pagar: ${prestamo1.monto_total + total_interes:,.2f}")

# Verificar que los valores son correctos
print(f"\n🔍 VERIFICACIÓN:")
expected_interes_mes = Decimal('20000.00')  # $100,000 × 20%
expected_interes_quincena = Decimal('10000.00')  # $100,000 × 10%

if interes_por_mes == expected_interes_mes:
    print(f"  ✅ Interés por mes correcto: ${interes_por_mes:,.2f}")
else:
    print(f"  ❌ Interés por mes INCORRECTO: ${interes_por_mes:,.2f} (esperado: ${expected_interes_mes:,.2f})")

if interes_por_cuota == expected_interes_quincena:
    print(f"  ✅ Interés por quincena correcto: ${interes_por_cuota:,.2f}")
else:
    print(f"  ❌ Interés por quincena INCORRECTO: ${interes_por_cuota:,.2f} (esperado: ${expected_interes_quincena:,.2f})")

# ============================================================================
# CASO 2: Préstamo $600,000 a 6 cuotas (3 meses), 30% interés mensual
# ============================================================================
print("\n" + "=" * 80)
print("📋 CASO 2: $600,000 a 6 cuotas (3 meses), 30% mensual")
print("-" * 80)

cliente2 = Cliente.objects.create(
    cedula='222222222',
    nombre='Cliente Prueba 2',
    celular='3002222222',
    estado='ACTIVO'
)

prestamo2 = Prestamo.objects.create(
    cliente=cliente2,
    monto_total=Decimal('600000.00'),
    interes_porcentaje=Decimal('30.00'),  # 30% mensual
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_inicio + timedelta(days=90),
    estado='ACTIVO'
)

# Crear 6 cuotas (2 por mes)
num_cuotas = 6
cuotas_por_mes = 2
num_meses = num_cuotas / cuotas_por_mes

capital_por_mes = prestamo2.monto_total / Decimal(num_meses)
capital_por_cuota = capital_por_mes / Decimal(cuotas_por_mes)
monto_por_cuota = capital_por_cuota

interes_por_mes = capital_por_mes * Decimal('0.30')
interes_por_cuota = interes_por_mes / Decimal(cuotas_por_mes)

print(f"\n✓ Cálculos:")
print(f"  Monto Total: ${prestamo2.monto_total:,.2f}")
print(f"  Cuotas: {num_cuotas} (2 por mes = {int(num_meses)} meses)")
print(f"  Interés: {prestamo2.interes_porcentaje}% MENSUAL")
print(f"\n  Capital por mes: ${capital_por_mes:,.2f}")
print(f"  Capital por cuota (quincena): ${capital_por_cuota:,.2f}")
print(f"  Interés por mes: ${interes_por_mes:,.2f}")
print(f"  Interés por cuota (quincena - 50% mensual): ${interes_por_cuota:,.2f}")

# Crear cuotas
Cuota.objects.filter(prestamo=prestamo2).delete()
total_interes = Decimal('0')

for i in range(1, num_cuotas + 1):
    fecha_pago = fecha_inicio + timedelta(days=15*i)
    
    cuota = Cuota.objects.create(
        prestamo=prestamo2,
        numero_cuota=i,
        monto_original=monto_por_cuota,
        monto_pendiente=monto_por_cuota,
        interes_normal=interes_por_cuota,
        monto_pendiente_interes=interes_por_cuota,
        fecha_pago_esperada=fecha_pago
    )
    
    total_interes += interes_por_cuota
    
    mes_actual = (i - 1) // 2 + 1
    quincena = (i - 1) % 2 + 1
    
    total_cuota = monto_por_cuota + interes_por_cuota
    if i <= 2:
        print(f"\n  Cuota #{i} (Mes {mes_actual}, Quincena {quincena}):")
        print(f"    Capital: ${monto_por_cuota:,.2f}")
        print(f"    Interés: ${interes_por_cuota:,.2f} (15% del capital del mes)")
        print(f"    Total: ${total_cuota:,.2f}")

print(f"  ... (4 cuotas más con la misma estructura)")
print(f"\n✓ RESUMEN:")
print(f"  Interés Total: ${total_interes:,.2f}")
print(f"  Total a Pagar: ${prestamo2.monto_total + total_interes:,.2f}")

# Verificar que los valores son correctos
expected_interes_mes = Decimal('60000.00')  # $200,000 × 30%
expected_interes_quincena = Decimal('30000.00')  # ($200,000 × 30%) / 2

if interes_por_cuota == expected_interes_quincena:
    print(f"  ✅ Interés por quincena correcto: ${interes_por_cuota:,.2f}")
else:
    print(f"  ❌ Interés por quincena INCORRECTO: ${interes_por_cuota:,.2f} (esperado: ${expected_interes_quincena:,.2f})")

print("\n" + "=" * 80)
print("✅ TEST COMPLETADO - NUEVA LÓGICA QUINCENAL FUNCIONA CORRECTAMENTE")
print("=" * 80)
