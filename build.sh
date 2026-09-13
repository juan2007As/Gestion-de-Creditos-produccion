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
from django.contrib.auth.models import User
username = 'admin'
email = 'admin@creditos.com'
password = 'Admin123!'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superusuario {username} creado')
else:
    print(f'Superusuario {username} ya existe')
" || echo "AVISO: No se pudo crear superusuario. Crea uno cuando la BD este disponible."

echo "========== BUILD: Roles y permisos =========="
python manage.py setup_admin || echo "AVISO: No se pudo configurar roles. Ejecuta 'python manage.py setup_admin' luego."

echo "========== BUILD COMPLETADO =========="
