#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota
from datetime import date, timedelta
from decimal import Decimal

# Crear cliente
cliente = Cliente.objects.create(
    cedula='123456789',
    nombre='Juan Perez',
    celular='3001234567',
    estado='ACTIVO'
)

# Crear préstamo: $1000 a 2 meses (60 días) = 4 cuotas
fecha_inicio = date.today()
fecha_fin = fecha_inicio + timedelta(days=60)  # 2 meses

prestamo = Prestamo.objects.create(
    cliente=cliente,
    monto_total=Decimal('1000.00'),
    interes_porcentaje=Decimal('15.00'),  # 15% mensual
    fecha_inicio=fecha_inicio,
    fecha_fin_estimada=fecha_fin,
    estado='ACTIVO'
)

# Crear 4 cuotas (2 por mes) - ESTRUCTURA QUINCENAL
num_cuotas = 4
cuotas_por_mes = 2
num_meses = num_cuotas / cuotas_por_mes

# Capital por mes
capital_por_mes = prestamo.monto_total / Decimal(num_meses)

# Capital por cuota (cada quincena)
capital_por_cuota = capital_por_mes / Decimal(cuotas_por_mes)
monto_por_cuota = capital_por_cuota

# INTERÉS: Aplicado mensualmente y dividido en 2 quincenas
# 15% mensual = 7.5% por quincena (cada cuota)
interes_por_mes = capital_por_mes * Decimal('0.15')
interes_por_cuota = interes_por_mes / Decimal(cuotas_por_mes)

for i in range(1, num_cuotas + 1):
    fecha_pago = fecha_inicio + timedelta(days=15*i)
    cuota = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=i,
        monto_original=monto_por_cuota,
        monto_pendiente=monto_por_cuota,
        interes_normal=interes_por_cuota,
        fecha_pago_esperada=fecha_pago
    )

print(f"✓ Cliente: {cliente.nombre}")
print(f"✓ Préstamo: ${prestamo.monto_total} a 2 meses (4 cuotas)")
print(f"\nCálculo:")
print(f"  Capital por mes: ${capital_por_mes}")
print(f"  Interés por mes (15%): ${interes_por_mes}")
print(f"  Interés por cuota (÷2): ${interes_por_cuota}")
print(f"\nDetalle de cuotas:")
for cuota in prestamo.cuotas.all():
    total = float(cuota.monto_original) + float(cuota.interes_normal)
    print(f"  Cuota #{cuota.numero_cuota}: ${cuota.monto_original} + ${cuota.interes_normal} = ${total:.2f}")

resumen = prestamo.resumen_financiero()
print(f"\nResumen financiero:")
print(f"  Interés Total: ${resumen['interes_total_credito']:.2f}")
print(f"  Total Crédito: ${resumen['total_credito']:.2f}")
