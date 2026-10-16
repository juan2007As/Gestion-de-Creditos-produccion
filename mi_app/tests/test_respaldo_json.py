"""
Backup/restauracion JSON de toda la base (dumpdata/loaddata).

Reemplaza al backup que copiaba db.sqlite3: en Render la base es Postgres
y ese archivo no existe, asi que el backup de la app nunca funciono en
produccion. Estos tests cubren:
- que el backup sale completo y se descarga directo (no se guarda en disco);
- que restaurar deja la base IDENTICA al backup, sin que las senales
  post_save dupliquen montos (total_prestado) ni perfiles de usuario;
- que un archivo invalido o corrupto no cambia nada (transaccion unica);
- que solo ADMIN puede sacar o meter informacion.
"""
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from mi_app.models import (
    AuditoriaBackup, Cliente, Cuota, Pago, Prestamo, Rol, UsuarioProfile,
)
from mi_app.services.backup_service import (
    BackupInvalidoError, generar_backup_json, restaurar_backup_json,
)


def _crear_rol(nombre):
    rol, _ = Rol.objects.get_or_create(
        nombre=nombre, defaults={'descripcion': f'{nombre} tests', 'activo': True}
    )
    return rol


def _crear_usuario(username, rol):
    user = User.objects.create_user(username=username, password='testpass123')  # pragma: allowlist secret
    UsuarioProfile.objects.update_or_create(usuario=user, defaults={'rol': rol, 'activo': True})
    return user


class BackupJsonServiceTests(TestCase):

    def setUp(self):
        self.rol_admin = _crear_rol('ADMIN')
        _crear_rol('OPERARIO')
        self.admin = _crear_usuario('admin_json', self.rol_admin)
        self.cliente = Cliente.objects.create(nombre='Cliente Uno', celular='3001112233', estado='ACTIVO')
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            tipo_pago='QUINCENAL',
            estado='ACTIVO',
        )
        cuota = self.prestamo.cuotas.order_by('numero_cuota').first()
        if cuota is not None:
            Pago.objects.create(cuota=cuota, monto=Decimal('1000'), fecha_pago=date.today(), tipo_pago='PARCIAL')

    def _foto(self):
        """Estado comparable de la base: conteos + montos de dinero del cliente."""
        cliente = Cliente.objects.get(celular='3001112233')
        return {
            'clientes': Cliente.objects.count(),
            'prestamos': Prestamo.objects.count(),
            'cuotas': Cuota.objects.count(),
            'pagos': Pago.objects.count(),
            'usuarios': User.objects.count(),
            'perfiles': UsuarioProfile.objects.count(),
            'roles': Rol.objects.count(),
            'total_prestado': cliente.total_prestado,
            'total_pagado_historico': cliente.total_pagado_historico,
            'etiqueta': cliente.etiqueta_cliente,
        }

    def test_backup_es_json_valido_con_los_datos(self):
        contenido = generar_backup_json()
        datos = json.loads(contenido)
        modelos = {obj['model'] for obj in datos}
        self.assertIn('mi_app.cliente', modelos)
        self.assertIn('mi_app.prestamo', modelos)
        self.assertIn('auth.user', modelos)
        # Sesiones, contenttypes y permisos se regeneran solos: no van en el backup.
        self.assertNotIn('sessions.session', modelos)
        self.assertNotIn('contenttypes.contenttype', modelos)

    def test_restaurar_deja_la_base_identica_sin_duplicar_montos(self):
        antes = self._foto()
        self.assertGreater(antes['total_prestado'], 0)  # la senal real si sumo al crear
        contenido = generar_backup_json()

        # Cambios posteriores al backup que la restauracion debe deshacer.
        Cliente.objects.create(nombre='Cliente Nuevo', celular='3009998877', estado='ACTIVO')
        Prestamo.objects.filter(pk=self.prestamo.pk).delete()

        restaurar_backup_json(contenido)

        self.assertEqual(self._foto(), antes)
        self.assertFalse(Cliente.objects.filter(celular='3009998877').exists())

    def test_archivo_que_no_es_json_no_cambia_nada(self):
        antes = self._foto()
        with self.assertRaises(BackupInvalidoError):
            restaurar_backup_json(b'esto no es json')
        self.assertEqual(self._foto(), antes)

    def test_lista_vacia_se_rechaza(self):
        # Restaurar una lista vacia borraria toda la base: se rechaza.
        antes = self._foto()
        with self.assertRaises(BackupInvalidoError):
            restaurar_backup_json(b'[]')
        self.assertEqual(self._foto(), antes)

    def test_modelo_ajeno_al_sistema_se_rechaza(self):
        antes = self._foto()
        falso = json.dumps([{'model': 'otraapp.cosa', 'pk': 1, 'fields': {}}]).encode()
        with self.assertRaises(BackupInvalidoError):
            restaurar_backup_json(falso)
        self.assertEqual(self._foto(), antes)

    def test_backup_sin_usuarios_se_rechaza(self):
        # Sin usuarios nadie podria volver a entrar despues de restaurar.
        datos = [o for o in json.loads(generar_backup_json()) if o['model'] != 'auth.user']
        antes = self._foto()
        with self.assertRaises(BackupInvalidoError):
            restaurar_backup_json(json.dumps(datos).encode())
        self.assertEqual(self._foto(), antes)

    def test_backup_corrupto_a_mitad_hace_rollback_completo(self):
        datos = json.loads(generar_backup_json())
        # Un prestamo que apunta a un cliente inexistente: falla al cargar,
        # despues de que la base ya fue vaciada. Debe volver todo atras.
        for obj in datos:
            if obj['model'] == 'mi_app.prestamo':
                obj['fields']['cliente'] = 999999
        antes = self._foto()
        with self.assertRaises(BackupInvalidoError):
            restaurar_backup_json(json.dumps(datos).encode())
        self.assertEqual(self._foto(), antes)


class BackupJsonVistasTests(TestCase):

    def setUp(self):
        self.http = Client()
        rol_admin = _crear_rol('ADMIN')
        rol_operario = _crear_rol('OPERARIO')
        self.admin = _crear_usuario('admin_vistas', rol_admin)
        self.operario = _crear_usuario('operario_vistas', rol_operario)
        Cliente.objects.create(nombre='Cliente Vista', celular='3005554433', estado='ACTIVO')

    def tearDown(self):
        # El rate limit cuenta por id de usuario en el cache; sin limpiar, el
        # contador se filtra a otros tests que reciclan el mismo id.
        cache.clear()

    def _login(self, username):
        self.http.login(username=username, password='testpass123')  # pragma: allowlist secret

    # ---- sacar informacion ----

    def test_backup_rapido_descarga_el_archivo_directo(self):
        self._login('admin_vistas')
        response = self.http.post(reverse('backup_rapido_generar'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('.json', response['Content-Disposition'])
        datos = json.loads(response.content)
        self.assertTrue(any(o['model'] == 'mi_app.cliente' for o in datos))
        self.assertTrue(AuditoriaBackup.objects.filter(usuario=self.admin, tipo_backup='DESCARGA').exists())

    def test_backups_crear_descarga_el_archivo_directo(self):
        self._login('admin_vistas')
        response = self.http.post(reverse('backups:crear'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment;', response['Content-Disposition'])
        json.loads(response.content)

    def test_operario_no_puede_sacar_backup(self):
        self._login('operario_vistas')
        self.assertEqual(self.http.post(reverse('backups:crear')).status_code, 403)

    def test_pagina_de_backups_carga(self):
        self._login('admin_vistas')
        response = self.http.get(reverse('backups:list'))
        self.assertEqual(response.status_code, 200)

    # ---- meter informacion ----

    def _archivo(self, contenido):
        return SimpleUploadedFile('backup.json', contenido, content_type='application/json')

    def test_operario_no_puede_restaurar(self):
        self._login('operario_vistas')
        response = self.http.post(reverse('backups:restaurar'), {
            'backup_file': self._archivo(generar_backup_json()), 'confirmacion': 'RESTAURAR',
        })
        self.assertEqual(response.status_code, 403)

    def test_restaurar_sin_escribir_confirmacion_no_hace_nada(self):
        contenido = generar_backup_json()
        Cliente.objects.create(nombre='Despues', celular='3001010101', estado='ACTIVO')
        self._login('admin_vistas')
        response = self.http.post(reverse('backups:restaurar'), {
            'backup_file': self._archivo(contenido), 'confirmacion': 'si',
        })
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Cliente.objects.filter(celular='3001010101').exists())

    def test_restaurar_devuelve_respaldo_previo_y_aplica_backup(self):
        contenido = generar_backup_json()
        Cliente.objects.create(nombre='Despues', celular='3001010101', estado='ACTIVO')
        self._login('admin_vistas')
        response = self.http.post(reverse('backups:restaurar'), {
            'backup_file': self._archivo(contenido), 'confirmacion': 'RESTAURAR',
        })
        self.assertEqual(response.status_code, 200)
        # La respuesta ES el respaldo del estado previo (red de seguridad),
        # que todavia contiene al cliente creado despues del backup.
        self.assertIn('antes_de_restaurar', response['Content-Disposition'])
        previo = json.loads(response.content)
        self.assertTrue(any(
            o['model'] == 'mi_app.cliente' and o['fields']['celular'] == '3001010101' for o in previo
        ))
        # Y la base quedo como el backup.
        self.assertFalse(Cliente.objects.filter(celular='3001010101').exists())
        self.assertTrue(Cliente.objects.filter(celular='3005554433').exists())

    def test_restaurar_archivo_invalido_responde_400_y_no_cambia_nada(self):
        self._login('admin_vistas')
        response = self.http.post(reverse('backups:restaurar'), {
            'backup_file': self._archivo(b'no es json'), 'confirmacion': 'RESTAURAR',
        })
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Cliente.objects.filter(celular='3005554433').exists())
