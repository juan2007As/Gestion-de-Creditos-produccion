"""
Script para crear roles y permisos iniciales en el sistema.

Crea:
1. 3 roles (ADMIN, GERENTE, OPERARIO)
2. ~15 permisos con diferentes categorías
3. Asigna permisos a cada rol según su nivel

Ejecutar:
    python scripts/crear_roles_iniciales.py
"""

import os
import sys
import django

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Rol, Permiso, RolPermiso


def crear_permisos():
    """Crea todos los permisos del sistema"""
    print("\n✓ Creando permisos...")
    
    permisos_data = {
        # LECTURA
        'LECTURA': [
            ('cliente.view', 'Ver listado y detalles de clientes'),
            ('prestamo.view', 'Ver listado y detalles de prestamos'),
            ('cuota.view', 'Ver listado de cuotas'),
            ('pago.view', 'Ver historial de pagos'),
            ('reporte.view', 'Ver reportes del sistema'),
            ('auditoria.view', 'Ver registro de auditoria'),
        ],
        # CREACIÓN
        'CREACION': [
            ('cliente.create', 'Crear nuevo cliente'),
            ('prestamo.create', 'Crear nuevo prestamo'),
            ('prestamo_rapido.create', 'Crear prestamo rapido'),
            ('pago.create', 'Registrar nuevo pago'),
        ],
        # EDICIÓN
        'EDICION': [
            ('cliente.edit', 'Editar datos de cliente'),
            ('prestamo.edit', 'Editar datos de prestamo'),
            ('configuracion.edit', 'Editar configuracion del sistema'),
        ],
        # IMPORTACIÓN
        'IMPORTACION': [
            ('excel.import', 'Importar datos desde Excel'),
        ],
        # EXPORTACIÓN
        'EXPORTACION': [
            ('reporte.export', 'Exportar reportes a Excel'),
            ('estadistica.export', 'Exportar estadisticas'),
        ],
        # SISTEMA
        'SISTEMA': [
            ('usuario.create', 'Crear nuevos usuarios'),
            ('usuario.edit', 'Editar usuarios'),
            ('backup.create', 'Crear respaldos de BD'),
            ('backup.view', 'Ver respaldos creados'),
        ],
    }
    
    for categoria, permisos in permisos_data.items():
        for codigo, descripcion in permisos:
            permiso, created = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'descripcion': descripcion,
                    'categoria': categoria,
                    'activo': True
                }
            )
            if created:
                print(f"  ✓ Creado: {codigo}")
            else:
                print(f"  - Ya existe: {codigo}")


def crear_roles():
    """Crea los 3 roles del sistema"""
    print("\n✓ Creando roles...")
    
    roles_data = {
        'ADMIN': 'Administrador - Control total del sistema',
        'GERENTE': 'Gerente - Gestion operativa con restricciones',
        'OPERARIO': 'Operario - Operaciones basicas (pagos, creacion)',
    }
    
    for nombre, descripcion in roles_data.items():
        rol, created = Rol.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': descripcion,
                'activo': True
            }
        )
        if created:
            print(f"  ✓ Creado: {nombre}")
        else:
            print(f"  - Ya existe: {nombre}")


def asignar_permisos_admin():
    """Asigna permisos al rol ADMIN"""
    print("\n✓ Asignando permisos a ADMIN...")
    
    rol_admin = Rol.objects.get(nombre='ADMIN')
    permisos = Permiso.objects.filter(activo=True)
    
    count = 0
    for permiso in permisos:
        obj, created = RolPermiso.objects.get_or_create(
            rol=rol_admin,
            permiso=permiso
        )
        if created:
            count += 1
    
    print(f"  ✓ {count} permisos asignados a ADMIN")


def asignar_permisos_gerente():
    """Asigna permisos al rol GERENTE"""
    print("\n✓ Asignando permisos a GERENTE...")
    
    rol_gerente = Rol.objects.get(nombre='GERENTE')
    
    # GERENTE PUEDE: Ver, crear clientes/prestamos, editar clientes, ver reportes
    permisos_gerente = [
        'cliente.view', 'cliente.create', 'cliente.edit',
        'prestamo.view', 'prestamo.create',
        'cuota.view', 'pago.view', 'pago.create',
        'reporte.view', 'reporte.export',
        'auditoria.view',
    ]
    
    count = 0
    for codigo in permisos_gerente:
        try:
            permiso = Permiso.objects.get(codigo=codigo)
            obj, created = RolPermiso.objects.get_or_create(
                rol=rol_gerente,
                permiso=permiso
            )
            if created:
                count += 1
        except Permiso.DoesNotExist:
            print(f"  ⚠ Permiso no encontrado: {codigo}")
    
    print(f"  ✓ {count} permisos asignados a GERENTE")


def asignar_permisos_operario():
    """Asigna permisos al rol OPERARIO"""
    print("\n✓ Asignando permisos a OPERARIO...")
    
    rol_operario = Rol.objects.get(nombre='OPERARIO')
    
    # OPERARIO PUEDE: Ver clientes/prestamos/cuotas, crear clientes/prestamos, registrar pagos
    permisos_operario = [
        'cliente.view', 'cliente.create',
        'prestamo.view', 'prestamo.create',
        'cuota.view', 'pago.view', 'pago.create',
    ]
    
    count = 0
    for codigo in permisos_operario:
        try:
            permiso = Permiso.objects.get(codigo=codigo)
            obj, created = RolPermiso.objects.get_or_create(
                rol=rol_operario,
                permiso=permiso
            )
            if created:
                count += 1
        except Permiso.DoesNotExist:
            print(f"  ⚠ Permiso no encontrado: {codigo}")
    
    print(f"  ✓ {count} permisos asignados a OPERARIO")


if __name__ == '__main__':
    print("=" * 60)
    print("CREAR ROLES Y PERMISOS INICIALES")
    print("=" * 60)
    
    crear_permisos()
    crear_roles()
    asignar_permisos_admin()
    asignar_permisos_gerente()
    asignar_permisos_operario()
    
    print("\n" + "=" * 60)
    print("✅ COMPLETADO - Roles y permisos creados correctamente")
    print("=" * 60)
