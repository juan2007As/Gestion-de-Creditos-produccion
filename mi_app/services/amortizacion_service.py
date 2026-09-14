"""
Motor de amortizacion compartido entre Prestamo/Cuota y PrestamoRapido/CuotaRapida.

Ver docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md para las
reglas de negocio completas. Funciones puras: reciben Decimal/date, no tocan
la base de datos ni hacen .save() -- eso lo decide quien las llama.
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal

TASA_INTERES_DEFAULT = Decimal('15')
DIAS_ANCLA = (5, 15, 20, 30)

# Repartir el capital en N cuotas nominales (capital_total / N, cada una
# quantize(0.01)) casi nunca cierra exacto en $0 -- ej. 500000/6 =
# 83333.33 x 6 = 499999.98, deja $0.02 sin cobrar. Sin tolerancia, ese
# residuo de centavos vuelve a generar una cuota nueva entera (con su
# propio interes calculado) para $0.02 de capital, en vez de dar el
# credito por cerrado. $1 es insignificante en pesos colombianos.
TOLERANCIA_CIERRE = Decimal('1.00')


def calcular_interes_periodo(capital_pendiente, tasa_porcentaje=TASA_INTERES_DEFAULT):
    """
    Interes de una quincena = capital_pendiente * tasa% / 2. Sin redondeo
    (decision explicita del dueno: "no hay que redondear" -- reemplaza la
    regla anterior de redondeo al millar).
    """
    capital_pendiente = Decimal(capital_pendiente)
    tasa_porcentaje = Decimal(tasa_porcentaje)
    interes = capital_pendiente * (tasa_porcentaje / Decimal('100')) / Decimal('2')
    return interes.quantize(Decimal('0.01'))


def generar_cronograma_interes(capital_base, tasa_porcentaje, num_cuotas):
    """
    Genera la lista de `num_cuotas` intereses por cuota segun la regla real
    del negocio: el interes de las primeras 2 cuotas (1 mes) es
    calcular_interes_periodo(capital_base, tasa); cada PAR siguiente de
    cuotas es la MITAD del par anterior, de forma fija -- no se recalcula
    dinamicamente cuota a cuota. Solo un abono extraordinario a capital
    dispara un recalculo (ver vistas de pago), que vuelve a arrancar esta
    misma secuencia desde el nuevo capital restante.
    """
    base = calcular_interes_periodo(capital_base, tasa_porcentaje)
    intereses = []
    for i in range(num_cuotas):
        par_index = i // 2
        intereses.append((base / (Decimal('2') ** par_index)).quantize(Decimal('0.01')))
    return intereses


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


def inferir_par(fecha):
    """
    Dada una fecha ancla ya existente (de una cuota ya creada), infiere a
    que par pertenece: (5, 20) o (15, 30). Los unicos anclas posibles son
    {5, 15, 20, 30} (30 ajustado a fin de mes en meses cortos/febrero).
    """
    if fecha.day in (5, 20):
        return (5, 20)
    return (15, 30)


def generar_fechas_cuotas(fecha_desembolso, num_cuotas):
    """Genera las `num_cuotas` fechas de pago siguientes al desembolso."""
    par, primera = determinar_par_y_primera_fecha(fecha_desembolso)
    fechas = [primera]
    actual = primera
    for _ in range(num_cuotas - 1):
        actual = siguiente_fecha_en_par(actual, par)
        fechas.append(actual)
    return fechas


def calcular_interes_pendiente_actual(prestamo, cuota):
    """Interes que corresponde pagar ahora: el de esta cuota + lo arrastrado."""
    return cuota.interes_normal + prestamo.interes_acumulado_sin_pagar


def interes_pendiente_total_desde_cuotas(prestamo, cuotas):
    """
    Igual que Prestamo._interes_pendiente_total_credito()/
    PrestamoRapido._interes_pendiente_total_credito() (interes de la cuota
    activa + todas las futuras aun no TRASLADADA), pero operando en
    Python puro sobre un iterable de cuotas YA CARGADO (por ejemplo via
    prefetch_related), sin lanzar queries nuevas. Usar esta version en
    contextos masivos/agregados (reportes sobre muchos prestamos a la
    vez) donde llamar la property de cada instancia causaria N+1 -- el
    .exclude()/.filter() de la property no reutiliza el cache de
    prefetch_related, cada llamada golpea la base de datos de nuevo.
    """
    activas = sorted(
        (c for c in cuotas if c.estado != 'TRASLADADA'),
        key=lambda c: c.numero_cuota,
    )
    if not activas:
        return prestamo.interes_acumulado_sin_pagar
    cuota_activa = activas[0]
    interes_pendiente_actual = cuota_activa.interes_normal + prestamo.interes_acumulado_sin_pagar
    interes_futuro = sum(
        (c.interes_normal for c in activas if c.numero_cuota > cuota_activa.numero_cuota),
        Decimal('0'),
    )
    return interes_pendiente_actual + interes_futuro


def aplicar_pago(prestamo, cuota, capital_pagado, interes_pagado, mora_pagada):
    """
    Aplica un pago ya validado sobre `prestamo` y `cuota` (muta los objetos
    en memoria, no hace .save() -- eso lo decide quien llama, dentro de una
    transaccion). Devuelve un resumen para registrar en el modelo Pago.
    """
    capital_pagado = Decimal(capital_pagado)
    interes_pagado = Decimal(interes_pagado)
    mora_pagada = Decimal(mora_pagada)

    capital_antes = prestamo.capital_pendiente
    interes_pendiente = calcular_interes_pendiente_actual(prestamo, cuota)

    if capital_pagado > capital_antes:
        raise ValueError(
            f"capital_pagado ({capital_pagado}) supera el capital pendiente ({capital_antes})"
        )
    if interes_pagado > interes_pendiente:
        raise ValueError(
            f"interes_pagado ({interes_pagado}) supera el interes pendiente ({interes_pendiente})"
        )

    prestamo.capital_pendiente = capital_antes - capital_pagado
    prestamo.interes_acumulado_sin_pagar = interes_pendiente - interes_pagado

    cuota.monto_pagado_principal += capital_pagado
    cuota.monto_pagado_interes += interes_pagado
    cuota.monto_pagado_mora += mora_pagada
    cuota.monto_pendiente = prestamo.capital_pendiente
    cuota.monto_pendiente_interes = prestamo.interes_acumulado_sin_pagar

    cerrado = (
        prestamo.capital_pendiente <= TOLERANCIA_CIERRE
        and prestamo.interes_acumulado_sin_pagar <= TOLERANCIA_CIERRE
    )
    if cerrado:
        # Snap a $0 exacto -- el residuo (si lo hay) es de redondeo, no
        # deuda real; no debe quedar un "$0.02 pendiente" fantasma en
        # ningun lado despues de cerrar.
        prestamo.capital_pendiente = Decimal('0')
        prestamo.interes_acumulado_sin_pagar = Decimal('0')
        cuota.monto_pendiente = Decimal('0')
        cuota.monto_pendiente_interes = Decimal('0')
        cuota.pagado = True
        cuota.fecha_pago_real = date.today()
        prestamo.estado = 'COMPLETADO'

    return {
        'capital_antes': capital_antes,
        'capital_despues': prestamo.capital_pendiente,
        'cerrado': cerrado,
    }
