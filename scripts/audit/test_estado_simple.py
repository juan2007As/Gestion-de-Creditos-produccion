"""
Test con login y setup correcto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from mi_app.models import Cliente

print("=" * 80)
print("TEST: Crear cliente y verificar estado inmediatamente")
print("=" * 80)

# Limpiar
Cliente.objects.filter(cedula="88888888").delete()

# TEST 1: Crear directamente sin formulario
print("\n[TEST DIRECTO]")
cliente_directo = Cliente.objects.create(
    nombre="Direct ACTIVO",
    cedula="88888888",
    celular="3008888888",
    email="direct@test.com",
    estado="ACTIVO",
)
print(f"✓ Creado: {cliente_directo.nombre}")
print(f"✓ Estado inmediato: {cliente_directo.estado}")

# Recuperar de BD
cliente_recuperado = Cliente.objects.get(id=cliente_directo.id)
print(f"✓ Estado recuperado BD: {cliente_recuperado.estado}")

# TEST 2: Ahora verificar en el admin
print(f"\n[VERIFICAR EN ADMIN]")
print(f"URL: http://localhost:8000/admin/mi_app/cliente/{cliente_directo.id}/change/")

print("\n" + "=" * 80)
