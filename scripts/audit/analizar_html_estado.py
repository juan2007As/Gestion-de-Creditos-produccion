"""
Test detallado del HTML del formulario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.forms import ClienteForm

form = ClienteForm()

print("=" * 80)
print("ANÁLISIS DETALLADO DEL CAMPO ESTADO")
print("=" * 80)

print("\n1. Campo estado:")
print(f"   - required: {form.fields['estado'].required}")
print(f"   - initial: {form.fields['estado'].initial}")
print(f"   - choices: {form.fields['estado'].choices}")

print("\n2. HTML del campo:")
html = str(form['estado'])
print(html)

print("\n3. Valor seleccionado por defecto:")
lines = html.split('\n')
for line in lines:
    if 'selected' in line:
        print(f"   {line.strip()}")

print("\n4. Primer option:")
print(f"   {lines[1].strip()}")

print("\n" + "=" * 80)
