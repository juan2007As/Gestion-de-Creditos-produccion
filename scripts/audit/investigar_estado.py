"""
Test para investigar POR QUÉ el estado queda INACTIVO
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente
from mi_app.forms import ClienteForm

print("=" * 80)
print("TEST: Investigando por qué estado queda INACTIVO")
print("=" * 80)

# TEST 1: Crear directamente en BD (sin formulario)
print("\n[TEST 1] Crear cliente DIRECTAMENTE sin formulario:")
try:
    cliente_directo = Cliente.objects.create(
        nombre="Test Directo ACTIVO",
        cedula="11111111",
        celular="3001111111",
        email="directo@test.com",
        estado="ACTIVO",
        notas="Test directo"
    )
    print(f"✓ Cliente creado: {cliente_directo.nombre}")
    print(f"✓ Estado en BD: {cliente_directo.estado}")
    cliente_directo_recuperado = Cliente.objects.get(id=cliente_directo.id)
    print(f"✓ Estado recuperado: {cliente_directo_recuperado.estado}")
except Exception as e:
    print(f"✗ Error: {e}")

# TEST 2: Crear con formulario (POST simulado)
print("\n[TEST 2] Crear cliente CON FORMULARIO:")
datos_formulario = {
    'nombre': 'Test Formulario ACTIVO',
    'cedula': '22222222',
    'celular': '3002222222',
    'email': 'formulario@test.com',
    'estado': 'ACTIVO',  # Seleccionado en formulario
    'notas': 'Test desde formulario',
}

form = ClienteForm(data=datos_formulario)
print(f"✓ Formulario válido: {form.is_valid()}")
if not form.is_valid():
    print(f"  Errores: {form.errors}")
else:
    cliente_form = form.save()
    print(f"✓ Cliente guardado: {cliente_form.nombre}")
    print(f"✓ Estado guardado: {cliente_form.estado}")
    
    cliente_form_recuperado = Cliente.objects.get(id=cliente_form.id)
    print(f"✓ Estado recuperado: {cliente_form_recuperado.estado}")

# TEST 3: Verificar valor del campo estado en el formulario
print("\n[TEST 3] Verificar widget del formulario:")
form_vacio = ClienteForm()
print(f"✓ Campo estado requerido: {form_vacio.fields['estado'].required}")
print(f"✓ Choices: {form_vacio.fields['estado'].choices}")
print(f"✓ Initial: {form_vacio.fields['estado'].initial}")
print(f"✓ Widget: {form_vacio.fields['estado'].widget}")

# TEST 4: Imprimir el HTML del campo estado
print("\n[TEST 4] HTML del campo estado:")
html_estado = str(form_vacio['estado'])
print(html_estado[:500])

print("\n" + "=" * 80)
print("FIN DE INVESTIGACIÓN")
print("=" * 80)
