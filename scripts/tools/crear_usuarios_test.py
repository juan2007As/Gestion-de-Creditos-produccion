#!/usr/bin/env python
"""
Script para crear usuarios de testing con sus roles asociados.
Ejecutar: python manage.py shell < crear_usuarios_test.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.contrib.auth.models import User
from mi_app.models import Rol, UsuarioProfile, Permiso, RolPermiso

# ===== CREAR ROLES =====
print("📋 Creando roles...")
admin_rol, _ = Rol.objects.get_or_create(nombre='ADMIN', defaults={'activo': True})
gerente_rol, _ = Rol.objects.get_or_create(nombre='GERENTE', defaults={'activo': True})
operario_rol, _ = Rol.objects.get_or_create(nombre='OPERARIO', defaults={'activo': True})
print("✅ Roles creados")

# ===== CREAR PERMISOS (20 totales) =====
print("📋 Creando permisos...")
permisos_data = [
    ('cliente.view', 'Ver clientes'),
    ('cliente.create', 'Crear clientes'),
    ('cliente.edit', 'Editar clientes'),
    ('cliente.delete', 'Eliminar clientes'),
    
    ('prestamo.view', 'Ver préstamos'),
    ('prestamo.create', 'Crear préstamos'),
    ('prestamo.edit', 'Editar préstamos'),
    ('prestamo.delete', 'Eliminar préstamos'),
    ('prestamo_rapido.view', 'Ver préstamos rápidos'),
    ('prestamo_rapido.create', 'Crear préstamos rápidos'),
    
    ('pago.view', 'Ver pagos'),
    ('pago.create', 'Crear pagos'),
    
    ('reporte.view', 'Ver reportes'),
    ('reporte.export', 'Exportar reportes'),
    
    ('cuota.view', 'Ver cuotas'),
    ('estadistica.view', 'Ver estadísticas'),
    
    ('auditoria.view', 'Ver auditoría'),
    ('auditoria.export', 'Exportar auditoría'),
    
    ('backup.perform', 'Realizar backups'),
    ('usuario.manage', 'Gestionar usuarios'),
    ('system.admin', 'Admin del sistema'),
]

permisos_dict = {}
for codigo, descripcion in permisos_data:
    permiso, _ = Permiso.objects.get_or_create(
        codigo=codigo,
        defaults={'descripcion': descripcion, 'activo': True}
    )
    permisos_dict[codigo] = permiso

print(f"✅ {len(permisos_dict)} permisos creados")

# ===== ASIGNAR PERMISOS A ROLES =====
print("📋 Asignando permisos a roles...")

# ADMIN: 20/20 (todos)
admin_permisos = list(permisos_dict.values())
for permiso in admin_permisos:
    RolPermiso.objects.get_or_create(rol=admin_rol, permiso=permiso)

# GERENTE: 15/20 (sin auditoria, backup, system)
gerente_codigos = [
    'cliente.view', 'cliente.create', 'cliente.edit', 'cliente.delete',
    'prestamo.view', 'prestamo.create', 'prestamo.edit', 'prestamo.delete',
    'prestamo_rapido.view', 'prestamo_rapido.create',
    'pago.view', 'pago.create',
    'reporte.view', 'reporte.export',
    'cuota.view', 'estadistica.view'
]
for codigo in gerente_codigos:
    RolPermiso.objects.get_or_create(rol=gerente_rol, permiso=permisos_dict[codigo])

# OPERARIO: 7/20 (solo cliente, prestamo, pago, reporte, cuota, estadistica, prestamo_rapido - view)
operario_codigos = [
    'cliente.view',
    'prestamo.view',
    'pago.view',
    'reporte.view',
    'cuota.view',
    'estadistica.view',
    'prestamo_rapido.view'
]
for codigo in operario_codigos:
    RolPermiso.objects.get_or_create(rol=operario_rol, permiso=permisos_dict[codigo])

print(f"✅ Permisos asignados (ADMIN:20, GERENTE:15, OPERARIO:7)")

# ===== CREAR USUARIOS =====
print("📋 Creando usuarios...")

# Admin
admin_user, created1 = User.objects.get_or_create(
    username='admin_test',
    defaults={
        'first_name': 'Admin',
        'last_name': 'Test',
        'email': 'admin@test.com',
        'is_staff': True,
        'is_superuser': True
    }
)
admin_user.set_password('Admin123!')
admin_user.save()

# Gerente
gerente_user, created2 = User.objects.get_or_create(
    username='gerente_test',
    defaults={
        'first_name': 'Gerente',
        'last_name': 'Test',
        'email': 'gerente@test.com'
    }
)
gerente_user.set_password('Gerente123!')
gerente_user.save()

# Operario
operario_user, created3 = User.objects.get_or_create(
    username='operario_test',
    defaults={
        'first_name': 'Operario',
        'last_name': 'Test',
        'email': 'operario@test.com'
    }
)
operario_user.set_password('Operario123!')
operario_user.save()

print("✅ Usuarios creados")

# ===== ASIGNAR ROLES A USUARIOS =====
print("📋 Asignando roles a usuarios...")

# Signal auto-creates UsuarioProfile, just update the roles
admin_profile = UsuarioProfile.objects.get(usuario=admin_user)
admin_profile.rol = admin_rol
admin_profile.save()

gerente_profile = UsuarioProfile.objects.get(usuario=gerente_user)
gerente_profile.rol = gerente_rol
gerente_profile.save()

operario_profile = UsuarioProfile.objects.get(usuario=operario_user)
operario_profile.rol = operario_rol
operario_profile.save()

print("✅ Roles asignados \n")

# ===== RESUMEN =====
print("=" * 60)
print("✅ USUARIOS DE TESTING CREADOS EXITOSAMENTE")
print("=" * 60)
print("\n📋 ADMIN:")
print("   Usuario: admin_test")
print("   Contraseña: Admin123!")
print("   Rol: ADMIN (20/20 permisos)")
print("\n📋 GERENTE:")
print("   Usuario: gerente_test")
print("   Contraseña: Gerente123!")
print("   Rol: GERENTE (15/20 permisos)")
print("\n📋 OPERARIO:")
print("   Usuario: operario_test")
print("   Contraseña: Operario123!")
print("   Rol: OPERARIO (7/20 permisos)")
print("\n" + "=" * 60)
