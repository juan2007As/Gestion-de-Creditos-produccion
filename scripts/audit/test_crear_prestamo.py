#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Prestamo, Cliente, Cuota, Configuracion
from datetime import date
from decimal import Decimal

print("\n" + "="*80)
print("TEST: CREAR NUEVO PRÉSTAMO CON LA LÓGICA CORREGIDA")
print("="*80)

# Obtener un cliente
cliente = Cliente.objects.first()
if not cliente:
    print("❌ No hay clientes")
    exit()

# Crear un préstamo de prueba
config = Configuracion.obtener_configuracion()
fecha_inicio = date(2026, 1, 25)

prestamo_test = Prestamo.objects.create(
    cliente=cliente,
    monto_total=Decimal('1000'),
    interes_porcentaje=Decimal('5'),
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_inicio,
    tipo_pago='QUINCENAL',
    estado='ACTIVO'
)

# Usar la función corregida para obtener fechas
from mi_app.models import calcular_fechas_pago
fechas = calcular_fechas_pago('QUINCENAL', 6, fecha_inicio)

print(f"\nPréstamo de prueba creado: ID {prestamo_test.id}")
print(f"Fecha inicio: {fecha_inicio}")
print(f"Fechas calculadas: {fechas}")
print(f"\nFechas con diferencias:")

for i, fecha in enumerate(fechas):
    if i > 0:
        dias = (fecha - fechas[i-1]).days
        status = "✓" if dias >= 15 else "❌"
        print(f"  {status} Cuota {i+1}: {fecha} ({dias} días)")
    else:
        print(f"   Cuota {i+1}: {fecha}")

# Crear cuotas con las fechas correctas
for i, fecha in enumerate(fechas, 1):
    Cuota.objects.create(
        prestamo=prestamo_test,
        numero_cuota=i,
        monto_original=Decimal('166.67'),
        monto_pendiente=Decimal('166.67'),
        interes_normal=Decimal('8.33'),
        fecha_pago_esperada=fecha
    )

print(f"\n✓ {len(fechas)} cuotas creadas exitosamente")
print(f"✓ Préstamo test: {prestamo_test.id}")
print("\n" + "="*80)
