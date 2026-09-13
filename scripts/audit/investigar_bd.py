import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente

print("=" * 60)
print("INVESTIGACIÓN DE CLIENTE 45")
print("=" * 60)

try:
    cliente_45 = Cliente.objects.get(id=45)
    print(f"\n✓ Cliente encontrado")
    print(f"  ID: {cliente_45.id}")
    print(f"  Nombre: {cliente_45.nombre}")
    print(f"  Estado DB: '{cliente_45.estado}'")
    print(f"  Estado tipo: {type(cliente_45.estado).__name__}")
    print(f"  Estado vacío: {cliente_45.estado == ''}")
    print(f"  Estado None: {cliente_45.estado is None}")
    print(f"  Estado repr: {repr(cliente_45.estado)}")
    
    print(f"\n  get_estado_display(): {cliente_45.get_estado_display()}")
    
except Cliente.DoesNotExist:
    print(f"✗ Cliente 45 no existe en la BD")

print("\n" + "=" * 60)
print("TODOS LOS CLIENTES Y SUS ESTADOS")
print("=" * 60)
clientes = Cliente.objects.all().values('id', 'nombre', 'estado')
for c in clientes:
    print(f"ID {c['id']:2d}: {c['nombre']:30s} -> Estado: '{c['estado']}'")

print("\n" + "=" * 60)
print("CONTEO POR ESTADO")
print("=" * 60)
activos = Cliente.objects.filter(estado='ACTIVO').count()
inactivos = Cliente.objects.filter(estado='INACTIVO').count()
vacio = Cliente.objects.filter(estado='').count()
none = Cliente.objects.filter(estado__isnull=True).count()

print(f"ACTIVO: {activos}")
print(f"INACTIVO: {inactivos}")
print(f"Vacío (''): {vacio}")
print(f"NULL: {none}")
