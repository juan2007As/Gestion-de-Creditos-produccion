# Diseño: interés dinámico sobre saldo (reemplaza el interés fijo actual)

> Estado: aprobado en brainstorming, pendiente de plan de implementación.
> Perfil del proyecto: P3 (dinero real). No hay préstamos reales en producción hoy — se migra el modelo actual sin necesidad de migración de datos de clientes.

## 1. Contexto y motivación

Hoy `Prestamo`/`Cuota` y `PrestamoRapido`/`CuotaRapida` calculan el interés **una sola vez, al crear el préstamo**, dividiendo el capital en `N` cuotas iguales con un interés fijo por cuota. Esto no permite abonos flexibles: un cliente no puede pagar "solo interés" o "solo capital" en cualquier proporción, porque los campos del formulario de pago están topados a lo que esa cuota puntual dice que debe — capital tope = `cuota.monto_pendiente` (un pedacito del préstamo), interés tope = `cuota.monto_pendiente_interes` (fijo desde la creación). Esto ya causó una queja real de un cliente (ver captura del 2026-09-13): con un préstamo de $200.000, el tope de interés mostraba $5.000 en vez de reflejar el interés real sobre el saldo vivo.

El cliente final del negocio (a través del dueño del proyecto) definió la lógica real que debe regir: **interés sobre saldo declinante**, recalculado cada quincena sobre el capital que realmente quede pendiente — no sobre el valor original del préstamo, y no fijado de antemano.

Esto reemplaza la lógica actual (se corrigen los dos sistemas, normal y rápido, en vez de crear un tercero) porque hoy no hay préstamos reales en producción — no hace falta migrar datos de clientes.

## 2. Reglas de negocio (fuente: especificación del dueño del proyecto, 2026-09-13)

1. **Capital**: se divide entre el número de cuotas al crear el préstamo. La suma debe cerrar EXACTO con el valor prestado — cualquier ajuste de redondeo se hace en el interés, nunca en el capital.
2. **Interés (corregido el 2026-09-13, ver §2.1 más abajo)**: NO se recalcula dinámicamente en cada cuota. Se arma un cronograma fijo al crear el préstamo: interés de las primeras 2 cuotas (1 mes) = `capital_total × 15% ÷ 2`; cada PAR siguiente de cuotas es la **mitad exacta** del par anterior, indefinidamente. Este cronograma NO cambia según lo que el cliente pague, salvo la regla 5 (abono extraordinario).
3. Si en una quincena el cliente **solo paga interés** (o paga exactamente el capital nominal de esa cuota), el interés de las cuotas siguientes **sigue el cronograma fijo de la regla 2** — no se recalcula por eso.
4. **Pago normal/parcial**: prioridad **interés primero, el resto a capital**. La interfaz mantiene los 3 campos manuales de siempre (capital / interés / mora) — no es un monto único que el sistema reparte solo; el operario decide cuánto entra en cada campo, con topes de referencia calculados por el sistema.
5. **Abonos extraordinarios a capital** (pagar MÁS capital que el pedacito nominal de esa cuota puntual — regla exacta de qué cuenta como "extra", ver §2.1): reducen `capital_pendiente` inmediatamente, Y disparan un recálculo completo del cronograma de TODAS las cuotas restantes: capital por cuota = `capital_pendiente_real ÷ cuotas_restantes`; el interés arranca un cronograma nuevo desde `capital_pendiente_real × 15% ÷ 2` para el próximo par, y sigue la regla 2 (mitad cada par siguiente) desde ahí. **No** eliminan ni reducen el número de cuotas pendientes nominales.
6. **Cierre del préstamo**: cuando `capital_pendiente` llega a $0 **y** el interés de ese período quedó completamente pagado, el préstamo se da por `COMPLETADO` ahí mismo — sin importar cuántas cuotas nominales quedaban en el calendario original.
7. **Interés no pagado completo en una quincena**: el faltante **se acumula** para la próxima quincena (se suma al nuevo interés calculado), no se convierte automáticamente en mora.
8. **Pagar solo intereses indefinidamente está permitido** — el sistema no fuerza el cierre del crédito ni lo cancela.
9. **Redondeo del interés**: NINGUNO (corregido el 2026-09-13 — la regla original de "redondeo al millar" quedó reemplazada; el dueño confirmó explícitamente "no hay que redondear" al revisar el cronograma real contra un ejemplo en Excel). El redondeo nunca se aplicó al capital, y ahora tampoco al interés.

### 2.1 Corrección del 2026-09-13 (post-implementación, hallada al comparar contra un Excel real del cliente)

La regla 2 original de este documento decía "recalculado sobre el capital que quede vivo en cada momento" — implementado inicialmente como recálculo dinámico en CADA cuota. Comparando contra un cronograma real que el dueño usa con sus clientes (Excel), se detectó que la regla real es la de arriba: un cronograma FIJO armado una sola vez (mitad cada par de cuotas), que solo se recalcula ante un abono extraordinario — no en cada pago. Ejemplo confirmado por el dueño: préstamo de $500.000 al 15%, 6 cuotas → interés $37.500 (cuotas 1-2), $18.750 (cuotas 3-4), $9.375 (cuotas 5-6) sin ningún abono extra. Si en la cuota 2 el cliente abona capital de más y queda un capital real de $200.000 (con 4 cuotas restantes), el cronograma se recalcula: capital por cuota = $50.000, interés = $15.000 (cuotas 3-4, el nuevo par), $7.500 (cuotas 5-6).

**Qué cuenta como "abono extraordinario"** (confirmado explícitamente): cualquier pago de capital que supere el `monto_original` (el pedacito nominal informativo) de esa cuota puntual — comparación por cuota individual, no acumulada.
10. **Mora**: monto **fijo en pesos por día** — **[corrección: esto ya es así hoy]** `Configuracion.tasa_mora_diaria` (default $2.000) ya se usa como monto fijo por día, no como porcentaje. Lo que cambia es que pasa de ser **un único valor global** para todo el sistema a ser **configurable por préstamo/cliente** (ej. $3.000 para un cliente puntual). Empieza a contar desde el **día 3** de atraso (ya existe como `Configuracion.dias_gracia_mora`, hoy en 5 — ver ambigüedad nueva más abajo). Se paga en un campo **manual, separado** de capital e interés (igual que hoy) — no se auto-descuenta de un pago general.
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
1. `capital_pendiente` del préstamo arranca en el capital total — es la única fuente de verdad, no se reparte en pedacitos fijos por cuota para efectos de tope de pago. El "capital por cuota" (`capital_total / num_cuotas`) que se muestra es una **referencia informativa** en la UI, pero además cumple un rol funcional: define qué cuenta como "abono extraordinario" (regla 5) — cualquier pago de capital que la supere, en esa cuota puntual.
2. Calcular **todas las fechas** de las `num_cuotas` cuotas de una vez, con el algoritmo de anclas (regla 11) — se conoce el calendario completo desde el inicio.
3. Calcular el **cronograma completo de interés** para las `num_cuotas`, de una sola vez (regla 2): interés base = `capital_total × 15% ÷ 2`, aplicado a las primeras 2 cuotas; cada par siguiente es la mitad del anterior. Se guarda como snapshot (`interes_normal`) en cada fila de `Cuota`/`CuotaRapida` desde la creación — no se calcula "cuando le toca el turno".

### 4.2 Al procesar un pago sobre la cuota "actual"
1. Tomar `interes_pendiente = interes_cuota_actual + interes_acumulado_sin_pagar` (regla 7). `interes_cuota_actual` es el snapshot ya guardado en esa cuota (de la creación, o de un recálculo anterior por abono extra) — nunca se recalcula en este paso.
2. Aplicar lo que el operario ingresó en cada campo (capital / interés / mora), validando que no exceda los topes de referencia:
   - Interés: tope = `interes_pendiente` (puede ser mayor al de un período si viene arrastrando).
   - Capital: tope = `capital_pendiente` completo del préstamo (no de esta cuota sola) — esto es lo que arregla la queja original.
   - Mora: manual, sin tope automático estricto (informativo).
3. `capital_pendiente -= capital_pagado`.
4. Si `interes_pagado < interes_pendiente`: `interes_acumulado_sin_pagar = interes_pendiente - interes_pagado` (se arrastra).
   Si `interes_pagado >= interes_pendiente`: `interes_acumulado_sin_pagar = 0`.
5. Registrar el `Pago` con snapshot `capital_antes`/`capital_despues`.
6. **Cierre**: si `capital_pendiente <= 0` y `interes_acumulado_sin_pagar <= 0` → `Prestamo.estado = 'COMPLETADO'`, se detiene el ciclo (no importa cuántas cuotas nominales quedaban).
7. Si no cerró: determinar si `capital_pagado` fue un **abono extraordinario** (regla 5, `capital_pagado > cuota_actual.monto_original`):
   - **Si NO hubo abono extra**: avanzar a la siguiente cuota programada (su fecha e interés ya existían desde la creación) sin tocar nada — el cronograma ya es correcto.
   - **Si SÍ hubo abono extra**: recalcular el cronograma de TODAS las cuotas restantes (existentes o por crear si se acabaron las nominales): capital por cuota = `capital_pendiente ÷ cuotas_restantes`; interés = arrancar un cronograma nuevo desde `capital_pendiente × 15% ÷ 2` para el próximo par, y seguir la regla 2 (mitad cada par) desde ahí.

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
- Cronograma inicial (6 cuotas, 500.000 al 15%): 37.500, 37.500, 18.750, 18.750, 9.375, 9.375 (mitad cada par, sin redondeo).
- Solo pago de interés (o pago exacto del capital nominal de la cuota): el cronograma de las cuotas siguientes NO cambia.
- Pago normal: interés 19.000, pago 144.000 → 19.000 a interés, 125.000 a capital (mecánica de aplicar_pago sin cambios).
- Pago parcial: capital 250.000, interés 19.000, pago 80.000 → 19.000 interés, 61.000 capital, nuevo capital 189.000.
- Abono extraordinario (ejemplo confirmado del dueño): capital 500.000, 6 cuotas, abono extra en cuota 2 deja capital real 200.000 con 4 cuotas restantes → capital por cuota recalculado a 50.000, interés de cuotas 3-4 a 15.000, cuotas 5-6 a 7.500.
- Interés parcial no cubierto: se arrastra a la próxima quincena (confirmado explícitamente por el dueño).
- Cierre anticipado: pago total de capital + interés en una sola cuota → préstamo `COMPLETADO` aunque queden cuotas nominales.
- Fechas: desembolso día 20 → primera cuota día 5; desembolso día 21 → primera cuota día 15; desembolso día 19 → primera cuota día 5 (no el 30); fin de mes/febrero → último día válido.
- Mora: 4 días de atraso (desde el día 3) × $2.000 = $8.000; con `mora_diaria_pesos` distinto (ej. 3.000) da 3×3.000=9.000 para 3 días de mora efectiva (ajustar según regla de "desde el día 3").

## 8. Ambigüedades resueltas durante el brainstorming (para no perderlas)

- Mora: fija mora_diaria_pesos por préstamo, no porcentual, configurable por cliente.
- Mora se paga manual y separada, nunca auto-descontada.
- El préstamo cierra por saldo (capital + interés en $0), no por conteo de cuotas.
- Pagar solo interés indefinidamente está permitido, sin límite de tiempo.
- Sin redondeo del interés ni del capital (corregido 2026-09-13; la regla original de redondeo al millar no aplica).
- Fechas: par fijo determinado por la primera cuota (regla de ancla ≥15 días), no recalculado cada quincena.
- Se corrige/reemplaza el sistema actual (no se crea uno en paralelo) — no hay préstamos reales que migrar.
- **(2026-09-13)** El interés NO se recalcula dinámicamente en cada cuota — es un cronograma fijo armado al crear el préstamo (mitad cada par de cuotas), que solo se recalcula ante un abono extraordinario a capital (ver §2.1).
