#!/usr/bin/env python
"""
Script para debugear préstamos rápidos y sus estados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import PrestamoRapido, Cliente

print("=" * 80)
print("DEBUG: PRÉSTAMOS RÁPIDOS")
print("=" * 80)

# Cliente Gabriela Moreno (ID 33)
try:
    cliente = Cliente.objects.get(id=33)
    print(f"\n✅ Cliente encontrado: {cliente.nombre}")
    print(f"   Total de préstamos rápidos: {cliente.prestamos_rapidos.count()}")
    
    for pr in cliente.prestamos_rapidos.all():
        print(f"\n📋 Préstamo Rápido #{pr.id}")
        print(f"   Monto: ${float(pr.monto):.2f}")
        print(f"   Tasa: {float(pr.interes_porcentaje)}%")
        print(f"   Total a pagar: ${float(pr.total_a_pagar):.2f}")
        print(f"   Monto pagado: ${float(pr.monto_pagado):.2f}")
        print(f"   Estado actual: {pr.estado}")
        print(f"   Saldo pendiente: ${float(pr.saldo_pendiente):.2f}")
        
        # Verificar si debe estar PAGADO
        if float(pr.monto_pagado) >= float(pr.total_a_pagar):
            print(f"   ⚠️  DEBERÍA ESTAR EN ESTADO 'PAGADO' PERO ESTÁ EN '{pr.estado}'")
        
except Cliente.DoesNotExist:
    print("❌ Cliente 33 no encontrado")

print("\n" + "=" * 80)
print("RESUMEN DE TODOS LOS PRÉSTAMOS RÁPIDOS:")
print("=" * 80)

por_estado = {}
for pr in PrestamoRapido.objects.all():
    estado = pr.estado
    if estado not in por_estado:
        por_estado[estado] = []
    por_estado[estado].append(pr)

for estado, prestamos in por_estado.items():
    print(f"\n{estado}: {len(prestamos)} préstamo(s)")
    for pr in prestamos:
        print(f"  - #{pr.id}: ${float(pr.monto):.2f} | Pagado: ${float(pr.monto_pagado):.2f} | Total: ${float(pr.total_a_pagar):.2f}")
