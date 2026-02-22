#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente

print("Clientes en la BD:")
clientes = Cliente.objects.all()
for cliente in clientes:
    print(f"  - ID: {cliente.id} | Nombre: {cliente.nombre} | Teléfono: {cliente.celular} | Cédula: {cliente.cedula}")

print(f"\nTotal: {clientes.count()} clientes")

# Prueba de búsqueda
print("\n--- PRUEBA DE BÚSQUEDA ---")

query = "juan"
clientes_filtrados = Cliente.objects.filter(nombre__icontains=query)

print(f"Búsqueda por nombre '{query}': {clientes_filtrados.count()} resultados")
for c in clientes_filtrados:
    print(f"  - {c.nombre} ({c.celular})")

# Prueba con cédula
print("\nPrueba de búsqueda por cédula 123:")
clientes_cedula = Cliente.objects.filter(cedula__icontains="123")
print(f"  Resultados: {clientes_cedula.count()}")
for c in clientes_cedula:
    print(f"  - {c.nombre} (Cédula: {c.cedula})")
