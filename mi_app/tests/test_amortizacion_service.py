from decimal import Decimal
from datetime import date
from django.test import SimpleTestCase

from mi_app.services.amortizacion_service import (
    calcular_interes_periodo,
    generar_cronograma_interes,
    ultimo_dia_valido_mes,
    determinar_par_y_primera_fecha,
    siguiente_fecha_en_par,
    generar_fechas_cuotas,
    inferir_par,
)


class CalcularInteresPeriodoTests(SimpleTestCase):
    def test_capital_500000_sin_redondeo(self):
        # 500000*15%/2 = 37500 exacto -- ya no se redondea al millar (decision
        # explicita del dueno: "no hay que redondear").
        self.assertEqual(calcular_interes_periodo(Decimal('500000')), Decimal('37500'))

    def test_capital_250000_sin_redondeo(self):
        self.assertEqual(calcular_interes_periodo(Decimal('250000')), Decimal('18750'))

    def test_capital_cero_da_interes_cero(self):
        self.assertEqual(calcular_interes_periodo(Decimal('0')), Decimal('0'))


class GenerarCronogramaInteresTests(SimpleTestCase):
    def test_ejemplo_del_cliente_500000_15_por_ciento_6_cuotas(self):
        cronograma = generar_cronograma_interes(Decimal('500000'), Decimal('15'), 6)
        self.assertEqual(
            cronograma,
            [
                Decimal('37500.00'), Decimal('37500.00'),
                Decimal('18750.00'), Decimal('18750.00'),
                Decimal('9375.00'), Decimal('9375.00'),
            ],
        )

    def test_cada_par_es_la_mitad_del_anterior_con_num_cuotas_impar(self):
        cronograma = generar_cronograma_interes(Decimal('400000'), Decimal('15'), 3)
        # base = 400000*7.5% = 30000
        self.assertEqual(cronograma, [Decimal('30000.00'), Decimal('30000.00'), Decimal('15000.00')])

    def test_una_sola_cuota(self):
        cronograma = generar_cronograma_interes(Decimal('100000'), Decimal('15'), 1)
        self.assertEqual(cronograma, [Decimal('7500.00')])


class UltimoDiaValidoMesTests(SimpleTestCase):
    def test_dia_30_en_mes_de_30_dias(self):
        self.assertEqual(ultimo_dia_valido_mes(2026, 4, 30), date(2026, 4, 30))

    def test_dia_30_en_febrero_no_bisiesto(self):
        self.assertEqual(ultimo_dia_valido_mes(2026, 2, 30), date(2026, 2, 28))

    def test_dia_30_en_febrero_bisiesto(self):
        self.assertEqual(ultimo_dia_valido_mes(2028, 2, 30), date(2028, 2, 29))


class DeterminarParYPrimeraFechaTests(SimpleTestCase):
    def test_desembolso_dia_20_da_dia_5_del_par_5_20(self):
        par, primera = determinar_par_y_primera_fecha(date(2026, 1, 20))
        self.assertEqual(par, (5, 20))
        self.assertEqual(primera, date(2026, 2, 5))

    def test_desembolso_dia_21_no_da_dia_5_da_dia_15(self):
        par, primera = determinar_par_y_primera_fecha(date(2026, 1, 21))
        self.assertEqual(par, (15, 30))
        self.assertEqual(primera, date(2026, 2, 15))

    def test_desembolso_dia_19_no_da_dia_30_da_dia_5(self):
        par, primera = determinar_par_y_primera_fecha(date(2026, 1, 19))
        self.assertEqual(par, (5, 20))
        self.assertEqual(primera, date(2026, 2, 5))


class SiguienteFechaEnParTests(SimpleTestCase):
    def test_de_5_pasa_a_20_mismo_mes(self):
        self.assertEqual(
            siguiente_fecha_en_par(date(2026, 2, 5), (5, 20)),
            date(2026, 2, 20),
        )

    def test_de_20_pasa_a_5_del_mes_siguiente(self):
        self.assertEqual(
            siguiente_fecha_en_par(date(2026, 2, 20), (5, 20)),
            date(2026, 3, 5),
        )

    def test_de_15_pasa_a_30_y_febrero_usa_28(self):
        self.assertEqual(
            siguiente_fecha_en_par(date(2026, 2, 15), (15, 30)),
            date(2026, 2, 28),
        )

    def test_de_diciembre_pasa_a_enero_del_anio_siguiente(self):
        self.assertEqual(
            siguiente_fecha_en_par(date(2026, 12, 20), (5, 20)),
            date(2027, 1, 5),
        )


class GenerarFechasCuotasTests(SimpleTestCase):
    def test_genera_num_cuotas_fechas_alternando_el_par(self):
        fechas = generar_fechas_cuotas(date(2026, 1, 20), 4)
        self.assertEqual(
            fechas,
            [date(2026, 2, 5), date(2026, 2, 20), date(2026, 3, 5), date(2026, 3, 20)],
        )


class InferirParTests(SimpleTestCase):
    def test_dia_5_pertenece_al_par_5_20(self):
        self.assertEqual(inferir_par(date(2026, 2, 5)), (5, 20))

    def test_dia_20_pertenece_al_par_5_20(self):
        self.assertEqual(inferir_par(date(2026, 2, 20)), (5, 20))

    def test_dia_15_pertenece_al_par_15_30(self):
        self.assertEqual(inferir_par(date(2026, 2, 15)), (15, 30))

    def test_dia_30_pertenece_al_par_15_30(self):
        self.assertEqual(inferir_par(date(2026, 1, 30)), (15, 30))

    def test_ultimo_dia_febrero_pertenece_al_par_15_30(self):
        # 28 de febrero representa el "30" ajustado a fin de mes
        self.assertEqual(inferir_par(date(2026, 2, 28)), (15, 30))


from types import SimpleNamespace


def _prestamo_fake(capital_pendiente, interes_acumulado_sin_pagar=Decimal('0')):
    return SimpleNamespace(
        capital_pendiente=Decimal(capital_pendiente),
        interes_acumulado_sin_pagar=Decimal(interes_acumulado_sin_pagar),
        estado='ACTIVO',
    )


def _cuota_fake(interes_normal):
    return SimpleNamespace(
        interes_normal=Decimal(interes_normal),
        monto_pagado_principal=Decimal('0'),
        monto_pagado_interes=Decimal('0'),
        monto_pagado_mora=Decimal('0'),
        monto_pendiente=Decimal('0'),
        monto_pendiente_interes=Decimal('0'),
        pagado=False,
        fecha_pago_real=None,
    )


from mi_app.services.amortizacion_service import (
    calcular_interes_pendiente_actual,
    aplicar_pago,
)


class AplicarPagoTests(SimpleTestCase):
    def test_pago_normal_interes_primero_resto_a_capital(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('250000'))
        cuota = _cuota_fake(interes_normal=Decimal('19000'))

        resultado = aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('125000'),
            interes_pagado=Decimal('19000'),
            mora_pagada=Decimal('0'),
        )

        self.assertEqual(prestamo.capital_pendiente, Decimal('125000'))
        self.assertEqual(prestamo.interes_acumulado_sin_pagar, Decimal('0'))
        self.assertEqual(resultado['capital_antes'], Decimal('250000'))
        self.assertEqual(resultado['capital_despues'], Decimal('125000'))
        self.assertFalse(resultado['cerrado'])

    def test_pago_parcial_capital_baja_a_189000(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('250000'))
        cuota = _cuota_fake(interes_normal=Decimal('19000'))

        aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('61000'),
            interes_pagado=Decimal('19000'),
            mora_pagada=Decimal('0'),
        )

        self.assertEqual(prestamo.capital_pendiente, Decimal('189000'))

    def test_solo_pagar_interes_no_baja_el_capital(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('250000'))
        cuota = _cuota_fake(interes_normal=Decimal('19000'))

        aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('0'),
            interes_pagado=Decimal('19000'),
            mora_pagada=Decimal('0'),
        )

        self.assertEqual(prestamo.capital_pendiente, Decimal('250000'))
        self.assertEqual(prestamo.interes_acumulado_sin_pagar, Decimal('0'))

    def test_abono_extraordinario_reduce_capital(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('300000'))
        cuota = _cuota_fake(interes_normal=Decimal('22500'))

        aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('100000'),
            interes_pagado=Decimal('22500'),
            mora_pagada=Decimal('0'),
        )

        self.assertEqual(prestamo.capital_pendiente, Decimal('200000'))

    def test_interes_pagado_incompleto_se_arrastra(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('250000'))
        cuota = _cuota_fake(interes_normal=Decimal('19000'))

        aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('0'),
            interes_pagado=Decimal('10000'),
            mora_pagada=Decimal('0'),
        )

        self.assertEqual(prestamo.interes_acumulado_sin_pagar, Decimal('9000'))

    def test_interes_pendiente_actual_suma_lo_arrastrado(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('250000'), interes_acumulado_sin_pagar=Decimal('9000'))
        cuota = _cuota_fake(interes_normal=Decimal('19000'))

        pendiente = calcular_interes_pendiente_actual(prestamo, cuota)

        self.assertEqual(pendiente, Decimal('28000'))

    def test_cierre_cuando_capital_e_interes_llegan_a_cero(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('125000'))
        cuota = _cuota_fake(interes_normal=Decimal('9000'))

        resultado = aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('125000'),
            interes_pagado=Decimal('9000'),
            mora_pagada=Decimal('0'),
        )

        self.assertTrue(resultado['cerrado'])
        self.assertEqual(prestamo.estado, 'COMPLETADO')
        self.assertTrue(cuota.pagado)

    def test_no_cierra_si_capital_en_cero_pero_falta_interes(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('125000'))
        cuota = _cuota_fake(interes_normal=Decimal('9000'))

        resultado = aplicar_pago(
            prestamo, cuota,
            capital_pagado=Decimal('125000'),
            interes_pagado=Decimal('5000'),
            mora_pagada=Decimal('0'),
        )

        self.assertFalse(resultado['cerrado'])
        self.assertEqual(prestamo.interes_acumulado_sin_pagar, Decimal('4000'))

    def test_capital_pagado_no_puede_superar_el_pendiente(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('50000'))
        cuota = _cuota_fake(interes_normal=Decimal('3750'))

        with self.assertRaises(ValueError):
            aplicar_pago(
                prestamo, cuota,
                capital_pagado=Decimal('60000'),
                interes_pagado=Decimal('0'),
                mora_pagada=Decimal('0'),
            )

    def test_interes_pagado_no_puede_superar_el_pendiente(self):
        prestamo = _prestamo_fake(capital_pendiente=Decimal('50000'))
        cuota = _cuota_fake(interes_normal=Decimal('3750'))

        with self.assertRaises(ValueError):
            aplicar_pago(
                prestamo, cuota,
                capital_pagado=Decimal('0'),
                interes_pagado=Decimal('4000'),
                mora_pagada=Decimal('0'),
            )
