#!/usr/bin/env python
"""
Script para CORREGIR los permisos incorrectos
Remueve los permisos extras que no debería haber
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Rol, RolPermiso, Permiso

print("\n" + "="*80)
print("🔧 CORRECCIÓN DE PERMISOS INCORRECTOS")
print("="*80)

# Permisos que DEBEN removerse
remociones = {
    'ADMIN': [
        'backup.create',
        'backup.view',
        'configuracion.edit',
        'estadistica.export',
        'excel.import',
        'usuario.create',
        'usuario.edit'
    ],
    'GERENTE': [
        'auditoria.view'
    ],
    'OPERARIO': [
        'cliente.create',
        'pago.create',
        'prestamo.create'
    ]
}

for rol_nombre, permisos_a_remover in remociones.items():
    rol = Rol.objects.get(nombre=rol_nombre)
    print(f"\n🔹 Procesando {rol_nombre}...")
    
    for perm_codigo in permisos_a_remover:
        try:
            permiso = Permiso.objects.get(codigo=perm_codigo)
            rol_permiso = RolPermiso.objects.get(rol=rol, permiso=permiso)
            rol_permiso.delete()
            print(f"   ✅ Removido: {perm_codigo}")
        except Exception as e:
            print(f"   ⚠️  No se pudo remover {perm_codigo}: {str(e)}")

print("\n" + "="*80)
print("✅ CORRECCIÓN COMPLETADA")
print("="*80 + "\n")
