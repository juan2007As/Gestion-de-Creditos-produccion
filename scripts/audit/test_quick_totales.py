#!/usr/bin/env python
"""Script de prueba para verificar que los métodos nuevos funcionan"""

import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from mi_app.models import Cliente, Prestamo
from decimal import Decimal

print("\n" + "=" * 80)
print("✅ TEST RÁPIDO - MÉTODOS DE TOTAL PRESTADO")
print("=" * 80 + "\n")

# Crear cliente
cliente, _ = Cliente.objects.get_or_create(
    cedula='99999999',
    defaults={
        'nombre': 'Test Cliente Totales',
        'celular': '+1234567890',
        'email': 'test_totales@example.com',
        'total_prestado': Decimal('0')
    }
)

print(f"📌 Cliente: {cliente.nombre}")
print()

# Prueba 1: Sin préstamos
print("TEST 1: Sin préstamos")
print(f"  total_prestado_real: ${cliente.total_prestado_real:,.2f}")
print(f"  total_prestado_activo: ${cliente.total_prestado_activo:,.2f}")
print(f"  total_prestado_completado: ${cliente.total_prestado_completado:,.2f}")
print()

# Crear préstamos de prueba
fecha = datetime.now().date()

prestamo1, _ = Prestamo.objects.get_or_create(
    cliente=cliente,
    monto_total=Decimal('100000'),
    defaults={
        'interes_porcentaje': Decimal('20'),
        'estado': 'ACTIVO',
        'fecha_inicio': fecha,
        'fecha_fin_estimada': fecha + timedelta(days=90),
        'tipo_pago': 'QUINCENAL'
    }
)

prestamo2, _ = Prestamo.objects.get_or_create(
    cliente=cliente,
    monto_total=Decimal('50000'),
    defaults={
        'interes_porcentaje': Decimal('15'),
        'estado': 'ACTIVO',
        'fecha_inicio': fecha,
        'fecha_fin_estimada': fecha + timedelta(days=180),
        'tipo_pago': 'MENSUAL'
    }
)

prestamo3, _ = Prestamo.objects.get_or_create(
    cliente=cliente,
    monto_total=Decimal('75000'),
    defaults={
        'interes_porcentaje': Decimal('25'),
        'estado': 'COMPLETADO',
        'fecha_inicio': fecha,
        'fecha_fin_estimada': fecha + timedelta(days=45),
        'tipo_pago': 'QUINCENAL'
    }
)

print("TEST 2: Con préstamos")
print(f"  Préstamo 1 (ACTIVO): ${prestamo1.monto_total:,.2f}")
print(f"  Préstamo 2 (ACTIVO): ${prestamo2.monto_total:,.2f}")
print(f"  Préstamo 3 (COMPLETADO): ${prestamo3.monto_total:,.2f}")
print()
print(f"  total_prestado_real: ${cliente.total_prestado_real:,.2f}")
print(f"  total_prestado_activo: ${cliente.total_prestado_activo:,.2f}")
print(f"  total_prestado_completado: ${cliente.total_prestado_completado:,.2f}")
print()

# Test 3: Detección de inconsistencia
print("TEST 3: Detección de inconsistencias")
print(f"  Total en BD: ${cliente.total_prestado:,.2f}")
print(f"  Total real: ${cliente.total_prestado_real:,.2f}")

tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
print(f"  ¿Hay inconsistencia? {tiene_inconsistencia}")
print(f"  Diferencia: ${diferencia:,.2f}")
print()

# Test 4: Corrección
print("TEST 4: Corrección de inconsistencias")
if not tiene_inconsistencia:
    # Crear inconsistencia manual
    cliente.total_prestado = Decimal('50000')
    cliente.save()
    print(f"  (Simulada inconsistencia: BD=${cliente.total_prestado:,.2f}, Real=${cliente.total_prestado_real:,.2f})")
    
    tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
    print(f"  ¿Hay inconsistencia? {tiene_inconsistencia}")
    print(f"  Diferencia: ${diferencia:,.2f}")
    print()
    
    # Corregir
    total_anterior, total_nuevo, diferencia = cliente.corregir_totales()
    print(f"  Corrección aplicada:")
    print(f"    Anterior: ${total_anterior:,.2f}")
    print(f"    Nuevo: ${total_nuevo:,.2f}")
    print(f"    Diferencia: ${diferencia:,.2f}")

print()
print("=" * 80)
print("✅ TODOS LOS TESTS COMPLETADOS")
print("=" * 80 + "\n")
