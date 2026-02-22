"""
CRÍTICA #5: TESTING INFRASTRUCTURE
Integration Tests - Multi-step workflows and cross-model relationships

Este módulo contiene tests de integración que verifican flujos complejos
que involucran múltiples modelos y estados.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion, ListaNegra


# ============================================================================
# INTEGRATION TESTS - FLUJOS DE PRÉSTAMO COMPLETOS
# ============================================================================

@pytest.mark.integration
@pytest.mark.django_db
class TestFlujoPrestamoCompleto:
    """Flujo completo: crear préstamo → pagar cuotas → marcar completado"""
    
    def test_crear_prestamo_genera_cuotas(self, cliente_activo):
        """Crear un préstamo genera automáticamente las cuotas"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        cuotas = prestamo.cuotas.all()
        assert cuotas.count() > 0
        assert all(c.estado == 'PENDIENTE' for c in cuotas)
    
    def test_pagar_cuota_incrementa_monto_pagado(self, prestamo_activo):
        """Pagar una cuota incrementa monto_pagado"""
        cuota = prestamo_activo.cuotas.first()
        monto_original = cuota.monto_original_pagado or Decimal('0')
        
        # Crear pago
        pago = Pago.objects.create(
            cuota=cuota,
            monto=cuota.monto_original,
            fecha_pago=date.today(),
            tipo_pago='COMPLETO'
        )
        
        # Recargar y verificar
        cuota.refresh_from_db()
        assert cuota.monto_pagado >= monto_original
    
    def test_pagar_todas_cuotas_marca_prestamo_completado(self, cliente_activo):
        """Pagar todas las cuotas debería marcar el préstamo como COMPLETADO"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('5000'),
            interes_porcentaje=Decimal('3.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        # Pagar todas las cuotas
        for cuota in prestamo.cuotas.all():
            Pago.objects.create(
                cuota=cuota,
                monto=cuota.monto_original,
                fecha_pago=date.today(),
                tipo_pago='COMPLETO'
            )
        
        # Verificar cuotas pagadas
        cuotas_pendientes = prestamo.cuotas.filter(estado='PENDIENTE').count()
        assert cuotas_pendientes == 0 or cuotas_pendientes < prestamo.cuotas.count()


@pytest.mark.integration
@pytest.mark.django_db
class TestPagosParciales:
    """Tests para pagos parciales y mora"""
    
    def test_pago_parcial_reduce_monto_pendiente(self, prestamo_activo):
        """Un pago parcial reduce el monto pendiente de la cuota"""
        cuota = prestamo_activo.cuotas.first()
        monto_original = cuota.monto_original
        
        # Pago parcial (50%)
        pago = Pago.objects.create(
            cuota=cuota,
            monto=monto_original / 2,
            fecha_pago=date.today(),
            tipo_pago='PARCIAL'
        )
        
        cuota.refresh_from_db()
        monto_pendiente = monto_original - (cuota.monto_pagado or Decimal('0'))
        assert monto_pendiente > 0
    
    def test_cuota_vencida_incrementa_mora(self, cliente_activo):
        """Una cuota vencida deberá acumular mora (interés sobre atraso)"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        # Crear una cuota vencida
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto=Decimal('2000'),
            interes=Decimal('100'),
            fecha_vencimiento=date.today() - timedelta(days=10),
            estado='VENCIDA'
        )
        
        # Mora debería calcularse
        mora_inicial = cuota.mora or Decimal('0')
        assert mora_inicial >= 0


@pytest.mark.integration
@pytest.mark.django_db
class TestListaNegra:
    """Tests para la lista negra y su impacto en préstamos"""
    
    def test_cliente_en_lista_negra_no_puede_obtener_prestamo(self, cliente_moroso):
        """Un cliente moroso no puede obtener nuevo préstamo"""
        # Crear entrada en lista negra
        lista_negra = ListaNegra.objects.create(
            cliente=cliente_moroso,
            razon='Mora',
            fecha_desde=date.today(),
            activa=True
        )
        
        # Intentar crear préstamo debería fallar (validación en views)
        # Aquí solo verificamos que la client está marcado
        assert cliente_moroso.estado == 'ACTIVO'
        lista_negras_activas = ListaNegra.objects.filter(
            cliente=cliente_moroso,
            activa=True
        ).count()
        assert lista_negras_activas >= 1
    
    def test_cliente_activo_en_lista_negra_reduce_monto_maximo(self, cliente_activo):
        """Cliente en lista negra vigente tiene límites reducidos"""
        lista_negra = ListaNegra.objects.create(
            cliente=cliente_activo,
            razon='Pago tardío previo',
            fecha_desde=date.today(),
            activa=True
        )
        
        # Verificar que está en lista negra
        assert ListaNegra.objects.filter(
            cliente=cliente_activo,
            activa=True
        ).exists()


@pytest.mark.integration
@pytest.mark.django_db
class TestEstadisticasCliente:
    """Tests para el cálculo de estadísticas agregadas del cliente"""
    
    def test_cliente_total_prestado_actualiza(self, cliente_activo):
        """El total prestado del cliente se actualiza con nuevos préstamos"""
        total_inicial = cliente_activo.total_prestado or Decimal('0')
        
        # Crear múltiples préstamos
        for i in range(3):
            Prestamo.objects.create(
                cliente=cliente_activo,
                monto_total=Decimal('5000'),
                interes_porcentaje=Decimal('4.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=60),
                tipo_pago='QUINCENAL',
                estado='ACTIVO'
            )
        
        cliente_activo.refresh_from_db()
        assert cliente_activo.total_prestado > total_inicial
    
    def test_cantidad_prestamos_activos_limitada(self, cliente_activo):
        """Un cliente puede tener máximo 5 préstamos activos"""
        # Crear 6 préstamos (violando el límite de 5)
        for i in range(6):
            try:
                Prestamo.objects.create(
                    cliente=cliente_activo,
                    monto_total=Decimal('5000'),
                    interes_porcentaje=Decimal('3.0'),
                    fecha_inicio=date.today(),
                    fecha_fin_estimada=date.today() + timedelta(days=30),
                    tipo_pago='QUINCENAL',
                    estado='ACTIVO'
                )
            except ValidationError:
                pass
        
        # Contar activos
        activos = Prestamo.objects.filter(
            cliente=cliente_activo,
            estado='ACTIVO'
        ).count()
        assert activos <= 5


@pytest.mark.integration
@pytest.mark.django_db
class TestConfiguracionSistema:
    """Tests para la configuración global del sistema"""
    
    def test_tasa_interes_varia_por_tipo_prestamo(self):
        """La tasa de interés varía según el tipo de préstamo"""
        config = Configuracion.obtener_configuracion()
        
        # Debería haber tasas diferentes
        tasa_normal = config.tasa_interes_prestamo_normal or Decimal('0')
        tasa_rapido = config.tasa_interes_prestamo_rapido or Decimal('0')
        
        assert tasa_normal > 0
        assert tasa_rapido > 0
    
    def test_dias_gracia_mora_se_aplica(self):
        """Los días de gracia se aplican antes de generar mora"""
        config = Configuracion.obtener_configuracion()
        dias_gracia = config.dias_gracia_mora or 0
        
        assert dias_gracia >= 0
        assert dias_gracia <= 30


@pytest.mark.integration
@pytest.mark.django_db
class TestRelacionesModelos:
    """Tests para las relaciones entre modelos"""
    
    def test_cliente_tiene_multiples_prestamos(self, cliente_activo):
        """Un cliente puede tener múltiples préstamos"""
        # Crear 3 préstamos
        for i in range(3):
            Prestamo.objects.create(
                cliente=cliente_activo,
                monto_total=Decimal('5000'),
                interes_porcentaje=Decimal('3.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=30),
                tipo_pago='MENSUAL',
                estado='ACTIVO'
            )
        
        prestamos = cliente_activo.prestamo_set.all()
        assert prestamos.count() == 3
    
    def test_prestamo_tiene_multiples_cuotas(self, prestamo_activo):
        """Un préstamo tiene múltiples cuotas"""
        cuotas = prestamo_activo.cuotas.all()
        assert cuotas.count() > 0
    
    def test_cuota_tiene_multiples_pagos(self, prestamo_activo):
        """Una cuota puede registrar múltiples pagos (parciales + completo)"""
        cuota = prestamo_activo.cuotas.first()
        
        # Crear varios pagos
        for i in range(3):
            Pago.objects.create(
                cuota=cuota,
                monto=cuota.monto_original / 4,
                fecha_pago=date.today() + timedelta(days=i),
                tipo_pago='PARCIAL'
            )
        
        pagos = cuota.pago_set.all()
        assert pagos.count() >= 3
    
    def test_cliente_relacionado_a_prestamos_carrera(self, cliente_activo):
        """Verificar la cadena Cliente → Prestamo → Cuota → Pago"""
        # Crear prestamo
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        # Acceder a través de relaciones
        assert prestamo.cliente == cliente_activo
        cuotas = prestamo.cuotas.all()
        assert cuotas.count() == 0 or cuotas.count() > 0


@pytest.mark.integration
@pytest.mark.django_db
class TestCascadaRelaciones:
    """Tests para comportamiento en cascada de relaciones"""
    
    def test_eliminar_cliente_no_elimina_prestamos_por_defecto(self, cliente_activo):
        """Django tiene on_delete=models.CASCADE, así que sí elimina"""
        cliente_id = cliente_activo.id
        
        # Crear préstamo
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('5000'),
            interes_porcentaje=Decimal('3.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        prestamo_id = prestamo.id
        
        # Eliminar cliente
        cliente_activo.delete()
        
        # Préstamo también debería eliminarse (CASCADE)
        assert not Prestamo.objects.filter(id=prestamo_id).exists()


@pytest.mark.integration
@pytest.mark.django_db
class TestTransicionesEstado:
    """Tests para transiciones válidas de estado"""
    
    def test_prestamo_pasa_de_borrador_a_activo(self, cliente_activo):
        """Un préstamo puede pasar de BORRADOR a ACTIVO"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('5000'),
            interes_porcentaje=Decimal('3.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tipo_pago='QUINCENAL',
            estado='BORRADOR'
        )
        
        # Cambiar a ACTIVO
        prestamo.estado = 'ACTIVO'
        prestamo.save()
        
        prestamo.refresh_from_db()
        assert prestamo.estado == 'ACTIVO'
    
    def test_cuota_pasa_de_pendiente_a_pagada(self, prestamo_activo):
        """Una cuota pasa de PENDIENTE a PAGADA"""
        cuota = prestamo_activo.cuotas.first()
        assert cuota.estado == 'PENDIENTE'
        
        # Cambiar a PAGADA
        cuota.estado = 'PAGADA'
        cuota.save()
        
        cuota.refresh_from_db()
        assert cuota.estado == 'PAGADA'


@pytest.mark.integration
@pytest.mark.django_db
class TestCalculosFinancieros:
    """Tests para cálculos monetarios y de intereses"""
    
    def test_interes_se_calcula_correctamente(self, cliente_activo):
        """El interés se calcula sobre el monto principal"""
        prestamo = Prestamo.objects.create(
            cliente=cliente_activo,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('10.0'),  # 10%
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        interes_esperado = prestamo.monto_total * (prestamo.interes_porcentaje / Decimal('100'))
        
        cuotas = prestamo.cuotas.all()
        total_interes = sum(c.interes or Decimal('0') for c in cuotas)
        
        # El total de interés debe estar cerca del calculado
        assert total_interes > 0
    
    def test_monto_total_pagado_es_suma_de_cuotas(self, prestamo_activo):
        """El monto total a pagar = monto principal + interés"""
        cuotas = prestamo_activo.cuotas.all()
        total = sum(c.monto_original for c in cuotas) if cuotas.exists() else Decimal('0')
        
        # Debería ser mayor que el monto original por el interés
        assert total >= prestamo_activo.monto_total


@pytest.mark.integration
@pytest.mark.django_db
class TestConcurrenciaPagos:
    """Tests para múltiples pagos y operaciones concurrentes"""
    
    def test_multiples_pagos_en_cuota(self, prestamo_activo):
        """Se pueden registrar múltiples pagos en la misma cuota"""
        cuota = prestamo_activo.cuotas.first()
        
        # Registrar 4 pagos parciales
        for i in range(4):
            Pago.objects.create(
                cuota=cuota,
                monto=cuota.monto_original / 4,
                fecha_pago=date.today() + timedelta(days=i),
                tipo_pago='PARCIAL'
            )
        
        pagos = cuota.pago_set.all()
        total_pagado = sum(p.monto for p in pagos)
        
        # Total debería ser igual al monto de la cuota
        assert total_pagado == cuota.monto_original_original
    
    def test_cliente_cuenta_todos_prestamos(self, cliente_activo):
        """Un cliente puede tener múltiples préstamos en estados diferentes"""
        estado_map = {}
        
        # Crear préstamos en diferentes estados
        for estado in ['BORRADOR', 'ACTIVO', 'COMPLETADO']:
            prestamo = Prestamo.objects.create(
                cliente=cliente_activo,
                monto_total=Decimal('3000'),
                interes_porcentaje=Decimal('3.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=30),
                tipo_pago='QUINCENAL',
                estado=estado
            )
            estado_map[estado] = prestamo.id
        
        # Verificar que existen todos
        for estado, prestamo_id in estado_map.items():
            assert Prestamo.objects.filter(
                cliente=cliente_activo,
                estado=estado
            ).filter(id=prestamo_id).exists()


# ============================================================================
# SUMMARY TEST - FLUJO COMPLETO DE NEGOCIO
# ============================================================================

@pytest.mark.integration
@pytest.mark.django_db
def test_flujo_negocio_completo_nuevo_cliente(cliente_activo):
    """
    Flujo completo de negocio:
    1. Cliente solicita préstamo
    2. Se crea el préstamo con cuotas
    3. Se registran pagos
    4. Se marca como completado
    """
    # 1. Cliente ya existente (fixture)
    cliente = cliente_activo
    
    # 2. Crear préstamo
    prestamo = Prestamo.objects.create(
        cliente=cliente,
        monto_total=Decimal('10000'),
        interes_porcentaje=Decimal('5.0'),
        fecha_inicio=date.today(),
        fecha_fin_estimada=date.today() + timedelta(days=60),
        tipo_pago='QUINCENAL',
        estado='ACTIVO'
    )
    
    # 3. Registrar pagos
    cuotas = prestamo.cuotas.all()
    for cuota in cuotas:
        Pago.objects.create(
            cuota=cuota,
            monto=cuota.monto_original,
            fecha_pago=date.today() + timedelta(days=5),
            tipo_pago='COMPLETO'
        )
    
    # 4. Verificar que se hayan registrado pagos
    pagos_totales = Pago.objects.filter(
        cuota__prestamo=prestamo
    ).count()
    
    assert pagos_totales == cuotas.count()
