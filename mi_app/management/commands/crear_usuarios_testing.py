"""
Management Command: Crear Usuarios de Testing
Crea 3 usuarios con roles ADMIN, GERENTE, OPERARIO para testing del sistema.
Uso: python manage.py crear_usuarios_testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mi_app.models import Rol, UsuarioProfile


class Command(BaseCommand):
    """
    Command para crear usuarios de testing automáticamente.
    
    Crea:
    - admin_user (ADMIN) - admin@test.local / Admin123!
    - gerente_user (GERENTE) - gerente@test.local / Gerente123!
    - operario_user (OPERARIO) - operario@test.local / Operario123!
    """
    
    help = 'Crea 3 usuarios de testing con roles ADMIN, GERENTE, OPERARIO'
    
    # Definir usuarios a crear
    USUARIOS_TESTING = [
        {
            'username': 'admin_user',
            'email': 'admin@test.local',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'Testing',
            'is_staff': True,
            'is_superuser': False,
            'rol': 'ADMIN',
        },
        {
            'username': 'gerente_user',
            'email': 'gerente@test.local',
            'password': 'Gerente123!',
            'first_name': 'Gerente',
            'last_name': 'Testing',
            'is_staff': False,
            'is_superuser': False,
            'rol': 'GERENTE',
        },
        {
            'username': 'operario_user',
            'email': 'operario@test.local',
            'password': 'Operario123!',
            'first_name': 'Operario',
            'last_name': 'Testing',
            'is_staff': False,
            'is_superuser': False,
            'rol': 'OPERARIO',
        },
    ]
    
    def add_arguments(self, parser):
        """Argumentos opcionales del command"""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina usuarios existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--show-passwords',
            action='store_true',
            help='Muestra las contraseñas de los usuarios creados',
        )
    
    def handle(self, *args, **options):
        """Ejecuta la creación de usuarios"""
        reset = options.get('reset', False)
        show_passwords = options.get('show_passwords', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 CREANDO USUARIOS DE TESTING'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        
        # Validar que los roles existan
        if not self._validar_roles():
            return
        
        # Reset si se solicita
        if reset:
            self._reset_usuarios()
        
        # Crear usuarios
        resultados = {
            'exitosos': [],
            'existentes': [],
            'errores': [],
        }
        
        for usuario_data in self.USUARIOS_TESTING:
            rol_nombre = usuario_data.pop('rol')
            resultado = self._crear_usuario(usuario_data, rol_nombre)
            
            if resultado['status'] == 'created':
                resultados['exitosos'].append(resultado)
            elif resultado['status'] == 'existing':
                resultados['existentes'].append(resultado)
            else:
                resultados['errores'].append(resultado)
        
        # Mostrar resultados
        self._mostrar_resultados(resultados, show_passwords)
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ PROCESO COMPLETADO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
    
    def _validar_roles(self):
        """Valida que todos los roles requeridos existan"""
        self.stdout.write('📋 Validando roles...')
        roles_requeridos = {'ADMIN', 'GERENTE', 'OPERARIO'}
        roles_existentes = set(Rol.objects.values_list('nombre', flat=True))
        
        if not roles_requeridos.issubset(roles_existentes):
            faltantes = roles_requeridos - roles_existentes
            self.stdout.write(
                self.style.ERROR(
                    f'❌ ERROR: Roles faltantes en la BD: {", ".join(faltantes)}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '   Ejecuta: python manage.py crear_roles_iniciales'
                )
            )
            return False
        
        self.stdout.write(self.style.SUCCESS('✅ Todos los roles existen'))
        self.stdout.write('')
        return True
    
    def _reset_usuarios(self):
        """Elimina usuarios de testing existentes"""
        self.stdout.write('🗑️  Eliminando usuarios existentes...')
        usernames = [u['username'] for u in self.USUARIOS_TESTING]
        deleted, _ = User.objects.filter(username__in=usernames).delete()
        self.stdout.write(self.style.WARNING(f'   Eliminados: {deleted} usuarios'))
        self.stdout.write('')
    
    def _crear_usuario(self, usuario_data, rol_nombre):
        """
        Crea un usuario y le asigna un rol
        
        Returns:
            dict con status, username, email, rol, password (si show_passwords=True)
        """
        username = usuario_data['username']
        email = usuario_data['email']
        password = usuario_data['password']
        
        try:
            # Obtener o crear usuario
            usuario, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': usuario_data.get('first_name', ''),
                    'last_name': usuario_data.get('last_name', ''),
                    'is_staff': usuario_data.get('is_staff', False),
                    'is_superuser': usuario_data.get('is_superuser', False),
                }
            )
            
            # Actualizar contraseña (siempre, para asegurar que es correcta)
            usuario.set_password(password)
            usuario.save()
            
            # Obtener rol
            rol = Rol.objects.get(nombre=rol_nombre)
            
            # Actualizar o crear UsuarioProfile
            profile, _ = UsuarioProfile.objects.get_or_create(usuario=usuario)
            profile.rol = rol
            profile.save()
            
            if created:
                return {
                    'status': 'created',
                    'username': username,
                    'email': email,
                    'rol': rol_nombre,
                    'password': password,
                }
            else:
                return {
                    'status': 'existing',
                    'username': username,
                    'email': email,
                    'rol': rol_nombre,
                    'password': password,
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'username': username,
                'error': str(e),
            }
    
    def _mostrar_resultados(self, resultados, show_passwords):
        """Muestra un resumen de los resultados"""
        # Usuarios creados
        if resultados['exitosos']:
            self.stdout.write(self.style.SUCCESS('✅ USUARIOS CREADOS:'))
            for u in resultados['exitosos']:
                self.stdout.write(
                    f'   • {u["username"]} ({u["rol"]}) - {u["email"]}'
                )
                if show_passwords:
                    self.stdout.write(f'      Contraseña: {u["password"]}')
            self.stdout.write('')
        
        # Usuarios que ya existían (actualizados)
        if resultados['existentes']:
            self.stdout.write(self.style.WARNING('⚠️  USUARIOS EXISTENTES (ACTUALIZADOS):'))
            for u in resultados['existentes']:
                self.stdout.write(
                    f'   • {u["username"]} ({u["rol"]}) - {u["email"]}'
                )
                if show_passwords:
                    self.stdout.write(f'      Contraseña: {u["password"]}')
            self.stdout.write('')
        
        # Errores
        if resultados['errores']:
            self.stdout.write(self.style.ERROR('❌ ERRORES:'))
            for u in resultados['errores']:
                self.stdout.write(f'   • {u["username"]}: {u["error"]}')
            self.stdout.write('')
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN:'))
        total_exitosos = len(resultados['exitosos'])
        total_existentes = len(resultados['existentes'])
        total_errores = len(resultados['errores'])
        
        self.stdout.write(f'   Creados: {total_exitosos}')
        self.stdout.write(f'   Actualizados: {total_existentes}')
        self.stdout.write(f'   Errores: {total_errores}')
        self.stdout.write('')
        
        # Instrucciones para login
        if total_exitosos > 0 or total_existentes > 0:
            self.stdout.write(self.style.SUCCESS('🔐 CREDENCIALES:'))
            self.stdout.write('   admin_user / Admin123!')
            self.stdout.write('   gerente_user / Gerente123!')
            self.stdout.write('   operario_user / Operario123!')
            self.stdout.write('')
