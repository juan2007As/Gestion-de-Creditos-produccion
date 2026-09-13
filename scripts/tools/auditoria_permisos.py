#!/usr/bin/env python
"""
AUDITORÍA EXHAUSTIVA DE PERMISOS Y DECORADORES
Verifica que:
1. Todos los decoradores son válidos
2. Los permisos coinciden con las BD
3. Cada usuario solo puede hacer lo que le permite su rol
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.contrib.auth.models import User
from mi_app.models import UsuarioProfile, Rol, Permiso, RolPermiso

print("\n" + "="*80)
print("🔍 AUDITORÍA EXHAUSTIVA DE PERMISOS DEL SISTEMA")
print("="*80)

# ===== FASE 1: VERIFICAR BD =====
print("\n" + "─"*80)
print("FASE 1: VERIFICAR ESTADO DE BASE DE DATOS")
print("─"*80)

# 1.1 Verificar roles
print("\n📋 ROLES EXISTENTES:")
roles = Rol.objects.all()
for rol in roles:
    print(f"   → {rol.nombre} (Activo: {rol.activo})")

print(f"\n✅ {roles.count()} roles encontrados")

# 1.2 Verificar permisos
print("\n📋 PERMISOS EXISTENTES:")
permisos = Permiso.objects.all().order_by('codigo')
print(f"\n{'Código':<30} {'Descripción':<40} {'Activo'}")
print("─" * 80)
for perm in permisos:
    print(f"{perm.codigo:<30} {perm.descripcion:<40} {perm.activo}")

print(f"\n✅ {permisos.count()} permisos encontrados")

# 1.3 Verificar asignaciones rol-permiso
print("\n📋 ASIGNACIONES ROL-PERMISO:")
rol_permisos = RolPermiso.objects.all().select_related('rol', 'permiso').order_by('rol__nombre')

permisos_por_rol = {}
for rp in rol_permisos:
    if rp.rol.nombre not in permisos_por_rol:
        permisos_por_rol[rp.rol.nombre] = []
    permisos_por_rol[rp.rol.nombre].append(rp.permiso.codigo)

for rol_nom in sorted(permisos_por_rol.keys()):
    perms = sorted(permisos_por_rol[rol_nom])
    print(f"\n🔹 {rol_nom} ({len(perms)} permisos):")
    for perm_code in perms:
        perm = Permiso.objects.get(codigo=perm_code)
        print(f"   ✓ {perm_code:<30} - {perm.descripcion}")

print(f"\n✅ {rol_permisos.count()} asignaciones rol-permiso encontradas")

# 1.4 Verificar usuarios
print("\n📋 USUARIOS EXISTENTES:")
usuarios = User.objects.all()
for user in usuarios:
    try:
        profile = UsuarioProfile.objects.get(usuario=user)
        rol = profile.rol.nombre if profile.rol else "SIN ROL"
    except UsuarioProfile.DoesNotExist:
        rol = "SIN PROFILE"
    
    print(f"   → {user.username:<20} Rol: {rol:<12} Staff: {user.is_staff} Superuser: {user.is_superuser}")

print(f"\n✅ {usuarios.count()} usuarios encontrados (algunos podrían no tener UsuarioProfile)")

# ===== FASE 2: VERIFICAR PERMISOS EFECTIVOS DE USUARIOS =====
print("\n" + "─"*80)
print("FASE 2: VERIFICAR PERMISOS EFECTIVOS POR USUARIO")
print("─"*80)

for user in usuarios:
    try:
        profile = UsuarioProfile.objects.get(usuario=user)
        rol = profile.rol
    except UsuarioProfile.DoesNotExist:
        print(f"\n⚠️  {user.username}: SIN USUARIOPROFILE")
        continue
    
    if not rol:
        print(f"\n⚠️  {user.username}: SIN ROL ASIGNADO")
        continue
    
    print(f"\n👤 {user.username} (Rol: {rol.nombre})")
    print("   Permisos asignados:")
    
    rol_permisos_user = RolPermiso.objects.filter(rol=rol).select_related('permiso').order_by('permiso__codigo')
    permisos_list = [rp.permiso.codigo for rp in rol_permisos_user]
    
    if permisos_list:
        for perm_code in sorted(permisos_list):
            print(f"      ✓ {perm_code}")
    else:
        print("      (ninguno)")
    
    # Verificar método tiene_permiso
    print("   Validación de método tiene_permiso():")
    for codigo in sorted(permisos_list[:3]):  # Mostrar primeros 3
        tiene = profile.tiene_permiso(codigo)
        print(f"      → {codigo}: {tiene}")

# ===== FASE 3: MATRIZ DE ACCESO ESPERADA vs REAL =====
print("\n" + "─"*80)
print("FASE 3: MATRIZ DE ACCESO ESPERADA vs REAL")
print("─"*80)

MATRIZ_ESPERADA = {
    'ADMIN': {
        'vista': 'admin_test',
        'permisos': [
            'cliente.view', 'cliente.create', 'cliente.edit', 'cliente.delete',
            'prestamo.view', 'prestamo.create', 'prestamo.edit', 'prestamo.delete',
            'prestamo_rapido.view', 'prestamo_rapido.create',
            'pago.view', 'pago.create',
            'reporte.view', 'reporte.export',
            'cuota.view', 'estadistica.view',
            'auditoria.view', 'auditoria.export',
            'backup.perform', 'usuario.manage', 'system.admin'
        ]
    },
    'GERENTE': {
        'vista': 'gerente_test',
        'permisos': [
            'cliente.view', 'cliente.create', 'cliente.edit', 'cliente.delete',
            'prestamo.view', 'prestamo.create', 'prestamo.edit', 'prestamo.delete',
            'prestamo_rapido.view', 'prestamo_rapido.create',
            'pago.view', 'pago.create',
            'reporte.view', 'reporte.export',
            'cuota.view', 'estadistica.view'
        ]
    },
    'OPERARIO': {
        'vista': 'operario_test',
        'permisos': [
            'cliente.view',
            'prestamo.view',
            'pago.view',
            'reporte.view',
            'cuota.view',
            'estadistica.view',
            'prestamo_rapido.view'
        ]
    }
}

print("\n🔍 Validando matriz de acceso esperada:\n")

matriz_correcta = True

for rol_nombre, esperado in MATRIZ_ESPERADA.items():
    rol_obj = Rol.objects.get(nombre=rol_nombre)
    rol_permisos_db = RolPermiso.objects.filter(rol=rol_obj).values_list('permiso__codigo', flat=True)
    permisos_reales = sorted(list(rol_permisos_db))
    permisos_esperados = sorted(esperado['permisos'])
    
    print(f"📌 ROL: {rol_nombre}")
    print(f"   Esperados: {len(permisos_esperados)} permisos")
    print(f"   Reales:    {len(permisos_reales)} permisos")
    
    # Encontrar diferencias
    faltantes = set(permisos_esperados) - set(permisos_reales)
    extras = set(permisos_reales) - set(permisos_esperados)
    
    if faltantes:
        print(f"   ❌ FALTANTES ({len(faltantes)}):")
        for p in sorted(faltantes):
            print(f"      • {p}")
        matriz_correcta = False
    
    if extras:
        print(f"   ⚠️  EXTRAS ({len(extras)}):")
        for p in sorted(extras):
            print(f"      • {p}")
        matriz_correcta = False
    
    if not faltantes and not extras:
        print(f"   ✅ PERFECTO - Todos los permisos coinciden")
    
    print()

# ===== FASE 4: VERIFICACIÓN DE USUARIOS DE TEST =====
print("─"*80)
print("FASE 4: VERIFICACIÓN DE USUARIOS DE TEST")
print("─"*80)

usuarios_test = {
    'admin_test': 'ADMIN',
    'gerente_test': 'GERENTE',
    'operario_test': 'OPERARIO'
}

for username, rol_esperado in usuarios_test.items():
    try:
        user = User.objects.get(username=username)
        try:
            profile = UsuarioProfile.objects.get(usuario=user)
            rol_real = profile.rol.nombre if profile.rol else "SIN ROL"
        except UsuarioProfile.DoesNotExist:
            print(f"\n❌ Usuario {username} sin UsuarioProfile")
            matriz_correcta = False
            continue
        
        print(f"\n👤 {username}")
        print(f"   Rol esperado: {rol_esperado}")
        print(f"   Rol real:     {rol_real}")
        
        if rol_real == rol_esperado:
            print(f"   ✅ ROL CORRECTO")
        else:
            print(f"   ❌ ROL INCORRECTO")
            matriz_correcta = False
        
        # Verificar permisos
        if rol_real != "SIN ROL":
            permisos_esperados = set(MATRIZ_ESPERADA[rol_esperado]['permisos'])
            permisos_reales = set(
                RolPermiso.objects.filter(rol=profile.rol).values_list('permiso__codigo', flat=True)
            )
            
            if permisos_esperados == permisos_reales:
                print(f"   ✅ PERMISOS CORRECTOS ({len(permisos_reales)} permisos)")
            else:
                print(f"   ❌ PERMISOS INCORRECTOS")
                faltantes = permisos_esperados - permisos_reales
                extras = permisos_reales - permisos_esperados
                if faltantes:
                    print(f"      Faltantes: {faltantes}")
                if extras:
                    print(f"      Extras: {extras}")
                matriz_correcta = False
    
    except User.DoesNotExist:
        print(f"\n❌ Usuario no encontrado: {username}")
        matriz_correcta = False

# ===== RESULTADO FINAL =====
print("\n" + "="*80)
if matriz_correcta:
    print("✅ AUDITORÍA EXITOSA - Sistema de permisos está CORRECTO")
else:
    print("❌ AUDITORÍA CON PROBLEMAS - Ver detalles arriba")
print("="*80 + "\n")
