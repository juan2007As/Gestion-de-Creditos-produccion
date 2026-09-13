# Diseño: interés dinámico sobre saldo (reemplaza el interés fijo actual)

> Estado: aprobado en brainstorming, pendiente de plan de implementación.
> Perfil del proyecto: P3 (dinero real). No hay préstamos reales en producción hoy — se migra el modelo actual sin necesidad de migración de datos de clientes.

## 1. Contexto y motivación

Hoy `Prestamo`/`Cuota` y `PrestamoRapido`/`CuotaRapida` calculan el interés **una sola vez, al crear el préstamo**, dividiendo el capital en `N` cuotas iguales con un interés fijo por cuota. Esto no permite abonos flexibles: un cliente no puede pagar "solo interés" o "solo capital" en cualquier proporción, porque los campos del formulario de pago están topados a lo que esa cuota puntual dice que debe — capital tope = `cuota.monto_pendiente` (un pedacito del préstamo), interés tope = `cuota.monto_pendiente_interes` (fijo desde la creación). Esto ya causó una queja real de un cliente (ver captura del 2026-09-13): con un préstamo de $200.000, el tope de interés mostraba $5.000 en vez de reflejar el interés real sobre el saldo vivo.

El cliente final del negocio (a través del dueño del proyecto) definió la lógica real que debe regir: **interés sobre saldo declinante**, recalculado cada quincena sobre el capital que realmente quede pendiente — no sobre el valor original del préstamo, y no fijado de antemano.

Esto reemplaza la lógica actual (se corrigen los dos sistemas, normal y rápido, en vez de crear un tercero) porque hoy no hay préstamos reales en producción — no hace falta migrar datos de clientes.

## 2. Reglas de negocio (fuente: especificación del dueño del proyecto, 2026-09-13)

1. **Capital**: se divide entre el número de cuotas al crear el préstamo. La suma debe cerrar EXACTO con el valor prestado — cualquier ajuste de redondeo se hace en el interés, nunca en el capital.
2. **Interés** = `capital_pendiente × 15% ÷ 2` (quincenal), recalculado sobre el capital que quede vivo en cada momento — nunca sobre el valor original del préstamo.
3. Si en una quincena el cliente **solo paga interés**, el capital pendiente no baja, y el interés de la próxima quincena se vuelve a calcular sobre el mismo capital.
4. **Pago normal/parcial**: prioridad **interés primero, el resto a capital**. La interfaz mantiene los 3 campos manuales de siempre (capital / interés / mora) — no es un monto único que el sistema reparte solo; el operario decide cuánto entra en cada campo, con topes de referencia calculados por el sistema.
5. **Abonos extraordinarios a capital**: reducen `capital_pendiente` inmediatamente. **No** eliminan ni reducen el número de cuotas pendientes nominales. El interés futuro se recalcula sobre el nuevo saldo.
6. **Cierre del préstamo**: cuando `capital_pendiente` llega a $0 **y** el interés de ese período quedó completamente pagado, el préstamo se da por `COMPLETADO` ahí mismo — sin importar cuántas cuotas nominales quedaban en el calendario original.
7. **Interés no pagado completo en una quincena**: el faltante **se acumula** para la próxima quincena (se suma al nuevo interés calculado), no se convierte automáticamente en mora.
8. **Pagar solo intereses indefinidamente está permitido** — el sistema no fuerza el cierre del crédito ni lo cancela.
9. **Redondeo del interés**: al millar más cercano (ej. $18.750 → $19.000). El redondeo nunca se aplica al capital.
10. **Mora**: monto **fijo en pesos por día** (default $2.000), **configurable por préstamo/cliente** (ej. $3.000) — reemplaza la tasa porcentual actual de `Configuracion.tasa_mora_diaria`. Empieza a contar desde el **día 3** de atraso. Se paga en un campo **manual, separado** de capital e interés (igual que hoy) — no se auto-descuenta de un pago general.
11. **Fechas de pago (quincenal)**: días ancla `{5, 15, 20, 30}` (fin de mes usa el último día válido si no existe el 30/31, incluida febrero). Dado el desembolso, la primera cuota cae en el **ancla más próxima tal que `ancla - desembolso >= 15 días`**. A partir de ahí, las cuotas siguientes alternan dentro del **mismo par** (`5↔20` o `15↔30`) — el par no se recalcula, solo la primera fecha lo determina.
12. **Datos por crédito**: capital inicial, saldo actual de capital, número de cuotas inicial/pendientes, % interés, interés actual, fecha de desembolso, fecha de próxima cuota, estado, total pagado a capital/interés/mora, mora pendiente.
13. **Datos por pago**: fecha, valor total, valor a interés/capital/mora, saldo de capital antes/después, interés calculado, cuota asociada.
14. **Invariantes que nunca se rompen**: capital pagado ≤ capital prestado; saldo de capital nunca negativo; capital final cierra en $0 exacto; interés se recalcula tras cada reducción de capital; mora desde el día 3, $/día configurable.

## 3. Modelo de datos

Se mantiene la estructura de tablas actual (`Prestamo`/`Cuota` y `PrestamoRapido`/`CuotaRapida` por separado) para no arriesgar una fusión de tablas — se corrige la **lógica**, compartida entre ambos, no la estructura.

**Campos nuevos en `Prestamo` y `PrestamoRapido`:**
- `capital_pendiente` (Decimal) — saldo vivo de capital, fuente única de verdad a nivel de préstamo (hoy está repartido entre `Cuota.monto_pendiente` de cada fila).
- `mora_diaria_pesos` (Decimal, default `Decimal('2000')`) — reemplaza el uso de `Configuracion.tasa_mora_diaria` para estos préstamos.
- `interes_acumulado_sin_pagar` (Decimal, default 0) — el faltante de interés que se arrastra (regla 7).

**Cambios en `Cuota` y `CuotaRapida`:**
- `interes_normal` deja de ser un valor fijado al crear el préstamo. Pasa a ser un **snapshot**: se calcula y se guarda en el momento en que esa cuota se convierte en "la próxima a cobrar" (no las N cuotas de una vez).
- El resto de campos (`monto_pagado_principal`, `monto_pagado_interes`, `monto_pagado_mora`, `fecha_pago_esperada`) se mantienen con su significado actual.

**Cambios en `Pago`:**
- Se agregan `capital_antes` y `capital_despues` (Decimal) — snapshot del saldo de capital del préstamo antes/después de ese pago puntual (regla 13).

## 4. Algoritmo

### 4.1 Generación de cuotas al crear el préstamo
1. `capital_pendiente` del préstamo arranca en el capital total — es la única fuente de verdad, no se reparte en pedacitos fijos por cuota. El "capital por cuota" (`capital_total / num_cuotas`) que se muestra es solo una **referencia informativa** en la UI ("esperado ~125.000 por quincena"); no es un tope contable que tenga que cuadrar exacto — por eso no hay problema de redondeo que resolver acá: la regla 1 ("el capital cierra exacto, el ajuste va al interés") ya se cumple sola, porque el capital real vive en un único saldo (`capital_pendiente`), no en N cuotas que tengan que sumar justo.
2. Calcular **todas las fechas** de las `num_cuotas` cuotas de una vez, con el algoritmo de anclas (regla 11) — se conoce el calendario completo desde el inicio.
3. **No** calcular el interés de cada cuota todavía (excepto la primera, que sí se puede calcular ya que se conoce el capital inicial completo).

### 4.2 Al procesar un pago sobre la cuota "actual"
1. Tomar `interes_pendiente = interes_cuota_actual + interes_acumulado_sin_pagar` (regla 7).
2. Aplicar lo que el operario ingresó en cada campo (capital / interés / mora), validando que no exceda los topes de referencia:
   - Interés: tope = `interes_pendiente` (puede ser mayor al de un período si viene arrastrando).
   - Capital: tope = `capital_pendiente` completo del préstamo (no de esta cuota sola) — esto es lo que arregla la queja original.
   - Mora: manual, sin tope automático estricto (informativo).
3. `capital_pendiente -= capital_pagado`.
4. Si `interes_pagado < interes_pendiente`: `interes_acumulado_sin_pagar = interes_pendiente - interes_pagado` (se arrastra).
   Si `interes_pagado >= interes_pendiente`: `interes_acumulado_sin_pagar = 0`.
5. Registrar el `Pago` con snapshot `capital_antes`/`capital_despues`.
6. **Cierre**: si `capital_pendiente <= 0` y `interes_acumulado_sin_pagar <= 0` → `Prestamo.estado = 'COMPLETADO'`, se detiene el ciclo (no importa cuántas cuotas nominales quedaban).
7. Si no cerró: avanzar a la siguiente cuota programada (su fecha ya existía desde la creación), calcular su interés = `capital_pendiente × 15% ÷ 2`, redondeado al millar, y guardarlo como snapshot de esa cuota.

### 4.3 Mora
- Se calcula para mostrar como referencia: `dias_de_atraso_desde_dia_3 × mora_diaria_pesos` del préstamo (o el default $2.000 si no se configuró otro).
- Se paga con el campo manual, separado — no se mezcla en el cálculo de capital/interés.

## 5. Organización del código

- Nuevo módulo `mi_app/services/amortizacion_service.py` (nombre sugerido) con funciones puras: `calcular_interes_periodo(capital_pendiente, tasa=Decimal('15'))`, `calcular_proxima_fecha_ancla(fecha_desde)`, `aplicar_pago(prestamo_o_rapido, cuota, capital_pagado, interes_pagado, mora_pagada)`.
- `Prestamo`/`PrestamoRapido` y `Cuota`/`CuotaRapida` llaman a este módulo compartido en vez de tener cada uno su propia copia — esto es lo que cierra la duplicación que ya causó un bug real esta sesión (`total_a_pagar()` divergente).
- Las vistas de pago (`registrar_pago`, `pagar_cuota_especifica`, `registrar_pago_rapido*`) delegan el cálculo a este servicio; dejan de tener la lógica de reparto inline.

## 6. Migración

No hay préstamos reales en producción — la migración de Django (nuevos campos) se aplica directo, sin necesidad de script de migración de datos de clientes. Los tests existentes que dependían del cálculo viejo (interés fijo por cuota) se actualizan como parte de la implementación.

## 7. Plan de pruebas (casos de la propia especificación del dueño)

Casos mínimos a cubrir con tests, tomados literal de los ejemplos que dio:
- Interés inicial: capital 500.000 → interés 37.500.
- Interés tras reducción: capital 250.000 → interés 18.750, redondeado a 19.000.
- Solo pago de interés: capital no cambia, próximo interés igual.
- Pago normal: interés 19.000, pago 144.000 → 19.000 a interés, 125.000 a capital.
- Pago parcial: capital 250.000, interés 19.000, pago 80.000 → 19.000 interés, 61.000 capital, nuevo capital 189.000.
- Abono extraordinario: capital 300.000, abono 100.000 → capital 200.000, cuotas pendientes no cambian.
- Interés parcial no cubierto: se arrastra a la próxima quincena (confirmado explícitamente por el dueño).
- Cierre anticipado: pago total de capital + interés en una sola cuota → préstamo `COMPLETADO` aunque queden cuotas nominales.
- Fechas: desembolso día 20 → primera cuota día 5; desembolso día 21 → primera cuota día 15; desembolso día 19 → primera cuota día 5 (no el 30); fin de mes/febrero → último día válido.
- Mora: 4 días de atraso (desde el día 3) × $2.000 = $8.000; con `mora_diaria_pesos` distinto (ej. 3.000) da 3×3.000=9.000 para 3 días de mora efectiva (ajustar según regla de "desde el día 3").

## 8. Ambigüedades resueltas durante el brainstorming (para no perderlas)

- Mora: fija mora_diaria_pesos por préstamo, no porcentual, configurable por cliente.
- Mora se paga manual y separada, nunca auto-descontada.
- El préstamo cierra por saldo (capital + interés en $0), no por conteo de cuotas.
- Pagar solo interés indefinidamente está permitido, sin límite de tiempo.
- Redondeo del interés al millar, nunca al capital.
- Fechas: par fijo determinado por la primera cuota (regla de ancla ≥15 días), no recalculado cada quincena.
- Se corrige/reemplaza el sistema actual (no se crea uno en paralelo) — no hay préstamos reales que migrar.
