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
import string
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

username = 'admin'
email = 'admin@creditos.com'
# Solo alfanumerico: nada de guiones/simbolos que se puedan copiar mal a mano.
alfabeto = string.ascii_letters + string.digits
password = ''.join(secrets.choice(alfabeto) for _ in range(20))

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

accion = 'creado' if created else 'existente, contraseña reseteada'
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
