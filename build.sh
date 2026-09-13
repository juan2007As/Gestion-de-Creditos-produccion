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
# Render (free tier) reconstruye la app entera cada vez que el servicio
# "despierta" de estar inactivo, no solo la reinicia — así que este paso
# corre mucho más seguido de lo que parece. Por eso la contraseña NO se
# genera al azar en cada build (cambiaría todo el tiempo, imposible de
# seguir): sale de ADMIN_PASSWORD si está seteada en el dashboard de
# Render, y solo si no está, se genera una al azar de emergencia.
python manage.py shell -c "
import os
import secrets
import string
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

username = 'admin'
email = 'admin@creditos.com'
password = os.environ.get('ADMIN_PASSWORD')
if not password:
    alfabeto = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alfabeto) for _ in range(20))
    print('AVISO: ADMIN_PASSWORD no está seteada en Render — usando una generada al azar (va a cambiar en cada build). Configurala en Environment para que quede fija.')

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

accion = 'creado' if created else 'existente, contraseña sincronizada'
print(f'Superusuario {username} {accion}. CONTRASEÑA (solo se muestra esta vez, copiala de este log): {password}')

# Verificacion en el momento: autentica de la misma forma que la vista de login real.
verificado = authenticate(username=username, password=password)
if verificado is not None:
    print(f'VERIFICACION OK: authenticate() confirma que {username}/{password} funciona ahora mismo.')
else:
    print('VERIFICACION FALLO: authenticate() NO reconoce el usuario recien creado/reseteado. Revisar AUTHENTICATION_BACKENDS o el hasher de contrasenas.')
" || echo "AVISO: No se pudo crear/resetear superusuario. Verifica la conexión a la BD."

echo "========== BUILD: Roles y permisos =========="
python manage.py setup_admin || echo "AVISO: No se pudo configurar roles. Ejecuta 'python manage.py setup_admin' luego."

echo "========== BUILD COMPLETADO =========="
