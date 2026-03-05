#!/usr/bin/env python
"""
SCRIPT PARA PREPARAR SISTEMA PARA PRODUCCIÓN

Este script configura todo lo necesario para el despliegue en producción:
- Crea archivo .env de producción
- Configura usuario admin con permisos completos
- Verifica configuración de seguridad
- Prepara comandos para PythonAnywhere

Ejecutar con: python prepare_production.py
"""

import os
import sys
import secrets
import string

def generate_secret_key(length=50):
    """Genera una SECRET_KEY segura para Django"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_production_env():
    """Crea archivo .env para producción"""
    print("🔧 Creando configuración de producción...")

    # Usar placeholders que el usuario debe editar
    print("\n📝 Creando archivo .env con placeholders - DEBES EDITAR MANUALMENTE:")
    usuario_pa = "TU_USUARIO_PYTHONANYWHERE"
    db_password = "TU_PASSWORD_BASE_DATOS"
    email_user = "tu-email@gmail.com"
    email_password = "tu-app-password"

    # Generar SECRET_KEY segura
    secret_key = generate_secret_key()

    print("   - Reemplaza TU_USUARIO_PYTHONANYWHERE con tu usuario real")
    print("   - Reemplaza TU_PASSWORD_BASE_DATOS con tu contraseña de MySQL")
    print("   - Configura el email si deseas envío de correos")

    # Crear contenido del .env
    env_content = f"""# Configuración para PythonAnywhere (PRODUCCIÓN)
# Generado automáticamente - NO MODIFICAR MANUALMENTE

ENVIRONMENT=production
DEBUG=False

# Configuración de seguridad
SECRET_KEY={secret_key}
ALLOWED_HOSTS={usuario_pa}.pythonanywhere.com,www.{usuario_pa}.pythonanywhere.com

# Base de datos MySQL (PythonAnywhere)
DB_ENGINE=django.db.backends.mysql
DB_NAME={usuario_pa}$proyecto_john
DB_USER={usuario_pa}
DB_PASSWORD={db_password}
DB_HOST={usuario_pa}.mysql.pythonanywhere-services.com
DB_PORT=3306

# Configuración de email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email_user}
EMAIL_HOST_PASSWORD={email_password}
DEFAULT_FROM_EMAIL=noreply@{usuario_pa}.pythonanywhere.com

# Configuración de la aplicación
MAX_LOAN_AMOUNT=10000000
MIN_LOAN_AMOUNT=100000
DEFAULT_INTEREST_RATE=15.0
MAX_PAYMENT_DAYS=30

# Funcionalidades avanzadas
ENABLE_ADVANCED_REPORTS=True
AUTO_BACKUP_ENABLED=True
BACKUP_RETENTION_DAYS=30
ENABLE_AUDIT_LOG=True
AUDIT_RETENTION_DAYS=365

# Configuración regional
LANGUAGE_CODE=es-co
TIME_ZONE=America/Bogota

# Configuración de seguridad adicional
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
"""

    # Guardar archivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("✅ Archivo .env de producción creado exitosamente")
    return True

def setup_admin_user():
    """Configura usuario admin con todos los permisos"""
    print("\n👤 Configurando usuario administrador...")

    # Configurar Django con settings locales temporalmente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')

    # Forzar configuración local para setup
    os.environ['ENVIRONMENT'] = 'local'
    os.environ['DEBUG'] = 'True'

    import django
    django.setup()

    from django.contrib.auth.models import User
    from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

    # Verificar/crear rol ADMIN
    admin_rol, created = Rol.objects.get_or_create(
        nombre='ADMIN',
        defaults={'descripcion': 'Administrador Total', 'activo': True}
    )

    # Verificar/crear usuario admin
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@gestion-creditos.com',
            'is_staff': True,
            'is_superuser': True
        }
    )

    if created:
        user.set_password('admin123')
        user.save()
        print("✅ Usuario 'admin' creado")

    # Configurar perfil con rol ADMIN
    profile, created = UsuarioProfile.objects.get_or_create(
        usuario=user,
        defaults={'rol': admin_rol, 'activo': True}
    )

    if not created and profile.rol != admin_rol:
        profile.rol = admin_rol
        profile.activo = True
        profile.save()

    # Asignar todos los permisos al rol ADMIN
    permisos_data = [
        ('reporte.view', 'Ver reportes y estadísticas'),
        ('cliente.view', 'Ver clientes'),
        ('cliente.create', 'Crear clientes'),
        ('cliente.edit', 'Editar clientes'),
        ('prestamo.view', 'Ver préstamos'),
        ('prestamo.create', 'Crear préstamos'),
        ('pago.view', 'Ver pagos'),
        ('pago.create', 'Registrar pagos'),
        ('pago.delete', 'Eliminar pagos'),
        ('config.view', 'Ver configuración'),
        ('config.edit', 'Editar configuración'),
        ('backup.manage', 'Gestionar backups'),
    ]

    permisos_asignados = 0
    for codigo, desc in permisos_data:
        permiso, _ = Permiso.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': desc, 'categoria': 'SISTEMA', 'activo': True}
        )

        rol_permiso, created = RolPermiso.objects.get_or_create(
            rol=admin_rol,
            permiso=permiso
        )

        if created:
            permisos_asignados += 1

    print(f"✅ Usuario admin configurado con rol ADMIN y {permisos_asignados} permisos")
    return True

def create_deployment_commands():
    """Crea archivo con comandos para PythonAnywhere"""
    print("\n📋 Generando comandos para PythonAnywhere...")

    commands = '''# ============================================================================
# 🚀 COMANDOS PARA DESPLIEGUE EN PYTHONANYWHERE
# ============================================================================
# Ejecuta estos comandos en orden en tu consola de PythonAnywhere
# ============================================================================

echo "=== PASO 1: Verificar entorno ==="
pwd
which python
python --version

echo "=== PASO 2: Ir al directorio del proyecto ==="
cd ~/Gestion-de-Creditos

echo "=== PASO 3: Activar entorno virtual ==="
source ~/.virtualenvs/mi-env/bin/activate  # Cambia 'mi-env' por tu entorno virtual

echo "=== PASO 4: Verificar que el entorno esté activo ==="
which python
python --version

echo "=== PASO 5: Hacer pull de los últimos cambios ==="
git status
git pull origin main

echo "=== PASO 6: Instalar dependencias nuevas (si las hay) ==="
pip install -r requirements.txt

echo "=== PASO 7: Aplicar migraciones de base de datos ==="
python manage.py migrate

echo "=== PASO 8: Recopilar archivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== PASO 9: Verificar configuración ==="
python manage.py check --deploy

echo "=== PASO 10: Probar que la aplicación funciona ==="
python manage.py shell -c "import django; django.setup(); print('✅ Django configurado correctamente')"

echo "=== PASO 11: Probar servidor de desarrollo (opcional) ==="
# python manage.py runserver 0.0.0.0:8000  # Solo para pruebas, luego detener con Ctrl+C

echo "=== PASO 12: IMPORTANTE - Reiniciar aplicación web ==="
echo "Ve a la pestaña 'Web' en PythonAnywhere y haz clic en 'Reload'"

echo "=== PASO 13: Verificar logs después del restart ==="
tail -f /var/log/pythonanywhere/error.log  # En otra terminal

echo "=== PASO 14: Probar aplicación en producción ==="
# Abre tu sitio web: https://tu-usuario.pythonanywhere.com

# ============================================================================
# 📊 VERIFICACIÓN POST-DESPLIEGUE
# ============================================================================

echo "=== Verificar que funciona el login ==="
curl -I https://tu-usuario.pythonanywhere.com/login/

echo "=== Verificar base de datos ==="
python manage.py shell -c "from mi_app.models import Cliente; print(f'Clientes: {Cliente.objects.count()}')"

echo "=== Verificar archivos estáticos ==="
ls -la staticfiles/

echo "=== Verificar configuración ==="
python manage.py shell -c "from django.conf import settings; print(f'DEBUG: {settings.DEBUG}'); print(f'ENVIRONMENT: {settings.ENVIRONMENT}')"

# ============================================================================
# 🆘 SOLUCIÓN DE PROBLEMAS
# ============================================================================

# Si hay error de SECRET_KEY:
# echo "SECRET_KEY=tu-nueva-secret-key-super-segura" >> .env

# Si hay error de ALLOWED_HOSTS:
# nano .env  # Agregar tu dominio a ALLOWED_HOSTS

# Si hay error de base de datos:
# python manage.py dbshell  # Verificar conexión
# python manage.py migrate  # Re-ejecutar migraciones

# Ver logs de error:
# tail -50 /var/log/pythonanywhere/error.log
# tail -50 /var/log/pythonanywhere/access.log

# Reiniciar servicios si es necesario:
# - Web tab -> Reload
# - Databases -> Reload (si cambiaste algo de BD)
'''

    with open('PYTHONANYWHERE_COMANDOS.txt', 'w', encoding='utf-8') as f:
        f.write(commands)

    print("✅ Archivo 'PYTHONANYWHERE_COMANDOS.txt' creado con todos los comandos")
    return True

def main():
    print("🚀 PREPARANDO SISTEMA PARA PRODUCCIÓN")
    print("=" * 50)

    try:
        # Paso 1: Crear configuración de producción
        if not create_production_env():
            print("❌ Error en configuración de producción")
            return False

        # Paso 2: Configurar usuario admin
        if not setup_admin_user():
            print("❌ Error en configuración de usuario admin")
            return False

        # Paso 3: Crear comandos para PythonAnywhere
        if not create_deployment_commands():
            print("❌ Error creando comandos de despliegue")
            return False

        print("\n" + "=" * 50)
        print("🎉 ¡PREPARACIÓN COMPLETA!")
        print("=" * 50)
        print("\n📁 Archivos generados:")
        print("  ✅ .env (configuración de producción)")
        print("  ✅ PYTHONANYWHERE_COMANDOS.txt (guía de despliegue)")
        print("\n👤 Usuario admin configurado:")
        print("  - Usuario: admin")
        print("  - Contraseña: admin123")
        print("  - Rol: ADMIN (todos los permisos)")
        print("\n🚀 Próximos pasos:")
        print("  1. Hacer commit y push: git add . && git commit -m 'Production ready' && git push")
        print("  2. Ir a PythonAnywhere y seguir los comandos en PYTHONANYWHERE_COMANDOS.txt")
        print("  3. Una vez desplegado, cambiar la contraseña del admin por seguridad")

        return True

    except Exception as e:
        print(f"❌ Error durante la preparación: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)