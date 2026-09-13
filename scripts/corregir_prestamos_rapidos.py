#!/usr/bin/env python
"""
Script para corregir el estado de préstamos rápidos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import PrestamoRapido

print("=" * 80)
print("CORRIGIENDO ESTADOS DE PRÉSTAMOS RÁPIDOS")
print("=" * 80)

# Actualizar todos los préstamos rápidos
for pr in PrestamoRapido.objects.all():
    estado_anterior = pr.estado
    pr.actualizar_estado()  # Esto llama a save()
    
    if estado_anterior != pr.estado:
        print(f"\n✅ Préstamo #{pr.id}:")
        print(f"   {estado_anterior} → {pr.estado}")
        print(f"   Monto pagado: ${float(pr.monto_pagado):.2f}")
        print(f"   Total a pagar: ${float(pr.total_a_pagar):.2f}")
    else:
        print(f"   Préstamo #{pr.id}: {pr.estado} (sin cambios)")

print("\n" + "=" * 80)
print("VERIFICACIÓN FINAL:")
print("=" * 80)

for pr in PrestamoRapido.objects.all():
    print(f"Préstamo #{pr.id}: {pr.estado}")

print("\n✅ CORECCIÓN COMPLETADA")
