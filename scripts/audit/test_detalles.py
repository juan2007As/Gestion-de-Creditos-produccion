#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto_john.settings")
django.setup()

from mi_app.models import Cuota

# Buscar una cuota que está PAGADA
cuota = Cuota.objects.filter(estado='PAGADA').first()
if cuota:
    detalles = cuota.detalles_completos()
    print(f'=== Cuota {cuota.numero_cuota} (PAGADA) ===')
    print()
    print('DESGLOSE PAGADO:')
    print(f'  Principal Pagado: ${detalles["pagado_principal"]:.2f}')
    print(f'  Interés Pagado: ${detalles["pagado_interes"]:.2f}')
    print(f'  Mora Pagada: ${detalles["pagado_mora"]:.2f}')
    print(f'  TOTAL PAGADO: ${detalles["pagado_total"]:.2f}')
    print()
    print('DESGLOSE PENDIENTE:')
    print(f'  Principal Pendiente: ${detalles["pendiente_principal"]:.2f}')
    print(f'  Interés Pendiente: ${detalles["pendiente_interes"]:.2f}')
    print(f'  Mora Pendiente: ${detalles["pendiente_mora"]:.2f}')
    print(f'  TOTAL PENDIENTE: ${detalles["pendiente_total"]:.2f}')
else:
    print('No hay cuotas pagadas')
