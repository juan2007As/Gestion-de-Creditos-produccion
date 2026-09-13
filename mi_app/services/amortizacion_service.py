"""
Motor de amortizacion compartido entre Prestamo/Cuota y PrestamoRapido/CuotaRapida.

Ver docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md para las
reglas de negocio completas. Funciones puras: reciben Decimal/date, no tocan
la base de datos ni hacen .save() -- eso lo decide quien las llama.
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

TASA_INTERES_DEFAULT = Decimal('15')
DIAS_ANCLA = (5, 15, 20, 30)


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


def ultimo_dia_valido_mes(anio, mes, dia):
    """Si `dia` no existe en ese mes (ej. 30 en febrero), devuelve el ultimo dia real del mes."""
    ultimo = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(dia, ultimo))


def _siguiente_mes(anio, mes):
    if mes == 12:
        return anio + 1, 1
    return anio, mes + 1


def determinar_par_y_primera_fecha(fecha_desembolso, dias_minimos=15):
    """
    Encuentra la primera fecha ancla (de {5,15,20,30}) tal que
    (fecha_ancla - fecha_desembolso).days > dias_minimos (estrictamente mas
    de 15, no >=15). Devuelve (par, primera_fecha), donde `par` es (5, 20)
    o (15, 30) segun a cual pertenezca el dia encontrado.
    """
    fecha_minima = fecha_desembolso + timedelta(days=dias_minimos)
    anio, mes = fecha_minima.year, fecha_minima.month
    for _ in range(36):  # tope de seguridad: 3 anios
        for dia in DIAS_ANCLA:
            fecha_ancla = ultimo_dia_valido_mes(anio, mes, dia)
            if (fecha_ancla - fecha_desembolso).days > dias_minimos:
                par = (5, 20) if dia in (5, 20) else (15, 30)
                return par, fecha_ancla
        anio, mes = _siguiente_mes(anio, mes)
    raise ValueError(f"No se encontro fecha ancla dentro de 3 anios desde {fecha_desembolso}")


def siguiente_fecha_en_par(fecha_actual, par):
    """
    Dada la fecha actual (que ya es una ocurrencia de `par`) y el par
    (ej (5, 20)), devuelve la siguiente fecha quincenal dentro del mismo par.
    """
    d1, d2 = par
    anio, mes = fecha_actual.year, fecha_actual.month
    ancla_d1 = ultimo_dia_valido_mes(anio, mes, d1)
    if fecha_actual == ancla_d1:
        return ultimo_dia_valido_mes(anio, mes, d2)
    anio, mes = _siguiente_mes(anio, mes)
    return ultimo_dia_valido_mes(anio, mes, d1)


def generar_fechas_cuotas(fecha_desembolso, num_cuotas):
    """Genera las `num_cuotas` fechas de pago siguientes al desembolso."""
    par, primera = determinar_par_y_primera_fecha(fecha_desembolso)
    fechas = [primera]
    actual = primera
    for _ in range(num_cuotas - 1):
        actual = siguiente_fecha_en_par(actual, par)
        fechas.append(actual)
    return fechas
