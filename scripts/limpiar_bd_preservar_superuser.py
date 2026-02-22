import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, PrestamoRapido, PagoPrestamoRapido
from django.contrib.auth.models import User

print("=" * 60)
print("LIMPIEZA DE BASE DE DATOS (Preservando Superuser)")
print("=" * 60)

# Contar antes
print("\n📊 ESTADO ANTES:")
print(f"  Clientes: {Cliente.objects.count()}")
print(f"  Préstamos: {Prestamo.objects.count()}")
print(f"  Cuotas: {Cuota.objects.count()}")
print(f"  Pagos: {Pago.objects.count()}")
print(f"  Préstamos Rápidos: {PrestamoRapido.objects.count()}")
print(f"  Pagos Rápidos: {PagoPrestamoRapido.objects.count()}")
print(f"  Usuarios: {User.objects.count()}")

# Preservar superuser
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    print(f"\n✓ Superuser a preservar: {superuser.username}")

# Eliminar datos
print("\n🗑️  Eliminando datos...")

# Eliminar en orden de dependencias
PagoPrestamoRapido.objects.all().delete()
print("  ✓ Pagos Rápidos eliminados")

Pago.objects.all().delete()
print("  ✓ Pagos eliminados")

PrestamoRapido.objects.all().delete()
print("  ✓ Préstamos Rápidos eliminados")

Cuota.objects.all().delete()
print("  ✓ Cuotas eliminadas")

Prestamo.objects.all().delete()
print("  ✓ Préstamos eliminados")

Cliente.objects.all().delete()
print("  ✓ Clientes eliminados")

# Eliminar usuarios excepto superuser
if superuser:
    User.objects.exclude(id=superuser.id).delete()
else:
    User.objects.all().delete()
print("  ✓ Usuarios (excepto superuser) eliminados")

print("\n📊 ESTADO DESPUÉS:")
print(f"  Clientes: {Cliente.objects.count()}")
print(f"  Préstamos: {Prestamo.objects.count()}")
print(f"  Cuotas: {Cuota.objects.count()}")
print(f"  Pagos: {Pago.objects.count()}")
print(f"  Préstamos Rápidos: {PrestamoRapido.objects.count()}")
print(f"  Pagos Rápidos: {PagoPrestamoRapido.objects.count()}")
print(f"  Usuarios: {User.objects.count()}")

if superuser:
    print(f"\n✓ Superuser preservado: {superuser.username}")

print("\n✅ LIMPIEZA COMPLETADA\n")
