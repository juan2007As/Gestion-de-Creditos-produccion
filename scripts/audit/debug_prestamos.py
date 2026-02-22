#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Prestamo, Cuota
from datetime import date

print("\n" + "="*80)
print("ANÁLISIS DE FECHAS DE PRÉSTAMOS EXISTENTES")
print("="*80)

# Buscar los últimos 3 préstamos
prestamos = Prestamo.objects.all().order_by('-id')[:3]

if not prestamos:
    print("❌ No hay préstamos en la base de datos")
else:
    for prestamo in prestamos:
        print(f"\n✓ Préstamo ID: {prestamo.id}")
        print(f"  Fecha inicio: {prestamo.fecha_inicio}")
        print(f"  Cliente: {prestamo.cliente.nombre}")
        print(f"  Tipo: {prestamo.tipo_pago}")
        print(f"  Cuotas:")
        
        cuotas = prestamo.cuotas.all().order_by('numero_cuota')
        for i, cuota in enumerate(cuotas):
            if i > 0:
                dias_diff = (cuota.fecha_pago_esperada - cuotas[i-1].fecha_pago_esperada).days
                status = "✓" if dias_diff >= 15 else "❌"
                print(f"    {status} Cuota {cuota.numero_cuota}: {cuota.fecha_pago_esperada} ({dias_diff} días desde anterior)")
            else:
                print(f"     Cuota {cuota.numero_cuota}: {cuota.fecha_pago_esperada}")

print("\n" + "="*80)
