from decimal import Decimal
from django.test import SimpleTestCase

from mi_app.services.amortizacion_service import redondear_al_millar, calcular_interes_periodo


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
