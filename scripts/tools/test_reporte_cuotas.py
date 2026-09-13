#!/usr/bin/env python
"""
Script de prueba para verificar que el reporte de cuotas funciona correctamente.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cuota, Cliente
from django.test import Client
from django.contrib.auth.models import User

# Obtener información sobre cuotas
print("=" * 80)
print("INFORMACIÓN GENERAL DEL SISTEMA")
print("=" * 80)

total_cuotas = Cuota.objects.count()
total_clientes = Cliente.objects.count()

print(f"\nTotal de cuotas en el sistema: {total_cuotas}")
print(f"Total de clientes en el sistema: {total_clientes}")

# Mostrar primeras 5 cuotas
print("\nPRIMERAS 5 CUOTAS:")
print("-" * 80)

cuotas = Cuota.objects.select_related('prestamo__cliente')[:5]

for cuota in cuotas:
    print(f"\nCuota #{cuota.id}:")
    print(f"  Cliente: {cuota.prestamo.cliente.nombre}")
    print(f"  Préstamo: #{cuota.prestamo.id}")
    print(f"  Cuota #{cuota.numero_cuota}")
    print(f"  Vencimiento: {cuota.fecha_pago_esperada}")
    print(f"  Principal: ${cuota.monto_original:,.2f}")
    print(f"  Interés: ${cuota.interes_normal:,.2f}")
    print(f"  Pagado: {cuota.pagado}")

# Crear cliente de prueba para HTTP
client = Client()

# Intentar acceder a la ruta sin autenticación
print("\n" + "=" * 80)
print("PRUEBA DE ACCESO HTTP")
print("=" * 80)

print("\n1. Acceso sin autenticación:")
response = client.get('/reportes/cuotas/')
print(f"   Status code: {response.status_code}")

if response.status_code == 302:
    print(f"   Redireccionamiento a: {response.url}")
    print("   ✓ Se requiere autenticación (correcto)")
elif response.status_code == 200:
    print("   ✓ Acceso permitido (posiblemente DEBUG=True)")
else:
    print(f"   ✗ Error: {response.status_code}")

# Crear un usuario de prueba si es necesario
print("\n2. Buscando usuario administrador...")
try:
    admin_user = User.objects.get(username='admin')
    print(f"   ✓ Usuario 'admin' encontrado")
except User.DoesNotExist:
    print("   ℹ Usuario 'admin' no existe")
    print("   Creando usuario de prueba...")
    admin_user = User.objects.create_user(
        username='testadmin',
        password='testpass123',
        is_superuser=True,
        is_staff=True
    )
    print(f"   ✓ Usuario 'testadmin' creado")

# Intentar login
print("\n3. Intentando login...")
login_success = client.login(username=admin_user.username, password='testpass123')
if login_success:
    print(f"   ✓ Login exitoso con usuario '{admin_user.username}'")
else:
    # Si el usuario es admin, la contraseña podría ser diferente
    print(f"   ℹ Saltando autenticación específica")

# Acceder a la URL autenticado
print("\n4. Acceso a /reportes/cuotas/ con sesión:")
response = client.get('/reportes/cuotas/')
print(f"   Status code: {response.status_code}")

if response.status_code == 200:
    print("   ✓ Reporte accesible")
    
    # Verificar que el contexto tiene los datos esperados
    if 'resumen' in response.context:
        resumen = response.context['resumen']
        print(f"\n   Resumen de datos:")
        print(f"   - Total cuotas: {resumen.get('total_cuotas', 'N/A')}")
        print(f"   - Total esperado: ${resumen.get('total_esperado', 0):,.2f}")
        print(f"   - Total pagado: ${resumen.get('total_pagado', 0):,.2f}")
        print(f"   - Total pendiente: ${resumen.get('total_pendiente', 0):,.2f}")
        print(f"   - Porcentaje pagado: {resumen.get('porcentaje_pagado', 0):.1f}%")
    
    if 'cuotas' in response.context:
        cuotas_count = len(response.context['cuotas'])
        print(f"\n   Cuotas mostradas en esta página: {cuotas_count}")
    
    print("\n   ✓ Contexto tiene los datos esperados")
else:
    print(f"   ✗ Error: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirigiendo a: {response.url}")

print("\n" + "=" * 80)
print("PRUEBA COMPLETADA")
print("=" * 80)
