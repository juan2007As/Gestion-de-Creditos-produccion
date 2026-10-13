from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.core.cache import cache
from django_ratelimit.exceptions import Ratelimited

from mi_app import views
from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile


class CrearClienteAjaxRatelimitTests(TestCase):
    """
    Regresión de auditoría de seguridad: crear_cliente_ajax (modal "cliente
    rápido", pensado para enviarse rápido sin recargar la página) no tenía
    @ratelimit -- cualquier usuario con permiso cliente.create podía
    automatizar creación masiva de clientes en bucle. Ahora limita a 10
    requests por minuto por usuario.

    Usa RequestFactory + llamado directo a la vista (no self.client) por el
    mismo bug de compatibilidad Django 4.2 + Python 3.14 documentado en
    test_cliente_preseleccionado_xss.py.
    """

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

        rol_operario, _ = Rol.objects.get_or_create(
            nombre='OPERARIO',
            defaults={'descripcion': 'Rol operario para tests', 'activo': True}
        )
        permiso_crear, _ = Permiso.objects.get_or_create(
            codigo='cliente.create',
            defaults={'descripcion': 'Crear clientes', 'categoria': 'CREACION'}
        )
        RolPermiso.objects.get_or_create(rol=rol_operario, permiso=permiso_crear)

        self.operario = User.objects.create_user(
            username='operario_ratelimit_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.operario,
            defaults={'rol': rol_operario, 'activo': True}
        )

    def _post(self):
        request = self.factory.post('/clientes/crear-ajax/', {})
        request.user = self.operario
        return views.crear_cliente_ajax(request)

    def test_request_11_en_el_mismo_minuto_es_bloqueada(self):
        # RequestFactory + llamado directo a la vista no pasa por el
        # middleware de manejo de excepciones de Django -- en una request
        # HTTP real, django_ratelimit.exceptions.Ratelimited (subclase de
        # PermissionDenied) se convierte automaticamente en un 403; acá
        # verificamos la excepcion cruda que el decorador efectivamente lanza.
        for i in range(10):
            response = self._post()
            self.assertEqual(
                response.status_code, 400,
                f'La request #{i + 1} no debería estar bloqueada todavía (form vacío, 400 esperado)'
            )

        with self.assertRaises(Ratelimited):
            self._post()
