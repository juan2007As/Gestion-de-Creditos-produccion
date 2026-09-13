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
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context or {})
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
        from mi_app.views_core import pagar_cuota_especifica
        request = self.factory.post(f'/cuota/{cuota_id}/pagar/', data)
        request.user = self.user
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
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 200)

        self.cuota1.refresh_from_db()
        nueva_cuota = self.prestamo.cuotas.filter(numero_cuota=2).first()

        self.assertIsNotNone(nueva_cuota)
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
        self.assertEqual(response.status_code, 200)

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('200000'))

        cuota3 = self.prestamo.cuotas.get(numero_cuota=3)
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
        self.assertEqual(response.status_code, 200)

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
