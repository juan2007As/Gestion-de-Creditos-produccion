"""
TEST 4: Verificar estado de las cuotas importadas
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cuota, Cliente
from datetime import date
from decimal import Decimal

print("=" * 80)
print("TEST 4: VERIFICAR ESTADO DE CUOTAS EN BD")
print("=" * 80)

# Obtener todas las cuotas
cuotas = Cuota.objects.all().select_related('prestamo__cliente').order_by('prestamo__cliente__nombre')

print(f"\nTotal de cuotas en BD: {cuotas.count()}\n")

for cuota in cuotas:
    cliente = cuota.prestamo.cliente
    dias_atraso = (date.today() - cuota.fecha_pago_esperada).days if cuota.fecha_pago_esperada else None
    mora_calculada = cuota.calcular_mora_diaria()
    
    print(f"Cuota #{cuota.numero_cuota} | Cliente: {cliente.nombre}")
    print(f"  Estado BD: {cuota.estado:<15} | Pagado: {str(cuota.pagado):<5} | Mora: ${mora_calculada}")
    print(f"  Fecha vencimiento: {cuota.fecha_pago_esperada} | Días atraso: {dias_atraso}")
    print(f"  Pagado: ${cuota.monto_pagado_principal} de ${cuota.monto_original}")
    print()

# Resumen de estados
print("\n" + "=" * 80)
print("RESUMEN POR ESTADO:")
print("=" * 80)

for estado in ['PENDIENTE', 'VENCIDA', 'VENCIDA_PARCIAL', 'PAGADA']:
    count = Cuota.objects.filter(estado=estado).count()
    print(f"  {estado}: {count} cuotas")

print("\n✅ TEST 4 COMPLETADO")
