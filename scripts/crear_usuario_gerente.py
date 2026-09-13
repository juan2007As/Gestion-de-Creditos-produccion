#!/usr/bin/env python
"""
Script para crear usuario gerente con permisos de admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.contrib.auth.models import User

# Verificar si el usuario ya existe
if User.objects.filter(username='gerente').exists():
    print("❌ El usuario 'gerente' ya existe")
    user = User.objects.get(username='gerente')
    print(f"   - Usuario: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - Activo: {user.is_active}")
    print(f"   - Permisos Admin: {user.is_staff}")
    print(f"   - Superuser: {user.is_superuser}")
else:
    # Crear usuario gerente con permisos de admin
    user = User.objects.create_user(
        username='gerente',
        email='gerente@sistema.com',
        password='gerente123',
        first_name='Gerente',
        last_name='Sistema'
    )
    
    # Darle permisos de admin (igual que admin)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print("✅ Usuario 'gerente' creado exitosamente")
    print(f"   - Usuario: {user.username}")
    print(f"   - Contraseña: gerente123")
    print(f"   - Email: {user.email}")
    print(f"   - Permisos: Admin completo (is_staff=True, is_superuser=True)")

print("\n✅ Lista de usuarios del sistema:")
print("="*70)
for u in User.objects.all():
    print(f"   - {u.username:15} (Superuser: {str(u.is_superuser):5}, Staff: {str(u.is_staff):5})")
print("="*70)
