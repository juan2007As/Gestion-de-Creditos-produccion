"""
Backup y restauracion completos de la base, independientes del motor.

Usa dumpdata/loaddata de Django, asi que funciona igual con SQLite (local)
y con PostgreSQL (Render). El backup se arma en memoria y se entrega al
navegador: nunca se guarda en el disco del servidor, que en Render es
efimero (se borra en cada deploy/reinicio).

La restauracion REEMPLAZA toda la base (decision de la duena, 2026-10-16):
vacia todas las tablas y carga el backup, todo dentro de UNA transaccion.
Si algo falla en cualquier punto, la base queda exactamente como estaba.
"""
import io
import json
import logging
import os
import tempfile

from django.apps import apps
from django.core.management import call_command
from django.db import transaction

logger = logging.getLogger(__name__)

# Tablas que Django regenera solo (contenttypes/permisos al vaciar la base)
# o que no tiene sentido restaurar (sesiones: restaurar cierra todas).
MODELOS_EXCLUIDOS = (
    'contenttypes.contenttype',
    'auth.permission',
    'sessions.session',
)

TAMANO_MAXIMO_BYTES = 50 * 1024 * 1024


class BackupInvalidoError(Exception):
    """El archivo no es un backup restaurable. La base no se toco."""


def _modelos_permitidos():
    return {
        modelo._meta.label_lower
        for modelo in apps.get_models()
        if modelo._meta.label_lower not in MODELOS_EXCLUIDOS
    }


def generar_backup_json():
    """Devuelve el backup completo de la base como bytes JSON (UTF-8)."""
    salida = io.StringIO()
    call_command(
        'dumpdata',
        exclude=list(MODELOS_EXCLUIDOS),
        natural_foreign=True,
        use_base_manager=True,  # incluye filas que un manager custom pudiera ocultar
        stdout=salida,
        verbosity=0,
    )
    return salida.getvalue().encode('utf-8')


def validar_backup_json(contenido):
    """
    Revisa que el contenido sea un backup de este sistema, sin tocar la base.
    Lanza BackupInvalidoError con un mensaje entendible para el usuario.
    """
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise BackupInvalidoError('El archivo es demasiado grande (maximo 50 MB).')
    try:
        datos = json.loads(contenido)
    except (ValueError, UnicodeDecodeError):
        raise BackupInvalidoError('El archivo no es un backup valido (no es JSON).')

    if not isinstance(datos, list) or not datos:
        raise BackupInvalidoError('El archivo esta vacio o no tiene el formato de un backup.')

    permitidos = _modelos_permitidos()
    for obj in datos:
        if not isinstance(obj, dict) or not isinstance(obj.get('fields'), dict):
            raise BackupInvalidoError('El archivo no tiene el formato de un backup de este sistema.')
        modelo = obj.get('model')
        if modelo not in permitidos:
            raise BackupInvalidoError(f'El archivo contiene datos que no son de este sistema ({modelo}).')

    # Sin usuarios, despues de restaurar nadie podria volver a entrar.
    if not any(obj['model'] == 'auth.user' for obj in datos):
        raise BackupInvalidoError('El backup no contiene usuarios: no se puede restaurar.')
    return datos


def restaurar_backup_json(contenido):
    """
    Reemplaza TODA la base por el contenido del backup, en una sola transaccion.
    Si falla, lanza BackupInvalidoError y la base queda sin cambios.
    """
    validar_backup_json(contenido)

    # loaddata necesita un archivo con extension .json. delete=False porque
    # en Windows no se puede reabrir un NamedTemporaryFile abierto.
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp.write(contenido)
        ruta = tmp.name
    try:
        with transaction.atomic():
            call_command('flush', interactive=False, verbosity=0)
            call_command('loaddata', ruta, verbosity=0)
    except Exception as e:
        logger.exception('Fallo la restauracion del backup; se hizo rollback completo.')
        raise BackupInvalidoError(
            'No se pudo restaurar: el backup tiene datos inconsistentes o de otra version '
            'del sistema. No se cambio nada.'
        ) from e
    finally:
        try:
            os.remove(ruta)
        except OSError:
            logger.warning('No se pudo borrar el archivo temporal %s', ruta)
