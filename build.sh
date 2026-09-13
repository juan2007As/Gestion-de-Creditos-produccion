#!/usr/bin/env bash
set -e

echo "========== BUILD: Instalando dependencias =========="
pip install --upgrade pip
pip install -r requirements.txt

echo "========== BUILD: Archivos estaticos =========="
python manage.py collectstatic --noinput

echo "========== BUILD: Migraciones =========="
python manage.py migrate --noinput || echo "AVISO: migrate fallo (posiblemente BD no disponible aun). Render la ejecutara al iniciar."

echo "========== BUILD: Superusuario =========="
python manage.py shell -c "
import secrets
from django.contrib.auth.models import User
username = 'admin'
email = 'admin@creditos.com'
password = secrets.token_urlsafe(16)
user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()
accion = 'creado' if created else 'existente, contraseña reseteada'
print(f'Superusuario {username} {accion}. CONTRASEÑA (solo se muestra esta vez, copiala de este log): {password}')
" || echo "AVISO: No se pudo crear/resetear superusuario. Verifica la conexión a la BD."

echo "========== BUILD: Roles y permisos =========="
python manage.py setup_admin || echo "AVISO: No se pudo configurar roles. Ejecuta 'python manage.py setup_admin' luego."

echo "========== BUILD COMPLETADO =========="
