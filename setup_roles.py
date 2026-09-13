import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.contrib.auth.models import User
from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

def setup():
    print("Iniciando configuración de roles y permisos...")
    
    # 1. Crear Roles básicos
    admin_rol, _ = Rol.objects.get_or_create(
        nombre='ADMIN', 
        defaults={'descripcion': 'Administrador Total', 'activo': True}
    )
    gerente_rol, _ = Rol.objects.get_or_create(
        nombre='GERENTE', 
        defaults={'descripcion': 'Gerente de Operaciones', 'activo': True}
    )
    operario_rol, _ = Rol.objects.get_or_create(
        nombre='OPERARIO', 
        defaults={'descripcion': 'Operario de Caja', 'activo': True}
    )

    # 2. Crear todos los permisos necesarios
    permisos_data = [
        ('reporte.view', 'Ver reportes y estadísticas', 'LECTURA'),
        ('cliente.view', 'Ver clientes', 'LECTURA'),
        ('cliente.create', 'Crear clientes', 'CREACION'),
        ('cliente.edit', 'Editar clientes', 'EDICION'),
        ('prestamo.view', 'Ver préstamos', 'LECTURA'),
        ('prestamo.create', 'Crear préstamos', 'CREACION'),
        ('pago.view', 'Ver pagos', 'LECTURA'),
        ('pago.create', 'Registrar pagos', 'CREACION'),
        ('pago.delete', 'Eliminar pagos', 'ELIMINACION'),
        ('config.view', 'Ver configuración', 'LECTURA'),
        ('config.edit', 'Editar configuración', 'EDICION'),
        ('backup.manage', 'Gestionar backups', 'SISTEMA'),
    ]

    for codigo, desc, cat in permisos_data:
        permiso, _ = Permiso.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': desc, 'categoria': cat, 'activo': True}
        )
        # Asignar todos al ADMIN por defecto
        RolPermiso.objects.get_or_create(rol=admin_rol, permiso=permiso)
        print(f"  - Permiso configurado: {codigo}")

    # 3. Asignar Rol ADMIN a tu usuario (Admin)
    # Intentamos con 'Admin' (el que mencionaste) y 'JuanAndresC' por si acaso
    for username in ['Admin', 'JuanAndresC']:
        user = User.objects.filter(username=username).first()
        if user:
            profile, _ = UsuarioProfile.objects.get_or_create(usuario=user)
            profile.rol = admin_rol
            profile.activo = True
            profile.save()
            print(f"✅ Usuario '{username}' ahora es ADMIN y tiene todos los permisos.")
            return

    print("❌ No se encontró el usuario 'Admin' ni 'JuanAndresC'.")
    print("Usuarios disponibles en la BD:")
    for u in User.objects.all():
        print(f"  - {u.username}")

if __name__ == '__main__':
    setup()
