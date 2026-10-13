from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from mi_app import views
from mi_app.models import Cliente, Rol, Permiso, RolPermiso, UsuarioProfile


class ClientePreseleccionadoXSSTests(TestCase):
    """
    Regresión de auditoría de seguridad: el nombre del cliente preseleccionado
    se interpolaba con json.dumps()+|safe dentro de un literal JS de comillas
    simples (`const clientePreselectionado_json = '{{ ... }}';`). Un nombre
    con una comilla simple rompia el literal y ejecutaba JS arbitrario
    (stored XSS), alcanzable incluso via el modal de "cliente rapido".
    Ahora se sirve via el filtro |json_script, que Django escapa para uso
    seguro dentro de HTML/JS.

    Usa RequestFactory + llamado directo a la vista (en vez de self.client)
    porque en este entorno (Django 4.2 + Python 3.14) el Client de test
    dispara un bug de compatibilidad ajeno a este cambio: al capturar
    response.context para CUALQUIER vista que renderiza un template,
    BaseContext.__copy__ hace `copy(super())`, que revienta con
    "'super' object has no attribute 'dicts'" en esta combinación de
    versiones. RequestFactory no pasa por ese mecanismo de captura.
    """

    def setUp(self):
        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='prestamo.create',
            defaults={'descripcion': 'prestamo.create', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_xss_check',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

    def _get(self, cliente_id):
        request = self.factory.get(f'/prestamos/crear/{cliente_id}/')
        request.user = self.user
        return views.crear_prestamo(request, cliente_id=cliente_id)

    def test_nombre_con_comilla_simple_no_rompe_el_script(self):
        payload = "Hacker'; alert(document.cookie); //"
        cliente = Cliente.objects.create(
            nombre=payload,
            celular='3000000000',
            estado='ACTIVO',
        )

        response = self._get(cliente.id)
        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode('utf-8')

        # El payload nunca debe aparecer interpolado crudo dentro de un
        # literal JS de comillas simples -- eso era exactamente el vector.
        self.assertNotIn("'" + payload, contenido)
        self.assertNotIn("const clientePreselectionado_json = '", contenido)

        # Debe ir dentro de un <script type="application/json"> (json_script),
        # que Django escapa (</, <, >, &) para que no se pueda romper el tag.
        self.assertIn('id="cliente-preseleccionado-data"', contenido)
        self.assertIn('type="application/json"', contenido)

    def test_cliente_preseleccionado_se_renderiza_correctamente(self):
        cliente = Cliente.objects.create(
            nombre='Cliente Normal',
            celular='3001112222',
            estado='ACTIVO',
        )

        response = self._get(cliente.id)
        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode('utf-8')
        self.assertIn('Cliente Normal', contenido)
        self.assertIn('id="cliente-preseleccionado-data"', contenido)
