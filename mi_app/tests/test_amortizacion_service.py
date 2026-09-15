from decimal import Decimal
from datetime import date
from django.test import SimpleTestCase

from mi_app.services.amortizacion_service import (
    calcular_interes_periodo,
    tasa_diaria,
    interes_para_cuota,
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


class TasaDiariaTests(SimpleTestCase):
    def test_capital_200000_tasa_15_da_1000_por_dia(self):
        # El mismo ejemplo real del cliente: 200000 * 15% / 2 / 15 = 1000/dia.
        self.assertEqual(tasa_diaria(Decimal('200000'), Decimal('15')), Decimal('1000'))

    def test_capital_500000_tasa_15_da_2500_por_dia(self):
        self.assertEqual(tasa_diaria(Decimal('500000'), Decimal('15')), Decimal('2500'))


class InteresParaCuotaTests(SimpleTestCase):
    def test_ejemplo_real_del_cliente_18000_por_17_dias_de_diferencia(self):
        # 200000 al 15%, desembolsado el 13/09, primera cuota el 30/09:
        # 17 dias de diferencia + 1 (conteo inclusivo, confirmado con el
        # dueno para que calce con el ejemplo real) = 18 dias x 1000/dia.
        interes = interes_para_cuota(
            Decimal('200000'), Decimal('15'), 0,
            date(2026, 9, 13), date(2026, 9, 30),
        )
        self.assertEqual(interes, Decimal('18000'))

    def test_par_index_1_es_la_mitad_de_la_tasa_diaria(self):
        # tasa del par 1 = 500/dia; 15 dias de diferencia + 1 = 16 dias.
        interes = interes_para_cuota(
            Decimal('200000'), Decimal('15'), 1,
            date(2026, 10, 15), date(2026, 10, 30),
        )
        self.assertEqual(interes, Decimal('8000'))


class GenerarCronogramaInteresTests(SimpleTestCase):
    def test_ejemplo_real_del_cliente_200000_15_por_ciento_desembolso_irregular(self):
        # Caso real reportado por el cliente: prestado el 13/09, primera
        # cuota cae el 30/09 (17 dias, no 15, porque el 13 no es fecha
        # ancla). El cronograma completo (4 cuotas) cobra los dias reales
        # de cada tramo, con la tasa diaria bajando a la mitad cada 2
        # cuotas (igual patron que el cronograma fijo de antes).
        fecha_desembolso = date(2026, 9, 13)
        fechas = [date(2026, 9, 30), date(2026, 10, 15), date(2026, 10, 30), date(2026, 11, 15)]
        cronograma = generar_cronograma_interes(Decimal('200000'), Decimal('15'), fecha_desembolso, fechas)
        self.assertEqual(
            cronograma,
            [Decimal('18000'), Decimal('16000'), Decimal('8000'), Decimal('8500')],
        )

    def test_periodos_de_15_dias_exactos_dan_igual_que_el_cronograma_fijo_de_antes(self):
        # Si cada tramo mide exactamente 15 dias (conteo inclusivo, 14 de
        # diferencia real entre fechas), el resultado coincide con el
        # viejo cronograma fijo -- confirma que el cambio no rompe el caso
        # "normal" sin desembolso irregular.
        fecha_desembolso = date(2026, 1, 1)
        fechas = [date(2026, 1, 15), date(2026, 1, 29), date(2026, 2, 12), date(2026, 2, 26)]
        cronograma = generar_cronograma_interes(Decimal('500000'), Decimal('15'), fecha_desembolso, fechas)
        self.assertEqual(
            cronograma,
            [Decimal('37500'), Decimal('37500'), Decimal('18750'), Decimal('18750')],
        )

    def test_una_sola_cuota(self):
        cronograma = generar_cronograma_interes(
            Decimal('100000'), Decimal('15'), date(2026, 1, 1), [date(2026, 1, 15)]
        )
        self.assertEqual(cronograma, [Decimal('7500')])


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
