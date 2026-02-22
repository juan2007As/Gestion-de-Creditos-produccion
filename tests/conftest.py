"""
PYTEST CONFIGURATION - Shared fixtures for all tests
=====================================================

Este archivo contiene fixtures compartidos para todos los tests.
Pytest los carga automáticamente desde conftest.py
"""

import pytest
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion, ListaNegra


# ============================================================================
# PYTEST MARKERS
# ============================================================================

def pytest_configure(config):
    """Registra markers personalizados"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "auth: Auth tests")
    config.addinivalue_line("markers", "financial: Financial tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# ============================================================================
# FIXTURES - USUARIOS
# ============================================================================

@pytest.fixture
def user_normal():
    """Usuario normal autenticado"""
    return User.objects.create_user(
        username='testuser',
        email='testuser@test.com',
        password='testpass123'
    )


@pytest.fixture
def user_admin():
    """Usuario admin"""
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )
    return user


@pytest.fixture
def user_staff():
    """Usuario staff (gerente)"""
    user = User.objects.create_user(
        username='staff',
        email='staff@test.com',
        password='staff123'
    )
    user.is_staff = True
    user.save()
    return user


# ============================================================================
# FIXTURES - CLIENTES
# ============================================================================

@pytest.fixture
def cliente_activo():
    """Cliente normal activo"""
    return Cliente.objects.create(
        nombre='Cliente Activo',
        cedula='1111111111',
        celular='3001234567',
        estado='ACTIVO',
        total_prestado=Decimal('0')
    )


@pytest.fixture
def cliente_inactivo():
    """Cliente inactivo"""
    return Cliente.objects.create(
        nombre='Cliente Inactivo',
        cedula='2222222222',
        celular='3002222222',
        estado='INACTIVO',
        total_prestado=Decimal('0')
    )


@pytest.fixture
def cliente_moroso():
    """Cliente en lista negra (moroso)"""
    cliente = Cliente.objects.create(
        nombre='Cliente Moroso',
        cedula='9999999999',
        celular='3009999999',
        estado='ACTIVO',
        total_prestado=Decimal('0')
    )
    return cliente


# ============================================================================
# FIXTURES - PRÉSTAMOS
# ============================================================================

@pytest.fixture
def prestamo_activo(cliente_activo):
    """Préstamo activo"""
    return Prestamo.objects.create(
        cliente=cliente_activo,
        monto_total=Decimal('50000'),
        interes_porcentaje=Decimal('5.0'),
        fecha_inicio=date.today(),
        fecha_fin_estimada=date.today() + timedelta(days=60),
        tipo_pago='QUINCENAL',
        estado='ACTIVO'
    )


@pytest.fixture
def prestamo_completado(cliente_activo):
    """Préstamo completado/pagado - usa fechas válidas (no retroactivas)"""
    prestamo = Prestamo.objects.create(
        cliente=cliente_activo,
        monto_total=Decimal('20000'),
        interes_porcentaje=Decimal('5.0'),
        fecha_inicio=date.today(),
        fecha_fin_estimada=date.today() + timedelta(days=60),
        tipo_pago='QUINCENAL',
        estado='COMPLETADO'
    )
    return prestamo


# ============================================================================
# FIXTURES - CUOTAS
# ============================================================================

@pytest.fixture
def cuota_pendiente(prestamo_activo):
    """Cuota sin pagar"""
    return Cuota.objects.create(
        prestamo=prestamo_activo,
        numero_cuota=1,
        monto_original=Decimal('5000'),
        monto_pendiente=Decimal('5000'),
        interes_normal=Decimal('250'),
        monto_pendiente_interes=Decimal('250'),
        fecha_pago_esperada=date.today() + timedelta(days=15),
        estado='PENDIENTE'
    )


@pytest.fixture
def cuota_pagada(prestamo_completado):
    """Cuota pagada"""
    cuota = Cuota.objects.create(
        prestamo=prestamo_completado,
        numero_cuota=1,
        monto_original=Decimal('5000'),
        monto_pendiente=Decimal('0'),
        interes_normal=Decimal('250'),
        monto_pendiente_interes=Decimal('0'),
        fecha_pago_esperada=date.today() - timedelta(days=45),
        estado='PAGADA',
        pagado=True,
        fecha_pago_real=date.today() - timedelta(days=40)
    )
    return cuota


@pytest.fixture
def cuota_vencida(prestamo_activo):
    """Cuota vencida (sin pagar)"""
    return Cuota.objects.create(
        prestamo=prestamo_activo,
        numero_cuota=2,
        monto_original=Decimal('5000'),
        monto_pendiente=Decimal('5000'),
        interes_normal=Decimal('250'),
        monto_pendiente_interes=Decimal('250'),
        fecha_pago_esperada=date.today() - timedelta(days=10),  # Hace 10 días
        estado='VENCIDA'
    )


# ============================================================================
# FIXTURES - PAGOS
# ============================================================================

@pytest.fixture
def pago_completo(cuota_pagada):
    """Pago completo de cuota"""
    return Pago.objects.create(
        cuota=cuota_pagada,
        monto_pagado=Decimal('5250'),  # Principal + interés
        monto_principal=Decimal('5000'),
        monto_interes=Decimal('250'),
        monto_mora=Decimal('0'),
        usuario_registra='admin',
        notas='Pago completo'
    )


@pytest.fixture
def pago_parcial(cuota_pendiente):
    """Pago parcial de cuota"""
    return Pago.objects.create(
        cuota=cuota_pendiente,
        monto_pagado=Decimal('2500'),  # Mitad del principal
        monto_principal=Decimal('2500'),
        monto_interes=Decimal('0'),
        monto_mora=Decimal('0'),
        usuario_registra='admin',
        notas='Pago parcial'
    )


# ============================================================================
# FIXTURES - CONFIGURACIÓN
# ============================================================================

@pytest.fixture
def config_default():
    """Configuración por defecto"""
    return Configuracion.objects.get_or_create(
        id=1,
        defaults={
            'tasa_interes_prestamo_normal': Decimal('5.0'),
            'tasa_interes_prestamo_rapido': Decimal('7.5'),
            'dias_gracia_mora': 5,
        }
    )[0]


# ============================================================================
# FIXTURES - LISTA NEGRA
# ============================================================================

@pytest.fixture
def lista_negra_activa(cliente_moroso, user_admin):
    """Cliente en lista negra vigente"""
    return ListaNegra.objects.create(
        cliente=cliente_moroso,
        razon='MOROSO',
        usuario_creador=user_admin,
        activa=True
    )


# ============================================================================
# FIXTURES - TRANSACCIONES
# ============================================================================

@pytest.fixture
def transactional_db():
    """Permite acceso a DB con transacciones (Django default)"""
    pass


# ============================================================================
# HELPERS
# ============================================================================

def create_test_loan(cliente, monto=Decimal('50000'), cuotas=4):
    """Helper: Crea préstamo con cuotas para testing"""
    prestamo = Prestamo.objects.create(
        cliente=cliente,
        monto_total=monto,
        interes_porcentaje=Decimal('5.0'),
        fecha_inicio=date.today(),
        fecha_fin_estimada=date.today() + timedelta(days=60),
        tipo_pago='QUINCENAL',
        estado='ACTIVO'
    )
    
    monto_por_cuota = monto / Decimal(cuotas)
    for i in range(cuotas):
        Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=i+1,
            monto_original=monto_por_cuota,
            monto_pendiente=monto_por_cuota,
            interes_normal=monto_por_cuota * Decimal('0.05'),
            monto_pendiente_interes=monto_por_cuota * Decimal('0.05'),
            fecha_pago_esperada=date.today() + timedelta(days=15*(i+1)),
            estado='PENDIENTE'
        )
    
    return prestamo
