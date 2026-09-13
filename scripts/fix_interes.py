#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cuota
from decimal import Decimal

# Contar cuotas con monto_pendiente_interes = 0
cuotas_cero = Cuota.objects.filter(monto_pendiente_interes=0)
print(f"Total cuotas con interés pendiente = 0: {cuotas_cero.count()}")

# Mostrar primeras 5
for cuota in cuotas_cero[:5]:
    print(f"  Cuota #{cuota.numero_cuota} - Interés: {cuota.interes_normal}, Pagado: {cuota.monto_pagado_interes}, Pendiente: {cuota.monto_pendiente_interes}")

# Arreglar todas las cuotas no pagadas que tengan interes_normal pero monto_pendiente_interes = 0
actualizar = []
for cuota in Cuota.objects.filter(pagado=False, interes_normal__gt=0, monto_pendiente_interes=0):
    # El pendiente es lo que debe pagar menos lo que ya pagó
    cuota.monto_pendiente_interes = cuota.interes_normal - cuota.monto_pagado_interes
    actualizar.append(cuota)

# Actualizar en lote
if actualizar:
    Cuota.objects.bulk_update(actualizar, ['monto_pendiente_interes'], batch_size=100)
    print(f"\n✅ Actualizadas {len(actualizar)} cuotas")
    
    # Verificar que quedó bien
    for cuota in actualizar[:3]:
        print(f"  Verificación - Cuota #{cuota.numero_cuota}: Pendiente Interés = {cuota.monto_pendiente_interes}")
else:
    print("\n✅ No hay cuotas para actualizar")
