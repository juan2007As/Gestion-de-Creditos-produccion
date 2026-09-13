#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente
from django.db.models import Q

print("Clientes en la BD:")
clientes = Cliente.objects.all()
for cliente in clientes:
    print(f"  - ID: {cliente.id} | Nombre: {cliente.nombre} | Teléfono: {cliente.celular} | Cédula: {cliente.cedula}")

print(f"\nTotal: {clientes.count()} clientes")

# Prueba de búsqueda
print("\n--- PRUEBA DE BÚSQUEDA ---")

query = "juan"
clientes_filtrados = Cliente.objects.filter(
    Q(nombre__icontains=query) | 
    Q(celular__icontains=query) | 
    Q(cedula__icontains=query)
)

print(f"Búsqueda por '{query}': {clientes_filtrados.count()} resultados")
for c in clientes_filtrados:
    print(f"  - {c.nombre} ({c.celular})")
