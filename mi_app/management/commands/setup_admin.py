"""
Comando: python manage.py setup_admin

Crea roles, permisos, y asigna rol ADMIN a TODOS los superusuarios.
Idempotente: no falla si ya existen.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile


PERMISOS = [
    ('reporte.view', 'Ver reportes y estadisticas', 'LECTURA'),
    ('cliente.view', 'Ver clientes', 'LECTURA'),
    ('cliente.create', 'Crear clientes', 'CREACION'),
    ('cliente.edit', 'Editar clientes', 'EDICION'),
    ('cliente.delete', 'Eliminar clientes', 'ELIMINACION'),
    ('prestamo.view', 'Ver prestamos', 'LECTURA'),
    ('prestamo.create', 'Crear prestamos', 'CREACION'),
    ('prestamo.edit', 'Editar prestamos', 'EDICION'),
    ('cuota.view', 'Ver cuotas', 'LECTURA'),
    ('pago.view', 'Ver pagos', 'LECTURA'),
    ('pago.create', 'Registrar pagos', 'CREACION'),
    ('pago.delete', 'Eliminar pagos', 'ELIMINACION'),
    ('config.view', 'Ver configuracion', 'LECTURA'),
    ('config.edit', 'Editar configuracion', 'EDICION'),
    ('backup.manage', 'Gestionar backups', 'SISTEMA'),
    ('auditoria.view', 'Ver auditoria', 'LECTURA'),
    ('importar.excel', 'Importar desde Excel', 'IMPORTACION'),
    ('exportar.datos', 'Exportar datos', 'EXPORTACION'),
    ('lista_negra.view', 'Ver lista negra', 'LECTURA'),
    ('lista_negra.edit', 'Editar lista negra', 'EDICION'),
]


class Command(BaseCommand):
    help = 'Configura roles, permisos y asigna ADMIN a todos los superusuarios'

    def handle(self, *args, **options):
        self.stdout.write('=== Setup de roles y permisos ===')

        # 1. Crear roles
        roles = {}
        for nombre, desc in [
            ('ADMIN', 'Administrador Total'),
            ('GERENTE', 'Gerente de Operaciones'),
            ('OPERARIO', 'Operario de Caja'),
        ]:
            rol, created = Rol.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'activo': True}
            )
            roles[nombre] = rol
            self.stdout.write(f'  Rol {nombre}: {"CREADO" if created else "ya existe"}')

        # 2. Crear permisos y asignar TODOS al ADMIN
        admin_rol = roles['ADMIN']
        for codigo, desc, cat in PERMISOS:
            permiso, created = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': desc, 'categoria': cat, 'activo': True}
            )
            _, linked = RolPermiso.objects.get_or_create(rol=admin_rol, permiso=permiso)
            if created:
                self.stdout.write(f'  Permiso {codigo}: CREADO')

        # 3. Asignar algunos permisos a GERENTE y OPERARIO
        gerente_permisos = [
            'reporte.view', 'cliente.view', 'cliente.create', 'cliente.edit',
            'prestamo.view', 'prestamo.create', 'cuota.view',
            'pago.view', 'pago.create', 'importar.excel', 'exportar.datos',
            'auditoria.view', 'lista_negra.view', 'config.view',
        ]
        for codigo in gerente_permisos:
            permiso = Permiso.objects.filter(codigo=codigo).first()
            if permiso:
                RolPermiso.objects.get_or_create(rol=roles['GERENTE'], permiso=permiso)

        operario_permisos = [
            'reporte.view', 'cliente.view', 'cliente.create',
            'prestamo.view', 'cuota.view', 'pago.view', 'pago.create',
            'importar.excel',
        ]
        for codigo in operario_permisos:
            permiso = Permiso.objects.filter(codigo=codigo).first()
            if permiso:
                RolPermiso.objects.get_or_create(rol=roles['OPERARIO'], permiso=permiso)

        # 4. Asignar ADMIN a TODOS los superusuarios
        superusers = User.objects.filter(is_superuser=True)
        if not superusers.exists():
            self.stdout.write(self.style.WARNING(
                'No hay superusuarios. Crea uno con: python manage.py createsuperuser'
            ))
            return

        for user in superusers:
            profile, created = UsuarioProfile.objects.get_or_create(
                usuario=user,
                defaults={'rol': admin_rol}
            )
            if profile.rol != admin_rol:
                profile.rol = admin_rol
                profile.activo = True
                profile.save()
                self.stdout.write(f'  Usuario {user.username}: ACTUALIZADO a ADMIN')
            else:
                self.stdout.write(f'  Usuario {user.username}: ya es ADMIN')

        self.stdout.write(self.style.SUCCESS(
            f'=== Listo: {superusers.count()} superusuario(s) con rol ADMIN y permisos totales ==='
        ))
