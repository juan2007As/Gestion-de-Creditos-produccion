# Reglas de Datos (Gestión de Créditos)

> Distinto de seguridad: esto es "que los datos tengan sentido, sean consistentes, no se corrompan y no se pierdan".

## 1. Modelo de datos

1. Las invariantes se garantizan en la base de datos cuando sea posible (unicidad, FK, `NOT NULL`), no solo en el código.
2. Se define explícitamente qué pasa al borrar una entidad referenciada. **Estado real**: `Cliente`→`Prestamo`→`Cuota`→`Pago` es `CASCADE` total (`models.py:517,685,932,1069,1326`) — borrar un cliente borra en cadena todo su historial financiero, sin soft-delete. Deuda cajón 2.
3. Solo hay 2 migraciones (`0001_initial`, `0002_...`) para 17 modelos con historia evidente de RBAC/scoring/lista negra — el historial se reseteó en algún momento. No asumir que el estado de la Postgres de Render coincide exactamente sin comprobarlo antes de una migración nueva.

## 2. Los dos temas que siempre se hacen mal

4. **Dinero nunca en coma flotante.** Los campos son `DecimalField` correctos, pero varios métodos de cálculo (`calcular_interes_total`, `calcular_mora_diaria`, `total_a_pagar`, etc. en `models.py`) convierten a `float()` internamente antes de operar. **Ya causó un bug real**: `Cuota.total_a_pagar()` (línea 835-838) suma el interés original completo en vez del pendiente — es el número que ve el operario para cobrarle al cliente. Al tocar cualquiera de estos métodos: operar en `Decimal` de punta a punta, sin pasar por `float` en ningún paso intermedio.
5. **Todo instante en UTC** — `USE_TZ=True` ya activo, confirmado sin mezcla de `datetime.now()` sin timezone en los archivos de cálculo (A3).
6. **El interés se recalcula sobre el saldo vivo, no sobre un valor fijo por cuota.** Pedido explícito del cliente (no era una decisión de diseño libre): el capital real vive en `Prestamo.capital_pendiente`/`PrestamoRapido.capital_pendiente` (`DecimalField`, fuente única de verdad — nunca se reparte "exacto" entre cuotas), y cada quincena el interés se recalcula como `capital_pendiente × tasa% ÷ 2`, redondeado al millar más cercano (`redondear_al_millar` en `mi_app/services/amortizacion_service.py`). El interés no pagado de un período se acumula en `interes_acumulado_sin_pagar` y se arrastra al siguiente, nunca se pierde. Los topes de pago (capital/interés máximo que se puede abonar) se calculan siempre contra estos dos campos del préstamo, nunca contra `Cuota.monto_pendiente`/`monto_pendiente_interes` de una cuota puntual — ver `docs/superpowers/specs/2026-09-13-interes-sobre-saldo-design.md` para las 14 reglas de negocio completas.

## 3. Concurrencia

6. Dos peticiones simultáneas son el caso normal. **Estado real**: solo `registrar_pago` (vía `@atomic_payment_view`/`registrar_pago_atomico` en `mi_app/utilities/transaction_integrity.py`) usa `transaction.atomic()` + `select_for_update()` (lock de fila real). `pagar_cuota_especifica` y `registrar_pago_rapido` ahora usan `transaction.atomic()` (agregado junto con el motor de interés sobre saldo) pero sin `select_for_update()` — mejor que antes, pero sin el lock de fila. El resto de la línea de "préstamos rápidos" sigue sin ninguno de los dos — deuda cajón 1 #3, riesgo activo con dinero real.
7. Cualquier vista nueva que mueva dinero (pagos, ajustes de saldo) debe pasar por el mismo patrón que `registrar_pago`, no reinventar uno propio sin lock.

## 4. Migraciones

8. Cambios de esquema vía migraciones versionadas, nunca a mano en producción.
9. Antes de una migración sobre producción, confirmar que la última corrida de `.github/workflows/backup.yml` pasó (backup reciente y restauración probada).

## 5. Backups y recuperación — ya resuelto en la Fase A4

10. **Existe** `.github/workflows/backup.yml`: `pg_dump` diario contra `DATABASE_URL` (secret de GitHub ya configurado por el dueño) + restauración real contra una base vacía en la misma corrida. Si no restaura, el job falla — no es un backup silencioso.
11. Antigüedad del backup: se puede ver en la pestaña Actions del repositorio (última corrida exitosa = último backup verificado).
12. Retención de los backups: 30 días vía `retention-days` del artifact de GitHub Actions — no es almacenamiento a largo plazo; si el negocio necesita retención mayor, es una decisión aparte (ver [[compliance-rules]]).

## 6. Rendimiento

13. `lista_clientes_api` (`views_core.py:125`) devuelve todos los clientes sin paginar. Bajo riesgo hoy (10 usuarios, volumen modesto) — revisar si el número de clientes crece significativamente. Deuda cajón 3.

## 7. Operar sobre datos reales

14. Nunca un `UPDATE`/`DELETE` sin `WHERE` en producción. Los scripts de `scripts/` que corrigen datos puntuales (`corregir_totales_prestamo.py`, `fix_interes.py`, etc.) se corren primero como consulta de lectura para ver qué filas tocan.
15. El acceso directo a la Postgres de producción es excepcional — hoy solo el dueño tiene acceso (confirmado en `CONTEXTO.md`).

## 8. Privacidad, retención y borrado

16. Identificar qué datos son personales (cédula, celular, nombre, historial financiero) — ya identificados, sin política de retención escrita todavía. Ver [[compliance-rules]].
17. No hay soft-delete implementado — un borrado de `Cliente` es físico y en cascada (ver punto 2).

## Antes de dar por cerrado un cambio de modelo de datos

- ¿Qué pasa con los datos existentes al aplicar este cambio?
- ¿Qué pasa si se borra esta entidad? (hoy: se borra todo en cascada)
- ¿Esta invariante está garantizada por la base de datos o solo por un `if`?
- ¿Qué pasa si dos peticiones hacen esto exactamente a la vez?
- ¿Hay un backup reciente y verificado antes de esta operación irreversible? (revisar la última corrida de `backup.yml`)
- ¿Este cálculo usa `Decimal` de punta a punta?
