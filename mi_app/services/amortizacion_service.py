"""
Motor de amortizacion compartido entre Prestamo/Cuota y PrestamoRapido/CuotaRapida.

Ver docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md para las
reglas de negocio completas. Funciones puras: reciben Decimal/date, no tocan
la base de datos ni hacen .save() -- eso lo decide quien las llama.
"""
from decimal import Decimal, ROUND_HALF_UP

TASA_INTERES_DEFAULT = Decimal('15')


def redondear_al_millar(valor):
    """Redondea un Decimal al millar (1000) mas cercano."""
    valor = Decimal(valor)
    return (valor / Decimal('1000')).to_integral_value(rounding=ROUND_HALF_UP) * Decimal('1000')


def calcular_interes_periodo(capital_pendiente, tasa_porcentaje=TASA_INTERES_DEFAULT):
    """
    Interes de una quincena = capital_pendiente * tasa% / 2, redondeado al millar.
    """
    capital_pendiente = Decimal(capital_pendiente)
    tasa_porcentaje = Decimal(tasa_porcentaje)
    interes = capital_pendiente * (tasa_porcentaje / Decimal('100')) / Decimal('2')
    return redondear_al_millar(interes)
