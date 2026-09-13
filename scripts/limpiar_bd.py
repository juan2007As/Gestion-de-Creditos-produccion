#!/usr/bin/env python
"""
Script para limpiar la BD manteniendo solo el superusuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, PrestamoRapido, PagoPrestamoRapido

print("=" * 60)
print("LIMPIEZA DE BASE DE DATOS")
print("=" * 60)
print("\n📊 ANTES DE LIMPIAR:")
print(f"   Clientes: {Cliente.objects.count()}")
print(f"   Préstamos: {Prestamo.objects.count()}")
print(f"   Cuotas: {Cuota.objects.count()}")
print(f"   Pagos: {Pago.objects.count()}")
print(f"   Préstamos Rápidos: {PrestamoRapido.objects.count()}")
print(f"   Pagos PR: {PagoPrestamoRapido.objects.count()}")

# Limpiar en orden (respetando FK)
print("\n🗑️  ELIMINANDO...")

# 1. Eliminar pagos de préstamos rápidos
count = PagoPrestamoRapido.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} pagos de PR")

# 2. Eliminar préstamos rápidos
count = PrestamoRapido.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} préstamos rápidos")

# 3. Eliminar pagos
count = Pago.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} pagos")

# 4. Eliminar cuotas
count = Cuota.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} cuotas")

# 5. Eliminar préstamos
count = Prestamo.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} préstamos")

# 6. Eliminar clientes
count = Cliente.objects.all().delete()[0]
print(f"   ✓ Eliminados {count} clientes")

print("\n📊 DESPUÉS DE LIMPIAR:")
print(f"   Clientes: {Cliente.objects.count()}")
print(f"   Préstamos: {Prestamo.objects.count()}")
print(f"   Cuotas: {Cuota.objects.count()}")
print(f"   Pagos: {Pago.objects.count()}")
print(f"   Préstamos Rápidos: {PrestamoRapido.objects.count()}")
print(f"   Pagos PR: {PagoPrestamoRapido.objects.count()}")

print("\n✅ ¡BD LIMPIADA EXITOSAMENTE!")
print("   Superusuario MANTENIDO ✓")
print("=" * 60)
