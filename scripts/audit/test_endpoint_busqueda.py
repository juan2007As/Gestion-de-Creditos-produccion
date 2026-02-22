#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test import Client as DjangoClient
import json

print("=== PROBANDO ENDPOINT /api/buscar-cliente/ ===\n")

client = DjangoClient()

# Prueba 1: Búsqueda por nombre
print("1. Búsqueda por nombre 'juan':")
response = client.get('/api/buscar-cliente/?q=juan')
data = response.json()
print(f"   Estatus: {response.status_code}")
print(f"   Resultados: {len(data['resultados'])}")
for r in data['resultados']:
    print(f"     - {r['display']}")

# Prueba 2: Búsqueda por nombre 'lina'
print("\n2. Búsqueda por nombre 'lina':")
response = client.get('/api/buscar-cliente/?q=lina')
data = response.json()
print(f"   Estatus: {response.status_code}")
print(f"   Resultados: {len(data['resultados'])}")
for r in data['resultados']:
    print(f"     - {r['display']}")

# Prueba 3: Búsqueda por cédula '123'
print("\n3. Búsqueda por cédula '123':")
response = client.get('/api/buscar-cliente/?q=123')
data = response.json()
print(f"   Estatus: {response.status_code}")
print(f"   Resultados: {len(data['resultados'])}")
for r in data['resultados']:
    print(f"     - {r['display']}")

# Prueba 4: Búsqueda por teléfono
print("\n4. Búsqueda por teléfono '3017653545':")
response = client.get('/api/buscar-cliente/?q=3017653545')
data = response.json()
print(f"   Estatus: {response.status_code}")
print(f"   Resultados: {len(data['resultados'])}")
for r in data['resultados']:
    print(f"     - {r['display']}")

# Prueba 5: Búsqueda vacía
print("\n5. Búsqueda vacía:")
response = client.get('/api/buscar-cliente/?q=')
data = response.json()
print(f"   Estatus: {response.status_code}")
print(f"   Resultados: {len(data['resultados'])}")

print("\n✓ Todas las pruebas completadas")
