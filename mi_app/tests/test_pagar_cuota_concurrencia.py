import threading
import time
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.test import Client, TransactionTestCase, skipUnlessDBFeature
from django.urls import reverse

from mi_app.models import Cliente, Cuota, Pago, Permiso, Prestamo, Rol, RolPermiso, UsuarioProfile
from mi_app.services import amortizacion_service


@skipUnlessDBFeature('has_select_for_update')
class PagarCuotaConcurrenciaTests(TransactionTestCase):
    """
    Regresion de auditoria de logica de dinero (2026-10-08): pagar_cuota_especifica
    leia prestamo.capital_pendiente y validaba contra el ANTES de abrir la
    transaccion/bloquear la fila. Dos pagos simultaneos sobre el mismo
    prestamo (doble clic, dos operarios) podian ambos leer el mismo
    capital_pendiente, validar los dos contra ese mismo valor viejo, y el
    segundo .save() pisaba el descuento del primero -- plata que quedaba
    registrada como pagada (2 filas en Pago) pero solo se descontaba una
    vez del capital real.

    Solo corre contra un backend que soporte select_for_update() de verdad
    (Postgres, como en produccion/CI) -- en SQLite (local) esa llamada es
    un no-op silencioso (connection.features.has_select_for_update es
    False), asi que este test no probaria nada ahi y se salta en vez de dar
    un falso positivo.

    Usa TransactionTestCase (no TestCase) porque necesita que cada hilo
    tenga su propia conexion real a la BD con commits reales y visibles
    entre hilos -- TestCase envuelve cada test en una transaccion que nunca
    se confirma.
    """

    def setUp(self):
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
            username='pagos_concurrencia',
            password='testpass123'  # pragma: allowlist secret
        )
        UsuarioProfile.objects.update_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )

        self.cliente = Cliente.objects.create(
            nombre='Cliente Concurrencia', celular='3000000000', estado='ACTIVO'
        )
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            capital_pendiente=Decimal('100000'),
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            estado='ACTIVO',
        )
        self.cuota = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            # Igual al capital total: un pago de 40000 (la mitad) nunca
            # cuenta como "abono extraordinario" (regla: > monto_original),
            # asi que ambos hilos pasan por la rama simple de aplicar_pago,
            # sin tocar _avanzar_a_siguiente_cuota de forma distinta entre
            # si -- lo unico que este test quiere probar es que el
            # descuento de capital de los dos pagos sobrevive.
            monto_original=Decimal('100000'),
            monto_pendiente=Decimal('100000'),
            interes_normal=Decimal('0'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=15),
        )

    def _pagar(self, monto_principal, resultados, indice):
        client = Client()
        client.login(username='pagos_concurrencia', password='testpass123')  # pragma: allowlist secret
        try:
            response = client.post(
                reverse('pagar_cuota_especifica', args=[self.cuota.id]),
                {'monto_principal': str(monto_principal), 'monto_interes': '0', 'monto_mora': '0'},
            )
            resultados[indice] = response.status_code
        finally:
            connection.close()

    def test_dos_pagos_simultaneos_de_capital_no_se_pisan(self):
        # Dos pagos de 40000 sobre un capital de 100000: cada uno es
        # individualmente valido contra el capital ORIGINAL (100000), y
        # juntos (80000) siguen sin cerrar el credito. El resultado
        # correcto final es capital_pendiente = 20000 y 2 pagos
        # registrados. Si la concurrencia pisa un descuento, el capital
        # queda en 60000 (solo se aplico uno de los dos).
        aplicar_pago_real = amortizacion_service.aplicar_pago

        def aplicar_pago_lento(*args, **kwargs):
            # Agranda deliberadamente la ventana entre "leer" y "guardar"
            # para que, si el locking no esta funcionando, los dos hilos
            # SIEMPRE se crucen (en vez de depender de timing de SO/GIL,
            # que haria el test flaky en vez de confiable).
            time.sleep(0.3)
            return aplicar_pago_real(*args, **kwargs)

        resultados = {}
        with patch('mi_app.services.amortizacion_service.aplicar_pago', side_effect=aplicar_pago_lento):
            hilo1 = threading.Thread(target=self._pagar, args=(Decimal('40000'), resultados, 0))
            hilo2 = threading.Thread(target=self._pagar, args=(Decimal('40000'), resultados, 1))

            hilo1.start()
            hilo2.start()
            hilo1.join(timeout=15)
            hilo2.join(timeout=15)

        self.assertEqual(resultados.get(0), 302, 'Pago 1 no se proceso correctamente')
        self.assertEqual(resultados.get(1), 302, 'Pago 2 no se proceso correctamente')

        self.prestamo.refresh_from_db()
        self.assertEqual(self.prestamo.capital_pendiente, Decimal('20000'))
        self.assertEqual(Pago.objects.filter(cuota_id=self.cuota.id).count(), 2)
