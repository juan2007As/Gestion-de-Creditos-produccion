from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from mi_app.models import Rol, UsuarioProfile


class RegisterViewPermissionsTests(TestCase):
    """
    Regresión de auditoría de seguridad: /register/ (auth_views.register_view)
    estaba completamente pública, sin login ni rate-limit. Combinada con la
    señal post_save `crear_user_profile` (models.py), que auto-asigna rol
    OPERARIO a cualquier User nuevo, cualquier persona anónima en internet
    podía crearse una cuenta operativa real en un sistema con dinero y PII
    de clientes. Ahora exige rol ADMIN -- es una herramienta de admin para
    crear usuarios, no un auto-registro.
    """

    def setUp(self):
        self.client_obj = Client()

        rol_operario, _ = Rol.objects.get_or_create(
            nombre='OPERARIO',
            defaults={'descripcion': 'Rol operario para tests', 'activo': True}
        )
        rol_admin, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )

        self.operario = User.objects.create_user(
            username='operario_register_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.operario,
            defaults={'rol': rol_operario, 'activo': True}
        )

        self.admin = User.objects.create_user(
            username='admin_register_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.admin,
            defaults={'rol': rol_admin, 'activo': True}
        )

    def test_anonimo_no_puede_crear_cuenta(self):
        response = self.client_obj.post(reverse('register'), {
            'username': 'intruso',
            'email': 'intruso@evil.com',
            'password': 'hackeame123',  # pragma: allowlist secret
            'password_confirm': 'hackeame123',  # pragma: allowlist secret
        })
        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(User.objects.filter(username='intruso').exists())

    def test_operario_no_puede_crear_cuenta(self):
        self.client_obj.login(username='operario_register_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('register'), {
            'username': 'intruso2',
            'email': 'intruso2@evil.com',
            'password': 'hackeame123',  # pragma: allowlist secret
            'password_confirm': 'hackeame123',  # pragma: allowlist secret
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username='intruso2').exists())

    def test_admin_puede_crear_cuenta(self):
        self.client_obj.login(username='admin_register_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('register'), {
            'username': 'nuevo_operario',
            'email': 'nuevo@empresa.com',
            'password': 'claveSegura123',  # pragma: allowlist secret
            'password_confirm': 'claveSegura123',  # pragma: allowlist secret
        })
        self.assertNotEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(username='nuevo_operario').exists())
