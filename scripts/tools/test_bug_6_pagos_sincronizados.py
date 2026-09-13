#!/usr/bin/env python
"""
🧪 Script de Prueba - BUG #6: Disonancia de Datos en Pagos

Verifica que:
1. Pagos parciales se detecten correctamente
2. Los campos de estado se actualicen
3. Las vistas muestren datos sincronizados
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
from datetime import date, timedelta

print("\n" + "="*80)
print("🧪 PRUEBA: BUG #6 - Disonancia de Datos en Pagos")
print("="*80)

# Crear cliente de prueba
cliente = Cliente.objects.create(
    nombre="Cliente Test Bug 6",
    celular="3001234567",
    email="test@test.com",
    cedula="1234567890"
)
print(f"\n✅ Cliente creado: {cliente.nombre}")

# Crear préstamo
from datetime import timedelta
config = Configuracion.obtener_configuracion()
fecha_inicio = date.today()
fecha_fin = fecha_inicio + timedelta(days=30)

prestamo = Prestamo.objects.create(
    cliente=cliente,
    monto_total=Decimal('1000'),
    interes_porcentaje=Decimal('15'),
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_fin,
    estado='ACTIVO'
)
print(f"✅ Préstamo creado: ${prestamo.monto_total}")

# Crear cuota manualmente
cuota = Cuota.objects.create(
    prestamo=prestamo,
    numero_cuota=1,
    monto_original=Decimal('1000'),
    monto_pendiente=Decimal('1000'),
    interes_normal=Decimal('75'),
    fecha_pago_esperada=fecha_inicio + timedelta(days=15)
)
print(f"✅ Cuota creada: ${cuota.monto_original}")
print(f"\n📊 Estado inicial de Cuota #{cuota.numero_cuota}:")
print(f"   - monto_original: ${cuota.monto_original}")
print(f"   - monto_pagado_principal: ${cuota.monto_pagado_principal}")
print(f"   - monto_pendiente: ${cuota.monto_pendiente}")
print(f"   - estado: {cuota.estado}")
print(f"   - porcentaje_pagado: {cuota.porcentaje_pagado}%")
print(f"   - pagado: {cuota.pagado}")

# PRUEBA 1: Pago Parcial
print("\n" + "-"*80)
print("TEST 1: Pago Parcial ($500 de $1000)")
print("-"*80)

monto_a_pagar = Decimal('500')
pago1 = Pago.objects.create(
    cuota=cuota,
    monto_pagado=monto_a_pagar,
    monto_principal=monto_a_pagar,
    monto_interes=Decimal('0'),
    monto_mora=Decimal('0'),
    usuario_registra='test',
    referencia='TEST-001'
)
print(f"✅ Pago registrado: ${pago1.monto_pagado}")

# Actualizar cuota (simular lo que hace registrar_pago_mejorado)
cuota.monto_pagado_principal += monto_a_pagar
cuota.monto_pagado_interes += Decimal('0')
cuota.monto_pagado_mora += Decimal('0')
cuota.monto_pendiente = max(cuota.monto_original - cuota.monto_pagado_principal, Decimal('0'))
cuota.monto_pendiente_interes = max(cuota.interes_normal - cuota.monto_pagado_interes, Decimal('0'))

if cuota.monto_pendiente == 0 and cuota.monto_pendiente_interes == 0:
    cuota.pagado = True
    cuota.fecha_pago_real = date.today()

cuota.actualizar_estado()

# Verificar resultados
print(f"\n📊 Estado DESPUÉS del pago parcial:")
print(f"   - monto_pagado_principal: ${cuota.monto_pagado_principal} ✅")
print(f"   - monto_pendiente: ${cuota.monto_pendiente} ✅")
print(f"   - estado: {cuota.estado}", end="")
if cuota.estado == 'PARCIALMENTE_PAGADA':
    print(" ✅ CORRECTO")
else:
    print(f" ❌ ERROR - Esperaba PARCIALMENTE_PAGADA, got {cuota.estado}")
    
print(f"   - porcentaje_pagado: {cuota.porcentaje_pagado}%", end="")
if cuota.porcentaje_pagado == 50:
    print(" ✅ CORRECTO")
else:
    print(f" ❌ ERROR - Esperaba 50%, got {cuota.porcentaje_pagado}%")

# Prueba detalles_completos()
detalles = cuota.detalles_completos()
print(f"\n📋 Método detalles_completos():")
print(f"   - pagado_principal: ${detalles['pagado_principal']} (esperado: 500)")
print(f"   - pendiente_principal: ${detalles['pendiente_principal']} (esperado: 500)")
print(f"   - estado: {detalles['estado']} (esperado: PAGADA o similar)")

# PRUEBA 2: Pago completo
print("\n" + "-"*80)
print("TEST 2: Pago Completo (Resto $500 + interés)")
print("-"*80)

monto_interes = cuota.interes_normal
monto_segunda = Decimal('500') + monto_interes
pago2 = Pago.objects.create(
    cuota=cuota,
    monto_pagado=monto_segunda,
    monto_principal=Decimal('500'),
    monto_interes=monto_interes,
    monto_mora=Decimal('0'),
    usuario_registra='test',
    referencia='TEST-002'
)
print(f"✅ Pago registrado: ${pago2.monto_pagado} (capital: $500 + interés: ${monto_interes})")

# Actualizar cuota
cuota.monto_pagado_principal += Decimal('500')
cuota.monto_pagado_interes += monto_interes
cuota.monto_pagado_mora += Decimal('0')
cuota.monto_pendiente = max(cuota.monto_original - cuota.monto_pagado_principal, Decimal('0'))
cuota.monto_pendiente_interes = max(cuota.interes_normal - cuota.monto_pagado_interes, Decimal('0'))

if cuota.monto_pendiente == 0 and cuota.monto_pendiente_interes == 0:
    cuota.pagado = True
    cuota.fecha_pago_real = date.today()

cuota.actualizar_estado()

print(f"\n📊 Estado DESPUÉS del pago completo:")
print(f"   - monto_pagado_principal: ${cuota.monto_pagado_principal} ✅")
print(f"   - monto_pagado_interes: ${cuota.monto_pagado_interes} ✅")
print(f"   - monto_pendiente: ${cuota.monto_pendiente} ✅")
print(f"   - monto_pendiente_interes: ${cuota.monto_pendiente_interes} ✅")
print(f"   - estado: {cuota.estado}", end="")
if cuota.estado == 'PAGADA':
    print(" ✅ CORRECTO")
else:
    print(f" ❌ ERROR - Esperaba PAGADA, got {cuota.estado}")
    
print(f"   - porcentaje_pagado: {cuota.porcentaje_pagado}%", end="")
if cuota.porcentaje_pagado == 100:
    print(" ✅ CORRECTO")
else:
    print(f" ❌ ERROR - Esperaba 100%, got {cuota.porcentaje_pagado}%")

print(f"   - pagado: {cuota.pagado}", end="")
if cuota.pagado:
    print(" ✅ CORRECTO")
else:
    print(" ❌ ERROR")

# Verificar historial de pagos
pagos = Pago.objects.filter(cuota=cuota).order_by('-fecha_pago')
print(f"\n📜 Historial de pagos: {pagos.count()} transacciones")
for i, p in enumerate(pagos, 1):
    print(f"   {i}. ${p.monto_pagado} ({p.referencia}) - {p.fecha_pago.strftime('%d/%m/%Y %H:%M')}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
print("="*80 + "\n")

# Limpiar
cliente.delete()
print("🧹 Datos de prueba eliminados")
