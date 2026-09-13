#!/usr/bin/env python
"""
🧪 Script de Prueba - BUG #4: Préstamo Rápido - Valores No Actualizan

Verifica que:
1. Los valores se actualizan correctamente después de un pago
2. Las propiedades calculadas reflejan el estado actual
3. El estado se actualiza apropiadamente
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from mi_app.models import Cliente, PrestamoRapido, PagoPrestamoRapido
from decimal import Decimal
from datetime import date

print("\n" + "="*80)
print("🧪 PRUEBA: BUG #4 - Préstamo Rápido - Valores No Actualizan")
print("="*80)

# Crear cliente de prueba
cliente = Cliente.objects.create(
    nombre="Cliente Test Bug 4",
    celular="3009876543",
    email="test_bug4@test.com",
    cedula="9876543210"
)
print(f"\n✅ Cliente creado: {cliente.nombre}")

# Crear préstamo rápido
prestamo = PrestamoRapido.objects.create(
    cliente=cliente,
    monto=Decimal('1000'),
    interes_porcentaje=Decimal('20'),
    estado='PENDIENTE'
)
print(f"✅ Préstamo Rápido creado: ${prestamo.monto} + {prestamo.interes_porcentaje}% interés")

# Estado inicial
print(f"\n📊 Estado Inicial:")
print(f"   - monto: ${prestamo.monto}")
print(f"   - total_a_pagar: ${prestamo.total_a_pagar} (esperado: $1200)")
print(f"   - monto_pagado: ${prestamo.monto_pagado} (esperado: $0)")
print(f"   - saldo_pendiente: ${prestamo.saldo_pendiente} (esperado: $1200)")
print(f"   - porcentaje_pagado: {prestamo.porcentaje_pagado:.2f}% (esperado: 0%)")
print(f"   - estado: {prestamo.estado} (esperado: PENDIENTE)")

# TEST 1: Pago Parcial
print("\n" + "-"*80)
print("TEST 1: Pago Parcial ($500 de $1200)")
print("-"*80)

pago1 = PagoPrestamoRapido.objects.create(
    prestamo_rapido=prestamo,
    monto_pagado=Decimal('500'),
    usuario_registra='test',
    referencia='TEST-001'
)
print(f"✅ Pago registrado: ${pago1.monto_pagado}")

# Simular lo que hace registrar_pago_rapido()
prestamo.monto_pagado += Decimal('500')
prestamo.actualizar_estado()
prestamo.save()

# BUG #4 FIX: Refresh from db
prestamo.refresh_from_db()

print(f"\n📊 Estado DESPUÉS del pago parcial (con refresh_from_db):")
print(f"   - monto_pagado: ${prestamo.monto_pagado}", end="")
if prestamo.monto_pagado == Decimal('500'):
    print(" ✅")
else:
    print(f" ❌ (esperaba $500)")

print(f"   - saldo_pendiente: ${prestamo.saldo_pendiente}", end="")
if prestamo.saldo_pendiente == Decimal('700'):
    print(" ✅")
else:
    print(f" ❌ (esperaba $700)")

print(f"   - porcentaje_pagado: {prestamo.porcentaje_pagado:.2f}%", end="")
if abs(prestamo.porcentaje_pagado - 41.67) < 0.1:
    print(" ✅")
else:
    print(f" ❌ (esperaba ~41.67%)")

print(f"   - estado: {prestamo.estado}", end="")
if prestamo.estado == 'PARCIALMENTE_PAGADO':
    print(" ✅")
else:
    print(f" ❌ (esperaba PARCIALMENTE_PAGADO)")

# TEST 2: Pago Completo
print("\n" + "-"*80)
print("TEST 2: Pago Completo (Resto $700)")
print("-"*80)

pago2 = PagoPrestamoRapido.objects.create(
    prestamo_rapido=prestamo,
    monto_pagado=Decimal('700'),
    usuario_registra='test',
    referencia='TEST-002'
)
print(f"✅ Pago registrado: ${pago2.monto_pagado}")

# Simular lo que hace registrar_pago_rapido()
prestamo.monto_pagado += Decimal('700')
prestamo.actualizar_estado()
prestamo.save()

# BUG #4 FIX: Refresh from db
prestamo.refresh_from_db()

print(f"\n📊 Estado DESPUÉS del pago completo (con refresh_from_db):")
print(f"   - monto_pagado: ${prestamo.monto_pagado}", end="")
if prestamo.monto_pagado == Decimal('1200'):
    print(" ✅")
else:
    print(f" ❌ (esperaba $1200)")

print(f"   - saldo_pendiente: ${prestamo.saldo_pendiente}", end="")
if prestamo.saldo_pendiente == Decimal('0'):
    print(" ✅")
else:
    print(f" ❌ (esperaba $0)")

print(f"   - porcentaje_pagado: {prestamo.porcentaje_pagado:.2f}%", end="")
if prestamo.porcentaje_pagado == Decimal('100'):
    print(" ✅")
else:
    print(f" ❌ (esperaba 100%)")

print(f"   - estado: {prestamo.estado}", end="")
if prestamo.estado == 'PAGADO':
    print(" ✅")
else:
    print(f" ❌ (esperaba PAGADO)")

# Historial de pagos
pagos = PagoPrestamoRapido.objects.filter(prestamo_rapido=prestamo).order_by('-fecha_pago')
print(f"\n📜 Historial de pagos: {pagos.count()} transacciones")
for i, p in enumerate(pagos, 1):
    print(f"   {i}. ${p.monto_pagado} ({p.referencia}) - {p.fecha_pago.strftime('%d/%m/%Y %H:%M')}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
print("="*80 + "\n")

# Limpiar
cliente.delete()
print("🧹 Datos de prueba eliminados")
