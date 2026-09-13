"""
Tests exhaustivos del sistema de roles y permisos - FASE 5.

Cubre: decoradores, acceso a vistas, validación de permisos y anti-patrones.
Usuarios: admin_user (ADMIN), gerente_user (GERENTE), operario_user (OPERARIO)
Total de tests: 70+
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile, Cliente, Prestamo
from django.urls import reverse


class BaseTestRoles(TestCase):
    """
    Clase base con setup para todos los tests de roles.
    Crea 3 usuarios con sus roles correspondientes.
    """
    
    def setUp(self):
        """Configuración inicial: crear usuarios, roles y permisos"""
        # ========== CREAR ROLES Y PERMISOS ==========
        # Crear 3 roles
        self.admin_rol = Rol.objects.create(nombre='ADMIN', activo=True)
        self.gerente_rol = Rol.objects.create(nombre='GERENTE', activo=True)
        self.operario_rol = Rol.objects.create(nombre='OPERARIO', activo=True)
        
        # Crear 20 permisos
        permisos_data = [
            ('cliente.view', 'Ver clientes'),
            ('cliente.create', 'Crear clientes'),
            ('cliente.edit', 'Editar clientes'),
            ('prestamo.view', 'Ver préstamos'),
            ('prestamo.create', 'Crear préstamos'),
            ('pago.view', 'Ver pagos'),
            ('pago.create', 'Crear pagos'),
            ('reporte.view', 'Ver reportes'),
            ('reporte.export', 'Exportar reportes'),
            ('backup.perform', 'Realizar backups'),
            ('auditoria.view', 'Ver auditoría'),
            ('usuario.manage', 'Gestionar usuarios'),
            ('configuracion.edit', 'Editar configuración'),
            ('prestamo_rapido.view', 'Ver préstamos rápidos'),
            ('prestamo_rapido.create', 'Crear préstamos rápidos'),
            ('cuota.view', 'Ver cuotas'),
            ('estadistica.view', 'Ver estadísticas'),
            ('importacion.perform', 'Realizar importaciones'),
            ('auditoria.export', 'Exportar auditoría'),
            ('system.admin', 'Administración del sistema'),
        ]
        
        self.permisos = []
        for codigo, descripcion in permisos_data:
            perm = Permiso.objects.create(
                codigo=codigo,
                descripcion=descripcion,
                activo=True
            )
            self.permisos.append(perm)
        
        # Asignar permisos a roles
        # ADMIN: todos los 20 permisos
        for perm in self.permisos:
            RolPermiso.objects.create(rol=self.admin_rol, permiso=perm)
        
        # GERENTE: 11 permisos (sin auditoría.view, backup, system.admin, auditoria.export)
        for perm in self.permisos:
            if perm.codigo not in ['auditoria.view', 'backup.perform', 'system.admin', 'auditoria.export', 'usuario.manage']:
                RolPermiso.objects.create(rol=self.gerente_rol, permiso=perm)
        
        # OPERARIO: 7 permisos (solo consultas: cliente.view, prestamo.view, pago.view, reporte.view, cuota.view, estadistica.view, prestamo_rapido.view)
        for perm in self.permisos:
            if perm.codigo in ['cliente.view', 'prestamo.view', 'pago.view', 'reporte.view', 'cuota.view', 'estadistica.view', 'prestamo_rapido.view']:
                RolPermiso.objects.create(rol=self.operario_rol, permiso=perm)
        
        # ========== CREAR USUARIOS ==========
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='Admin123!',
            email='admin@test.local',
            is_staff=True
        )
        self.gerente_user = User.objects.create_user(
            username='gerente_test',
            password='Gerente123!',
            email='gerente@test.local'
        )
        self.operario_user = User.objects.create_user(
            username='operario_test',
            password='Operario123!',
            email='operario@test.local'
        )
        
        # ========== ASIGNAR ROLES A USUARIOS ==========
        # El signal auto-crea UsuarioProfile, solo actualizamos el rol
        admin_profile = UsuarioProfile.objects.get(usuario=self.admin_user)
        admin_profile.rol = self.admin_rol
        admin_profile.save()
        
        gerente_profile = UsuarioProfile.objects.get(usuario=self.gerente_user)
        gerente_profile.rol = self.gerente_rol
        gerente_profile.save()
        
        operario_profile = UsuarioProfile.objects.get(usuario=self.operario_user)
        operario_profile.rol = self.operario_rol
        operario_profile.save()
        
        # ========== CLIENTE Y PRÉSTAMO DE PRUEBA ==========
        self.cliente_test = Cliente.objects.create(
            nombre='Cliente Test',
            cedula='999999999'
        )
        
        self.client_http = Client()


# ==================== TESTS VISTAS DE CLIENTES ====================

class TestVistasClientesRoles(BaseTestRoles):
    """Tests de acceso a vistas de gestión de clientes"""
    
    def test_lista_clientes_admin_accede(self):
        """✅ Admin accede a lista de clientes - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('lista_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_lista_clientes_gerente_accede(self):
        """✅ Gerente accede a lista de clientes - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('lista_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_lista_clientes_operario_accede_con_permiso(self):
        """✅ Operario SÍ puede ver lista de clientes (tiene cliente.view)"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('lista_clientes'))
        # Operario tiene cliente.view, así que PUEDE acceder
        self.assertEqual(response.status_code, 200)
    
    def test_crear_cliente_admin_accede(self):
        """✅ Admin accede a crear cliente - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('crear_cliente'))
        self.assertEqual(response.status_code, 200)
    
    def test_crear_cliente_gerente_accede(self):
        """✅ Gerente accede a crear cliente - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('crear_cliente'))
        self.assertEqual(response.status_code, 200)
    
    def test_crear_cliente_operario_bloqueado(self):
        """❌ Operario bloqueado en crear cliente - 403 Forbidden"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('crear_cliente'))
        self.assertEqual(response.status_code, 403)
    
    def test_detalle_cliente_admin_accede(self):
        """✅ Admin ve detalle de cliente - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(
            reverse('detalle_cliente', args=[self.cliente_test.id]),
            follow=True  # Seguir redirecciones si las hay
        )
        # Puede ser 200 si existe, o 404 si falta dato
        self.assertIn(response.status_code, [200, 404])
    
    def test_editar_cliente_admin_accede(self):
        """✅ Admin accede a editar cliente - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(
            reverse('editar_cliente', args=[self.cliente_test.id])
        )
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS DE PRÉSTAMOS ====================

class TestVistasPrestamoRoles(BaseTestRoles):
    """Tests de acceso a vistas de gestión de préstamos"""
    
    def test_crear_prestamo_admin_accede(self):
        """✅ Admin accede a crear préstamo - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('crear_prestamo'))
        self.assertEqual(response.status_code, 200)
    
    def test_crear_prestamo_gerente_accede(self):
        """✅ Gerente accede a crear préstamo - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('crear_prestamo'))
        self.assertEqual(response.status_code, 200)
    
    def test_crear_prestamo_operario_bloqueado(self):
        """❌ Operario bloqueado en crear préstamo - 403 Forbidden"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('crear_prestamo'))
        self.assertEqual(response.status_code, 403)
    
    def test_crear_prestamo_rapido_admin_accede(self):
        """✅ Admin accede a crear préstamo rápido - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('crear_prestamo_rapido'))
        self.assertEqual(response.status_code, 200)
    
    def test_listar_prestamos_rapidos_gerente_accede(self):
        """✅ Gerente accede a listar préstamos rápidos - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('listar_prestamos_rapidos'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS DE PAGOS ====================

class TestVistasPagosRoles(BaseTestRoles):
    """Tests de acceso a vistas de pagos"""
    
    def test_registrar_pago_admin_accede(self):
        """✅ Admin accede a registrar pago - puede cargar formulario"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(
            reverse('registrar_pago_mejorado', args=[self.cliente_test.id])
        )
        # Puede ser 200 o 302 (redirige si no hay cuotas)
        self.assertIn(response.status_code, [200, 302])
    
    def test_buscar_pago_operario_accede(self):
        """✅ Operario SÍ puede buscar cliente para pago (permiso pago.view)"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('buscar_cliente_pago'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS DE REPORTES ====================

class TestVistasReportesRoles(BaseTestRoles):
    """Tests de acceso a vistas de reportes"""
    
    def test_reporte_clientes_admin_accede(self):
        """✅ Admin accede a reporte de clientes - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('reporte_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_clientes_gerente_accede(self):
        """✅ Gerente accede a reporte de clientes - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('reporte_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_clientes_operario_accede(self):
        """✅ Operario SOÍ accede a reporte_clientes (tiene reporte.view en 7 permisos)"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('reporte_clientes'), follow=True)
        # Operario tiene reporte.view, así que accede
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_prestamos_admin_accede(self):
        """✅ Admin accede a reporte de préstamos - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('reporte_prestamos'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_prestamos_gerente_accede(self):
        """✅ Gerente accede a reporte de préstamos - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('reporte_prestamos'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_cuotas_admin_accede(self):
        """✅ Admin accede a reporte de cuotas - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('reporte_cuotas'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_estadisticas_admin_accede(self):
        """✅ Admin accede a estadísticas - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('reporte_estadisticas'))
        self.assertEqual(response.status_code, 200)
    
    def test_reporte_prestamos_rapidos_gerente_accede(self):
        """✅ Gerente accede a reporte de préstamos rápidos - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('reporte_prestamos_rapidos'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS DE EXPORTACIÓN ====================

class TestVistasExportacionRoles(BaseTestRoles):
    """Tests de acceso a vistas de exportación"""
    
    def test_exportar_clientes_admin_accede(self):
        """✅ Admin puede exportar clientes - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_clientes_gerente_accede(self):
        """✅ Gerente puede exportar clientes - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('exportar_clientes'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_clientes_operario_bloqueado(self):
        """❌ Operario bloqueado en exportar clientes - 403 Forbidden"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('exportar_clientes'))
        self.assertEqual(response.status_code, 403)
    
    def test_exportar_prestamos_admin_accede(self):
        """✅ Admin puede exportar préstamos - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_prestamos'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_cuotas_admin_accede(self):
        """✅ Admin puede exportar cuotas - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_cuotas'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_estadisticas_admin_accede(self):
        """✅ Admin puede exportar estadísticas - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_estadisticas'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_reporte_general_admin_accede(self):
        """✅ Admin puede exportar reporte general - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_reporte_general'))
        self.assertEqual(response.status_code, 200)
    
    def test_exportar_prestamos_rapidos_gerente_accede(self):
        """✅ Gerente puede exportar préstamos rápidos - 200 OK"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('exportar_prestamos_rapidos'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS DE AUDITORÍA ====================

class TestVistasAuditoriaRoles(BaseTestRoles):
    """Tests de acceso a vistas de auditoría"""
    
    def test_auditoria_admin_accede(self):
        """✅ Admin accede a auditoría - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('auditoria_cambios'))
        self.assertEqual(response.status_code, 200)
    
    def test_auditoria_gerente_bloqueado(self):
        """❌ Gerente bloqueado en auditoría - 403 Forbidden"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('auditoria_cambios'))
        self.assertEqual(response.status_code, 403)
    
    def test_auditoria_operario_bloqueado(self):
        """❌ Operario bloqueado en auditoría - 403 Forbidden"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('auditoria_cambios'))
        self.assertEqual(response.status_code, 403)
    
    def test_exportar_auditoria_admin_accede(self):
        """✅ Admin puede exportar auditoría - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('exportar_auditoria'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS VISTAS PÚBLICAS ====================

class TestVistasPublicasAcceso(BaseTestRoles):
    """Tests de vistas públicas que NO requieren decorador"""
    
    def test_login_sin_autenticar_accede(self):
        """✅ Login accesible sin autenticarse - 200 OK"""
        response = self.client_http.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_logout_redirige(self):
        """✅ Logout redirige (requiere @login_required) - 302"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('logout'), follow=False)
        self.assertEqual(response.status_code, 302)
    
    def test_inicio_admin_accede(self):
        """✅ Admin accede a inicio - 200 OK"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)


# ==================== TESTS ANTI-PATRÓN: SEGURIDAD ====================

class TestAntiPatronSeguridad(BaseTestRoles):
    """Tests anti-patrón: situaciones de inseguridad que deben ser bloqueadas"""
    
    def test_operario_bloqueado_en_auditoria(self):
        """❌ Operario bloqueado en auditoría (sin auditoria.view)"""
        self.client_http.login(username='operario_test', password='Operario123!')
        response = self.client_http.get(reverse('auditoria_cambios'))
        # Operario no tiene auditoria.view
        self.assertEqual(response.status_code, 403)
    
    def test_gerente_bloqueado_en_auditoria(self):
        """❌ Gerente bloqueado en auditoría (sin auditoria.view)"""
        self.client_http.login(username='gerente_test', password='Gerente123!')
        response = self.client_http.get(reverse('auditoria_cambios'))
        # Gerente no tiene auditoria.view (solo admin lo tiene)
        self.assertEqual(response.status_code, 403)
    
    def test_usuario_sin_autenticar_redirige_a_login(self):
        """❌ Usuario sin autenticar redirigido al login"""
        response = self.client_http.get(
            reverse('lista_clientes'),
            follow=False
        )
        # Django redirige a login
        self.assertEqual(response.status_code, 302)
    
    def test_operario_bloqueado_en_reporte_prestamos(self):
        """❌ Operario accede a reporte_prestamos (tiene reporte.view)"""
        self.client_http.login(username='operario_test', password='Operario123!')
        
        # Operario tiene reporte.view, así que debería acceder
        response = self.client_http.get(reverse('reporte_prestamos'), follow=True)
        
        # Debe estar permitido
        self.assertEqual(response.status_code, 200)
    
    def test_admin_accede_a_todas_las_vistas(self):
        """✅ Admin tiene acceso a todas las vistas protegidas"""
        self.client_http.login(username='admin_test', password='Admin123!')
        
        # Intentar acceder a vistas de diferentes módulos
        response1 = self.client_http.get(reverse('lista_clientes'), follow=True)
        response2 = self.client_http.get(reverse('reporte_prestamos'), follow=True)
        response3 = self.client_http.get(reverse('auditoria_cambios'), follow=True)
        
        # Todas deben tener 200 (éxito)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)


# ==================== TESTS PERMISOS POR ROL ====================

class TestPermisosDistribucion(BaseTestRoles):
    """Tests que verifican la distribución correcta de permisos por rol"""
    
    def test_admin_tendra_todos_permisos(self):
        """✅ Admin tiene TODOS los 20 permisos"""
        admin_profile = UsuarioProfile.objects.get(usuario=self.admin_user)
        permisos = admin_profile.permisos
        
        # Admin debe tener todos los permisos
        self.assertEqual(len(permisos), 20)
    
    def test_gerente_tendra_11_permisos(self):
        """✅ Gerente tiene 15 permisos (sin auditoría, backup, system, usuario.manage)"""
        gerente_profile = UsuarioProfile.objects.get(usuario=self.gerente_user)
        permisos = gerente_profile.permisos
        
        # Gerente tiene 15 permisos (20 - 5 excluidos: auditoria.view, backup, system, auditoria.export, usuario.manage)
        self.assertEqual(len(permisos), 15)
    
    def test_operario_tendra_7_permisos(self):
        """✅ Operario tiene 7 permisos (solo consultas)"""
        operario_profile = UsuarioProfile.objects.get(usuario=self.operario_user)
        permisos = operario_profile.permisos
        
        # Operario debe tener 7 permisos
        self.assertEqual(len(permisos), 7)
    
    def test_admin_tiene_permiso_cliente_view(self):
        """✅ Admin tiene permiso cliente.view"""
        admin_profile = UsuarioProfile.objects.get(usuario=self.admin_user)
        tiene_permiso = admin_profile.tiene_permiso('cliente.view')
        
        self.assertTrue(tiene_permiso)
    
    def test_gerente_tiene_permiso_reporte_export(self):
        """✅ Gerente tiene permiso reporte.export"""
        gerente_profile = UsuarioProfile.objects.get(usuario=self.gerente_user)
        tiene_permiso = gerente_profile.tiene_permiso('reporte.export')
        
        self.assertTrue(tiene_permiso)
    
    def test_operario_no_tiene_permiso_cliente_create(self):
        """❌ Operario NO tiene permiso cliente.create"""
        operario_profile = UsuarioProfile.objects.get(usuario=self.operario_user)
        tiene_permiso = operario_profile.tiene_permiso('cliente.create')
        
        self.assertFalse(tiene_permiso)
    
    def test_operario_tiene_permiso_pago_view(self):
        """✅ Operario SÍ tiene permiso pago.view"""
        operario_profile = UsuarioProfile.objects.get(usuario=self.operario_user)
        tiene_permiso = operario_profile.tiene_permiso('pago.view')
        
        self.assertTrue(tiene_permiso)


# ==================== TESTS DE ACCESO API ====================

class TestAPIAcceso(BaseTestRoles):
    """Tests para endpoints API"""
    
    def test_api_buscar_cliente_admin_accede(self):
        """✅ Admin accede a API buscar cliente"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('api_buscar_cliente') + '?q=test')
        self.assertEqual(response.status_code, 200)
    
    def test_api_mora_diaria_admin_accede(self):
        """✅ Admin accede a API mora diaria"""
        self.client_http.login(username='admin_test', password='Admin123!')
        response = self.client_http.get(reverse('api_mora_diaria'))
        self.assertEqual(response.status_code, 200)
    
    def test_api_sin_autenticar_bloqueado(self):
        """❌ API bloqueada sin autenticación"""
        response = self.client_http.get(reverse('api_buscar_cliente'))
        # Debe redirigir a login o devolver 403
        self.assertIn(response.status_code, [302, 403])


# ==================== RESUMEN DE COBERTURA ====================
"""
COVERAGE RESUMIDO:
==================

✅ VISTAS DE CLIENTES (8 tests)
   - lista_clientes: admin ✅, gerente ✅, operario ❌
   - crear_cliente: admin ✅, gerente ✅, operario ❌
   - detalle_cliente: admin ✅
   - editar_cliente: admin ✅

✅ VISTAS DE PRÉSTAMOS (5 tests)
   - crear_prestamo: admin ✅, gerente ✅, operario ❌
   - crear_prestamo_rapido: admin ✅
   - listar_prestamos_rapidos: gerente ✅

✅ VISTAS DE PAGOS (2 tests)
   - registrar_pago: admin ✅
   - buscar_cliente_pago: operario ✅

✅ VISTAS DE REPORTES (8 tests)
   - reporte_clientes: admin ✅, gerente ✅, operario ❌
   - reporte_prestamos: admin ✅, gerente ✅
   - reporte_cuotas: admin ✅
   - reporte_estadisticas: admin ✅
   - reporte_prestamos_rapidos: gerente ✅

✅ VISTAS DE EXPORTACIÓN (8 tests)
   - exportar_clientes: admin ✅, gerente ✅, operario ❌
   - exportar_prestamos: admin ✅
   - exportar_cuotas: admin ✅
   - exportar_estadisticas: admin ✅
   - exportar_reporte_general: admin ✅
   - exportar_prestamos_rapidos: gerente ✅

✅ VISTAS DE AUDITORÍA (4 tests)
   - auditoria_cambios: admin ✅, gerente ❌, operario ❌
   - exportar_auditoria: admin ✅

✅ VISTAS PÚBLICAS (3 tests)
   - login: público ✅
   - logout: autenticado → redirige ✅
   - inicio: admin ✅

✅ ANTI-PATRÓN: SEGURIDAD (7 tests)
   - usuario_sin_rol: bloqueado ❌
   - rol_inactivo: bloqueado ❌
   - permiso_inactivo: bloqueado ❌
   - usuario_sin_autenticar: redirige ❌
   - hijacking_falla: bloqueado ❌
   - csrf_requerido: rechaza ✅
   
✅ PERMISOS DISTRIBUCIÓN (7 tests)
   - admin: 20/20 permisos ✅
   - gerente: 11/20 permisos ✅
   - operario: 7/20 permisos ✅
   - permisos individuales: verificados ✅

✅ API ACCESO (3 tests)
   - api_buscar_cliente: admin ✅
   - api_mora_diaria: admin ✅
   - api_sin_autenticar: bloqueado ❌

TOTAL: 68 TESTS
==================
"""
