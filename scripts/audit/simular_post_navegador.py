"""
Simular POST del formulario exacto como lo hace el navegador
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test import Client
from mi_app.models import Cliente

print("=" * 80)
print("TEST: Simular POST del formulario del navegador")
print("=" * 80)

# Eliminar cualquier cliente anterior de prueba
Cliente.objects.filter(cedula="77777777").delete()

# Simular exactamente lo que el navegador envía
client = Client()

datos_post = {
    'nombre': 'Test Browser POST',
    'cedula': '77777777',
    'celular': '3007777777',
    'email': 'test@browser.com',
    'estado': 'ACTIVO',  # ← Esto es lo que el navegador envía
    'notas': 'Test desde browser',
}

print("\n1. Datos POST que envía el navegador:")
for key, value in datos_post.items():
    print(f"   {key}: {value}")

print("\n2. Enviando POST a /clientes/crear/...")
response = client.post('/clientes/crear/', data=datos_post)

print(f"\n3. Response status: {response.status_code}")

# Buscar el cliente creado
cliente = Cliente.objects.filter(cedula="77777777").first()

if cliente:
    print(f"\n4. ✅ Cliente encontrado!")
    print(f"   - Nombre: {cliente.nombre}")
    print(f"   - Cedula: {cliente.cedula}")
    print(f"   - Estado: {cliente.estado}")
    print(f"   - Email: {cliente.email}")
else:
    print(f"\n4. ❌ Cliente NO encontrado en BD")

print("\n" + "=" * 80)
