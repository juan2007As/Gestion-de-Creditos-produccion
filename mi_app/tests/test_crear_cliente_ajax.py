import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from mi_app.models import Cliente, Rol, Permiso, RolPermiso, UsuarioProfile


class CrearClienteAjaxTests(TestCase):
    """
    Modal de "cliente rapido" en los formularios de prestamo: crea un
    Cliente real (mismo ClienteForm/validaciones que crear_cliente) y
    responde JSON en vez de redirigir.
    """

    def setUp(self):
        self.client_obj = Client()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='cliente.create',
            defaults={'descripcion': 'cliente.create', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_cliente_ajax',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.client_obj.login(username='testuser_cliente_ajax', password='testpass123')  # pragma: allowlist secret

    def test_crea_cliente_activo_solo_con_nombre_y_celular(self):
        # El modal siempre manda 'estado' (preseleccionado en ACTIVO) --
        # el campo es requerido a nivel de ClienteForm, no queda en blanco.
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Rapido Modal',
            'celular': '3001234567',
            'estado': 'ACTIVO',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

        cliente = Cliente.objects.get(id=data['cliente']['id'])
        self.assertEqual(cliente.nombre, 'Cliente Rapido Modal')
        self.assertEqual(cliente.celular, '3001234567')
        self.assertEqual(cliente.estado, 'ACTIVO')
        self.assertEqual(cliente.cedula, '')

    def test_acepta_cedula_opcional(self):
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Con Cedula',
            'celular': '3009876543',
            'cedula': '123456789',
            'estado': 'ACTIVO',
        })
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['cliente']['cedula'], '123456789')

    def test_permite_marcar_inactivo(self):
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Inactivo Modal',
            'celular': '3005551234',
            'estado': 'INACTIVO',
        })
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        cliente = Cliente.objects.get(id=data['cliente']['id'])
        self.assertEqual(cliente.estado, 'INACTIVO')

    def test_sin_nombre_devuelve_error_400_sin_crear_cliente(self):
        total_antes = Cliente.objects.count()
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'celular': '3001234567',
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('nombre', data['errors'])
        self.assertEqual(Cliente.objects.count(), total_antes)

    def test_sin_celular_devuelve_error_400(self):
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Sin Celular',
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('celular', data['errors'])

    def test_cedula_duplicada_devuelve_error_400(self):
        Cliente.objects.create(nombre='Existente', celular='3000000000', cedula='999111222')
        response = self.client_obj.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Duplicado',
            'celular': '3001112222',
            'cedula': '999111222',
            'estado': 'ACTIVO',
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('cedula', data['errors'])

    def test_get_no_permitido(self):
        response = self.client_obj.get(reverse('crear_cliente_ajax'))
        self.assertEqual(response.status_code, 405)

    def test_requiere_login(self):
        client_anonimo = Client()
        response = client_anonimo.post(reverse('crear_cliente_ajax'), {
            'nombre': 'Cliente Sin Login',
            'celular': '3001234567',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cliente.objects.filter(nombre='Cliente Sin Login').count(), 0)
