#!/usr/bin/env bash
set -e

echo "========== BUILD: Instalando dependencias =========="
pip install --upgrade pip
pip install -r requirements.txt

echo "========== BUILD: Migraciones =========="
python manage.py migrate --noinput

echo "========== BUILD: Archivos estaticos =========="
python manage.py collectstatic --noinput

echo "========== BUILD COMPLETADO =========="
