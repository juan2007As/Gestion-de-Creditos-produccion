"""
CRÍTICA #7: TESTS - TRANSACTION INTEGRITY
Pruebas para garantizar atomicidad de operaciones transaccionales
"""

import pytest
from django.db import transaction, IntegrityError
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

from mi_app.models import Cliente, Prestamo, Cuota, Pago, AuditLog
from mi_app.utilities.transaction_integrity import (
    registrar_pago_atomico, actualizar_estado_cuota_atomica,
    actualizar_estado_prestamo_atomica, eliminar_pago_atomico,
    PaymentError, CuotaError, validate_payment_amount
)


@pytest.mark.django_db
class TestPaymentValidation:
    """Tests para validación de montos de pago"""
    
    def test_validate_payment_amount_positivo(self):
        """Valida que monto positivo sea aceptado"""
        monto = validate_payment_amount(Decimal('100.00'), Decimal('500.00'))
        assert monto == Decimal('100.00')
    
    def test_validate_payment_amount_nulo(self):
        """Valida que monto nulo lance error"""
        with pytest.raises(PaymentError):
            validate_payment_amount(None, Decimal('500.00'))
    
    def test_validate_payment_amount_negativo(self):
        """Valida que monto negativo lance error"""
        with pytest.raises(PaymentError):
            validate_payment_amount(Decimal('-100.00'), Decimal('500.00'))
    
    def test_validate_payment_amount_cero(self):
        """Valida que monto cero lance error"""
        with pytest.raises(PaymentError):
            validate_payment_amount(Decimal('0'), Decimal('500.00'))
    
    def test_validate_payment_amount_excede_pendiente(self):
        """Valida que monto mayor que pendiente lance error"""
        with pytest.raises(PaymentError):
            validate_payment_amount(Decimal('600.00'), Decimal('500.00'))
    
    def test_validate_payment_amount_invalido(self):
        """Valida que monto no numérico lance error"""
        with pytest.raises(PaymentError):
            validate_payment_amount("abc", Decimal('500.00'))


@pytest.mark.django_db
class TestRegistrarPagoAtomico:
    """Tests para registrar pago de forma atómica"""
    
    @pytest.fixture
    def setup_data(self, db):
        """Setup: Cliente + Préstamo + Cuota + Usuario"""
        from datetime import date, timedelta
        
        usuario = User.objects.create_user(username='admin', password='pass')
        cliente = Cliente.objects.create(
            nombre='Test Cliente',
            cedula='123456',
            estado='ACTIVO'
        )
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('1000.00'),
            interes_porcentaje=Decimal('2.5'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=150),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('200.00'),
            monto_pendiente=Decimal('200.00'),
            interes_normal=Decimal('5.00'),
            fecha_pago_esperada=date.today() + timedelta(days=30)
        )
        return {
            'usuario': usuario,
            'cliente': cliente,
            'prestamo': prestamo,
            'cuota': cuota
        }
    
    def test_registrar_pago_exitoso(self, setup_data):
        """Prueba registro exitoso de pago"""
        cuota = setup_data['cuota']
        usuario = setup_data['usuario']
        
        pago = registrar_pago_atomico(
            cuota=cuota,
            monto_pago=Decimal('100.00'),
            usuario=usuario,
            notas='Test pago'
        )
        
        # Verificar pago creado
        assert pago.id is not None
        assert pago.monto_pagado == Decimal('100.00')
        assert pago.cuota == cuota
        
        # Verificar cuota actualizada
        cuota.refresh_from_db()
        assert cuota.monto_pendiente == Decimal('100.00')
        assert cuota.monto_pagado_principal == Decimal('100.00')
        assert cuota.pagado == False  # Aún no está 100% pagada
        
        # Verificar auditoría creada
        logs = AuditLog.objects.filter(modelo='Pago', objeto_id=pago.id)
        assert logs.count() == 1
        assert logs.first().accion == 'CREATE'
    
    def test_registrar_pago_completa_cuota(self, setup_data):
        """Prueba que pago completo marca cuota como pagada"""
        cuota = setup_data['cuota']
        usuario = setup_data['usuario']
        
        pago = registrar_pago_atomico(
            cuota=cuota,
            monto_pago=cuota.monto_pendiente,
            usuario=usuario
        )
        
        # Verificar cuota completamente pagada
        cuota.refresh_from_db()
        assert cuota.monto_pendiente == Decimal('0')
        assert cuota.pagado == True
        assert cuota.fecha_pago_real is not None
    
    def test_registrar_pago_cuota_pagada_falla(self, setup_data):
        """Prueba que pagar cuota ya pagada lanza error"""
        cuota = setup_data['cuota']
        usuario = setup_data['usuario']
        
        # Marcar cuota como pagada
        cuota.pagado = True
        cuota.save()
        
        # Intentar pagar debe fallar
        with pytest.raises(CuotaError):
            registrar_pago_atomico(
                cuota=cuota,
                monto_pago=Decimal('100.00'),
                usuario=usuario
            )
    
    def test_registrar_pago_monto_excedido_falla(self, setup_data):
        """Prueba que pagar más de lo pendiente falla"""
        cuota = setup_data['cuota']
        usuario = setup_data['usuario']
        
        with pytest.raises(PaymentError):
            registrar_pago_atomico(
                cuota=cuota,
                monto_pago=Decimal('300.00'),  # Cuota es 200
                usuario=usuario
            )
        
        # Verificar que nada cambió (rollback)
        cuota.refresh_from_db()
        assert cuota.monto_pendiente == cuota.monto_original
        assert Pago.objects.filter(cuota=cuota).count() == 0
    
    def test_registrar_pago_actualiza_prestamo_completado(self, setup_data):
        """Prueba que pagar todas las cuotas marca préstamo como COMPLETADO"""
        prestamo = setup_data['prestamo']
        usuario = setup_data['usuario']
        
        # Obtener la única cuota
        cuota = prestamo.cuotas.first()
        
        # Pagar completamente
        registrar_pago_atomico(
            cuota=cuota,
            monto_pago=cuota.monto_pendiente,
            usuario=usuario
        )
        
        # Verificar préstamo marcado como COMPLETADO
        prestamo.refresh_from_db()
        assert prestamo.estado == 'COMPLETADO'
    
    def test_registrar_pago_atomicidad_sin_cambios_en_error(self, setup_data):
        """Prueba que en error todo se revierte (atomicidad)"""
        cuota = setup_data['cuota']
        usuario = setup_data['usuario']
        
        # Intentar pago con error
        try:
            registrar_pago_atomico(
                cuota=cuota,
                monto_pago=cuota.monto_pendiente + Decimal('1'),  # Excede
                usuario=usuario
            )
        except PaymentError:
            pass
        
        # Verificar que BD está sin cambios
        assert Pago.objects.filter(cuota=cuota).count() == 0
        cuota.refresh_from_db()
        assert cuota.monto_pendiente == cuota.monto_original
        assert cuota.monto_pagado_principal == Decimal('0')


@pytest.mark.django_db
class TestEliminarPagoAtomico:
    """Tests para eliminación de pago con rollback"""
    
    @pytest.fixture
    def setup_pago(self, db):
        """Setup: Crear pago registrado"""
        from datetime import timedelta
        usuario = User.objects.create_user(username='admin', password='pass')
        cliente = Cliente.objects.create(nombre='Test', cedula='123456', estado='ACTIVO')
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('1000'),
            interes_porcentaje=Decimal('2.5'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=150),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('200'),
            monto_pendiente=Decimal('200'),
            interes_normal=Decimal('5'),
            fecha_pago_esperada=date.today() + timedelta(days=30)
        )
        
        # Registrar pago
        pago = registrar_pago_atomico(
            cuota=cuota,
            monto_pago=Decimal('100'),
            usuario=usuario
        )
        
        return {'pago': pago, 'cuota': cuota, 'usuario': usuario}
    
    def test_eliminar_pago_revierte_cambios(self, setup_pago):
        """Prueba que eliminar pago revierte cambios en cuota"""
        pago = setup_pago['pago']
        cuota_id = setup_pago['cuota'].id
        usuario = setup_pago['usuario']
        
        # Estado antes de eliminar
        cuota_antes = Cuota.objects.get(id=cuota_id)
        assert cuota_antes.monto_pendiente == Decimal('100')  # 200 - 100
        
        # Eliminar pago
        eliminar_pago_atomico(pago, usuario)
        
        # Verificar que cuota fue revertida
        cuota_despues = Cuota.objects.get(id=cuota_id)
        assert cuota_despues.monto_pendiente == Decimal('200')  # Vuelve a 200
        assert cuota_despues.monto_pagado_principal == Decimal('0')
        
        # Verificar que pago fue eliminado
        assert Pago.objects.filter(id=pago.id).count() == 0
        
        # Verificar auditoría de eliminación
        logs = AuditLog.objects.filter(accion='DELETE', modelo='Pago')
        assert logs.count() == 1


@pytest.mark.django_db
class TestRaceConditionProtection:
    """Tests para protección contra race conditions"""
    
    @pytest.fixture
    def setup_cuota(self, db):
        """Setup cuota para race condition tests"""
        from datetime import timedelta
        usuario = User.objects.create_user(username='admin', password='pass')
        cliente = Cliente.objects.create(nombre='Test', cedula='123456', estado='ACTIVO')
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('1000'),
            interes_porcentaje=Decimal('2.5'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=150),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('200'),
            monto_pendiente=Decimal('200'),
            interes_normal=Decimal('5'),
            fecha_pago_esperada=date.today() + timedelta(days=30)
        )
        
        return {'usuario': usuario, 'cuota': cuota}
    
    def test_select_for_update_evita_condicion_carrera(self, setup_cuota):
        """Prueba que select_for_update previene race conditions"""
        cuota = setup_cuota['cuota']
        usuario = setup_cuota['usuario']
        
        # Usar select_for_update para obtener lock
        with transaction.atomic():
            cuota_locked = Cuota.objects.select_for_update().get(pk=cuota.pk)
            
            # Simular operación con delay
            import time
            time.sleep(0.01)
            
            # Pago debe funcionar porque tenemos el lock
            cuota_locked.monto_pendiente = Decimal('100')
            cuota_locked.save()
        
        # Verificar cambios
        cuota.refresh_from_db()
        assert cuota.monto_pendiente == Decimal('100')


@pytest.mark.django_db
@pytest.mark.integration
class TestTransactionIntegration:
    """Tests de integración para transacciones completas"""
    
    def test_flujo_pago_completo(self, db):
        """Prueba flujo completo: crear préstamo, cuotas, registrar pagos"""
        from datetime import timedelta
        
        # Setup
        usuario = User.objects.create_user(username='admin', password='pass')
        cliente = Cliente.objects.create(
            nombre='Cliente Pago',
            cedula='999999',
            estado='ACTIVO'
        )
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('500'),
            interes_porcentaje=Decimal('2.5'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        cuotas = []
        for i in range(1, 3):
            cuota = Cuota.objects.create(
                prestamo=prestamo,
                numero_cuota=i,
                monto_original=Decimal('250'),
                monto_pendiente=Decimal('250'),
                interes_normal=Decimal('6.25'),
                fecha_pago_esperada=date.today() + timedelta(days=30*i)
            )
            cuotas.append(cuota)
        
        # Registrar pagos
        for cuota in cuotas:
            registrar_pago_atomico(
                cuota=cuota,
                monto_pago=cuota.monto_pendiente,
                usuario=usuario
            )
        
        # Verificar estado final
        prestamo.refresh_from_db()
        assert prestamo.estado == 'COMPLETADO'
        
        for cuota in cuotas:
            cuota.refresh_from_db()
            assert cuota.pagado == True
            assert cuota.monto_pendiente == Decimal('0')
        
        # Verificar pagos creados
        assert Pago.objects.filter(cuota__prestamo=prestamo).count() == 2
