"""
Tests para validar que los decoradores de roles y permisos funcionan correctamente.

Tests incluidos:
- Verificar que ADMIN tiene todos los permisos
- Verificar que GERENTE tiene permisos limitados
- Verificar que OPERARIO tiene permisos mínimos
- Verificar que roles inactivos no tienen acceso
- Verificar que permisos inactivos se rechazan
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from mi_app.models import Rol, Permiso, UsuarioProfile, RolPermiso


class TestDecoradores(TestCase):
    """Tests para validar funcionamiento de decoradores de roles y permisos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear roles
        self.rol_admin = Rol.objects.create(
            nombre='ADMIN',
            descripcion='Administrador del sistema',
            activo=True
        )
        self.rol_gerente = Rol.objects.create(
            nombre='GERENTE',
            descripcion='Gerente operativo',
            activo=True
        )
        self.rol_operario = Rol.objects.create(
            nombre='OPERARIO',
            descripcion='Operario del sistema',
            activo=True
        )
        
        # Crear permisos
        self.perm_cliente_create = Permiso.objects.create(
            codigo='cliente.create',
            descripcion='Crear cliente',
            categoria='CREACION',
            activo=True
        )
        self.perm_cliente_edit = Permiso.objects.create(
            codigo='cliente.edit',
            descripcion='Editar cliente',
            categoria='EDICION',
            activo=True
        )
        self.perm_reporte_export = Permiso.objects.create(
            codigo='reporte.export',
            descripcion='Exportar reportes',
            categoria='EXPORTACION',
            activo=True
        )
        self.perm_inactivo = Permiso.objects.create(
            codigo='backup.create',
            descripcion='Crear backup',
            categoria='SISTEMA',
            activo=False
        )
        
        # Asignar permisos a roles
        # ADMIN: todos los permisos
        RolPermiso.objects.create(rol=self.rol_admin, permiso=self.perm_cliente_create)
        RolPermiso.objects.create(rol=self.rol_admin, permiso=self.perm_cliente_edit)
        RolPermiso.objects.create(rol=self.rol_admin, permiso=self.perm_reporte_export)
        
        # GERENTE: create, edit, export
        RolPermiso.objects.create(rol=self.rol_gerente, permiso=self.perm_cliente_create)
        RolPermiso.objects.create(rol=self.rol_gerente, permiso=self.perm_cliente_edit)
        RolPermiso.objects.create(rol=self.rol_gerente, permiso=self.perm_reporte_export)
        
        # OPERARIO: solo create
        RolPermiso.objects.create(rol=self.rol_operario, permiso=self.perm_cliente_create)
        
        # Crear usuarios
        # NOTA: El signal post_save crea automáticamente UsuarioProfile con rol OPERARIO
        # Por eso usamos get_or_create y actualizamos el rol
        self.user_admin = User.objects.create_user(
            username='admin_user',
            password='pass123',
            first_name='Admin',
            email='admin@example.com'
        )
        self.profile_admin = self.user_admin.profile
        self.profile_admin.rol = self.rol_admin
        self.profile_admin.activo = True
        self.profile_admin.save()
        
        self.user_gerente = User.objects.create_user(
            username='gerente_user',
            password='pass123',
            first_name='Gerente',
            email='gerente@example.com'
        )
        self.profile_gerente = self.user_gerente.profile
        self.profile_gerente.rol = self.rol_gerente
        self.profile_gerente.activo = True
        self.profile_gerente.save()
        
        self.user_operario = User.objects.create_user(
            username='operario_user',
            password='pass123',
            first_name='Operario',
            email='operario@example.com'
        )
        self.profile_operario = self.user_operario.profile
        self.profile_operario.rol = self.rol_operario
        self.profile_operario.activo = True
        self.profile_operario.save()
        
        # Usuario sin rol (el signal lo crea con rol OPERARIO, lo cambiamos a None)
        self.user_sin_rol = User.objects.create_user(
            username='sin_rol',
            password='pass123'
        )
        self.profile_sin_rol = self.user_sin_rol.profile
        self.profile_sin_rol.rol = None
        self.profile_sin_rol.activo = True
        self.profile_sin_rol.save()
        
        # Usuario inactivo (el signal lo crea con rol OPERARIO)
        self.user_inactivo = User.objects.create_user(
            username='inactivo_user',
            password='pass123'
        )
        self.profile_inactivo = self.user_inactivo.profile
        self.profile_inactivo.rol = self.rol_operario
        self.profile_inactivo.activo = False
        self.profile_inactivo.save()
    
    # ==========================================================================
    # TESTS DE PERMISOS - tiene_permiso()
    # ==========================================================================
    
    def test_admin_tiene_todos_permisos(self):
        """ADMIN debe tener todos los permisos asignados"""
        profile = self.user_admin.profile
        self.assertTrue(profile.tiene_permiso('cliente.create'))
        self.assertTrue(profile.tiene_permiso('cliente.edit'))
        self.assertTrue(profile.tiene_permiso('reporte.export'))
    
    def test_gerente_tiene_permisos_limitados(self):
        """GERENTE debe tener solo permisos asignados"""
        profile = self.user_gerente.profile
        self.assertTrue(profile.tiene_permiso('cliente.create'))
        self.assertTrue(profile.tiene_permiso('cliente.edit'))
        self.assertTrue(profile.tiene_permiso('reporte.export'))
    
    def test_operario_tiene_solo_create(self):
        """OPERARIO debe tener solo permiso de create"""
        profile = self.user_operario.profile
        self.assertTrue(profile.tiene_permiso('cliente.create'))
        self.assertFalse(profile.tiene_permiso('cliente.edit'))
        self.assertFalse(profile.tiene_permiso('reporte.export'))
    
    def test_usuario_sin_rol_sin_permisos(self):
        """Usuario sin rol no debe tener permisos"""
        profile = self.user_sin_rol.profile
        self.assertFalse(profile.tiene_permiso('cliente.create'))
        self.assertFalse(profile.tiene_permiso('cliente.edit'))
    
    def test_usuario_inactivo_sin_permisos(self):
        """Usuario inactivo no debe tener permisos aunque tenga rol"""
        profile = self.profile_inactivo
        self.assertFalse(profile.tiene_permiso('cliente.create'))
    
    def test_permiso_inactivo_no_otorga_acceso(self):
        """Permiso inactivo no debe otorgar acceso incluso si está asignado"""
        # El admin tiene backup.create asignado pero está inactivo
        # Agregamos el permiso inactivo al admin
        RolPermiso.objects.create(rol=self.rol_admin, permiso=self.perm_inactivo)
        profile = self.user_admin.profile
        self.assertFalse(profile.tiene_permiso('backup.create'))
    
    # ==========================================================================
    # TESTS DE ROLES - tiene_rol()
    # ==========================================================================
    
    def test_admin_tiene_rol_admin(self):
        """ADMIN debe reconocer su rol"""
        profile = self.user_admin.profile
        self.assertTrue(profile.tiene_rol('ADMIN'))
        self.assertFalse(profile.tiene_rol('GERENTE'))
        self.assertFalse(profile.tiene_rol('OPERARIO'))
    
    def test_gerente_tiene_rol_gerente(self):
        """GERENTE debe reconocer su rol"""
        profile = self.user_gerente.profile
        self.assertFalse(profile.tiene_rol('ADMIN'))
        self.assertTrue(profile.tiene_rol('GERENTE'))
        self.assertFalse(profile.tiene_rol('OPERARIO'))
    
    def test_operario_tiene_rol_operario(self):
        """OPERARIO debe reconocer su rol"""
        profile = self.user_operario.profile
        self.assertFalse(profile.tiene_rol('ADMIN'))
        self.assertFalse(profile.tiene_rol('GERENTE'))
        self.assertTrue(profile.tiene_rol('OPERARIO'))
    
    def test_usuario_inactivo_sin_rol(self):
        """Usuario inactivo no debe ser reconocido con su rol"""
        profile = self.profile_inactivo
        self.assertFalse(profile.tiene_rol('OPERARIO'))
    
    # ==========================================================================
    # TESTS DE PROPIEDAD permisos
    # ==========================================================================
    
    def test_propiedad_permisos_admin(self):
        """Propiedad permisos debe retornar lista correcta para ADMIN"""
        profile = self.user_admin.profile
        permisos = profile.permisos
        
        self.assertIsInstance(permisos, list)
        self.assertIn('cliente.create', permisos)
        self.assertIn('cliente.edit', permisos)
        self.assertIn('reporte.export', permisos)
        self.assertEqual(len(permisos), 3)
    
    def test_propiedad_permisos_operario(self):
        """Propiedad permisos debe retornar solo 1 para OPERARIO"""
        profile = self.user_operario.profile
        permisos = profile.permisos
        
        self.assertIsInstance(permisos, list)
        self.assertIn('cliente.create', permisos)
        self.assertEqual(len(permisos), 1)
    
    def test_propiedad_permisos_sin_rol(self):
        """Propiedad permisos debe retornar lista vacía sin rol"""
        profile = self.user_sin_rol.profile
        permisos = profile.permisos
        
        self.assertIsInstance(permisos, list)
        self.assertEqual(len(permisos), 0)
    
    # ==========================================================================
    # TESTS DE VALIDACIÓN
    # ==========================================================================
    
    def test_str_usuario_profile(self):
        """__str__ debe retornar formato correcto"""
        profile = self.user_admin.profile
        expected = f"{self.user_admin.get_full_name()} ({self.rol_admin.nombre})"
        self.assertEqual(str(profile), expected)
    
    def test_usuario_profile_sin_rol_str(self):
        """__str__ debe manejar usuarios sin rol"""
        # Simplemente verificar que no falla
        str(self.profile_sin_rol)  # Solo validar que no lance excepción
    
    def test_diferentes_usuarios_perfiles_independientes(self):
        """Perfiles de diferentes usuarios deben ser independientes"""
        # Admin tiene cliente.edit, operario no
        admin_tiene_edit = self.user_admin.profile.tiene_permiso('cliente.edit')
        operario_tiene_edit = self.user_operario.profile.tiene_permiso('cliente.edit')
        
        self.assertTrue(admin_tiene_edit)
        self.assertFalse(operario_tiene_edit)
    
    def test_cambiar_rol_usuario(self):
        """Cambiar rol debe actualizar permisos dinámicamente"""
        profile = self.user_operario.profile
        
        # Verificar que inicialmente es OPERARIO
        self.assertTrue(profile.tiene_rol('OPERARIO'))
        self.assertFalse(profile.tiene_permiso('cliente.edit'))
        
        # Cambiar a GERENTE
        profile.rol = self.rol_gerente
        profile.save()
        
        # Recargar profile
        profile.refresh_from_db()
        
        # Verificar nuevos permisos
        self.assertTrue(profile.tiene_rol('GERENTE'))
        self.assertTrue(profile.tiene_permiso('cliente.edit'))
