# Interés dinámico sobre saldo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el interés fijo calculado una sola vez al crear un préstamo por un interés dinámico recalculado sobre el capital pendiente real en cada quincena, con pagos manuales de capital/interés/mora en campos separados sin los topes artificiales actuales, unificando la lógica entre `Prestamo`/`Cuota` y `PrestamoRapido`/`CuotaRapida` en un solo servicio compartido.

**Architecture:** Nuevo módulo `mi_app/services/amortizacion_service.py` con funciones puras (sin efectos secundarios, sin acceso a BD) para: redondeo, cálculo de interés por período, generación de fechas quincenales, y aplicación de un pago. Los modelos y las vistas de creación/pago pasan a delegar en este servicio en vez de tener cada uno su propia copia de la lógica (la duplicación entre `Cuota` y `CuotaRapida` ya causó un bug de dinero real esta sesión).

**Tech Stack:** Django 4.2.30, Python 3.10, `Decimal` para todo cálculo de dinero (nunca `float`), Django test runner / pytest para los tests.

**Spec:** `docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md`

## Global Constraints

- Todo cálculo de dinero usa `Decimal`, nunca `float` — ver `reglas/data-rules.md` §2 y el bug ya corregido en `Cuota.total_a_pagar()`.
- No hay préstamos reales en producción hoy (confirmado por el dueño) — no hace falta script de migración de datos de clientes, solo migración de esquema.
- El redondeo del interés es **al millar más cercano** (`Decimal('1000')`), nunca al capital.
- La fecha ancla de una cuota debe estar **estrictamente más de 15 días** después de la fecha de referencia (no `>=15`, confirmado explícitamente por el dueño).
- Mora: monto fijo en pesos por día, tomado de `prestamo.mora_diaria_pesos` si está seteado, si no de `Configuracion.tasa_mora_diaria` (global). Empieza a contar después de `Configuracion.dias_gracia_mora` días (pasa de 5 a 2 en este plan, para que la mora arranque el día 3).
- Pago con 3 campos manuales (capital / interés / mora) — nunca un monto único que el sistema reparte solo. La mora nunca se auto-descuenta de un pago general.
- **Fuera de alcance de este plan** (seguimiento aparte): convertir la UI de `registrar_pago_rapido.html` (un solo campo `monto_pagado`) a 3 campos separados como `pagar_cuota_especifica.html`. Este plan corrige su **cálculo** (topes correctos, orden interés→capital, usa el servicio compartido) pero mantiene su interfaz de un solo campo.

---

## Task 1: Migración de esquema

**Files:**
- Modify: `mi_app/models.py:511-543` (clase `Prestamo`)
- Modify: `mi_app/models.py:927` (clase `Pago`, agregar campos al final de los existentes, antes de cualquier `Meta`)
- Modify: `mi_app/models.py:1058-1085` (clase `PrestamoRapido`)
- Modify: `mi_app/models.py:1019-1032` (clase `Configuracion`, campo `dias_gracia_mora`)
- Create: migración Django generada con `makemigrations` (nombre exacto se conoce al correr el comando)
- Create: `mi_app/migrations/00XX_dias_gracia_mora_default.py` (migración de datos, ver Step 4)

**Interfaces:**
- Produces: `Prestamo.capital_pendiente`, `Prestamo.mora_diaria_pesos`, `Prestamo.interes_acumulado_sin_pagar`, mismos tres campos en `PrestamoRapido`, `Pago.capital_antes`, `Pago.capital_despues` — todos como `Decimal` accesibles como atributos normales de instancia.

- [ ] **Step 1: Agregar los campos nuevos a `Prestamo`**

En `mi_app/models.py`, dentro de la clase `Prestamo` (después de la línea `notas_admin = models.TextField(blank=True)`, línea 539), agregar:

```python
    capital_pendiente = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        help_text="Saldo de capital vivo. Fuente única de verdad — no se reparte en las cuotas."
    )
    mora_diaria_pesos = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Mora fija en pesos por día para este préstamo. Si es null, se usa Configuracion.tasa_mora_diaria."
    )
    interes_acumulado_sin_pagar = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        help_text="Interés de períodos anteriores que quedó sin pagar y se arrastra."
    )
```

- [ ] **Step 2: Agregar los mismos tres campos a `PrestamoRapido`**

En la clase `PrestamoRapido` (después de sus campos existentes, antes de `def __str__`, cerca de la línea 1085), agregar el mismo bloque de 3 campos que en el Step 1 (idéntico, copiado literal).

- [ ] **Step 3: Agregar los campos de snapshot a `Pago`**

En la clase `Pago` (`mi_app/models.py:927`), localizar el final de sus campos de instancia (antes de cualquier método o `Meta`) y agregar:

```python
    capital_antes = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Saldo de capital del préstamo justo antes de este pago."
    )
    capital_despues = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Saldo de capital del préstamo justo después de este pago."
    )
```

- [ ] **Step 4: Cambiar el default de `dias_gracia_mora` y generar migración de datos**

En `mi_app/models.py:1029-1032`, cambiar:

```python
    dias_gracia_mora = models.IntegerField(
        default=5,
        help_text="Días de gracia antes de empezar a cobrar mora (PROBLEMA #12)"
    )
```

por:

```python
    dias_gracia_mora = models.IntegerField(
        default=2,
        help_text="Días de gracia antes de empezar a cobrar mora — mora arranca el día 3 de atraso."
    )
```

- [ ] **Step 5: Generar las migraciones de esquema**

Run: `python manage.py makemigrations mi_app`
Expected: crea un archivo nuevo en `mi_app/migrations/` (ej. `0003_...py`) con los `AddField` de los 5 campos nuevos y el `AlterField` de `dias_gracia_mora`.

- [ ] **Step 6: Escribir la migración de datos para `Configuracion` existente**

Crear `mi_app/migrations/00XX_actualizar_dias_gracia_existente.py` (usar el número que siga al de Step 5):

```python
from django.db import migrations


def actualizar_dias_gracia(apps, schema_editor):
    Configuracion = apps.get_model('mi_app', 'Configuracion')
    # Solo actualiza si sigue en el valor viejo (5) — si alguien ya lo
    # cambió a mano a otra cosa, no lo pisamos.
    Configuracion.objects.filter(dias_gracia_mora=5).update(dias_gracia_mora=2)


def revertir(apps, schema_editor):
    Configuracion = apps.get_model('mi_app', 'Configuracion')
    Configuracion.objects.filter(dias_gracia_mora=2).update(dias_gracia_mora=5)


class Migration(migrations.Migration):

    dependencies = [
        ('mi_app', '0003_XXXX'),  # reemplazar por el nombre real generado en Step 5
    ]

    operations = [
        migrations.RunPython(actualizar_dias_gracia, revertir),
    ]
```

- [ ] **Step 7: Aplicar las migraciones localmente**

Run: `python manage.py migrate mi_app`
Expected: `Applying mi_app.0003_..._... OK` y `Applying mi_app.00XX_actualizar... OK`, sin errores.

- [ ] **Step 8: Commit**

```bash
git add mi_app/models.py mi_app/migrations/
git commit -m "feat: campos de esquema para interes dinamico sobre saldo (capital_pendiente, mora_diaria_pesos, interes_acumulado_sin_pagar)"
```

---

## Task 2: Servicio — redondeo e interés por período

**Files:**
- Create: `mi_app/services/amortizacion_service.py`
- Test: `mi_app/tests/test_amortizacion_service.py`

**Interfaces:**
- Produces: `redondear_al_millar(valor: Decimal) -> Decimal`, `calcular_interes_periodo(capital_pendiente: Decimal, tasa_porcentaje: Decimal = Decimal('15')) -> Decimal`.

- [ ] **Step 1: Crear el archivo del servicio con el redondeo**

Create `mi_app/services/amortizacion_service.py`:

```python
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
```

- [ ] **Step 2: Escribir el test que falla para `redondear_al_millar`**

Create `mi_app/tests/test_amortizacion_service.py`:

```python
from decimal import Decimal
from django.test import SimpleTestCase

from mi_app.services.amortizacion_service import redondear_al_millar


class RedondearAlMillarTests(SimpleTestCase):
    def test_redondea_hacia_arriba_desde_mitad(self):
        self.assertEqual(redondear_al_millar(Decimal('18750')), Decimal('19000'))

    def test_redondea_hacia_abajo(self):
        self.assertEqual(redondear_al_millar(Decimal('18400')), Decimal('18000'))

    def test_valor_exacto_no_cambia(self):
        self.assertEqual(redondear_al_millar(Decimal('37500')), Decimal('38000'))
```

Nota sobre el tercer caso: `37500` está exactamente a mitad de camino entre `37000` y `38000`; `ROUND_HALF_UP` redondea la mitad hacia arriba, por eso da `38000`, no `37500`.

- [ ] **Step 3: Correr los tests para confirmar que pasan**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v`
Expected: 3 tests, todos `PASS` (la implementación del Step 1 ya es correcta, este paso es de verificación).

- [ ] **Step 4: Agregar `calcular_interes_periodo` al servicio**

Append to `mi_app/services/amortizacion_service.py`:

```python
def calcular_interes_periodo(capital_pendiente, tasa_porcentaje=TASA_INTERES_DEFAULT):
    """
    Interes de una quincena = capital_pendiente * tasa% / 2, redondeado al millar.
    """
    capital_pendiente = Decimal(capital_pendiente)
    tasa_porcentaje = Decimal(tasa_porcentaje)
    interes = capital_pendiente * (tasa_porcentaje / Decimal('100')) / Decimal('2')
    return redondear_al_millar(interes)
```

- [ ] **Step 5: Escribir los tests de los ejemplos exactos del dueño**

Append to `mi_app/tests/test_amortizacion_service.py`:

```python
from mi_app.services.amortizacion_service import calcular_interes_periodo


class CalcularInteresPeriodoTests(SimpleTestCase):
    def test_capital_500000(self):
        # 500000*15%/2 = 37500 exacto, redondea hacia arriba a 38000 (mismo criterio que 18750->19000)
        self.assertEqual(calcular_interes_periodo(Decimal('500000')), Decimal('38000'))

    def test_capital_250000_redondea_a_19000(self):
        self.assertEqual(calcular_interes_periodo(Decimal('250000')), Decimal('19000'))

    def test_capital_cero_da_interes_cero(self):
        self.assertEqual(calcular_interes_periodo(Decimal('0')), Decimal('0'))
```

- [ ] **Step 6: Correr los tests**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v`
Expected: 6 tests, todos `PASS`.

- [ ] **Step 7: Commit**

```bash
git add mi_app/services/amortizacion_service.py mi_app/tests/test_amortizacion_service.py
git commit -m "feat: calculo de interes dinamico sobre saldo con redondeo al millar"
```

---

## Task 3: Servicio — fechas ancla y generación de calendario

**Files:**
- Modify: `mi_app/services/amortizacion_service.py`
- Test: `mi_app/tests/test_amortizacion_service.py`

**Interfaces:**
- Consumes: nada nuevo (usa `datetime.date`, `datetime.timedelta`, `calendar` de stdlib).
- Produces: `ultimo_dia_valido_mes(anio, mes, dia) -> date`, `determinar_par_y_primera_fecha(fecha_desembolso, dias_minimos=15) -> tuple[tuple[int,int], date]`, `siguiente_fecha_en_par(fecha_actual, par) -> date`, `generar_fechas_cuotas(fecha_desembolso, num_cuotas) -> list[date]`.

- [ ] **Step 1: Escribir los tests que fallan para las fechas (los ejemplos exactos del dueño)**

Append to `mi_app/tests/test_amortizacion_service.py`:

```python
from datetime import date

from mi_app.services.amortizacion_service import (
    ultimo_dia_valido_mes,
    determinar_par_y_primera_fecha,
    siguiente_fecha_en_par,
    generar_fechas_cuotas,
)


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
        # gap exacto de 15 dias al dia 5 (excluido, tiene que ser >15) -> pasa al 15
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
```

- [ ] **Step 2: Correr los tests para confirmar que fallan**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v -k "UltimoDia or DeterminarPar or SiguienteFecha or GenerarFechas"`
Expected: `FAIL` con `ImportError` o `AttributeError` (las funciones todavía no existen).

- [ ] **Step 3: Implementar las funciones de fecha**

Append to `mi_app/services/amortizacion_service.py`:

```python
import calendar
from datetime import date, timedelta

DIAS_ANCLA = (5, 15, 20, 30)


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
```

- [ ] **Step 4: Correr los tests para confirmar que pasan**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v`
Expected: todos los tests del archivo (los de Task 2 + los nuevos) en `PASS`.

- [ ] **Step 5: Commit**

```bash
git add mi_app/services/amortizacion_service.py mi_app/tests/test_amortizacion_service.py
git commit -m "feat: generacion de fechas quincenales por pares (5/20, 15/30) con regla de >15 dias estricto"
```

---

## Task 4: Servicio — aplicar un pago

**Files:**
- Modify: `mi_app/services/amortizacion_service.py`
- Test: `mi_app/tests/test_amortizacion_service.py`

**Interfaces:**
- Consumes: un objeto "préstamo" con atributos `capital_pendiente` e `interes_acumulado_sin_pagar` (funciona igual para `Prestamo` que para `PrestamoRapido`, no importa la clase real); un objeto "cuota" con `interes_normal`, `monto_pagado_principal`, `monto_pagado_interes`, `monto_pagado_mora`, `monto_pendiente`, `monto_pendiente_interes`, `pagado`, `fecha_pago_real` (funciona igual para `Cuota` que `CuotaRapida`).
- Produces: `calcular_interes_pendiente_actual(prestamo, cuota) -> Decimal`, `aplicar_pago(prestamo, cuota, capital_pagado, interes_pagado, mora_pagada) -> dict` con claves `capital_antes`, `capital_despues`, `cerrado` (bool). **No hace `.save()`** — el llamador decide cuándo guardar, dentro de una transacción.

- [ ] **Step 1: Escribir un objeto de prueba simple (fake) para los tests**

Append to `mi_app/tests/test_amortizacion_service.py`, antes de la clase de tests de `aplicar_pago`:

```python
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
```

- [ ] **Step 2: Escribir los tests que fallan, con los ejemplos exactos del dueño**

Append to `mi_app/tests/test_amortizacion_service.py`:

```python
from mi_app.services.amortizacion_service import (
    calcular_interes_pendiente_actual,
    aplicar_pago,
)


class AplicarPagoTests(SimpleTestCase):
    def test_pago_normal_interes_primero_resto_a_capital(self):
        # Interes actual: 19.000, pago recibido: 144.000
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
        # Capital pendiente 250.000, interes 19.000, cliente paga 80.000:
        # 19.000 a interes, 61.000 a capital -> nuevo capital 189.000
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
        # Capital pendiente 300.000, abono 100.000 -> nuevo capital 200.000
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
        # Le tocaban 19.000 de interes, paga solo 10.000 -> quedan 9.000 arrastrados
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
```

- [ ] **Step 3: Correr los tests para confirmar que fallan**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v -k AplicarPago`
Expected: `FAIL` con `ImportError` (las funciones no existen todavía).

- [ ] **Step 4: Implementar `calcular_interes_pendiente_actual` y `aplicar_pago`**

Append to `mi_app/services/amortizacion_service.py`:

```python
from datetime import date as date_cls


def calcular_interes_pendiente_actual(prestamo, cuota):
    """Interes que corresponde pagar ahora: el de esta cuota + lo arrastrado."""
    return cuota.interes_normal + prestamo.interes_acumulado_sin_pagar


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

    cerrado = prestamo.capital_pendiente <= 0 and prestamo.interes_acumulado_sin_pagar <= 0
    if cerrado:
        cuota.pagado = True
        cuota.fecha_pago_real = date_cls.today()
        prestamo.estado = 'COMPLETADO'

    return {
        'capital_antes': capital_antes,
        'capital_despues': prestamo.capital_pendiente,
        'cerrado': cerrado,
    }
```

- [ ] **Step 5: Correr todos los tests del servicio para confirmar que pasan**

Run: `python -m pytest mi_app/tests/test_amortizacion_service.py -v`
Expected: todos los tests (Task 2, 3 y 4) en `PASS`, cero fallos.

- [ ] **Step 6: Commit**

```bash
git add mi_app/services/amortizacion_service.py mi_app/tests/test_amortizacion_service.py
git commit -m "feat: aplicar_pago compartido -- interes primero, capital despues, cierre por saldo en cero"
```

---

## Task 5: Cuota y CuotaRapida usan `mora_diaria_pesos` del préstamo

**Files:**
- Modify: `mi_app/models.py:718-735` (`Cuota.calcular_mora_diaria`)
- Modify: `mi_app/models.py` (`CuotaRapida.calcular_mora_diaria`, mismo patrón, unas líneas después de la definición de `CuotaRapida`)
- Test: `mi_app/tests/test_unit_models.py` (clase `TestCuotaModel`, o una nueva clase en el mismo archivo)

**Interfaces:**
- Consumes: nada nuevo de otras tasks.
- Produces: `Cuota.calcular_mora_diaria()` y `CuotaRapida.calcular_mora_diaria()` siguen devolviendo `Decimal`, mismo nombre y firma — solo cambia de dónde sacan la tasa diaria.

- [ ] **Step 1: Escribir el test que falla**

Append to `mi_app/tests/test_unit_models.py` (dentro de `class TestCalculosCuota:`, después de los tests existentes):

```python
    def test_mora_usa_mora_diaria_pesos_del_prestamo_si_esta_seteada(self, prestamo_activo):
        from datetime import date, timedelta
        prestamo_activo.mora_diaria_pesos = Decimal('3000')
        prestamo_activo.save()

        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('1000'),
            interes_normal=Decimal('100'),
            monto_pendiente_interes=Decimal('100'),
            fecha_pago_esperada=date.today() - timedelta(days=6),  # 6 dias de atraso, gracia=2 -> 4 dias de mora
        )

        self.assertEqual(cuota.calcular_mora_diaria(), Decimal('12000'))  # 4 * 3000

    def test_mora_usa_default_global_si_prestamo_no_tiene_mora_propia(self, prestamo_activo):
        from datetime import date, timedelta
        from mi_app.models import Configuracion
        config = Configuracion.obtener_configuracion()

        cuota = Cuota.objects.create(
            prestamo=prestamo_activo,
            numero_cuota=1,
            monto_original=Decimal('1000'),
            monto_pendiente=Decimal('1000'),
            interes_normal=Decimal('100'),
            monto_pendiente_interes=Decimal('100'),
            fecha_pago_esperada=date.today() - timedelta(days=6),
        )

        self.assertEqual(cuota.calcular_mora_diaria(), Decimal('4') * config.tasa_mora_diaria)
```

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python -m pytest mi_app/tests/test_unit_models.py -k mora_diaria_pesos -v`
Expected: `FAIL` en `test_mora_usa_mora_diaria_pesos_del_prestamo_si_esta_seteada` (da el resultado con la tasa global en vez de la 3000 del préstamo).

- [ ] **Step 3: Modificar `Cuota.calcular_mora_diaria`**

En `mi_app/models.py:718-735`, reemplazar:

```python
    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        PROBLEMA #12 SOLUCIONADO: Incluye período de gracia antes de cobrar mora
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')
        
        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days
        
        # Los primeros N días: No hay mora (período de gracia)
        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')
        
        # Después del período de gracia: Cobrar mora
        dias_mora = dias_atraso - config.dias_gracia_mora
        return Decimal(str(dias_mora)) * config.tasa_mora_diaria
```

por:

```python
    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        Usa prestamo.mora_diaria_pesos si esta seteada; si no, el default
        global de Configuracion.tasa_mora_diaria.
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')
        
        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days
        
        # Los primeros N días: No hay mora (período de gracia)
        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')
        
        # Después del período de gracia: Cobrar mora
        dias_mora = dias_atraso - config.dias_gracia_mora
        tasa_diaria = self.prestamo.mora_diaria_pesos or config.tasa_mora_diaria
        return Decimal(str(dias_mora)) * tasa_diaria
```

- [ ] **Step 4: Modificar `CuotaRapida.calcular_mora_diaria` con el mismo cambio**

En el método `calcular_mora_diaria` de la clase `CuotaRapida` (buscar `def calcular_mora_diaria` dentro de `class CuotaRapida`), reemplazar:

```python
    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        Respeta período de gracia configurado.
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')

        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days

        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')

        dias_mora = dias_atraso - config.dias_gracia_mora
        return Decimal(str(dias_mora)) * config.tasa_mora_diaria
```

por:

```python
    def calcular_mora_diaria(self):
        """
        Calcula la mora acumulada según días de atraso.
        Usa prestamo_rapido.mora_diaria_pesos si esta seteada; si no, el
        default global de Configuracion.tasa_mora_diaria.
        """
        if self.pagado or not self.fecha_pago_esperada:
            return Decimal('0')

        config = Configuracion.obtener_configuracion()
        dias_atraso = (date.today() - self.fecha_pago_esperada).days

        if dias_atraso <= config.dias_gracia_mora:
            return Decimal('0')

        dias_mora = dias_atraso - config.dias_gracia_mora
        tasa_diaria = self.prestamo_rapido.mora_diaria_pesos or config.tasa_mora_diaria
        return Decimal(str(dias_mora)) * tasa_diaria
```

- [ ] **Step 5: Correr los tests para confirmar que pasan**

Run: `python -m pytest mi_app/tests/test_unit_models.py -k mora_diaria_pesos -v`
Expected: 2 tests, `PASS`.

- [ ] **Step 6: Correr toda la suite para confirmar cero regresiones**

Run: `python manage.py test mi_app`
Expected: mismo conteo de failures/errors que antes de este task (documentado en `DEUDA-TECNICA.md`), ninguno nuevo.

- [ ] **Step 7: Commit**

```bash
git add mi_app/models.py mi_app/tests/test_unit_models.py
git commit -m "feat: mora configurable por prestamo/cliente (mora_diaria_pesos), con fallback al default global"
```

---

## Task 6: Crear préstamo (normal) usa el nuevo motor

**Files:**
- Modify: `mi_app/views_core.py:601-834` (`crear_prestamo`), específicamente el bloque de líneas 780-823
- Modify: `mi_app/models.py:15-94` (retirar `calcular_fechas_pago`, ya sin llamadores tras este task y el Task 7)
- Modify: `mi_app/views_core.py:16` (quitar `calcular_fechas_pago` del import)
- Test: `mi_app/tests/test_unit_models.py` o un test de vista nuevo

**Interfaces:**
- Consumes: `mi_app.services.amortizacion_service.generar_fechas_cuotas`, `calcular_interes_periodo`.
- Produces: `Prestamo.capital_pendiente` queda seteado en el monto total al crear; solo la primera `Cuota` tiene `interes_normal` calculado, las demás quedan en `0` (se calculan cuando les toque, en Task 8).

- [ ] **Step 1: Escribir el test de integración que falla**

Añadir en `mi_app/tests/test_integration_workflows.py` (o crear una clase nueva si no existe una adecuada — revisar el archivo primero):

```python
class CrearPrestamoConMotorNuevoTests(TestCase):
    def test_crear_prestamo_setea_capital_pendiente_y_solo_primera_cuota_con_interes(self):
        from mi_app.models import Cliente, Prestamo

        cliente = Cliente.objects.create(nombre="Test Motor Nuevo", celular="3000000000", cedula="999888777")

        self.client.login(username='admin', password='adminpass')  # ajustar segun fixture de auth disponible
        response = self.client.post(reverse('crear_prestamo'), {
            'cliente': cliente.id,
            'monto': '500000',
            'interes_porcentaje': '15',
            'num_cuotas': '4',
        })

        prestamo = Prestamo.objects.get(cliente=cliente)
        self.assertEqual(prestamo.capital_pendiente, Decimal('500000'))

        cuotas = list(prestamo.cuotas.order_by('numero_cuota'))
        self.assertEqual(len(cuotas), 4)
        self.assertEqual(cuotas[0].interes_normal, Decimal('38000'))  # 500000 * 15% / 2 = 37500, redondea a 38000
        self.assertEqual(cuotas[1].interes_normal, Decimal('0'))  # todavia no calculada
        self.assertEqual(cuotas[2].interes_normal, Decimal('0'))
        self.assertEqual(cuotas[3].interes_normal, Decimal('0'))
```

Nota para quien ejecute este step: revisar el nombre exacto del campo de login/fixture de usuario admin usado en los demás tests de `test_integration_workflows.py` (por ejemplo puede requerir crear un `User` con permisos primero) y ajustar el bloque de login de este test para que coincida con el patrón ya usado en ese archivo.

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python manage.py test mi_app.tests.test_integration_workflows.CrearPrestamoConMotorNuevoTests -v 2`
Expected: `FAIL` (hoy todas las cuotas tienen `interes_normal` distinto de 0, calculado de una sola vez).

- [ ] **Step 3: Modificar el bloque de creación en `crear_prestamo`**

En `mi_app/views_core.py:780-823`, reemplazar el bloque completo (desde `# Calcular fechas automáticamente` hasta el `for` que crea las cuotas) por:

```python
            from mi_app.services.amortizacion_service import generar_fechas_cuotas, calcular_interes_periodo

            # Calcular fechas automáticamente: primera ancla a mas de 15 dias
            # del desembolso, siguientes alternando el mismo par (5/20 o 15/30)
            fecha_inicio = date.today()
            fechas_pago = generar_fechas_cuotas(fecha_inicio, num_cuotas)
            fecha_fin_estimada = fechas_pago[-1] if fechas_pago else fecha_inicio

            # Crear préstamo CON VALIDACIONES APLICADAS
            prestamo = Prestamo.objects.create(
                cliente=cliente,
                monto_total=monto,
                interes_porcentaje=interes_porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin_estimada=fecha_fin_estimada,
                tipo_pago='QUINCENAL',
                estado='ACTIVO',
                capital_pendiente=monto,
            )

            # Capital de referencia por cuota -- solo informativo para la UI,
            # el capital real vive en prestamo.capital_pendiente (ver spec).
            capital_por_cuota = (monto / Decimal(num_cuotas)).quantize(Decimal('0.01'))

            # Solo la primera cuota tiene interes calculado ya (se conoce el
            # capital inicial completo); las demas se calculan cuando les
            # toque ser la cuota actual (Task 8).
            interes_primera_cuota = calcular_interes_periodo(monto, interes_porcentaje)

            for i, fecha_pago in enumerate(fechas_pago, 1):
                interes_cuota = interes_primera_cuota if i == 1 else Decimal('0')
                Cuota.objects.create(
                    prestamo=prestamo,
                    numero_cuota=i,
                    monto_original=capital_por_cuota,
                    monto_pendiente=monto if i == 1 else Decimal('0'),
                    interes_normal=interes_cuota,
                    monto_pendiente_interes=interes_cuota,
                    fecha_pago_esperada=fecha_pago
                )
```

- [ ] **Step 4: Quitar el import de `calcular_fechas_pago` de `views_core.py`**

En `mi_app/views_core.py:16`, quitar `calcular_fechas_pago` de la lista de imports:

```python
from .models import Cliente, Prestamo, Cuota, Pago, Configuracion, PrestamoRapido, PagoPrestamoRapido, CuotaRapida, ListaNegra, AuditoriaBackup
```

También quitar la función local `obtener_proximas_fechas_pago` (líneas 629-636, que hacía de wrapper) y su único uso (línea 783 en el original, ya reemplazado en el Step 3 por `generar_fechas_cuotas` directo).

- [ ] **Step 5: Confirmar que `calcular_fechas_pago` no se retira todavía**

`crear_prestamo_rapido` (Task 7) todavía llama a `calcular_fechas_pago` directamente — **no borrar la función en este task**, se retira recién en el Task 7 (Step 5 de ese task), una vez que ningún caller la use. Este task solo deja de usarla desde `crear_prestamo`.

- [ ] **Step 6: Correr el test para confirmar que pasa**

Run: `python manage.py test mi_app.tests.test_integration_workflows.CrearPrestamoConMotorNuevoTests -v 2`
Expected: `PASS`.

- [ ] **Step 7: Correr toda la suite para confirmar cero regresiones nuevas**

Run: `python manage.py test mi_app`
Expected: mismo conteo base de failures/errors documentado en `DEUDA-TECNICA.md`, sin nuevos. Si aparecen nuevos fallos en tests que dependían del `interes_normal` fijo de todas las cuotas (por ejemplo en `resumen_financiero`), anotarlos y decidir si ese test se actualiza como parte de este mismo commit (son consecuencia directa y esperada del cambio de modelo).

- [ ] **Step 8: Commit**

```bash
git add mi_app/views_core.py mi_app/models.py mi_app/tests/test_integration_workflows.py
git commit -m "feat: crear_prestamo usa el motor de interes dinamico -- capital_pendiente + solo primera cuota calculada"
```

---

## Task 7: Crear préstamo rápido usa el mismo motor

**Files:**
- Modify: `mi_app/views_core.py:2939-3007` (`crear_prestamo_rapido`), bloque de líneas 2973-3004
- Test: agregar a la misma clase de test de integración del Task 6, o una paralela

**Interfaces:**
- Consumes: mismo `generar_fechas_cuotas`, `calcular_interes_periodo` del servicio.
- Produces: mismo comportamiento que Task 6 pero sobre `PrestamoRapido`/`CuotaRapida`.

- [ ] **Step 1: Escribir el test que falla**

Append a la misma clase o una nueva en `mi_app/tests/test_integration_workflows.py`:

```python
    def test_crear_prestamo_rapido_setea_capital_pendiente_y_solo_primera_cuota(self):
        from mi_app.models import Cliente, PrestamoRapido

        cliente = Cliente.objects.create(nombre="Test Rapido Motor Nuevo", celular="3000000001", cedula="999888778")

        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('crear_prestamo_rapido'), {
            'cliente_id': cliente.id,
            'monto': '300000',
            'interes_porcentaje': '15',
            'usar_cuotas': 'on',
            'num_cuotas': '2',
        })

        prestamo = PrestamoRapido.objects.get(cliente=cliente)
        self.assertEqual(prestamo.capital_pendiente, Decimal('300000'))

        cuotas = list(prestamo.cuotas_rapidas.order_by('numero_cuota'))
        self.assertEqual(cuotas[0].interes_normal, Decimal('23000'))  # 300000 * 15% / 2 = 22500, redondea a 23000
        self.assertEqual(cuotas[1].interes_normal, Decimal('0'))
```

Nota: revisar los nombres exactos de campos que espera `PrestamoRapidoForm` (los usados en el POST del test) antes de correrlo — leer `mi_app/forms.py` si el test falla por validación de formulario en vez de por el comportamiento que se quiere probar.

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python manage.py test mi_app.tests.test_integration_workflows -k rapido_motor_nuevo -v 2`
Expected: `FAIL`.

- [ ] **Step 3: Modificar el bloque de creación en `crear_prestamo_rapido`**

En `mi_app/views_core.py:2973-3004`, reemplazar el bloque completo (desde `fecha_inicio = date.today()` hasta el `for` que crea `CuotaRapida`) por:

```python
                from mi_app.services.amortizacion_service import generar_fechas_cuotas, calcular_interes_periodo

                fecha_inicio = date.today()
                fechas_pago = generar_fechas_cuotas(fecha_inicio, num_cuotas)

                capital_total = Decimal(str(prestamo_rapido.monto))
                tasa = Decimal(str(prestamo_rapido.interes_porcentaje))

                prestamo_rapido.capital_pendiente = capital_total
                prestamo_rapido.save(update_fields=['capital_pendiente'])

                capital_por_cuota = (capital_total / Decimal(num_cuotas)).quantize(Decimal('0.01'))
                interes_primera_cuota = calcular_interes_periodo(capital_total, tasa)

                for i, fecha_pago in enumerate(fechas_pago, 1):
                    interes_cuota = interes_primera_cuota if i == 1 else Decimal('0')
                    CuotaRapida.objects.create(
                        prestamo_rapido=prestamo_rapido,
                        numero_cuota=i,
                        monto_original=capital_por_cuota,
                        monto_pendiente=capital_total if i == 1 else Decimal('0'),
                        interes_normal=interes_cuota,
                        monto_pendiente_interes=interes_cuota,
                        fecha_pago_esperada=fecha_pago,
                    )
```

Nota: verificar el nombre exacto del campo de tasa en `PrestamoRapido` (usado arriba como `prestamo_rapido.interes_porcentaje`) leyendo la clase `PrestamoRapido` en `mi_app/models.py:1058` antes de aplicar este cambio — si el campo se llama distinto (por ejemplo `interes_porcentaje` podría no existir y en su lugar usarse un valor fijo de `Configuracion.tasa_interes_prestamo_rapido`), ajustar la línea `tasa = ...` para leer el valor real.

- [ ] **Step 4: Correr el test para confirmar que pasa**

Run: `python manage.py test mi_app.tests.test_integration_workflows -k rapido_motor_nuevo -v 2`
Expected: `PASS`.

- [ ] **Step 5: Retirar `calcular_fechas_pago` de `models.py` (ahora sí, sin callers)**

Run: `grep -rn "calcular_fechas_pago" mi_app/ --include="*.py"`
Expected: solo la definición. Borrar la función `calcular_fechas_pago` completa de `mi_app/models.py:15-94`.

- [ ] **Step 6: Correr toda la suite para confirmar cero regresiones nuevas**

Run: `python manage.py test mi_app`
Expected: mismo conteo base documentado en `DEUDA-TECNICA.md`, sin nuevos fallos no explicados.

- [ ] **Step 7: Commit**

```bash
git add mi_app/views_core.py mi_app/models.py mi_app/tests/test_integration_workflows.py
git commit -m "feat: crear_prestamo_rapido usa el mismo motor de interes dinamico; retira calcular_fechas_pago sin uso"
```

---

## Task 8: `pagar_cuota_especifica` (normal) usa el motor y los topes correctos

**Files:**
- Modify: `mi_app/views_core.py:1365-1481` (`pagar_cuota_especifica`)
- Test: `mi_app/tests/test_integration_workflows.py`

**Interfaces:**
- Consumes: `aplicar_pago`, `calcular_interes_pendiente_actual` del servicio (Task 4).
- Produces: el tope de "Interés a Pagar" pasa a ser `capital_pendiente_actual × 15% ÷ 2` (dinámico) en vez del `monto_pendiente_interes` fijo de la cuota; el tope de "Principal a Pagar" pasa a ser `prestamo.capital_pendiente` completo, no `cuota.monto_pendiente`.

- [ ] **Step 1: Escribir el test que falla — el caso exacto de la queja original**

Append a `mi_app/tests/test_integration_workflows.py`:

```python
class PagarCuotaEspecificaMotorNuevoTests(TestCase):
    def test_puede_pagar_mas_capital_del_que_decia_la_cuota_vieja(self):
        # Reproduce la queja original: prestamo de 200.000, el operario
        # quiere poder abonar mucho mas capital del que la cuota puntual
        # decia (topada antes a un pedacito fijo).
        from mi_app.models import Cliente, Prestamo, Cuota

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

        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('pagar_cuota_especifica', kwargs={'cuota_id': cuota.id}),
            {'monto_principal': '150000', 'monto_interes': '15000', 'monto_mora': '0'},
        )

        prestamo.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context or {})
        self.assertEqual(prestamo.capital_pendiente, Decimal('50000'))
```

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python manage.py test mi_app.tests.test_integration_workflows.PagarCuotaEspecificaMotorNuevoTests -v 2`
Expected: `FAIL` — hoy el tope de `monto_principal` es `cuota.monto_pendiente` (200.000 en este caso coincide, pero el de interés está mal); el objetivo real de este test es documentar el comportamiento correcto end-to-end, y sirve de red para el resto de este task.

- [ ] **Step 3: Modificar `pagar_cuota_especifica`**

En `mi_app/views_core.py:1365-1481`, reemplazar el cuerpo completo de la función por:

```python
def pagar_cuota_especifica(request, cuota_id):
    """
    Vista dedicada al pago de una cuota especifica, con capital/interes/mora
    en 3 campos manuales separados. Los topes de referencia se calculan de
    forma dinamica sobre el capital_pendiente real del prestamo (no un
    pedacito fijo por cuota) -- ver docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md
    """
    from .models import Pago
    from mi_app.services.amortizacion_service import calcular_interes_pendiente_actual, aplicar_pago
    from django.db import transaction

    cuota = get_object_or_404(Cuota, id=cuota_id)
    prestamo = cuota.prestamo
    cliente = prestamo.cliente
    interes_pendiente = calcular_interes_pendiente_actual(prestamo, cuota)
    mora_actual = cuota.calcular_mora_diaria()

    if request.method == 'POST':
        monto_principal = Decimal(request.POST.get('monto_principal', '0').strip() or '0')
        monto_interes = Decimal(request.POST.get('monto_interes', '0').strip() or '0')
        monto_mora = Decimal(request.POST.get('monto_mora', '0').strip() or '0')
        referencia = request.POST.get('referencia', '')
        notas = request.POST.get('notas', '')

        monto_total = monto_principal + monto_interes + monto_mora

        if monto_total <= 0:
            contexto = {
                'cuota': cuota, 'prestamo': prestamo, 'cliente': cliente,
                'capital_pendiente': prestamo.capital_pendiente,
                'interes_pendiente': interes_pendiente, 'mora_actual': mora_actual,
                'error': '❌ El monto debe ser mayor a $0',
            }
            return render(request, 'mi_app/pagar_cuota_especifica.html', contexto)

        if monto_principal > prestamo.capital_pendiente:
            contexto = {
                'cuota': cuota, 'prestamo': prestamo, 'cliente': cliente,
                'capital_pendiente': prestamo.capital_pendiente,
                'interes_pendiente': interes_pendiente, 'mora_actual': mora_actual,
                'error': f'❌ Capital pendiente del préstamo: ${prestamo.capital_pendiente}',
            }
            return render(request, 'mi_app/pagar_cuota_especifica.html', contexto)

        if monto_interes > interes_pendiente:
            contexto = {
                'cuota': cuota, 'prestamo': prestamo, 'cliente': cliente,
                'capital_pendiente': prestamo.capital_pendiente,
                'interes_pendiente': interes_pendiente, 'mora_actual': mora_actual,
                'error': f'❌ Interés pendiente: ${interes_pendiente}',
            }
            return render(request, 'mi_app/pagar_cuota_especifica.html', contexto)

        with transaction.atomic():
            resumen = aplicar_pago(prestamo, cuota, monto_principal, monto_interes, monto_mora)

            pago = Pago.objects.create(
                cuota=cuota,
                monto_pagado=monto_total,
                monto_principal=monto_principal,
                monto_interes=monto_interes,
                monto_mora=monto_mora,
                usuario_registra=request.user.username,
                referencia=referencia,
                notas=notas,
                capital_antes=resumen['capital_antes'],
                capital_despues=resumen['capital_despues'],
            )

            cuota.actualizar_estado()
            cuota.save()
            prestamo.save()

        detalles = cuota.detalles_completos()
        contexto = {
            'pago': pago, 'cuota': cuota, 'prestamo': prestamo, 'cliente': cliente,
            'detalles': detalles,
            'pagos': Pago.objects.filter(cuota=cuota).order_by('-fecha_pago'),
            'comprobante': pago.comprobante_texto(),
            'success': True,
        }
        return render(request, 'mi_app/pagar_cuota_especifica.html', contexto)

    else:  # GET
        pagos = Pago.objects.filter(cuota=cuota).order_by('-fecha_pago')
        detalles = cuota.detalles_completos()
        contexto = {
            'cuota': cuota, 'prestamo': prestamo, 'cliente': cliente,
            'detalles': detalles, 'pagos': pagos,
            'capital_pendiente': prestamo.capital_pendiente,
            'interes_pendiente': interes_pendiente,
            'mora_actual': mora_actual,
        }
        return render(request, 'mi_app/pagar_cuota_especifica.html', contexto)
```

- [ ] **Step 4: Actualizar el template para usar los nuevos topes**

En `mi_app/templates/mi_app/pagar_cuota_especifica.html`, buscar dónde se muestra el "Máximo" del campo de Principal (probablemente algo como `Máximo: {{ cuota.monto_pendiente }}` o similar) y reemplazarlo por `Máximo: {{ capital_pendiente }}`. Buscar el "Máximo" del campo de Interés (probablemente `{{ cuota.monto_pendiente_interes }}`) y reemplazarlo por `{{ interes_pendiente }}`. Revisar el archivo primero con el editor para ubicar el texto exacto antes de reemplazarlo — los nombres de variable de contexto cambiaron (`capital_pendiente` e `interes_pendiente` en vez de leer directo de `cuota`).

- [ ] **Step 5: Correr el test para confirmar que pasa**

Run: `python manage.py test mi_app.tests.test_integration_workflows.PagarCuotaEspecificaMotorNuevoTests -v 2`
Expected: `PASS`.

- [ ] **Step 6: Correr toda la suite para confirmar cero regresiones nuevas**

Run: `python manage.py test mi_app`
Expected: mismo conteo base documentado en `DEUDA-TECNICA.md`, sin nuevos fallos no explicados por este cambio.

- [ ] **Step 7: Commit**

```bash
git add mi_app/views_core.py mi_app/templates/mi_app/pagar_cuota_especifica.html mi_app/tests/test_integration_workflows.py
git commit -m "fix: pagar_cuota_especifica usa capital_pendiente del prestamo (no un pedacito fijo por cuota) e interes dinamico"
```

---

## Task 9: `registrar_pago_rapido` usa el mismo motor (mantiene su UI de 1 campo)

**Files:**
- Modify: `mi_app/views_core.py:3112-3229` (`registrar_pago_rapido`)
- Test: `mi_app/tests/test_integration_workflows.py`

**Interfaces:**
- Consumes: `aplicar_pago`, `calcular_interes_pendiente_actual` del servicio.
- Produces: el waterfall de un único `monto_pagado` ahora reparte **interés primero, capital después** (antes era capital primero) y el tope total pasa a considerar `prestamo.capital_pendiente` en vez del `monto_pendiente` de la cuota sola.

- [ ] **Step 1: Escribir el test que falla**

Append a `mi_app/tests/test_integration_workflows.py`:

```python
class RegistrarPagoRapidoMotorNuevoTests(TestCase):
    def test_pago_unico_reparte_interes_primero_luego_capital(self):
        from mi_app.models import Cliente, PrestamoRapido, CuotaRapida

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

        self.client.login(username='admin', password='adminpass')
        self.client.post(
            reverse('registrar_pago_rapido', kwargs={'cuota_id': cuota.id}),
            {'monto_pagado': '80000', 'usuario_registra': 'admin'},
        )

        prestamo.refresh_from_db()
        # 19.000 a interes, 61.000 a capital -> capital queda en 189.000
        self.assertEqual(prestamo.capital_pendiente, Decimal('189000'))
```

Nota: revisar los nombres de campo reales que espera `PrestamoRapidoForm`/creación directa de `PrestamoRapido` (puede requerir un campo `tipo_pago` u otro obligatorio) leyendo `mi_app/models.py:1058` y `mi_app/forms.py` antes de correr — ajustar el `PrestamoRapido.objects.create(...)` de este test si falta algún campo requerido.

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python manage.py test mi_app.tests.test_integration_workflows.RegistrarPagoRapidoMotorNuevoTests -v 2`
Expected: `FAIL` (hoy reparte capital primero: capital quedaría en 250000-80000=170000, no 189000).

- [ ] **Step 3: Modificar `registrar_pago_rapido`**

En `mi_app/views_core.py:3112-3229`, reemplazar el bloque del método POST (líneas 3127 a 3193, desde `if form.is_valid():` hasta el `PagoPrestamoRapido.objects.create(...)`) por:

```python
        if form.is_valid():
            from mi_app.services.amortizacion_service import calcular_interes_pendiente_actual, aplicar_pago
            from django.db import transaction

            monto_pagado = Decimal(str(form.cleaned_data.get('monto_pagado')))
            usuario_registra = form.cleaned_data.get('usuario_registra', 'Sistema')
            referencia = form.cleaned_data.get('referencia', '')
            notas = form.cleaned_data.get('notas', '')

            mora = Decimal(str(cuota.calcular_mora_diaria()))
            interes_pendiente = calcular_interes_pendiente_actual(prestamo, cuota)
            total_debido = prestamo.capital_pendiente + interes_pendiente + mora

            if monto_pagado > total_debido:
                form.add_error('monto_pagado', f'El monto no puede ser mayor a {total_debido}')
                return render(request, 'mi_app/registrar_pago_rapido.html', {
                    'form': form, 'prestamo': prestamo, 'cuota': cuota,
                    'total_debido': total_debido, 'mora_actual': mora,
                })

            # Interes primero, despues capital, despues mora -- con lo que sobre
            monto_restante = monto_pagado
            interes_a_pagar = min(interes_pendiente, monto_restante)
            monto_restante -= interes_a_pagar
            capital_a_pagar = min(prestamo.capital_pendiente, monto_restante)
            monto_restante -= capital_a_pagar
            mora_a_pagar = min(mora, monto_restante)

            with transaction.atomic():
                resumen = aplicar_pago(prestamo, cuota, capital_a_pagar, interes_a_pagar, mora_a_pagar)

                PagoPrestamoRapido.objects.create(
                    prestamo_rapido=prestamo,
                    cuota_rapida=cuota,
                    monto_pagado=monto_pagado,
                    usuario_registra=usuario_registra,
                    referencia=referencia,
                    notas=notas,
                )

                cuota.actualizar_estado()
                cuota.save()
                prestamo.save()
```

Nota: el bloque original seguía con `total_pagado = prestamo.pagos.aggregate(...)`, `prestamo.actualizar_estado()`, etc. — revisar si `PrestamoRapido` tiene un método propio `actualizar_estado()` (distinto del de `Cuota`) y si sigue haciendo falta tras el cambio; si `aplicar_pago` ya deja `prestamo.estado = 'COMPLETADO'` cuando corresponde, puede que ese bloque quede redundante o en conflicto — leer `PrestamoRapido.actualizar_estado()` (si existe) antes de decidir si se conserva, se ajusta o se retira, y dejar la vista terminando con el mismo `HttpResponseRedirect` que ya tenía.

- [ ] **Step 4: Correr el test para confirmar que pasa**

Run: `python manage.py test mi_app.tests.test_integration_workflows.RegistrarPagoRapidoMotorNuevoTests -v 2`
Expected: `PASS`.

- [ ] **Step 5: Correr toda la suite para confirmar cero regresiones nuevas**

Run: `python manage.py test mi_app`
Expected: mismo conteo base documentado en `DEUDA-TECNICA.md`, sin nuevos fallos no explicados.

- [ ] **Step 6: Commit**

```bash
git add mi_app/views_core.py mi_app/tests/test_integration_workflows.py
git commit -m "fix: registrar_pago_rapido reparte interes antes que capital, tope real del prestamo (no de la cuota sola)"
```

---

## Task 10: Actualizar `DEUDA-TECNICA.md` y `reglas/data-rules.md`

**Files:**
- Modify: `DEUDA-TECNICA.md`
- Modify: `reglas/data-rules.md`

**Interfaces:** ninguna — task de documentación.

- [ ] **Step 1: Marcar como resuelto el hallazgo original de la queja de interés**

En `DEUDA-TECNICA.md`, agregar una entrada nueva describiendo que el tope de interés/capital en el formulario de pago ya no está atado a una sola cuota sino al `capital_pendiente`/interés dinámico del préstamo completo, con referencia al spec (`docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md`) y a este plan.

- [ ] **Step 2: Actualizar `reglas/data-rules.md`**

Agregar una nota en la sección de dinero (§2) mencionando que el interés ahora se recalcula sobre `capital_pendiente` en cada período (no un valor fijo por cuota), con puntero al spec, para que quede escrito el motivo de la nueva regla — igual que se hizo con el bug de `total_a_pagar()` durante la adopción.

- [ ] **Step 3: Commit**

```bash
git add DEUDA-TECNICA.md reglas/data-rules.md
git commit -m "docs: registrar el interes dinamico sobre saldo en DEUDA-TECNICA y data-rules"
```
