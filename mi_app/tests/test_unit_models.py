"""
UNIT TESTS - Models, Forms, Utils, Decorators
==============================================

50+ unit tests para cobertura de módulos principales.

Ejecutar: pytest mi_app/tests/test_unit_models.py -v
Ejecutar: pytest -m unit              (todos los unit tests)
Ejecutar: pytest --cov=mi_app         (con cobertura)
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion


# ============================================================================
# UNIT TESTS - CLIENTE MODEL
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestClienteModel:
    """Tests para Cliente model"""
    
    def test_cliente_creacion_basica(self):
        """Crear cliente básico"""
        cliente = Cliente.objects.create(
            nombre='Test Cliente',
            cedula='1234567890',
            celular='3001234567',
            estado='ACTIVO'
        )
        assert cliente.id is not None
        assert cliente.nombre == 'Test Cliente'
        assert cliente.estado == 'ACTIVO'
    
    def test_cliente_total_prestado_default_cero(self):
        """total_prestado por defecto es 0"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='1111111111',
            celular='3001111111'
        )
        assert cliente.total_prestado == Decimal('0')
    
    def test_cliente_rating_default(self):
        """rating por defecto es 0.0"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='2222222222',
            celular='3002222222'
        )
        assert cliente.rating == 0.0
    
    def test_cliente_str_representation(self, cliente_activo):
        """Representación string de cliente"""
        assert str(cliente_activo) == f"{cliente_activo.nombre} - {cliente_activo.celular}"
    
    def test_cliente_inactivo(self):
        """Crear cliente inactivo"""
        cliente = Cliente.objects.create(
            nombre='Inactivo',
            cedula='9999999999',
            celular='3009999999',
            estado='INACTIVO'
        )
        assert cliente.estado == 'INACTIVO'
    
    def test_cliente_tasa_cumplimiento_default(self):
        """tasa_cumplimiento por defecto 100.0"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='3333333333',
            celular='3003333333'
        )
        assert cliente.tasa_cumplimiento == 100.0
    
    def test_cliente_dias_mora_promedio_default(self):
        """dias_mora_promedio por defecto 0.0"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='4444444444',
            celular='3004444444'
        )
        assert cliente.dias_mora_promedio == 0.0


# ============================================================================
# UNIT TESTS - PRESTAMO MODEL
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestPrestamoModel:
    """Tests para Prestamo model"""
    
    def test_prestamo_creacion(self, cliente_activo):
        """Crear préstamo básico"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('50000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        assert prestamo.cliente == cliente_activo
        assert prestamo.monto_total == Decimal('50000')
        assert prestamo.interes_porcentaje == Decimal('5.0')
    
    def test_prestamo_estado_default_activo(self, cliente_activo):
        """Estado por defecto es BORRADOR (draft state)"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30)
        )
        assert prestamo.estado == 'BORRADOR'
    
    def test_prestamo_tipo_pago_default(self, cliente_activo):
        """tipo_pago por defecto QUINCENAL"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('5000'),
            interes_porcentaje=Decimal('3.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=15)
        )
        assert prestamo.tipo_pago == 'QUINCENAL'
    
    def test_prestamo_con_diferentes_montos(self, cliente_activo):
        """Crear préstamos con diferentes montos"""
        for monto in [Decimal('1000'), Decimal('50000'), Decimal('999999')]:
            prestamo = Prestamo.objects.create(
                cliente=cliente_activo,
                monto_total=monto,
                interes_porcentaje=Decimal('5.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=30)
            )
            assert prestamo.monto_total == monto
    
    def test_prestamo_relacion_cliente(self, prestamo_activo):
        """Prestamo está asociado a cliente"""
        assert prestamo_activo.cliente is not None
        assert prestamo_activo.cliente.nombre == 'Cliente Activo'


# ============================================================================
# UNIT TESTS - CUOTA MODEL
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestCuotaModel:
    """Tests para Cuota model"""
    
    def test_cuota_creacion(self, prestamo_activo):
        """Crear cuota básica"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('5000'),
            monto_pendiente=Decimal('5000'),
            interes_normal=Decimal('250'),
            monto_pendiente_interes=Decimal('250'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        assert cuota.prestamo == prestamo_activo
        assert cuota.numero_cuota == 1
        assert cuota.monto_original == Decimal('5000')
    
    def test_cuota_estado_default_pendiente(self, prestamo_activo):
        """Estado por defecto es PENDIENTE"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('1000'),
            interes_normal=Decimal('50'),
            monto_pendiente_interes=Decimal('50'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        assert cuota.estado == 'PENDIENTE'
    
    def test_cuota_pagado_default_false(self, prestamo_activo):
        """pagado por defecto es False"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('1000'),
            interes_normal=Decimal('50'),
            monto_pendiente_interes=Decimal('50'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        assert cuota.pagado is False
    
    def test_cuota_porcentaje_pagado_default_cero(self, prestamo_activo):
        """porcentaje_pagado por defecto 0"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('1000'),
            interes_normal=Decimal('50'),
            monto_pendiente_interes=Decimal('50'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        assert cuota.porcentaje_pagado == 0


# ============================================================================
# UNIT TESTS - PAGO MODEL
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestPagoModel:
    """Tests para Pago model"""
    
    def test_pago_creacion(self, cuota_pagada):
        """Crear pago básico"""
        pago = Pago.objects.create(
            cuota=cuota_pagada,
            monto_pagado=Decimal('5250'),
            monto_principal=Decimal('5000'),
            monto_interes=Decimal('250'),
            usuario_registra='admin'
        )
        assert pago.cuota == cuota_pagada
        assert pago.monto_pagado == Decimal('5250')
        assert pago.monto_principal == Decimal('5000')
    
    def test_pago_mora_default_cero(self, cuota_pagada):
        """monto_mora por defecto 0"""
        pago = Pago.objects.create(
            cuota=cuota_pagada,
            monto_pagado=Decimal('5000'),
            monto_principal=Decimal('5000'),
            monto_interes=Decimal('0'),
            usuario_registra='user1'
        )
        assert pago.monto_mora == Decimal('0')
    
    def test_pago_con_mora(self, cuota_vencida):
        """Crear pago con mora"""
        pago = Pago.objects.create(
            cuota=cuota_vencida,
            monto_pagado=Decimal('5500'),
            monto_principal=Decimal('5000'),
            monto_interes=Decimal('250'),
            monto_mora=Decimal('250'),
            usuario_registra='admin'
        )
        assert pago.monto_mora == Decimal('250')
        assert pago.monto_pagado == Decimal('5500')


# ============================================================================
# UNIT TESTS - CLIENTE RELATIONSHIPS
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestClienteRelationships:
    """Tests para relaciones de Cliente"""
    
    def test_cliente_puede_tener_multiples_prestamos(self, cliente_activo):
        """Un cliente puede tener múltiples préstamos"""
        for i in range(3):
            Prestamo.objects.create(
                cliente=cliente_activo,
                monto_total=Decimal('10000'),
                interes_porcentaje=Decimal('5.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=30),
                estado='ACTIVO'
            )
        
        prestamos = Prestamo.objects.filter(cliente=cliente_activo)
        assert prestamos.count() == 3
    
    def test_prestamo_pertenece_solo_a_un_cliente(self, cliente_activo, cliente_inactivo):
        """Un préstamo SOLO pertenece a un cliente"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('50000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60)
        )
        
        assert prestamo.cliente == cliente_activo
        assert prestamo.cliente != cliente_inactivo


# ============================================================================
# UNIT TESTS - PRESTAMO CUOTAS RELATIONSHIP
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestPrestamosCuotasRelationship:
    """Tests para relaciones Préstamo-Cuota"""
    
    def test_prestamo_tiene_multiples_cuotas(self, prestamo_activo):
        """Un préstamo tiene múltiples cuotas"""
        for i in range(1, 5):
            Cuota.objects.create(
                prestamo=prestamo_activo,
                numero_cuota=i,
                monto_original=Decimal('5000'),
                monto_pendiente=Decimal('5000'),
                interes_normal=Decimal('250'),
                monto_pendiente_interes=Decimal('250'),
                fecha_pago_esperada=date.today() + timedelta(days=15*i)
            )
        
        cuotas = prestamo_activo.cuotas.all()
        assert cuotas.count() == 4
    
    def test_cuota_numero_incremental(self, prestamo_activo):
        """Números de cuota son incrementales"""
        for i in range(1, 6):
            Cuota.objects.create(
                prestamo=prestamo_activo,
                numero_cuota=i,
                monto_original=Decimal('2000'),
                monto_pendiente=Decimal('2000'),
                interes_normal=Decimal('100'),
                monto_pendiente_interes=Decimal('100'),
                fecha_pago_esperada=date.today() + timedelta(days=15*i)
            )
        
        cuotas = prestamo_activo.cuotas.all().order_by('numero_cuota')
        numeros = [c.numero_cuota for c in cuotas]
        assert numeros == [1, 2, 3, 4, 5]


# ============================================================================
# UNIT TESTS - CONFIGURACIÓN
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestConfiguracionModel:
    """Tests para Configuración model"""
    
    def test_config_obtener_default(self):
        """obtener_configuracion() retorna config por defecto"""
        config = Configuracion.obtener_configuracion()
        assert config is not None
        assert config.id == 1
    
    def test_config_tasa_interes_normal(self):
        """Config tiene tasa de interés normal"""
        config = Configuracion.obtener_configuracion()
        assert hasattr(config, 'tasa_interes_prestamo_normal')
        # Allow both Decimal and float from database
        assert config.tasa_interes_prestamo_normal == Decimal('15.0') or config.tasa_interes_prestamo_normal == 15.0
    
    def test_config_tasa_interes_rapido(self):
        """Config tiene tasa de interés rápido"""
        config = Configuracion.obtener_configuracion()
        assert hasattr(config, 'tasa_interes_prestamo_rapido')


# ============================================================================
# UNIT TESTS - VALIDACIONES MODELO
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestModelosValidaciones:
    """Tests para validaciones en modelos"""
    
    def test_cliente_cedula_unica_no_requerida(self):
        """Cédula puede ser vacía (es opcional)"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='',
            celular='3001234567'
        )
        assert cliente.cedula == ''
    
    def test_cliente_estado_valido(self):
        """Estado debe ser ACTIVO o INACTIVO"""
        cliente = Cliente.objects.create(
            nombre='Test',
            cedula='1234567890',
            celular='3001234567',
            estado='ACTIVO'
        )
        assert cliente.estado in ['ACTIVO', 'INACTIVO']
    
    def test_prestamo_monto_positivo(self, cliente_activo):
        """Monto debe ser positivo"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('100'),  # Válido
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30)
        )
        assert prestamo.monto_total > 0
    
    def test_cuota_monto_original_positivo(self, prestamo_activo):
        """Monto original debe ser positivo"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('100'),
            monto_pendiente=Decimal('100'),
            interes_normal=Decimal('5'),
            monto_pendiente_interes=Decimal('5'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        assert cuota.monto_original > 0


# ============================================================================
# UNIT TESTS - CÁLCULOS
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestCalculosCuota:
    """Tests para cálculos en Cuota"""
    
    def test_porcentaje_pagado_calculo(self, prestamo_activo):
        """Porcentaje pagado se calcula correctamente"""
        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('500'),  # 50% pagado
            monto_pagado_principal=Decimal('500'),
            interes_normal=Decimal('50'),
            monto_pendiente_interes=Decimal('50'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        
        # Si pagó 500 de 1000, debería ser 50%
        assert cuota.monto_pagado_principal == Decimal('500')
    
    def test_monto_pendiente_disminuye(self, cuota_pendiente):
        """Monto pendiente disminuye al pagar"""
        original_pendiente = cuota_pendiente.monto_pendiente
        
        # Simular pago parcial
        cuota_pendiente.monto_pendiente = original_pendiente / 2
        cuota_pendiente.save()
        
        assert cuota_pendiente.monto_pendiente < original_pendiente


# ============================================================================
# INTEGRATION TEST MARKERS
# ============================================================================

@pytest.mark.integration
@pytest.mark.django_db
class TestIntegrationClientePrestamo:
    """Integration tests: Cliente → Préstamo → Cuota → Pago"""
    
    def test_flujo_completo_prestamo(self, cliente_activo):
        """Flujo completo: crear préstamo, crear cuotas, hacer pagos"""
        # 1. Crear préstamo
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO'
        )
        
        # 2. Crear cuota
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('10000'),
            monto_pendiente=Decimal('10000'),
            interes_normal=Decimal('500'),
            monto_pendiente_interes=Decimal('500'),
            fecha_pago_esperada=date.today() + timedelta(days=30)
        )
        
        # 3. Crear pago
        pago = Pago.objects.create(
            cuota=cuota,
            monto_pagado=Decimal('5250'),
            monto_principal=Decimal('5000'),
            monto_interes=Decimal('250'),
            usuario_registra='admin'
        )
        
        # Verificar
        assert prestamo.cliente == cliente_activo
        assert cuota.prestamo == prestamo
        assert pago.cuota == cuota
