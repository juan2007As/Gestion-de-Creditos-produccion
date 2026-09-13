# Reglas de Datos (Gestión de Créditos)

> Distinto de seguridad: esto es "que los datos tengan sentido, sean consistentes, no se corrompan y no se pierdan".

## 1. Modelo de datos

1. Las invariantes se garantizan en la base de datos cuando sea posible (unicidad, FK, `NOT NULL`), no solo en el código.
2. Se define explícitamente qué pasa al borrar una entidad referenciada. **Estado real**: `Cliente`→`Prestamo`→`Cuota`→`Pago` es `CASCADE` total (`models.py:517,685,932,1069,1326`) — borrar un cliente borra en cadena todo su historial financiero, sin soft-delete. Deuda cajón 2.
3. Solo hay 2 migraciones (`0001_initial`, `0002_...`) para 17 modelos con historia evidente de RBAC/scoring/lista negra — el historial se reseteó en algún momento. No asumir que el estado de la Postgres de Render coincide exactamente sin comprobarlo antes de una migración nueva.

## 2. Los dos temas que siempre se hacen mal

4. **Dinero nunca en coma flotante.** Los campos son `DecimalField` correctos, pero varios métodos de cálculo (`calcular_interes_total`, `calcular_mora_diaria`, `total_a_pagar`, etc. en `models.py`) convierten a `float()` internamente antes de operar. **Ya causó un bug real**: `Cuota.total_a_pagar()` (línea 835-838) suma el interés original completo en vez del pendiente — es el número que ve el operario para cobrarle al cliente. Al tocar cualquiera de estos métodos: operar en `Decimal` de punta a punta, sin pasar por `float` en ningún paso intermedio.
5. **Todo instante en UTC** — `USE_TZ=True` ya activo, confirmado sin mezcla de `datetime.now()` sin timezone en los archivos de cálculo (A3).

## 3. Concurrencia

6. Dos peticiones simultáneas son el caso normal. **Estado real**: solo `registrar_pago` (vía `@atomic_payment_view`/`registrar_pago_atomico` en `mi_app/utilities/transaction_integrity.py`) usa `transaction.atomic()` + lock. `pagar_cuota_especifica` y toda la línea de "préstamos rápidos" (`views_core.py:3118,3240,3260`) mutan saldos sin ninguno de los dos — deuda cajón 1, riesgo activo con dinero real.
7. Cualquier vista nueva que mueva dinero (pagos, ajustes de saldo) debe pasar por el mismo patrón que `registrar_pago`, no reinventar uno propio sin lock.

## 4. Migraciones

8. Cambios de esquema vía migraciones versionadas, nunca a mano en producción.
9. Antes de una migración sobre producción, confirmar que la última corrida de `.github/workflows/backup.yml` pasó (backup reciente y restauración probada).

## 5. Backups y recuperación — ya resuelto en la Fase A4

10. **Existe** `.github/workflows/backup.yml`: `pg_dump` diario contra `DATABASE_URL` (secret de GitHub, pendiente de que el dueño lo configure) + restauración real contra una base vacía en la misma corrida. Si no restaura, el job falla — no es un backup silencioso.
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
