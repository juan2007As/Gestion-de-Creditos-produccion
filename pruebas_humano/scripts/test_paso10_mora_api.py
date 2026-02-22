"""
TEST 5: Verificar que mora_diaria_api() sincroniza correctamente
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test import RequestFactory
from mi_app.views import mora_diaria_api
from mi_app.models import Cuota
from datetime import date
import json

print("=" * 80)
print("TEST 5: VERIFICAR mora_diaria_api()")
print("=" * 80)

# Antes de llamar a la API
print("\n1️⃣  ANTES de llamar a mora_diaria_api():")
print("-" * 80)

cuota_juan = Cuota.objects.filter(
    prestamo__cliente__nombre='Juan Carlos Pérez',
    numero_cuota=2
).first()

if cuota_juan:
    print(f"Cuota #2 Juan Carlos Pérez:")
    print(f"  Estado: {cuota_juan.estado}")
    print(f"  Mora calculada: ${cuota_juan.calcular_mora_diaria()}")
    print(f"  Días atraso: {(date.today() - cuota_juan.fecha_pago_esperada).days}")

# Llamar a la API
print("\n2️⃣  Llamando mora_diaria_api()...")
from django.contrib.auth.models import User

factory = RequestFactory()
request = factory.get('/api/mora-diaria')

# Crear user ficticio para @login_required
try:
    user = User.objects.first() or User.objects.create_user('test_user', 'test@test.com', 'pass')
except:
    user = User.objects.filter().first()

if user:
    request.user = user
else:
    print("⚠️  No hay usuarios en BD, creando uno temporalmente...")
    user = User.objects.create_user('test_api', 'test@test.com', 'pass123')
    request.user = user

response = mora_diaria_api(request)
data = json.loads(response.content)

print(f"\n📊 RESPUESTA de mora_diaria_api():")
print(f"  Total mora detectada: ${data['total_mora']}")
print(f"  Cuotas vencidas: {data['total_cuotas_vencidas']}")
print(f"  Cuotas con mora: {data['cuotas_con_mora']}")
print(f"  ✅ Estados sincronizados durante API: {data.get('estados_sincronizados', 0)}")

# Mostrar cuotas con mora
if data['cuotas']:
    print(f"\n📋 Cuotas con mora:")
    for cuota_data in data['cuotas']:
        print(f"  • Cliente: {cuota_data['cliente_nombre']}")
        print(f"    Cuota #{cuota_data['numero_cuota']}")
        print(f"    Mora: ${cuota_data['mora']}")
        print(f"    Estado: {cuota_data['estado']}")
        print(f"    Días atraso: {cuota_data['dias_atraso']}")

# Después de llamar a la API
print("\n3️⃣  DESPUÉS de llamar a mora_diaria_api():")
print("-" * 80)

# Recargar cuota desde BD
cuota_juan.refresh_from_db()
print(f"Cuota #2 Juan Carlos Pérez:")
print(f"  Estado: {cuota_juan.estado}")
print(f"  Mora calculada: ${cuota_juan.calcular_mora_diaria()}")

# Verificaciones
print("\n" + "=" * 80)
print("✅ VERIFICACIONES:")
print("=" * 80)

checks = [
    ("Mora detectada > 0", float(data['total_mora']) > 0),
    ("Cuotas vencidas encontradas", data['total_cuotas_vencidas'] > 0),
    ("Cuota #2 Juan Carlos está en mora", any(
        c['numero_cuota'] == 2 and c['cliente_nombre'] == 'Juan Carlos Pérez' 
        for c in data['cuotas']
    )),
    ("Estado VENCIDA presente en respuesta", any(
        c['estado'] == 'VENCIDA' for c in data['cuotas']
    )),
]

all_passed = True
for check_name, result in checks:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status}: {check_name}")
    if not result:
        all_passed = False

if all_passed:
    print("\n🎉 TEST 5 COMPLETADO - TODOS LOS CHECKS PASARON!")
else:
    print("\n⚠️  TEST 5 COMPLETADO - ALGUNOS CHECKS FALLARON")

