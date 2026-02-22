#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota
from datetime import date, timedelta

# Obtener cliente
cliente = Cliente.objects.get(nombre='Juan Carlos Pérez')
print(f"Cliente: {cliente.nombre}")
print(f"Total de préstamos: {cliente.prestamo_set.count()}")

# Listar todos los préstamos
for i, prestamo in enumerate(cliente.prestamo_set.all(), 1):
    cuotas_count = prestamo.cuotas.count()
    print(f"\nPréstamo #{i}:")
    print(f"  Monto: ${prestamo.monto_total:,}")
    print(f"  Cuotas: {cuotas_count}")
    
    # Listar cuotas
    for j, cuota in enumerate(prestamo.cuotas.all(), 1):
        print(f"    Cuota #{j}: Principal ${cuota.monto_original:,} + Interés ${cuota.interes_normal:,} - Estado: {cuota.estado}")

# Ahora simular vencimiento en la SEGUNDA cuota (la PENDIENTE)
print("\n" + "="*60)
print("SIMULANDO VENCIMIENTO...")
print("="*60)

prestamo1 = cliente.prestamo_set.first()
# Obtener la segunda cuota (la PENDIENTE)
cuota2 = prestamo1.cuotas.all()[1]

print(f"\nPréstamo: ${prestamo1.monto_total:,}")
print(f"Cuota #2 (PENDIENTE) - Principal: ${cuota2.monto_original:,} + Interés: ${cuota2.interes_normal:,}")
print(f"Estado ANTES: {cuota2.estado}")

# Modificar fecha a 15 días atrás
cuota2.fecha_pago_esperada = date.today() - timedelta(days=15)
cuota2.save()

print(f"\n✅ Cuota modificada: Vencida hace 15 días")
print(f"   Fecha vencimiento: {cuota2.fecha_pago_esperada}")
print(f"   Mora calculada: ${cuota2.calcular_mora_diaria():,}")
print(f"   Estado DESPUÉS: {cuota2.estado}")
