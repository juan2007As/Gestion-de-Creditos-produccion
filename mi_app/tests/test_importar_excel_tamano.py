from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from mi_app import views
from mi_app.models import Rol, UsuarioProfile


class ImportarExcelTamanoTests(TestCase):
    """
    Regresión de auditoría de seguridad: importar_excel (unica vista que
    pasa un archivo subido por el usuario directo a pd.read_excel()) no
    tenia limite de tamano -- un ADMIN (unico rol con acceso) podia subir
    un archivo arbitrariamente grande, cargado entero en memoria por
    pandas/openpyxl, DoS trivial contra el dyno de Render. Ahora rechaza
    archivos de mas de 10 MB antes de intentar parsearlos.

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
            username='admin_import_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.admin,
            defaults={'rol': rol_admin, 'activo': True}
        )

    def test_archivo_mayor_a_10mb_es_rechazado_sin_parsear(self):
        archivo_grande = SimpleUploadedFile(
            'clientes.xlsx',
            b'0' * (11 * 1024 * 1024),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        request = self.factory.post('/importar/excel/', {'archivo': archivo_grande})
        request.user = self.admin
        response = views.importar_excel(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'tama\xc3\xb1o m\xc3\xa1ximo', response.content)
