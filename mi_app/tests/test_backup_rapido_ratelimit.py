from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from mi_app.models import Rol, UsuarioProfile


class BackupRapidoRatelimitTests(TestCase):
    """
    Regresión + verificación de un hallazgo RETRACTADO (DEUDA-TECNICA.md
    #22bis): se sospechaba que backup_rapido_generar/descargar/correo no
    bloqueaban de verdad por no tener block=True explícito en @ratelimit.
    Verificado con este mismo test (desactivando block=True temporalmente):
    la sospecha era incorrecta -- en django-ratelimit==4.1.0 (el instalado
    en este proyecto), block=True ya es el default, así que estas vistas
    SIEMPRE bloquearon correctamente. Se dejó block=True explícito de todas
    formas (no hace daño, documenta la intención). Este test confirma el
    comportamiento correcto, no un fix de un bug real.

    django_ratelimit.exceptions.Ratelimited (subclase de PermissionDenied)
    se lanza al exceder el límite, y Django la convierte automáticamente en
    un 403 -- sin necesidad de RateLimitMiddleware (que solo está activo en
    PRODUCTION/STAGING) ni de un 403.html propio (no existe, así que no hay
    renderizado de template de por medio -- esto evita el bug de
    compatibilidad Django 4.2 + Python 3.14 documentado en
    test_cliente_preseleccionado_xss.py, por eso usamos el Client normal
    acá en vez de RequestFactory).
    """

    def setUp(self):
        self.client_obj = Client()

        rol_admin, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        self.admin = User.objects.create_user(
            username='admin_backup_ratelimit_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.admin,
            defaults={'rol': rol_admin, 'activo': True}
        )
        self.client_obj.login(
            username='admin_backup_ratelimit_test',
            password='testpass123'  # pragma: allowlist secret
        )

    def test_generar_backup_bloquea_despues_de_5_por_minuto(self):
        for i in range(5):
            response = self.client_obj.post(reverse('backup_rapido_generar'))
            self.assertNotEqual(
                response.status_code, 403,
                f'La request #{i + 1} no debería estar bloqueada todavía'
            )

        response_bloqueada = self.client_obj.post(reverse('backup_rapido_generar'))
        self.assertEqual(response_bloqueada.status_code, 403)

    def test_correo_backup_bloquea_despues_de_3_por_minuto(self):
        for i in range(3):
            response = self.client_obj.post(reverse('backup_rapido_correo'))
            self.assertNotEqual(
                response.status_code, 403,
                f'La request #{i + 1} no debería estar bloqueada todavía'
            )

        response_bloqueada = self.client_obj.post(reverse('backup_rapido_correo'))
        self.assertEqual(response_bloqueada.status_code, 403)

    def test_descargar_backup_bloquea_despues_de_10_por_minuto(self):
        for i in range(10):
            response = self.client_obj.get(reverse('backup_rapido_descargar'))
            self.assertNotEqual(
                response.status_code, 403,
                f'La request #{i + 1} no debería estar bloqueada todavía'
            )

        response_bloqueada = self.client_obj.get(reverse('backup_rapido_descargar'))
        self.assertEqual(response_bloqueada.status_code, 403)
