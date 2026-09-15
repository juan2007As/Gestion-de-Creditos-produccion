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

# El sistema trabaja en pesos colombianos enteros -- no hay centavos
# (decision explicita del dueno: "no son dolares, son pesos"). Todo monto
# calculado por este servicio se redondea a la unidad peso.
UNIDAD_MONETARIA = Decimal('1')

# Repartir el capital en N cuotas nominales (capital_total / N, cada una
# redondeada a la unidad peso) casi nunca cierra exacto en $0 -- ej.
# 500000/6 = 83333.33... -> 83333 x 6 = 499998, deja $2 sin cobrar. Sin
# tolerancia, ese residuo de redondeo vuelve a generar una cuota nueva
# entera (con su propio interes calculado) para esos pocos pesos, en vez
# de dar el credito por cerrado. Con 6 cuotas como maximo, el residuo de
# redondeo nunca supera unos pocos pesos -- insignificante en pesos
# colombianos, $10 de margen es mas que suficiente.
TOLERANCIA_CIERRE = Decimal('10')


def calcular_interes_periodo(capital_pendiente, tasa_porcentaje=TASA_INTERES_DEFAULT):
    """
    Interes de una quincena "de referencia" = capital_pendiente * tasa% / 2,
    redondeado a la unidad peso (sin centavos -- decision explicita del
    dueno). Usado hoy solo como estimado/preview (ej. antes de conocer las
    fechas reales de las cuotas) -- el interes REAL que se cobra por cuota
    sale de interes_para_cuota()/generar_cronograma_interes(), que cuentan
    los dias reales entre fechas en vez de asumir 15 dias fijos.
    """
    capital_pendiente = Decimal(capital_pendiente)
    tasa_porcentaje = Decimal(tasa_porcentaje)
    interes = capital_pendiente * (tasa_porcentaje / Decimal('100')) / Decimal('2')
    return interes.quantize(UNIDAD_MONETARIA)


def tasa_diaria(capital_pendiente, tasa_porcentaje=TASA_INTERES_DEFAULT):
    """
    Interes por dia sobre el capital pendiente: el interes de una quincena
    completa (capital*tasa%/2) dividido entre 15. Sin redondear aqui -- se
    redondea el interes final de cada cuota, despues de multiplicar por
    los dias reales del periodo, para no perder precision en el camino.
    """
    capital_pendiente = Decimal(capital_pendiente)
    tasa_porcentaje = Decimal(tasa_porcentaje)
    return capital_pendiente * (tasa_porcentaje / Decimal('100')) / Decimal('2') / Decimal('15')


def interes_para_cuota(capital_base, tasa_porcentaje, par_index, fecha_anterior, fecha_cuota):
    """
    Interes real de una cuota individual: la tasa diaria del par que le
    toca (par_index 0 = primeras 2 cuotas, 1 = siguiente par -- la mitad de
    la tasa, 2 -- un cuarto, etc; el mismo patron "mitad cada 2 cuotas" que
    ya regia el cronograma fijo) multiplicada por los dias reales entre
    `fecha_anterior` (la fecha del periodo previo, o el desembolso si es
    la primera cuota) y `fecha_cuota`.

    Conteo de dias INCLUSIVO (+1): del 13 al 15 son 3 dias, no 2 --
    decision explicita del dueno/cliente (caso real: prestamo el 13,
    primera cuota el 30 -> cobra por 18 dias, no 17), confirmada aun
    sabiendo que un periodo "normal" de 15 dias de diferencia calendario
    tambien cuenta como 15 dias de interes bajo este conteo (14 dias de
    diferencia + 1).
    """
    dias = (fecha_cuota - fecha_anterior).days + 1
    tasa_del_par = tasa_diaria(capital_base, tasa_porcentaje) / (Decimal('2') ** par_index)
    return (tasa_del_par * dias).quantize(UNIDAD_MONETARIA)


def generar_cronograma_interes(capital_base, tasa_porcentaje, fecha_desde, fechas_cuotas):
    """
    Genera el interes REAL (por dias transcurridos, ver interes_para_cuota)
    de cada cuota en `fechas_cuotas`, contando desde `fecha_desde` (el
    desembolso del prestamo, o la fecha desde la que arranca un recalculo
    por abono extraordinario) para la primera cuota, y desde la fecha de
    la cuota anterior para las siguientes. La tasa se sigue reduciendo a
    la mitad cada 2 cuotas (mismo patron que el cronograma fijo de antes),
    pero ya no se recalcula dinamicamente cuota a cuota salvo por un nuevo
    abono extraordinario a capital (ver vistas de pago), que vuelve a
    arrancar esta misma secuencia desde el nuevo capital restante.
    """
    intereses = []
    fecha_anterior = fecha_desde
    for i, fecha_cuota in enumerate(fechas_cuotas):
        intereses.append(interes_para_cuota(capital_base, tasa_porcentaje, i // 2, fecha_anterior, fecha_cuota))
        fecha_anterior = fecha_cuota
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
