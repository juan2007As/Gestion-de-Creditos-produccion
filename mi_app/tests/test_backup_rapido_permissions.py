from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from mi_app.models import Rol, UsuarioProfile


class BackupRapidoPermissionsTests(TestCase):
    """
    Regresión de auditoría de seguridad: backup_rapido_generar/descargar/correo
    exponen un volcado completo de la base de datos (todos los clientes,
    prestamos y pagos). Antes de este fix solo tenian @login_required, por lo
    que cualquier usuario autenticado de cualquier rol (incluido OPERARIO)
    podia generar, descargar y auto-enviarse por correo un backup completo.
    Deben exigir rol ADMIN, igual que el sistema de backups "real"
    (backups_list/backup_create/backup_delete/backup_restore).
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

        # NOTA: un post_save signal en User (models.py, crear_user_profile)
        # auto-crea un UsuarioProfile con rol OPERARIO apenas existe ese rol
        # en BD -- como aqui creamos tanto OPERARIO como ADMIN antes de crear
        # los usuarios, ese signal se adelanta y deja al UsuarioProfile ya
        # creado (con OPERARIO) antes de que corra get_or_create() de mas
        # abajo, que al encontrarlo existente ignora 'defaults'. Por eso se
        # usa update_or_create (fuerza el rol correcto sin importar lo que
        # haya hecho el signal).
        self.operario = User.objects.create_user(
            username='operario_backup_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.operario,
            defaults={'rol': rol_operario, 'activo': True}
        )

        self.admin = User.objects.create_user(
            username='admin_backup_test',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.admin,
            defaults={'rol': rol_admin, 'activo': True}
        )

    def test_operario_no_puede_generar_backup(self):
        self.client_obj.login(username='operario_backup_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('backup_rapido_generar'))
        self.assertEqual(response.status_code, 403)

    def test_operario_no_puede_descargar_backup(self):
        self.client_obj.login(username='operario_backup_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.get(reverse('backup_rapido_descargar'))
        self.assertEqual(response.status_code, 403)

    def test_operario_no_puede_enviar_backup_por_correo(self):
        self.client_obj.login(username='operario_backup_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('backup_rapido_correo'))
        self.assertEqual(response.status_code, 403)

    def test_anonimo_no_puede_generar_backup(self):
        response = self.client_obj.post(reverse('backup_rapido_generar'))
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, (302, 403))

    def test_admin_no_recibe_403_al_generar_backup(self):
        self.client_obj.login(username='admin_backup_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('backup_rapido_generar'))
        self.assertNotEqual(response.status_code, 403)

    def test_admin_no_recibe_403_al_enviar_backup_por_correo(self):
        self.client_obj.login(username='admin_backup_test', password='testpass123')  # pragma: allowlist secret
        response = self.client_obj.post(reverse('backup_rapido_correo'))
        self.assertNotEqual(response.status_code, 403)
