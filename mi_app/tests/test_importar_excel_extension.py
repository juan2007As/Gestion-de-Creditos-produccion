from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from mi_app import views
from mi_app.models import Rol, UsuarioProfile


class ImportarExcelExtensionTests(TestCase):
    """
    Regresión de auditoría de seguridad: importar_excel no validaba la
    extensión del archivo antes de pasarlo a pd.read_excel() -- confiaba en
    que esa librería fallara sola ante contenido no-Excel, gastando
    CPU/memoria parseando algo que de entrada no podía ser válido. Ahora
    rechaza cualquier archivo que no termine en .xlsx/.xls antes de intentar
    parsearlo.

    Usa RequestFactory + llamado directo a la vista (no self.client) por el
    mismo bug de compatibilidad Django 4.2 + Python 3.14 documentado en
    test_cliente_preseleccionado_xss.py.
    """

    def setUp(self):
        self.factory = RequestFactory()

        rol_admin, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        self.admin = User.objects.create_user(
            username='admin_import_ext_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.admin,
            defaults={'rol': rol_admin, 'activo': True}
        )

    def test_archivo_sin_extension_excel_es_rechazado_sin_parsear(self):
        archivo_invalido = SimpleUploadedFile(
            'clientes.txt',
            b'esto no es un excel, es texto plano',
            content_type='text/plain',
        )
        request = self.factory.post('/importar/excel/', {'archivo': archivo_invalido})
        request.user = self.admin
        response = views.importar_excel(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'debe ser un Excel', response.content)

    def test_archivo_con_extension_xlsx_pasa_el_chequeo_de_extension(self):
        # No hace falta un .xlsx real y válido para este test: solo
        # confirmamos que pasa el chequeo de extensión y llega al parseo
        # real (que fallará con su propio error, no con el de extensión).
        archivo_xlsx_invalido = SimpleUploadedFile(
            'clientes.xlsx',
            b'contenido que no es un xlsx real',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        request = self.factory.post('/importar/excel/', {'archivo': archivo_xlsx_invalido})
        request.user = self.admin
        response = views.importar_excel(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'debe ser un Excel', response.content)
