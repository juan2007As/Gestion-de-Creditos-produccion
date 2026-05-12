#!/usr/bin/env bash
set -e

echo "========== BUILD: Instalando dependencias =========="
pip install --upgrade pip
pip install -r requirements.txt

echo "========== BUILD: Archivos estaticos =========="
python manage.py collectstatic --noinput

echo "========== BUILD: Migraciones =========="
python manage.py migrate --noinput || echo "AVISO: migrate fallo (posiblemente BD no disponible aun). Render la ejecutara al iniciar."

echo "========== BUILD COMPLETADO =========="
