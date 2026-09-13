#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente
from decimal import Decimal

print("=== VERIFICANDO ESTADÍSTICAS DE CLIENTES ===\n")

clientes = Cliente.objects.all()

for cliente in clientes:
    # Calcular totales reales desde préstamos
    total_prestado_real = sum(p.monto_total for p in cliente.prestamo_set.all())
    
    # Calcular total pagado real desde cuotas
    total_pagado_real = Decimal('0')
    for prestamo in cliente.prestamo_set.all():
        for cuota in prestamo.cuotas.filter(pagado=True):
            total_pagado_real += cuota.monto_original
    
    # Obtener valores almacenados
    total_prestado_almacenado = cliente.total_prestado
    total_pagado_almacenado = cliente.total_pagado
    
    print(f"Cliente: {cliente.nombre}")
    print(f"  Total Prestado - Base de Datos: ${total_prestado_almacenado:.2f}")
    print(f"  Total Prestado - Calculado: ${total_prestado_real:.2f}")
    print(f"  ✓ OK" if total_prestado_almacenado == total_prestado_real else f"  ✗ MISMATCH!")
    
    print(f"  Total Pagado - Base de Datos: ${total_pagado_almacenado:.2f}")
    print(f"  Total Pagado - Calculado: ${total_pagado_real:.2f}")
    print(f"  ✓ OK" if total_pagado_almacenado == total_pagado_real else f"  ✗ MISMATCH!")
    
    if total_prestado_real > 0:
        porcentaje_pagado_bd = (total_pagado_almacenado / total_prestado_real * 100) if total_prestado_real > 0 else 0
        porcentaje_pagado_real = (total_pagado_real / total_prestado_real * 100) if total_prestado_real > 0 else 0
        print(f"  % Pagado (BD): {porcentaje_pagado_bd:.1f}%")
        print(f"  % Pagado (Real): {porcentaje_pagado_real:.1f}%")
    
    print()

print("✓ Verificación completada")
