#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente
from decimal import Decimal

print("=== VERIFICANDO CÁLCULO DE 'EN CIRCULACIÓN' ===\n")

clientes = Cliente.objects.filter(prestamo__estado='ACTIVO').distinct()

for cliente in clientes:
    prestamos_activos = cliente.prestamo_set.filter(estado='ACTIVO')
    
    print(f"Cliente: {cliente.nombre}")
    
    total_en_circulacion = Decimal('0')
    for prestamo in prestamos_activos:
        print(f"  Préstamo #{prestamo.id}")
        print(f"    Monto Total: ${prestamo.monto_total}")
        print(f"    Total Crédito (principal + interés): ${prestamo.total_credito:.2f}")
        print(f"    Total Pagado: ${prestamo.total_pagado:.2f}")
        print(f"    Total Pendiente: ${prestamo.total_pendiente:.2f}")
        total_en_circulacion += Decimal(str(prestamo.total_pendiente))
    
    print(f"  Total En Circulación: ${total_en_circulacion:.2f}")
    print()

print("✓ Verificación completada")
