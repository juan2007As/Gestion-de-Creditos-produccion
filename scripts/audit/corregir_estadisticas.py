#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente
from decimal import Decimal

print("=== CORRIGIENDO ESTADÍSTICAS DE CLIENTES ===\n")

clientes = Cliente.objects.all()
correcciones = 0

for cliente in clientes:
    # Calcular totales reales desde préstamos
    total_prestado_nuevo = sum(Decimal(str(p.monto_total)) for p in cliente.prestamo_set.all())
    
    # Calcular total pagado real desde cuotas
    total_pagado_nuevo = Decimal('0')
    for prestamo in cliente.prestamo_set.all():
        for cuota in prestamo.cuotas.filter(pagado=True):
            total_pagado_nuevo += Decimal(str(cuota.monto_original))
    
    # Actualizar si hay cambios
    if cliente.total_prestado != total_prestado_nuevo or cliente.total_pagado != total_pagado_nuevo:
        print(f"Actualizando: {cliente.nombre}")
        print(f"  Total Prestado: ${cliente.total_prestado:.2f} → ${total_prestado_nuevo:.2f}")
        print(f"  Total Pagado: ${cliente.total_pagado:.2f} → ${total_pagado_nuevo:.2f}")
        
        cliente.total_prestado = total_prestado_nuevo
        cliente.total_pagado = total_pagado_nuevo
        cliente.save()
        correcciones += 1
        print()

print(f"✓ Se actualizaron {correcciones} clientes")
