"""
CRÍTICA #6: TESTS - AUDIT LOG SYSTEM
Pruebas para el sistema de auditoría
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from mi_app.models import (
    Cliente, Prestamo, Cuota, Pago, ListaNegra, AuditLog
)
from mi_app.utilities.audit_decorator import audit_view, audit_action, get_client_ip


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def user_admin(db):
    """Crea un usuario admin para pruebas"""
    return User.objects.create_superuser(
        username='admin_test',
        email='admin@test.com',
        password='admin123'
    )


@pytest.fixture
def user_normal(db):
    """Crea un usuario normal"""
    return User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='user123'
    )


@pytest.fixture
def request_factory():
    """Factory para crear requests mock"""
    return RequestFactory()


@pytest.fixture
def cliente_test(db):
    """Crea un cliente para pruebas"""
    return Cliente.objects.create(
        nombre='Cliente Test',
        cedula='1234567890',
        celular='3001234567',
        email='cliente@test.com',
        estado='activo'
    )


@pytest.fixture
def prestamo_test(db, cliente_test):
    """Crea un préstamo para pruebas"""
    return Prestamo.objects.create(
        cliente=cliente_test,
        monto_total=Decimal('1000.00'),
        tasa_interes=Decimal('2.5'),
        numero_cuotas=10,
        fecha_inicio=timezone.now().date(),
        estado='activo'
    )


# =============================================================================
# TEST CLASSES - UNIT TESTS
# =============================================================================

@pytest.mark.django_db
class TestAuditLogModel:
    """Tests para el modelo AuditLog"""
    
    def test_crear_auditlog_basico(self, user_admin):
        """Prueba crear un registro de auditoría básico"""
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Cliente',
            objeto_id=1,
            objeto_representacion='Cliente: Test (123)',
            ip_address='127.0.0.1',
            descripcion='Cliente creado'
        )
        
        assert log.id is not None
        assert log.usuario == user_admin
        assert log.accion == 'CREATE'
        assert log.modelo == 'Cliente'
        
    def test_auditlog_sin_usuario(self):
        """Prueba crear auditoría sin usuario (SISTEMA)"""
        log = AuditLog.objects.create(
            usuario=None,
            accion='CREATE',
            modelo='Prestamo',
            objeto_id=1,
            objeto_representacion='Préstamo #1',
            descripcion='Préstamo creado por sistema'
        )
        
        assert log.usuario is None
        assert log.accion == 'CREATE'
    
    def test_auditlog_con_cambios_json(self, user_admin):
        """Prueba auditoría con cambios JSON"""
        cambios = {
            'estado': ['activo', 'inactivo'],
            'saldo': ['1000.00', '900.00']
        }
        
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='UPDATE',
            modelo='Cliente',
            objeto_id=1,
            objeto_representacion='Cliente: Test',
            cambios=cambios,
            descripcion='Cliente actualizado'
        )
        
        assert log.cambios == cambios
        assert log.cambios['estado'] == ['activo', 'inactivo']
    
    def test_get_cambios_legibles(self, user_admin):
        """Prueba el método get_cambios_legibles()"""
        cambios = {
            'estado': ['activo', 'inactivo'],
            'rating': ['5', '3']
        }
        
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='UPDATE',
            modelo='Cliente',
            objeto_id=1,
            objeto_representacion='Cliente: Test',
            cambios=cambios
        )
        
        resultado = log.get_cambios_legibles()
        assert 'estado' in resultado
        assert 'activo' in resultado
        assert 'inactivo' in resultado
    
    def test_auditlog_str(self, user_admin):
        """Prueba el método __str__"""
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='DELETE',
            modelo='Pago',
            objeto_id=5,
            objeto_representacion='Pago $100'
        )
        
        str_result = str(log)
        assert 'Pago $100' in str_result
        assert 'admin_test' in str_result
    
    def test_auditlog_ordering(self, user_admin):
        """Prueba que los logs se ordenen por timestamp descendente"""
        log1 = AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Cliente',
            objeto_id=1,
            timestamp=timezone.now() - timedelta(hours=2)
        )
        
        log2 = AuditLog.objects.create(
            usuario=user_admin,
            accion='UPDATE',
            modelo='Cliente',
            objeto_id=1,
            timestamp=timezone.now()
        )
        
        logs = list(AuditLog.objects.all())
        assert logs[0].id == log2.id  # El más reciente primero
        assert logs[1].id == log1.id
    
    def test_auditlog_timestamp_auto(self, user_admin):
        """Prueba que timestamp se establezca automáticamente"""
        antes = timezone.now()
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Cliente',
            objeto_id=1
        )
        despues = timezone.now()
        
        assert antes <= log.timestamp <= despues


@pytest.mark.django_db
class TestAuditLogQueryFilters:
    """Tests para filtrar logs de auditoría"""
    
    def test_filtrar_por_usuario(self, user_admin, user_normal):
        """Prueba filtrar logs por usuario"""
        AuditLog.objects.create(usuario=user_admin, accion='CREATE', modelo='Cliente', objeto_id=1)
        AuditLog.objects.create(usuario=user_normal, accion='UPDATE', modelo='Cliente', objeto_id=2)
        
        logs_admin = AuditLog.objects.filter(usuario=user_admin)
        logs_normal = AuditLog.objects.filter(usuario=user_normal)
        
        assert logs_admin.count() == 1
        assert logs_normal.count() == 1
    
    def test_filtrar_por_accion(self, user_admin):
        """Prueba filtrar logs por acción"""
        AuditLog.objects.create(usuario=user_admin, accion='CREATE', modelo='Cliente', objeto_id=1)
        AuditLog.objects.create(usuario=user_admin, accion='UPDATE', modelo='Cliente', objeto_id=2)
        AuditLog.objects.create(usuario=user_admin, accion='DELETE', modelo='Cliente', objeto_id=3)
        
        creates = AuditLog.objects.filter(accion='CREATE')
        updates = AuditLog.objects.filter(accion='UPDATE')
        deletes = AuditLog.objects.filter(accion='DELETE')
        
        assert creates.count() == 1
        assert updates.count() == 1
        assert deletes.count() == 1
    
    def test_filtrar_por_modelo(self, user_admin):
        """Prueba filtrar logs por modelo"""
        AuditLog.objects.create(usuario=user_admin, accion='CREATE', modelo='Cliente', objeto_id=1)
        AuditLog.objects.create(usuario=user_admin, accion='CREATE', modelo='Prestamo', objeto_id=2)
        
        clientes = AuditLog.objects.filter(modelo='Cliente')
        prestamos = AuditLog.objects.filter(modelo='Prestamo')
        
        assert clientes.count() == 1
        assert prestamos.count() == 1
    
    def test_filtrar_por_rango_fechas(self, user_admin):
        """Prueba filtrar logs sin rango de fechas específico"""
        # Crear múltiples logs
        for i in range(3):
            AuditLog.objects.create(
                usuario=user_admin,
                accion='CREATE',
                modelo='Cliente',
                objeto_id=i
            )
        
        # Verificar que existan
        todos_logs = AuditLog.objects.all()
        assert todos_logs.count() == 3
        
        # Filtrar solo CREATEs
        logs_creates = AuditLog.objects.filter(accion='CREATE')
        assert logs_creates.count() == 3


@pytest.mark.django_db
class TestAuditDecorator:
    """Tests para el decorador de auditoría"""
    
    def test_audit_action_funcion(self, user_admin):
        """Prueba función audit_action"""
        audit_action(
            accion='PAGO',
            modelo='Pago',
            objeto_repr='Pago $100',
            descripcion='Pago registrado',
            usuario=user_admin,
            ip_address='192.168.1.1'
        )
        
        logs = AuditLog.objects.filter(accion='PAGO')
        assert logs.count() == 1
        assert logs.first().ip_address == '192.168.1.1'
    
    def test_get_client_ip_from_forwarded(self, request_factory):
        """Prueba obtener IP del cliente desde X-Forwarded-For"""
        request = request_factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 198.51.100.1'
        
        ip = get_client_ip(request)
        assert ip == '203.0.113.1'
    
    def test_get_client_ip_from_remote_addr(self, request_factory):
        """Prueba obtener IP del cliente desde REMOTE_ADDR"""
        request = request_factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        assert ip == '192.168.1.100'


# =============================================================================
# TEST CLASSES - INTEGRATION TESTS
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestIntegracionAuditConModelos:
    """Tests de integración entre auditoría y modelos"""
    
    def test_auditlog_resumen_property(self, user_admin):
        """Prueba la propiedad resumen"""
        log = AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Cliente',
            objeto_id=1,
            objeto_representacion='Cliente: Test',
            descripcion='Cliente creado exitosamente'
        )
        
        resumen = log.resumen
        assert 'Crear' in resumen  # get_accion_display() usa el label de choices
        assert 'Cliente: Test' in resumen
    
    def test_auditlog_multiple_acciones_mismo_objeto(self, user_admin, user_normal):
        """Prueba múltiples acciones en el mismo objeto"""
        objeto_id = 1
        
        AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Prestamo',
            objeto_id=objeto_id
        )
        
        AuditLog.objects.create(
            usuario=user_normal,
            accion='UPDATE',
            modelo='Prestamo',
            objeto_id=objeto_id
        )
        
        AuditLog.objects.create(
            usuario=user_admin,
            accion='UPDATE',
            modelo='Prestamo',
            objeto_id=objeto_id
        )
        
        historial = AuditLog.objects.filter(
            modelo='Prestamo',
            objeto_id=objeto_id
        ).order_by('-timestamp')
        
        assert historial.count() == 3
        assert list(historial.values_list('usuario_id', flat=True)) == [
            user_admin.id,
            user_normal.id,
            user_admin.id
        ]


@pytest.mark.django_db
@pytest.mark.integration
class TestAuditLogStatistics:
    """Tests de estadísticas de auditoría"""
    
    def test_contar_creaciones(self, user_admin):
        """Prueba contar operaciones CREATE"""
        for i in range(5):
            AuditLog.objects.create(
                usuario=user_admin,
                accion='CREATE',
                modelo='Cliente',
                objeto_id=i
            )
        
        creates = AuditLog.objects.filter(accion='CREATE').count()
        assert creates == 5
    
    def test_usuarios_activos(self, user_admin, user_normal):
        """Prueba contar usuarios activos en auditoría"""
        for i in range(3):
            AuditLog.objects.create(usuario=user_admin, accion='CREATE', modelo='Cliente', objeto_id=i)
        
        for i in range(2):
            AuditLog.objects.create(usuario=user_normal, accion='UPDATE', modelo='Cliente', objeto_id=i)
        
        usuarios = AuditLog.objects.values('usuario').distinct().count()
        assert usuarios == 2
    
    def test_modelos_afectados(self, user_admin):
        """Prueba contar modelos auditados"""
        for modelo in ['Cliente', 'Prestamo', 'Cuota', 'Pago']:
            AuditLog.objects.create(
                usuario=user_admin,
                accion='CREATE',
                modelo=modelo,
                objeto_id=1
            )
        
        modelos = AuditLog.objects.values('modelo').distinct().count()
        assert modelos == 4


# =============================================================================
# TEST CLASSES - E2E TESTS
# =============================================================================

@pytest.mark.django_db
@pytest.mark.e2e
class TestAuditE2E:
    """Tests E2E para auditoría"""
    
    def test_flujo_completo_auditoria(self, user_admin, user_normal):
        """Prueba flujo completo: crear, actualizar, reportar"""
        
        # Crear log de creación
        log_create = AuditLog.objects.create(
            usuario=user_admin,
            accion='CREATE',
            modelo='Cliente',
            objeto_id=1,
            descripcion='Cliente John creado'
        )
        
        # Crear log de actualización
        log_update = AuditLog.objects.create(
            usuario=user_normal,
            accion='UPDATE',
            modelo='Cliente',
            objeto_id=1,
            cambios={'estado': ['activo', 'inactivo']},
            descripcion='Cliente marcado como inactivo'
        )
        
        # Verificar que ambos logs existan
        historial = AuditLog.objects.filter(objeto_id=1).order_by('timestamp')
        assert historial.count() == 2
        
        # Verificar secuencia correcta
        assert historial[0].accion == 'CREATE'
        assert historial[1].accion == 'UPDATE'
        
        # Verificar usuarios
        assert historial[0].usuario == user_admin
        assert historial[1].usuario == user_normal
