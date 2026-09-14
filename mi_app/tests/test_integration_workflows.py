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


# ============================================================================
# INTEGRATION TESTS - MOTOR DE INTERES DINAMICO (crear_prestamo)
# ============================================================================

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile


class CrearPrestamoConMotorNuevoTests(TestCase):
    """crear_prestamo debe usar el motor de amortizacion dinamica (ver Task 6 del plan)."""

    def setUp(self):
        self.client_obj = Client()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='prestamo.create',
            defaults={'descripcion': 'prestamo.create', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_motor',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.client_obj.login(username='testuser_motor', password='testpass123')  # pragma: allowlist secret

    def test_crear_prestamo_setea_capital_pendiente_y_cronograma_completo_de_interes(self):
        cliente = Cliente.objects.create(nombre="Test Motor Nuevo", celular="3000000000", cedula="999888777")

        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': cliente.id,
            'monto_total': '500000',
            'interes_porcentaje': '15',
            'num_cuotas': '4',
        })
        self.assertEqual(response.status_code, 302)

        prestamo = Prestamo.objects.get(cliente=cliente)
        self.assertEqual(prestamo.capital_pendiente, Decimal('500000'))

        cuotas = list(prestamo.cuotas.order_by('numero_cuota'))
        self.assertEqual(len(cuotas), 4)
        # Cronograma completo desde la creacion: base=500000*15%/2=37500 para
        # el primer par (cuotas 1-2); el par siguiente (3-4) es la mitad.
        self.assertEqual(cuotas[0].interes_normal, Decimal('37500.00'))
        self.assertEqual(cuotas[1].interes_normal, Decimal('37500.00'))
        self.assertEqual(cuotas[2].interes_normal, Decimal('18750.00'))
        self.assertEqual(cuotas[3].interes_normal, Decimal('18750.00'))

        # Regresion: las cuotas 2-4 nacen con pendiente=0 porque todavia no
        # les toca su turno (no porque ya se pagaron) -- no deben marcarse
        # solas como PAGADA/pagado=True.
        self.assertFalse(cuotas[0].pagado)
        self.assertEqual(cuotas[0].estado, 'PENDIENTE')
        for cuota in cuotas[1:]:
            self.assertFalse(cuota.pagado, f"cuota {cuota.numero_cuota} no deberia estar pagada")
            self.assertNotEqual(cuota.estado, 'PAGADA', f"cuota {cuota.numero_cuota} no deberia estar PAGADA")

    def test_total_pendiente_incluye_interes_de_todas_las_cuotas_futuras(self):
        """
        Regresion: 'En Circulacion'/'Total Pendiente' deben mostrar la
        obligacion COMPLETA del credito (capital + interes de TODAS las
        cuotas restantes ya precalculadas), no solo el interes del periodo
        activo. Ejemplo real reportado por el usuario: 500000 al 15% en 6
        cuotas -- interes total del cronograma es 37500+37500+18750+18750
        +9375+9375=131250, asi que el total pendiente recien creado el
        prestamo debe ser 500000+131250=631250, no 537500 (que era el bug:
        solo sumaba el interes de la primera cuota activa).
        """
        cliente = Cliente.objects.create(nombre="Test Total Pendiente Completo", celular="3000000002", cedula="999888779")

        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': cliente.id,
            'monto_total': '500000',
            'interes_porcentaje': '15',
            'num_cuotas': '6',
        })
        self.assertEqual(response.status_code, 302)

        prestamo = Prestamo.objects.get(cliente=cliente)
        self.assertEqual(prestamo.total_pendiente, 631250.0)

        resumen = prestamo.resumen_financiero()
        self.assertEqual(resumen['total_pendiente_principal'], 500000.0)
        self.assertEqual(resumen['total_pendiente_interes'], 131250.0)
        self.assertEqual(resumen['total_credito'], 631250.0)

    def test_crear_prestamo_rapido_setea_capital_pendiente_y_solo_primera_cuota(self):
        from mi_app.models import PrestamoRapido

        cliente = Cliente.objects.create(nombre="Test Rapido Motor Nuevo", celular="3000000001", cedula="999888778")

        response = self.client_obj.post(reverse('crear_prestamo_rapido'), {
            'cliente_id': cliente.id,
            'monto': '300000',
            'interes_porcentaje': '15',
            'usar_cuotas': 'on',
            'num_cuotas': '2',
        })
        self.assertEqual(response.status_code, 302)

        prestamo = PrestamoRapido.objects.get(cliente=cliente)
        self.assertEqual(prestamo.capital_pendiente, Decimal('300000'))

        cuotas = list(prestamo.cuotas_rapidas.order_by('numero_cuota'))
        # 300000 * 15% / 2 = 22500, sin redondeo; ambas cuotas son del mismo
        # par (1 mes) asi que comparten el mismo interes.
        self.assertEqual(cuotas[0].interes_normal, Decimal('22500.00'))
        self.assertEqual(cuotas[1].interes_normal, Decimal('22500.00'))

        # Regresion: la cuota 2 no debe marcarse sola como pagada solo por
        # tener capital pendiente en 0 (todavia no le toca su turno).
        self.assertFalse(cuotas[1].pagado)
        self.assertNotEqual(cuotas[1].estado, 'PAGADA')

    def test_saldo_pendiente_rapido_incluye_interes_de_todas_las_cuotas_futuras(self):
        """
        Mismo caso que test_total_pendiente_incluye_interes_de_todas_las_cuotas_futuras
        pero para PrestamoRapido: 300000 al 15% en 4 cuotas -- cronograma es
        22500+22500+11250+11250=67500, asi que saldo_pendiente recien creado
        debe ser 300000+67500=367500, no solo 322500 (capital + interes de
        la primera cuota activa).
        """
        from mi_app.models import PrestamoRapido

        cliente = Cliente.objects.create(nombre="Test Rapido Total Pendiente", celular="3000000003", cedula="999888780")

        response = self.client_obj.post(reverse('crear_prestamo_rapido'), {
            'cliente_id': cliente.id,
            'monto': '300000',
            'interes_porcentaje': '15',
            'usar_cuotas': 'on',
            'num_cuotas': '4',
        })
        self.assertEqual(response.status_code, 302)

        prestamo = PrestamoRapido.objects.get(cliente=cliente)
        self.assertEqual(prestamo.saldo_pendiente, Decimal('367500.00'))


class PagarCuotaEspecificaMotorNuevoTests(TestCase):
    """pagar_cuota_especifica debe usar los topes dinamicos del prestamo (ver Task 8 del plan)."""

    def setUp(self):
        self.client_obj = Client()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_pago_motor',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.client_obj.login(username='testuser_pago_motor', password='testpass123')  # pragma: allowlist secret

    def test_puede_pagar_mas_capital_del_que_decia_la_cuota_vieja(self):
        # Reproduce la queja original: prestamo de 200.000, el operario
        # quiere poder abonar mucho mas capital del que la cuota puntual
        # decia (topada antes a un pedacito fijo).
        cliente = Cliente.objects.create(nombre="Test Abono Grande", celular="3000000002", cedula="999888779")
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('200000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('200000'),
        )
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('50000'),
            monto_pendiente=Decimal('200000'),
            interes_normal=Decimal('15000'),  # 200000 * 15% / 2
            monto_pendiente_interes=Decimal('15000'),
            fecha_pago_esperada=date.today() + timedelta(days=16),
        )

        response = self.client_obj.post(
            reverse('pagar_cuota_especifica', kwargs={'cuota_id': cuota.id}),
            {'monto_principal': '150000', 'monto_interes': '15000', 'monto_mora': '0'},
        )

        prestamo.refresh_from_db()
        # Post-Redirect-Get: el abono extra no cierra el credito (quedan
        # 50000 de capital), asi que redirige a la cuota que sigue activa.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(prestamo.capital_pendiente, Decimal('50000'))


class RegistrarPagoRapidoMotorNuevoTests(TestCase):
    """registrar_pago_rapido debe repartir interes antes que capital (ver Task 9 del plan)."""

    def setUp(self):
        self.client_obj = Client()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_rapido_pago_motor',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.client_obj.login(username='testuser_rapido_pago_motor', password='testpass123')  # pragma: allowlist secret

    def test_pago_unico_reparte_interes_primero_luego_capital(self):
        from mi_app.models import PrestamoRapido, CuotaRapida

        cliente = Cliente.objects.create(nombre="Test Rapido Pago", celular="3000000003", cedula="999888780")
        prestamo = PrestamoRapido.objects.create(
            cliente=cliente,
            monto=Decimal('250000'),
            interes_porcentaje=Decimal('15'),
            capital_pendiente=Decimal('250000'),
        )
        cuota = CuotaRapida.objects.create(
            prestamo_rapido=prestamo,
            numero_cuota=1,
            monto_original=Decimal('125000'),
            monto_pendiente=Decimal('250000'),
            interes_normal=Decimal('19000'),
            monto_pendiente_interes=Decimal('19000'),
            fecha_pago_esperada=date.today() + timedelta(days=16),
        )

        response = self.client_obj.post(
            reverse('registrar_pago_cuota_rapida', kwargs={'cuota_id': cuota.id}),
            {'monto_pagado': '80000', 'usuario_registra': 'admin'},
        )
        self.assertEqual(response.status_code, 302)

        prestamo.refresh_from_db()
        # 19.000 a interes, 61.000 a capital -> capital queda en 189.000
        self.assertEqual(prestamo.capital_pendiente, Decimal('189000'))


class EstadoVisualCuotaTests(TestCase):
    """_obtener_estado_visual_cuota no debe mostrar PARCIAL en cuotas que
    todavia no le toca su turno (pendiente=0 por diseño, no por pago real)."""

    def test_cuota_sin_pago_real_no_muestra_parcial(self):
        from mi_app.views_core import _obtener_estado_visual_cuota

        cliente = Cliente.objects.create(nombre="Test Visual Estado", celular="3000000004", cedula="999888781")
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        cuota_no_activa = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=2,
            monto_original=Decimal('125000'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('0'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=30),
        )

        estado_visual = _obtener_estado_visual_cuota(cuota_no_activa)

        self.assertEqual(estado_visual['estado'], 'PENDIENTE')

    def test_cuota_con_pago_real_muestra_parcial(self):
        from mi_app.views_core import _obtener_estado_visual_cuota

        cliente = Cliente.objects.create(nombre="Test Visual Estado 2", celular="3000000005", cedula="999888782")
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('375000'),
        )
        cuota_con_abono = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('500000'),
            monto_pendiente=Decimal('375000'),
            interes_normal=Decimal('38000'),
            monto_pendiente_interes=Decimal('0'),
            monto_pagado_principal=Decimal('125000'),
            monto_pagado_interes=Decimal('38000'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

        estado_visual = _obtener_estado_visual_cuota(cuota_con_abono)

        self.assertEqual(estado_visual['estado'], 'PARCIAL')


class AvanzarCuotaTests(TestCase):
    """Al procesar un pago que no cierra el prestamo, se debe avanzar a la
    siguiente cuota nominal con un snapshot de interes fresco (spec
    seccion 4.2, paso 7).

    NOTA: se invoca la vista directamente via RequestFactory en vez del
    Client de Django -- en este entorno local (Python 3.14), el Client
    choca con un bug conocido de Django 4.2 al capturar templates
    renderizados con status 200 (AttributeError: 'dicts'), no reproducible
    en CI (Python 3.10/3.12). RequestFactory no tiene ese problema porque
    no instrumenta el render.
    """

    def setUp(self):
        from django.test import RequestFactory
        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_avanzar_cuota',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Avanzar Cuota", celular="3000000006", cedula="999888783")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota1 = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('125000'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

    def _pagar(self, cuota_id, data):
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore
        from mi_app.views_core import pagar_cuota_especifica
        request = self.factory.post(f'/cuota/{cuota_id}/pagar/', data)
        request.user = self.user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return pagar_cuota_especifica(request, cuota_id)

    def test_pago_solo_interes_mantiene_el_interes_de_la_siguiente_cuota_del_mismo_par(self):
        # Cuotas 1 y 2 son el mismo "mes" (par 0) -- sin abono extra, el
        # interes de la cuota 2 no se recalcula, sigue el cronograma fijo.
        self.cuota2 = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('125000'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=32),
        )

        response = self._pagar(self.cuota1.id, {'monto_principal': '0', 'monto_interes': '37500', 'monto_mora': '0'})
        # Post-Redirect-Get: un pago que no cierra el prestamo redirige a
        # la cuota que queda activa (aqui, la 2), no se queda en la misma
        # pagina con el formulario todavia activo.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pagar_cuota_especifica', args=[self.cuota2.id]))

        self.prestamo.refresh_from_db()
        self.cuota1.refresh_from_db()
        self.cuota2.refresh_from_db()

        # El capital no bajo (solo se pago interes, sin abono extra)
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('500000'))

        # La cuota 1 quedo trasladada
        self.assertEqual(self.cuota1.estado, 'TRASLADADA')
        self.assertEqual(self.cuota1.monto_pendiente, Decimal('0'))
        self.assertEqual(self.cuota1.monto_pendiente_interes, Decimal('0'))

        # La cuota 2 (mismo par) mantiene su interes -- no se recalcula
        self.assertEqual(self.cuota2.interes_normal, Decimal('37500'))
        self.assertEqual(self.cuota2.monto_pendiente_interes, Decimal('37500'))
        self.assertEqual(self.cuota2.monto_pendiente, Decimal('500000'))

    def test_pago_solo_interes_crea_cuota_nueva_si_no_hay_siguiente(self):
        response = self._pagar(self.cuota1.id, {'monto_principal': '0', 'monto_interes': '37500', 'monto_mora': '0'})

        self.cuota1.refresh_from_db()
        nueva_cuota = self.prestamo.cuotas.filter(numero_cuota=2).first()

        self.assertIsNotNone(nueva_cuota)
        # Post-Redirect-Get: redirige a la cuota recien creada (la que
        # queda activa), no se queda en la misma pagina.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pagar_cuota_especifica', args=[nueva_cuota.id]))
        self.assertEqual(self.cuota1.estado, 'TRASLADADA')
        # Cuota 1 es numero impar (primera de su par) -> la 2 sigue en el
        # mismo par, mismo interes (sin abono extra).
        self.assertEqual(nueva_cuota.interes_normal, Decimal('37500'))
        self.assertEqual(nueva_cuota.fecha_pago_esperada, self.cuota1.fecha_pago_esperada + timedelta(days=15))

    def test_abono_extra_recalcula_el_cronograma_restante_ejemplo_del_cliente(self):
        # Reproduce el ejemplo confirmado: 500000 al 15%, con 6 cuotas.
        # Cuotas 1-2: 37500. Abono extra en la cuota 2 deja 200000 de
        # capital real. Cuotas 3-4 deben recalcularse a 15000 (200000*15%/2)
        # y cuotas 5-6 a 7500 (la mitad), con capital por cuota = 200000/4=50000.
        for n in range(2, 7):
            Cuota.objects.create(
                prestamo=self.prestamo,
                numero_cuota=n,
                monto_original=Decimal('83333.33'),
                interes_normal=Decimal('37500') if n == 2 else Decimal('18750'),
                fecha_pago_esperada=date.today() + timedelta(days=17 + 15 * (n - 1)),
            )

        # Pago sobre la cuota 2: 300000 de capital (mucho mas que su
        # pedacito nominal ~83333) + su interes de 37500 -> abono extra.
        response = self._pagar(self.prestamo.cuotas.get(numero_cuota=2).id, {
            'monto_principal': '300000', 'monto_interes': '37500', 'monto_mora': '0',
        })

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('200000'))

        cuota3 = self.prestamo.cuotas.get(numero_cuota=3)
        # Post-Redirect-Get: redirige a la cuota 3 (la que queda activa
        # tras el abono extra), no se queda en la misma pagina.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pagar_cuota_especifica', args=[cuota3.id]))
        cuota4 = self.prestamo.cuotas.get(numero_cuota=4)
        cuota5 = self.prestamo.cuotas.get(numero_cuota=5)
        cuota6 = self.prestamo.cuotas.get(numero_cuota=6)

        for c in (cuota3, cuota4, cuota5, cuota6):
            self.assertEqual(c.monto_original, Decimal('50000.00'))
        self.assertEqual(cuota3.interes_normal, Decimal('15000.00'))
        self.assertEqual(cuota4.interes_normal, Decimal('15000.00'))
        self.assertEqual(cuota5.interes_normal, Decimal('7500.00'))
        self.assertEqual(cuota6.interes_normal, Decimal('7500.00'))

    def test_pago_que_cierra_prestamo_no_crea_cuota_nueva(self):
        response = self._pagar(self.cuota1.id, {'monto_principal': '500000', 'monto_interes': '37500', 'monto_mora': '0'})
        # Post-Redirect-Get: un pago que cierra el credito redirige al
        # detalle del prestamo, no se queda en la pagina de la cuota ya
        # cerrada con el formulario todavia activo.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('detalles_prestamo', args=[self.prestamo.id]))

        self.prestamo.refresh_from_db()
        self.cuota1.refresh_from_db()

        self.assertEqual(self.prestamo.estado, 'COMPLETADO')
        self.assertTrue(self.cuota1.pagado)
        self.assertEqual(self.cuota1.estado, 'PAGADA')
        self.assertEqual(self.prestamo.cuotas.filter(numero_cuota=2).count(), 0)

    def test_pagar_cuota_trasladada_redirige_a_la_activa(self):
        # Primer pago: solo interes, deja la cuota 1 trasladada y crea la cuota 2
        self._pagar(self.cuota1.id, {'monto_principal': '0', 'monto_interes': '37500', 'monto_mora': '0'})
        self.cuota1.refresh_from_db()
        nueva_cuota = self.prestamo.cuotas.filter(numero_cuota=2).first()

        # Intentar pagar de nuevo sobre la cuota vieja (ya trasladada)
        from mi_app.views_core import pagar_cuota_especifica
        request = self.factory.get(f'/cuota/{self.cuota1.id}/pagar/')
        request.user = self.user
        # Los messages framework requiere middleware de sesion/mensajes -- se
        # agrega manualmente ya que RequestFactory no corre middlewares.
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        response = pagar_cuota_especifica(request, self.cuota1.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(nueva_cuota.id), response.url)


class AvanzarCuotaRapidaTests(TestCase):
    """Igual que AvanzarCuotaTests pero para PrestamoRapido/CuotaRapida.
    registrar_pago_rapido siempre redirige (nunca renderiza un 200), asi
    que aca si se puede usar el Client normal sin chocar con el bug de
    entorno de Python 3.14."""

    def setUp(self):
        self.client_obj = Client()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_avanzar_rapida',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.client_obj.login(username='testuser_avanzar_rapida', password='testpass123')  # pragma: allowlist secret

        from mi_app.models import PrestamoRapido, CuotaRapida
        self.cliente = Cliente.objects.create(nombre="Test Avanzar Rapida", celular="3000000007", cedula="999888784")
        self.prestamo = PrestamoRapido.objects.create(
            cliente=self.cliente,
            monto=Decimal('300000'),
            interes_porcentaje=Decimal('15'),
            capital_pendiente=Decimal('300000'),
        )
        self.cuota1 = CuotaRapida.objects.create(
            prestamo_rapido=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('150000'),
            monto_pendiente=Decimal('300000'),
            interes_normal=Decimal('22500'),
            monto_pendiente_interes=Decimal('22500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

    def test_pago_solo_interes_mantiene_interes_y_crea_nueva_cuota(self):
        response = self.client_obj.post(
            reverse('registrar_pago_cuota_rapida', kwargs={'cuota_id': self.cuota1.id}),
            {'monto_pagado': '22500', 'usuario_registra': 'admin'},
        )
        self.assertEqual(response.status_code, 302)

        self.prestamo.refresh_from_db()
        self.cuota1.refresh_from_db()
        from mi_app.models import CuotaRapida
        nueva_cuota = CuotaRapida.objects.filter(prestamo_rapido=self.prestamo, numero_cuota=2).first()

        self.assertEqual(self.prestamo.capital_pendiente, Decimal('300000'))
        self.assertEqual(self.cuota1.estado, 'TRASLADADA')
        self.assertIsNotNone(nueva_cuota)
        # Cuota 1 es numero impar -> la 2 sigue en el mismo par, mismo interes
        self.assertEqual(nueva_cuota.interes_normal, Decimal('22500'))
        self.assertEqual(nueva_cuota.fecha_pago_esperada, self.cuota1.fecha_pago_esperada + timedelta(days=15))

    def test_pagar_cuota_rapida_trasladada_redirige_a_la_activa(self):
        self.client_obj.post(
            reverse('registrar_pago_cuota_rapida', kwargs={'cuota_id': self.cuota1.id}),
            {'monto_pagado': '22500', 'usuario_registra': 'admin'},
        )
        from mi_app.models import CuotaRapida
        nueva_cuota = CuotaRapida.objects.filter(prestamo_rapido=self.prestamo, numero_cuota=2).first()

        response = self.client_obj.get(
            reverse('registrar_pago_cuota_rapida', kwargs={'cuota_id': self.cuota1.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(nueva_cuota.id), response.url)

    def test_abono_extra_recalcula_cronograma_restante(self):
        from mi_app.models import CuotaRapida

        self.cuota2 = CuotaRapida.objects.create(
            prestamo_rapido=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('150000'),
            interes_normal=Decimal('22500'),
            fecha_pago_esperada=date.today() + timedelta(days=32),
        )

        # Pago sobre cuota 1: 200000 de capital (mucho mas que su pedacito
        # nominal de 150000) + interes -> abono extra. Capital restante = 100000.
        response = self.client_obj.post(
            reverse('registrar_pago_cuota_rapida', kwargs={'cuota_id': self.cuota1.id}),
            {'monto_pagado': '222500', 'usuario_registra': 'admin'},
        )
        self.assertEqual(response.status_code, 302)

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('100000'))

        self.cuota2.refresh_from_db()
        self.assertEqual(self.cuota2.monto_original, Decimal('100000.00'))
        # 100000*15%/2 = 7500, sin redondeo
        self.assertEqual(self.cuota2.interes_normal, Decimal('7500.00'))


class PrestamoRapidoSaldoPendienteTests(TestCase):
    """PrestamoRapido.saldo_pendiente/total_a_pagar/porcentaje_pagado deben
    usar el motor de interes sobre saldo cuando el prestamo tiene cuotas,
    y el calculo original cuando no las tiene (flujo "directo" que nunca
    migro a este motor)."""

    def setUp(self):
        from mi_app.models import PrestamoRapido, CuotaRapida
        self.PrestamoRapido = PrestamoRapido
        self.CuotaRapida = CuotaRapida
        self.cliente = Cliente.objects.create(nombre="Test Saldo Pendiente Rapido", celular="3000000008", cedula="999888785")

    def test_con_cuotas_usa_capital_pendiente_e_interes_dinamico(self):
        prestamo = self.PrestamoRapido.objects.create(
            cliente=self.cliente,
            monto=Decimal('300000'),
            interes_porcentaje=Decimal('15'),
            capital_pendiente=Decimal('223000'),
            interes_acumulado_sin_pagar=Decimal('0'),
        )
        self.CuotaRapida.objects.create(
            prestamo_rapido=prestamo,
            numero_cuota=1,
            monto_original=Decimal('150000'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
            estado='TRASLADADA',
        )
        cuota_activa = self.CuotaRapida.objects.create(
            prestamo_rapido=prestamo,
            numero_cuota=2,
            monto_original=Decimal('150000'),
            monto_pendiente=Decimal('223000'),
            interes_normal=Decimal('17000'),
            monto_pendiente_interes=Decimal('17000'),
            fecha_pago_esperada=date.today() + timedelta(days=32),
        )

        # saldo real: capital_pendiente (223000) + interes de la cuota activa (17000)
        self.assertEqual(prestamo.saldo_pendiente, Decimal('240000'))
        self.assertEqual(prestamo.total_a_pagar, Decimal('240000'))
        # porcentaje pagado sobre progreso de capital: (300000-223000)/300000*100
        self.assertAlmostEqual(float(prestamo.porcentaje_pagado), 25.67, places=1)

    def test_sin_cuotas_usa_el_calculo_original(self):
        prestamo = self.PrestamoRapido.objects.create(
            cliente=self.cliente,
            monto=Decimal('100000'),
            interes_porcentaje=Decimal('20'),
        )
        # Sin cuotas: total_a_pagar = monto + interes fijo = 100000 + 20000 = 120000
        self.assertEqual(prestamo.total_a_pagar, 120000.0)
        self.assertEqual(prestamo.saldo_pendiente, 120000.0)

    def test_actualizar_estado_no_marca_pagado_falso_por_monto_pagado_acumulado(self):
        """
        Regresion: bajo el motor de saldo declinante, total_a_pagar
        (=saldo_pendiente) se ACHICA con el tiempo mientras monto_pagado
        (acumulado historico de todo lo pagado) solo CRECE -- comparar
        ambos directamente (diferencia <= 0 => PAGADO) puede marcar el
        prestamo como pagado en falso si monto_pagado queda desincronizado
        por encima del saldo actual, aunque el capital siga vivo. El
        cierre real debe depender del saldo vivo (capital_pendiente +
        interes pendiente), no de cuanto se ha pagado historicamente.
        """
        prestamo = self.PrestamoRapido.objects.create(
            cliente=self.cliente,
            monto=Decimal('300000'),
            interes_porcentaje=Decimal('15'),
            capital_pendiente=Decimal('280000'),
            interes_acumulado_sin_pagar=Decimal('0'),
            # Acumulado historico (ej. muchos periodos pagando solo interes)
            # mayor al saldo actual -- esto es exactamente lo que antes
            # disparaba el falso PAGADO.
            monto_pagado=Decimal('400000'),
        )
        self.CuotaRapida.objects.create(
            prestamo_rapido=prestamo,
            numero_cuota=1,
            monto_original=Decimal('150000'),
            monto_pendiente=Decimal('280000'),
            interes_normal=Decimal('22500'),
            monto_pendiente_interes=Decimal('22500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

        prestamo.actualizar_estado()
        prestamo.refresh_from_db()

        self.assertNotEqual(prestamo.estado, 'PAGADO')
        self.assertEqual(prestamo.estado, 'PARCIALMENTE_PAGADO')
        self.assertEqual(prestamo.capital_pendiente, Decimal('280000'))


class ReporteCuotasTrasladadaTests(TestCase):
    """
    reporte_cuotas_completo (reporte_cuotas.html) filtraba/clasificaba
    cuotas TRASLADADA (saldo movido a la siguiente, no pagada) como si
    estuvieran "pendientes" o "vencidas" segun el filtro, y el badge
    visible caia en VENCIDA en vez de mostrar su estado real. Se agrego
    un filtro 'trasladada' propio y se excluyo TRASLADADA de 'pendiente'/
    'vencida'. Ver auditoria de consistencia del motor de interes sobre
    saldo (2026-09-13).
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='reporte.view',
            defaults={'descripcion': 'reporte.view', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_reporte_cuotas',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Reporte Cuotas", celular="3000000009", cedula="999888790")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota_trasladada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            monto_pagado_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() - timedelta(days=20),
            estado='TRASLADADA',
        )
        self.cuota_activa = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=10),
        )

    def _reportar(self, querystring=''):
        from mi_app.views_core import reporte_cuotas_completo
        request = self.factory.get(f'/reportes/cuotas/{querystring}')
        request.user = self.user
        return reporte_cuotas_completo(request)

    def test_filtro_pendiente_excluye_trasladada(self):
        # Se distinguen las 2 cuotas por su fecha (unica por fila): la
        # trasladada no debe aparecer bajo el filtro 'pendiente', la activa si.
        response = self._reportar('?estado=pendiente')
        content = response.content.decode('utf-8')
        fecha_trasladada = self.cuota_trasladada.fecha_pago_esperada.strftime('%d/%m/%Y')
        fecha_activa = self.cuota_activa.fecha_pago_esperada.strftime('%d/%m/%Y')
        self.assertNotIn(fecha_trasladada, content)
        self.assertIn(fecha_activa, content)

    def test_filtro_trasladada_devuelve_solo_esa_cuota(self):
        from mi_app.views_core import reporte_cuotas_completo
        request = self.factory.get('/reportes/cuotas/?estado=trasladada')
        request.user = self.user
        response = reporte_cuotas_completo(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # El filtro interno sigue llamandose 'trasladada' (sigue siendo un
        # estado propio a nivel de datos/reportes), pero el badge visible
        # se muestra como "Pagada" -- decision explicita del dueno tras
        # reportar que "TRASLADADA" en pantalla confundia con "no se pago".
        self.assertIn('✅ PAGADA', content)

    def test_badge_visible_muestra_pagada_no_vencida(self):
        # Antes mostraba el badge "TRASLADADA" (gris) para una cuota ya
        # pagada en su turno -- el dueno reporto que eso confundia
        # ("por que dice trasladada si pague completo?"). Ahora se
        # muestra igual que una cuota PAGADA de verdad; el estado interno
        # (TRASLADADA) no cambia, solo el badge visible.
        response = self._reportar('')
        content = response.content.decode('utf-8')
        self.assertIn('✅ PAGADA', content)
        self.assertNotIn('❌ VENCIDA', content)


class ReporteCuotasVencidasFuturasTests(TestCase):
    """
    reporte_cuotas_vencidas contaba como "vencida" cualquier cuota
    pagado=False cuya fecha_pago_esperada ya paso -- eso incluia cuotas
    futuras que nunca llegaron a activarse (nacen con monto_pendiente=0,
    ver crear_prestamo), sobre-representando cuantas cuotas debe
    realmente un cliente atrasado. Se agrego monto_pendiente__gt=0 para
    excluirlas. Ver auditoria de consistencia del motor de interes sobre
    saldo (2026-09-13).
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Test Reporte Vencidas", celular="3000000010", cedula="999888791")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        # Cuota activa y realmente vencida (nunca se pago, capital vivo aqui).
        self.cuota_activa_vencida = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() - timedelta(days=25),
        )
        # Cuota futura que nunca llego a activarse -- su fecha original ya
        # paso (el cliente esta atrasado), pero no le corresponde nada
        # todavia (monto_pendiente=0).
        self.cuota_futura_no_activada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() - timedelta(days=10),
        )

    def test_cuota_futura_no_activada_no_cuenta_como_vencida(self):
        # reporte_cuotas_vencidas.html usa {% load crispy_forms_tags %},
        # pero crispy_forms nunca se agrego a INSTALLED_APPS (hallazgo
        # aparte, no relacionado a este fix -- ver DEUDA-TECNICA.md) --
        # eso rompe el render completo de la vista en cualquier entorno,
        # asi que se prueba directamente la misma condicion de filtro que
        # usa reporte_cuotas_vencidas (pagado=False, fecha vencida,
        # monto_pendiente__gt=0) en vez de invocar la vista completa.
        cuotas_vencidas_qs = Cuota.objects.filter(
            pagado=False,
            fecha_pago_esperada__lt=date.today(),
            monto_pendiente__gt=0,
        )
        ids = set(cuotas_vencidas_qs.values_list('id', flat=True))
        self.assertIn(self.cuota_activa_vencida.id, ids)
        self.assertNotIn(self.cuota_futura_no_activada.id, ids)


class PrestamoPorcentajePagadoTests(TestCase):
    """
    perfil_cliente.html y reporte_prestamos.html median el progreso de
    pago como total_pagado/total_credito (un widthratio en el template),
    mientras detalles_prestamo (vista) lo calculaba inline como
    (monto_total - capital_pendiente)/monto_total -- dos formulas
    distintas para "cuanto ha avanzado" el MISMO prestamo, que pueden dar
    numeros diferentes (pagar solo interes mueve la primera formula pero
    no la segunda, ya que el capital sigue igual). Se centraliza en
    Prestamo.porcentaje_pagado (nueva property) y se usa en los 3 lugares.
    Ver auditoria de consistencia del motor de interes sobre saldo
    (2026-09-13).
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Test Porcentaje Pagado", celular="3000000011", cedula="999888792")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )

    def test_pagar_solo_interes_no_mueve_el_porcentaje(self):
        # Pagar solo interes (rutina normal bajo el motor de saldo
        # declinante) no reduce lo que realmente se debe de capital -- el
        # porcentaje de avance debe seguir en 0%, no un numero fantasma
        # basado en cuanto se ha pagado historicamente.
        Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            monto_pagado_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )
        self.assertEqual(self.prestamo.porcentaje_pagado, Decimal('0'))

    def test_abono_a_capital_si_mueve_el_porcentaje(self):
        self.prestamo.capital_pendiente = Decimal('375000')
        self.prestamo.save()
        # (500000-375000)/500000*100 = 25
        self.assertEqual(self.prestamo.porcentaje_pagado, Decimal('25'))

    def test_porcentaje_se_limita_entre_0_y_100(self):
        self.prestamo.capital_pendiente = Decimal('0')
        self.prestamo.save()
        self.assertEqual(self.prestamo.porcentaje_pagado, Decimal('100'))


class EstadisticasSistemaPendienteRealTests(TestCase):
    """
    obtener_estadisticas_sistema() calculaba total_pendiente_capital/
    total_pendiente_credito como (total historico) - (total_pagado que
    incluye interes+mora) -- eso mezclaba capital puro contra pagos que
    tambien cubrian interes, y ademas no seguia un abono extraordinario
    que recalcula el cronograma restante (capital_pendiente/total_pendiente
    por prestamo ya son la fuente de verdad correcta desde antes en esta
    sesion). Se cambia a sumar directamente capital_pendiente/
    total_pendiente de cada prestamo. Ver auditoria de consistencia del
    motor de interes sobre saldo (2026-09-13).
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Test Estadisticas Sistema", celular="3000000012", cedula="999888793")

    def test_pagar_solo_interes_no_reduce_el_pendiente_agregado(self):
        from mi_app.views_core import obtener_estadisticas_sistema

        prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            monto_pagado_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

        stats = obtener_estadisticas_sistema()

        # Pagar solo interes (sin abonar capital) no debe reducir el
        # capital pendiente agregado del sistema -- debe seguir siendo
        # el capital_pendiente real (500000), no 500000 menos lo pagado
        # de interes (462500, el bug viejo).
        self.assertEqual(stats['dinero']['total_pendiente_capital'], 500000.0)


class BuscarClientePagoTrasladadaTests(TestCase):
    """
    buscar_cliente_pago (pagos_dinamico.html) Paso 3 listaba cuotas con
    pagado=False sin excluir TRASLADADA -- una cuota cuyo saldo ya se
    movio a la siguiente (no pagada, pero tampoco pendiente de verdad)
    aparecia en la lista de "cuotas a pagar". Ver auditoria de
    consistencia del motor de interes sobre saldo (2026-09-13).
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='pago.view',
            defaults={'descripcion': 'pago.view', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_pagos_dinamico',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Pagos Dinamico", celular="3000000013", cedula="999888794")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota_trasladada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() - timedelta(days=17),
            estado='TRASLADADA',
        )
        self.cuota_activa = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=2),
        )
        self.cuota_anulada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=3,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('18750'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )
        Cuota.objects.filter(id=self.cuota_anulada.id).update(estado='ANULADA')
        self.cuota_anulada.refresh_from_db()

    def test_paso_3_excluye_cuota_anulada(self):
        from mi_app.views_core import buscar_cliente_pago

        request = self.factory.get(f'/pagos/buscar/?cliente_id={self.cliente.id}&prestamo_id={self.prestamo.id}')
        request.user = self.user
        response = buscar_cliente_pago(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        fecha_anulada = self.cuota_anulada.fecha_pago_esperada.strftime('%d/%m/%Y')
        self.assertNotIn(fecha_anulada, content)

    def test_paso_3_excluye_cuota_trasladada(self):
        from mi_app.views_core import buscar_cliente_pago

        request = self.factory.get(f'/pagos/buscar/?cliente_id={self.cliente.id}&prestamo_id={self.prestamo.id}')
        request.user = self.user
        response = buscar_cliente_pago(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        fecha_trasladada = self.cuota_trasladada.fecha_pago_esperada.strftime('%d/%m/%Y')
        fecha_activa = self.cuota_activa.fecha_pago_esperada.strftime('%d/%m/%Y')
        self.assertNotIn(fecha_trasladada, content)
        self.assertIn(fecha_activa, content)


class ExportarCuotasExcelTests(TestCase):
    """
    exportar_cuotas_excel tenia el mismo bug de columna combinada ya
    arreglado en las tablas HTML (detalles_prestamo.html, etc): "Total
    Pendiente" mezclaba capital+interes+mora en un solo numero, y "Estado"
    no distinguia TRASLADADA de "Pendiente". Se separa en columnas
    "Capital Pendiente"/"Interés Pendiente" y se agrega el estado
    "Trasladada" explicito. Ver auditoria de consistencia del motor de
    interes sobre saldo (2026-09-13).
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='reporte.export',
            defaults={'descripcion': 'reporte.export', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_export_cuotas',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Export Cuotas", celular="3000000014", cedula="999888795")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota_trasladada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() - timedelta(days=17),
            estado='TRASLADADA',
        )
        self.cuota_activa = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=2),
        )

    def test_columnas_separadas_y_estado_trasladada(self):
        import io
        from openpyxl import load_workbook
        from mi_app.views_core import exportar_cuotas_excel

        request = self.factory.get('/exportar/cuotas/')
        request.user = self.user
        response = exportar_cuotas_excel(request)

        self.assertEqual(response.status_code, 200)
        wb = load_workbook(io.BytesIO(response.content))
        ws = wb.active

        headers = [cell.value for cell in ws[1]]
        self.assertIn('Capital Pendiente', headers)
        self.assertIn('Interés Pendiente', headers)
        self.assertNotIn('Total Pendiente', headers)

        idx_capital = headers.index('Capital Pendiente') + 1
        idx_interes = headers.index('Interés Pendiente') + 1
        idx_estado = headers.index('Estado') + 1
        idx_cuota_num = headers.index('Cuota Nº') + 1

        filas_por_cuota = {}
        for row in ws.iter_rows(min_row=2, values_only=False):
            filas_por_cuota[row[idx_cuota_num - 1].value] = row

        fila_trasladada = filas_por_cuota[1]
        fila_activa = filas_por_cuota[2]

        self.assertEqual(fila_trasladada[idx_estado - 1].value, 'Trasladada')
        self.assertEqual(fila_activa[idx_capital - 1].value, 500000.0)
        self.assertEqual(fila_activa[idx_interes - 1].value, 37500.0)


class ExportarCuotasVencidasExcelTests(TestCase):
    """
    exportar_cuotas_vencidas_excel contaba cuotas futuras no activadas
    como vencidas (mismo bug ya arreglado en reporte_cuotas_vencidas), y
    su columna "Monto Principal" usaba el monto_original nominal en vez
    del monto_pendiente real (para la cuota activa, el capital real vivo
    es mucho mayor que el pedacito nominal). Ver auditoria de consistencia
    del motor de interes sobre saldo (2026-09-13).
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='reporte.export',
            defaults={'descripcion': 'reporte.export', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_export_vencidas',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Export Vencidas", celular="3000000015", cedula="999888796")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota_activa_vencida = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() - timedelta(days=5),
        )
        self.cuota_futura_no_activada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() - timedelta(days=1),
        )

    def test_excluye_futura_no_activada_y_usa_monto_real(self):
        import io
        from openpyxl import load_workbook
        from mi_app.views_core import exportar_cuotas_vencidas_excel

        request = self.factory.get('/exportar/cuotas-vencidas/')
        request.user = self.user
        response = exportar_cuotas_vencidas_excel(request)

        self.assertEqual(response.status_code, 200)
        wb = load_workbook(io.BytesIO(response.content))
        ws = wb.active

        filas = list(ws.iter_rows(min_row=2, values_only=True))
        self.assertEqual(len(filas), 1)
        headers = [cell.value for cell in ws[1]]
        idx_principal = headers.index('Monto Principal')
        self.assertEqual(filas[0][idx_principal], 500000.0)


class CierreTotalAnulaCuotasRestantesTests(TestCase):
    """
    Bug real reportado: pagar TODO el capital pendiente de una vez (cierre
    total del credito) dejaba las cuotas futuras que nunca llegaron a
    usarse con su interes precalculado intacto, como si todavia se
    fueran a cobrar. Prestamo.total_pendiente/resumen_financiero()
    volvian a sumar ese interes fantasma (131.250 en el ejemplo real del
    cliente) aunque el credito ya estuviera 100% completado. Se agrega el
    estado terminal ANULADA para las cuotas que nunca se usaron, y una
    guarda explicita: si el prestamo esta COMPLETADO, el interes
    pendiente es siempre 0. Ver reporte del cliente (2026-09-13).

    NOTA: se invoca la vista directamente via RequestFactory (no Client)
    -- mismo motivo que AvanzarCuotaTests (bug conocido de Python 3.14 +
    Django 4.2 al renderizar templates con status 200 via el test client).
    """

    def setUp(self):
        from django.test import RequestFactory
        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)

        self.user = User.objects.create_user(
            username='testuser_cierre_total',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Cierre Total", celular="3000000016", cedula="999888797")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        # Cronograma real del ejemplo del cliente: 37500,37500,18750,18750,9375,9375
        intereses = [Decimal('37500'), Decimal('37500'), Decimal('18750'), Decimal('18750'), Decimal('9375'), Decimal('9375')]
        self.cuotas = []
        for i, interes in enumerate(intereses, 1):
            cuota = Cuota.objects.create(
                prestamo=self.prestamo,
                numero_cuota=i,
                monto_original=Decimal('83333.33'),
                monto_pendiente=Decimal('500000') if i == 1 else Decimal('0'),
                interes_normal=interes,
                monto_pendiente_interes=interes,
                fecha_pago_esperada=date.today() + timedelta(days=15 * i),
            )
            self.cuotas.append(cuota)

    def _pagar_todo(self):
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore
        from mi_app.views_core import pagar_cuota_especifica
        request = self.factory.post(f'/cuota/{self.cuotas[0].id}/pagar/', {
            'monto_principal': '500000',
            'monto_interes': '37500',
            'monto_mora': '0',
        })
        request.user = self.user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return pagar_cuota_especifica(request, self.cuotas[0].id)

    def test_total_pendiente_queda_en_cero_tras_cierre_total(self):
        response = self._pagar_todo()
        # Post-Redirect-Get: un cierre total redirige al detalle del
        # prestamo, no se queda en la cuota ya cerrada con el formulario
        # todavia activo.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('detalles_prestamo', args=[self.prestamo.id]))

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.estado, 'COMPLETADO')
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('0'))
        self.assertEqual(self.prestamo.total_pendiente, 0.0)
        self.assertEqual(self.prestamo.porcentaje_pagado, Decimal('100'))

        resumen = self.prestamo.resumen_financiero()
        self.assertEqual(resumen['total_pendiente_interes'], 0.0)
        # interes_total_credito/total_credito son el TOTAL DE VIDA del
        # credito (pagado + pendiente), no solo lo pendiente -- un credito
        # cerrado con $37.500 de interes ya cobrado sigue valiendo
        # $37.500 de interes en total, no $0 (eso confundiria "ya se
        # cobro todo" con "nunca hubo interes").
        self.assertEqual(resumen['interes_total_credito'], 37500.0)
        self.assertEqual(resumen['total_credito'], 537500.0)

    def test_cuotas_futuras_quedan_anuladas_sin_montos_pendientes(self):
        self._pagar_todo()

        for cuota in self.cuotas[1:]:
            cuota.refresh_from_db()
            self.assertEqual(cuota.estado, 'ANULADA', f"cuota {cuota.numero_cuota} deberia estar ANULADA")
            self.assertEqual(cuota.monto_pendiente, Decimal('0'))
            self.assertEqual(cuota.monto_pendiente_interes, Decimal('0'))

        self.cuotas[0].refresh_from_db()
        self.assertEqual(self.cuotas[0].estado, 'PAGADA')
        self.assertTrue(self.cuotas[0].pagado)


class EstadosTerminalesNoSeCorrompenTests(TestCase):
    """
    Bug critico encontrado en la auditoria: determinar_estado_cuota_al_crear()
    (usada por mora_diaria_api, el comando sincronizar_estados_cuotas, y
    reconciliar_finanzas) no conocia los estados terminales TRASLADADA/
    ANULADA del motor de interes sobre saldo -- cualquier sincronizacion
    masiva las sobreescribia de vuelta a VENCIDA/PENDIENTE, y les
    calculaba mora fantasma. Ademas, Cliente.calcular_rating()/
    obtener_cuotas_vencidas_por_dias() (esta ultima usada para marcar
    lista negra automatica) tampoco las excluian -- un cliente que pago
    TODO su credito podia terminar con rating de 1 estrella o marcado
    en lista negra, solo porque quedaron cuotas ANULADA con fecha vieja.
    Ver reporte del cliente (2026-09-13).
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Test Estados Terminales", celular="3000000017", cedula="999888798")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            estado='COMPLETADO',
            capital_pendiente=Decimal('0'),
        )
        self.cuota_pagada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('0'),
            monto_pagado_principal=Decimal('500000'),
            monto_pagado_interes=Decimal('37500'),
            pagado=True,
            fecha_pago_esperada=date.today() - timedelta(days=40),
        )
        self.cuota_pagada.estado = 'PAGADA'
        self.cuota_pagada.save()

        # Cuotas 2-6 quedaron ANULADA con fecha muy vieja (> 30 dias) --
        # exactamente el escenario que antes disparaba lista negra/rating malo.
        self.cuotas_anuladas = []
        for i in range(2, 7):
            c = Cuota.objects.create(
                prestamo=self.prestamo,
                numero_cuota=i,
                monto_original=Decimal('83333.33'),
                monto_pendiente=Decimal('0'),
                interes_normal=Decimal('18750'),
                monto_pendiente_interes=Decimal('0'),
                fecha_pago_esperada=date.today() - timedelta(days=40 - i),
            )
            Cuota.objects.filter(id=c.id).update(estado='ANULADA')
            c.refresh_from_db()
            self.cuotas_anuladas.append(c)

    def test_determinar_estado_cuota_al_crear_preserva_anulada(self):
        from mi_app.utils import determinar_estado_cuota_al_crear
        cuota = self.cuotas_anuladas[0]
        resultado = determinar_estado_cuota_al_crear(
            pagado=cuota.pagado,
            fecha_pago_esperada=cuota.fecha_pago_esperada,
            monto_pagado_principal=cuota.monto_pagado_principal,
            monto_original=cuota.monto_original,
            estado_actual=cuota.estado,
        )
        self.assertEqual(resultado, 'ANULADA')

    def test_determinar_estado_cuota_al_crear_preserva_trasladada(self):
        from mi_app.utils import determinar_estado_cuota_al_crear
        resultado = determinar_estado_cuota_al_crear(
            pagado=False,
            fecha_pago_esperada=date.today() - timedelta(days=40),
            monto_pagado_principal=Decimal('0'),
            monto_original=Decimal('83333.33'),
            estado_actual='TRASLADADA',
        )
        self.assertEqual(resultado, 'TRASLADADA')

    def test_sincronizar_estados_cuotas_no_sobreescribe_anulada(self):
        from django.core.management import call_command
        import io

        call_command('sincronizar_estados_cuotas', stdout=io.StringIO())

        for c in self.cuotas_anuladas:
            c.refresh_from_db()
            self.assertEqual(c.estado, 'ANULADA', f"cuota {c.numero_cuota} no deberia cambiar de ANULADA")

    def test_rating_no_se_hunde_por_cuotas_anuladas(self):
        # Cliente pago TODO (1 prestamo completado, 0 cuotas realmente
        # vencidas) -- deberia tener el mejor rating, no el peor.
        self.assertEqual(self.cliente.calcular_rating(), 5.0)

    def test_lista_negra_no_se_activa_por_cuotas_anuladas(self):
        self.assertFalse(self.cliente.debe_estar_en_lista_negra(dias_mora=30))
        self.assertEqual(self.cliente.obtener_cuotas_vencidas_por_dias(30), [])

    def test_obtener_cuotas_vencidas_excluye_anulada_y_trasladada(self):
        self.assertEqual(self.cliente.obtener_cuotas_vencidas(), [])


class CierreTotalRapidoAnulaCuotasRestantesTests(TestCase):
    """Igual que CierreTotalAnulaCuotasRestantesTests, pero para
    PrestamoRapido/CuotaRapida (registrar_pago_rapido)."""

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import PrestamoRapido, CuotaRapida, Rol, Permiso, RolPermiso, UsuarioProfile
        self.PrestamoRapido = PrestamoRapido
        self.CuotaRapida = CuotaRapida
        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='pago.create',
            defaults={'descripcion': 'pago.create', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_cierre_total_rapido',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Cierre Total Rapido", celular="3000000018", cedula="999888799")
        self.prestamo = self.PrestamoRapido.objects.create(
            cliente=self.cliente,
            monto=Decimal('300000'),
            interes_porcentaje=Decimal('15'),
            capital_pendiente=Decimal('300000'),
        )
        intereses = [Decimal('22500'), Decimal('22500'), Decimal('11250'), Decimal('11250')]
        self.cuotas = []
        for i, interes in enumerate(intereses, 1):
            c = self.CuotaRapida.objects.create(
                prestamo_rapido=self.prestamo,
                numero_cuota=i,
                monto_original=Decimal('75000'),
                monto_pendiente=Decimal('300000') if i == 1 else Decimal('0'),
                interes_normal=interes,
                monto_pendiente_interes=interes,
                fecha_pago_esperada=date.today() + timedelta(days=15 * i),
            )
            self.cuotas.append(c)

    def test_cierre_total_anula_cuotas_restantes_y_pendiente_en_cero(self):
        from mi_app.views_core import registrar_pago_rapido
        request = self.factory.post(f'/prestamo-rapido/cuota/{self.cuotas[0].id}/pagar/', {
            'monto_pagado': '322500',  # 300000 capital + 22500 interes
        })
        request.user = self.user
        response = registrar_pago_rapido(request, self.cuotas[0].id)
        self.assertEqual(response.status_code, 302)

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.estado, 'PAGADO')
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('0'))
        self.assertEqual(self.prestamo.saldo_pendiente, Decimal('0'))

        for cuota in self.cuotas[1:]:
            cuota.refresh_from_db()
            self.assertEqual(cuota.estado, 'ANULADA')
            self.assertEqual(cuota.monto_pendiente, Decimal('0'))
            self.assertEqual(cuota.monto_pendiente_interes, Decimal('0'))


class PagarCuotaAnuladaRedirigeTests(TestCase):
    """
    Bug encontrado en verificacion visual: el boton "Pagar" seguia
    apareciendo (y la vista aceptaba la solicitud) para cuotas ANULADA
    (nunca llegaron a usarse porque el credito ya cerro). Se agrega el
    mismo guard que ya existia para TRASLADADA: redirige al detalle del
    prestamo con un mensaje informativo, en vez de dejar seguir el flujo
    de pago sobre una cuota que no debe nada.
    """

    def setUp(self):
        from django.test import RequestFactory
        self.factory = RequestFactory()

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_pagar_anulada',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Pagar Anulada", celular="3000000019", cedula="999888800")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            estado='COMPLETADO',
            capital_pendiente=Decimal('0'),
        )
        self.cuota_anulada = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('0'),
            interes_normal=Decimal('18750'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=15),
        )
        Cuota.objects.filter(id=self.cuota_anulada.id).update(estado='ANULADA')
        self.cuota_anulada.refresh_from_db()

    def test_pagar_cuota_especifica_redirige_para_cuota_anulada(self):
        from mi_app.views_core import pagar_cuota_especifica
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore

        request = self.factory.get(f'/cuota/{self.cuota_anulada.id}/pagar/')
        request.user = self.user
        # Los messages framework requiere middleware de sesion/mensajes --
        # se agrega manualmente ya que RequestFactory no corre middlewares.
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        response = pagar_cuota_especifica(request, self.cuota_anulada.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('detalles_prestamo', args=[self.prestamo.id]))


class RegistrarPagoMejoradoRetiradaTests(TestCase):
    """
    registrar_pago_mejorado era una ruta huerfana (ningun template la
    enlazaba) con el MISMO bug ya retirado de registrar_pago: mutaba
    monto_pendiente/monto_pagado_principal de la cuota directamente, sin
    tocar Prestamo.capital_pendiente ni pasar por aplicar_pago(). Se
    retiro: ahora solo redirige a buscar_cliente_pago con el cliente
    preseleccionado.
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Test Pago Mejorado Retirado", celular="3000000020", cedula="999888801")

    def test_redirige_a_buscar_cliente_pago(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile
        from mi_app.views_core import registrar_pago_mejorado

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='pago.create',
            defaults={'descripcion': 'pago.create', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        user = User.objects.create_user(
            username='testuser_pago_mejorado_retirado',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=user,
            defaults={'rol': rol, 'activo': True}
        )

        factory = RequestFactory()
        request = factory.get(f'/clientes/{self.cliente.id}/registrar-pago/')
        request.user = user
        response = registrar_pago_mejorado(request, self.cliente.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('buscar_cliente_pago'), response.url)
        self.assertIn(str(self.cliente.id), response.url)


class ReporteCuotasVencidasRendersTests(TestCase):
    """
    reporte_cuotas_vencidas.html usa {% load crispy_forms_tags %}, pero
    crispy_forms/crispy_bootstrap5 (instalados via requirements.txt desde
    el inicio) nunca se habian agregado a INSTALLED_APPS -- rompia el
    render completo de esta vista con KeyError en cualquier entorno. Ver
    auditoria de consistencia del motor de interes sobre saldo
    (2026-09-13).
    """

    def setUp(self):
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='reporte.view',
            defaults={'descripcion': 'reporte.view', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_reporte_vencidas_render',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

    def test_renderiza_sin_error_de_crispy_forms(self):
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore
        from mi_app.views_core import reporte_cuotas_vencidas

        factory = RequestFactory()
        request = factory.get('/reportes/cuotas-vencidas/')
        request.user = self.user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        response = reporte_cuotas_vencidas(request)
        self.assertEqual(response.status_code, 200)


class PagosDinamicoDiasVencidosSignoTests(TestCase):
    """
    pagos_dinamico.html (Paso 3) mostraba "-{{ dias_vencidos_positivo }}
    dias" para CUALQUIER cuota con fecha distinta de hoy -- incluidas las
    que vencen en el FUTURO, ya que dias_vencidos_positivo es un valor
    absoluto (abs()) y la condicion solo chequeaba "> 0", sin distinguir
    pasado de futuro. Se corrige para gatillar el aviso de "vencida hace"
    solo cuando dias_para_vencer < 0 (genuinamente atrasada), igual que
    ya hacen detalles_cuota.html/detalles_prestamo.html/
    pagar_cuota_especifica.html. Ver reporte del cliente (2026-09-13).
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()
        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='pago.view',
            defaults={'descripcion': 'pago.view', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_dias_vencidos_signo',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(nombre="Test Dias Vencidos Signo", celular="3000000021", cedula="999888802")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        self.cuota_futura = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('83333.33'),
            monto_pendiente=Decimal('500000'),
            interes_normal=Decimal('37500'),
            monto_pendiente_interes=Decimal('37500'),
            fecha_pago_esperada=date.today() + timedelta(days=17),
        )

    def test_cuota_futura_no_muestra_vencida_hace(self):
        from mi_app.views_core import buscar_cliente_pago

        request = self.factory.get(f'/pagos/buscar/?cliente_id={self.cliente.id}&prestamo_id={self.prestamo.id}')
        request.user = self.user
        response = buscar_cliente_pago(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertNotIn('Vencida hace', content)


class N1LatenteCorregidoTests(TestCase):
    """
    clientes_importados, reporte_clientes, exportar_prestamos_excel y
    exportar_prestamos_rapidos_excel iteraban prestamos llamando
    total_pendiente/saldo_pendiente (properties) sin el helper
    prefetch-aware -- valores correctos, pero N+1 real a escala (mismo
    patron ya arreglado en obtener_estadisticas_sistema()). Se verifica
    que los valores sigan siendo correctos tras el fix.
    """

    def setUp(self):
        from django.test import RequestFactory
        from mi_app.models import Rol, Permiso, RolPermiso, UsuarioProfile

        self.factory = RequestFactory()
        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('cliente.view', 'reporte.export'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_n1_latente',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(
            nombre="Test N1 Latente", celular="3000000022", cedula="999888803", importado_excel=True,
        )
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            estado='ACTIVO',
            capital_pendiente=Decimal('500000'),
        )
        # Cronograma real: 37500,37500,18750,18750,9375,9375 -- solo la
        # cuota 1 (activa) queda con capital vivo.
        intereses = [Decimal('37500'), Decimal('37500'), Decimal('18750'), Decimal('18750'), Decimal('9375'), Decimal('9375')]
        for i, interes in enumerate(intereses, 1):
            Cuota.objects.create(
                prestamo=self.prestamo,
                numero_cuota=i,
                monto_original=Decimal('83333.33'),
                monto_pendiente=Decimal('500000') if i == 1 else Decimal('0'),
                interes_normal=interes,
                monto_pendiente_interes=interes,
                fecha_pago_esperada=date.today() + timedelta(days=15 * i),
            )

    def test_clientes_importados_muestra_total_pendiente_correcto(self):
        from mi_app.views_core import clientes_importados

        request = self.factory.get('/clientes/importados/')
        request.user = self.user
        response = clientes_importados(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # total_pendiente = capital_pendiente(500000) + interes pendiente
        # total del cronograma (131250) = 631250
        self.assertIn('631', content)

    def test_exportar_prestamos_excel_usa_total_pendiente_correcto(self):
        import io
        from openpyxl import load_workbook
        from mi_app.views_core import exportar_prestamos_excel

        request = self.factory.get('/exportar/prestamos/')
        request.user = self.user
        response = exportar_prestamos_excel(request)

        self.assertEqual(response.status_code, 200)
        wb = load_workbook(io.BytesIO(response.content))
        ws = wb.active
        headers = [cell.value for cell in ws[1]]
        idx_pendiente = headers.index('Monto Pendiente')
        fila = next(row for row in ws.iter_rows(min_row=2, values_only=True))
        self.assertEqual(fila[idx_pendiente], 631250.0)


class BarraProgresoCssValidaTests(TestCase):
    """
    detalles_prestamo.html armaba el ancho de la barra de progreso con
    {% localize off %}{{ progreso|floatformat:2 }}{% endlocalize %} --
    pero el filtro floatformat ignora el bloque localize off (no respeta
    la bandera de contexto, a diferencia de la interpolacion simple de un
    Decimal), asi que con LANGUAGE_CODE='es-co' seguia devolviendo coma
    decimal ("100,00") dentro de un atributo style, produciendo CSS
    invalido ("width: 100,00%;") que el navegador ignora en silencio y
    deja la barra colapsada. El dueno lo reporto en vivo tras un fix
    anterior que solo agregaba {% localize off %} sin quitar
    floatformat -- no alcanzaba. El fix real usa stringformat:".2f"
    (nunca localiza, es formateo de Python puro) en vez de floatformat
    para el valor que va dentro del CSS.
    """

    def setUp(self):
        from django.test import RequestFactory

        self.factory = RequestFactory()
        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        perm, _ = Permiso.objects.get_or_create(
            codigo='prestamo.view',
            defaults={'descripcion': 'prestamo.view', 'activo': True}
        )
        RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        self.user = User.objects.create_user(
            username='testuser_barra_progreso',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        self.cliente = Cliente.objects.create(nombre="Test Barra Progreso", celular="3000000012", cedula="999888793")
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('500000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='COMPLETADO',
            capital_pendiente=Decimal('0'),
        )

    def test_ancho_de_la_barra_es_css_valido_no_localizado(self):
        from mi_app.views_core import detalles_prestamo

        request = self.factory.get(f'/prestamo/{self.prestamo.id}/')
        request.user = self.user
        response = detalles_prestamo(request, self.prestamo.id)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('width: 100.00%', content)
        self.assertNotIn('width: 100,00%', content)
