from decimal import Decimal
from datetime import date
from django.test import SimpleTestCase

from mi_app.services.amortizacion_service import (
    redondear_al_millar,
    calcular_interes_periodo,
    ultimo_dia_valido_mes,
    determinar_par_y_primera_fecha,
    siguiente_fecha_en_par,
    generar_fechas_cuotas,
)


class RedondearAlMillarTests(SimpleTestCase):
    def test_redondea_hacia_arriba_desde_mitad(self):
        self.assertEqual(redondear_al_millar(Decimal('18750')), Decimal('19000'))

    def test_redondea_hacia_abajo(self):
        self.assertEqual(redondear_al_millar(Decimal('18400')), Decimal('18000'))

    def test_valor_exacto_no_cambia(self):
        self.assertEqual(redondear_al_millar(Decimal('37500')), Decimal('38000'))


class CalcularInteresPeriodoTests(SimpleTestCase):
    def test_capital_500000(self):
        # 500000*15%/2 = 37500 exacto, a mitad de camino entre 37000 y 38000 ->
        # redondeo consistente (mismo criterio que 18750->19000) sube a 38000.
        self.assertEqual(calcular_interes_periodo(Decimal('500000')), Decimal('38000'))

    def test_capital_250000_redondea_a_19000(self):
        self.assertEqual(calcular_interes_periodo(Decimal('250000')), Decimal('19000'))

    def test_capital_cero_da_interes_cero(self):
        self.assertEqual(calcular_interes_periodo(Decimal('0')), Decimal('0'))


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
