# DEUDA-TECNICA.md — Sistema de Gestión de Créditos

> Generado en **Fase A3 del protocolo de adopción**. Perfil **P3**. Nada de esto se ha arreglado todavía — es inventario, no acción. Clasificado en los 4 cajones del protocolo (`01-adopcion-protocol.md`).

---

## Cajón 1 — Se arregla ya, antes de tocar nada más

| # | Hallazgo | Archivo:línea | Por qué importa | Dueño de regla |
|---|---|---|---|---|
| 1 | **Bug de dinero real**: `Cuota.total_a_pagar()` suma el interés *original completo* en vez del *interés pendiente* en cualquier cuota del flujo normal que ya tuvo un abono de interés — cobra de más. `CuotaRapida.total_a_pagar()` sí lo hace bien. | `mi_app/models.py:835-838` (bug) vs `:1244-1247` (correcto). Se muestra en `views_core.py:1136` → `registrar_pago.html` | Es el número que el operario usa para cobrarle al cliente. Plata real, hoy, en producción. | data-rules §2 |
| 2 | `tech_debt_fixes.py` (`ConsolidatedCalculations`/`ConsolidatedValidations`) fue escrito para resolver exactamente esta duplicación (mora, interés, validaciones) pero **nunca se conectó** al código real — solo lo usan sus propios tests. Da falsa sensación de que la deuda ya se pagó. | `mi_app/utilities/tech_debt_fixes.py` (431 líneas, 0 usos fuera de `test_tech_debt_critica10.py`) | Mientras nadie lo mire, cualquiera asume que la lógica ya está centralizada. No lo está. | evolution-rules / architecture-rules |
| 3 | Pagos sin atomicidad ni bloqueo: solo `registrar_pago` (vía `@atomic_payment_view`) usa `transaction.atomic()`/lock. `pagar_cuota_especifica` y toda la línea de "préstamos rápidos" mutan saldos sin ninguno de los dos. | `views_core.py:1370-1450`, `:3118`, `:3240`, `:3260` vs `:997` (el único protegido) | Dos requests simultáneos sobre la misma cuota (doble clic, dos pestañas) pueden dejar el saldo o el estado inconsistente. | data-rules §3 |
| 4 | **[CORREGIDO, más grave de lo reportado en A3]** El control de "esto es tuyo" (`valida_propiedad_cliente`/`valida_propiedad_prestamo`) no es que falte en algunas vistas: es un **no-op en TODAS las vistas donde se usa**, incluidas las que A3 marcó como "protegidas". `Cliente` y `Prestamo` no tienen ningún campo de dueño/creador (`usuario_creador` solo existe en `ListaNegra`, un modelo distinto). El decorador hace `es_propietario = cliente.usuario_creador == request.user if hasattr(...) else True` — como el atributo no existe, `hasattr` es `False` y `es_propietario` es **siempre `True`**. | `mi_app/utilities/decorators.py:300` y `:356` | Cualquier operario autenticado puede ver/editar/pagar el cliente o préstamo de cualquier otro operario, en TODAS las vistas, no solo en las que A3 señaló sin decorador. Requiere decisión de producto antes de tocar código (ver abajo). | identity-rules §4 |
| 5 | ~~Backup real inexistente para producción~~ **[EN PROGRESO — A4]** `BackupManager` solo sirve para SQLite. Se implementó `.github/workflows/backup.yml`: `pg_dump` diario + restauración real contra una base vacía en cada corrida (falla si no restaura). Pendiente: el dueño debe agregar el secret `DATABASE_URL` (la cadena **externa** de Render, no la interna) en GitHub → Settings → Secrets → Actions para que corra. | `mi_app/utilities/backup_manager.py`, `.github/workflows/backup.yml` | Ya no depende de un backup que nunca sirvió; falta solo la credencial para activarlo. | data-rules §5 |
| 6 | Sin registro de errores que sobreviva ni alerta de ningún tipo. **[Decisión del dueño: se deja anotado, no se implementa por ahora.]** | `settings.py:209-229` | Si algo se rompe en producción, nadie se entera salvo que un usuario lo reporte. Sigue en cajón 1 porque el riesgo no cambió, solo la decisión de cuándo resolverlo. | observability-rules |
| 7 | `login_view` sin `@ratelimit` ni ningún control de intentos fallidos. | `views_core.py:41` | Fuerza bruta viable contra cualquier cuenta, incluida la del dueño/admin. | security-rules |
| 8 | `/admin/` en ruta por defecto, sin MFA ni restricción adicional — exigido desde P3. | `proyecto_john/urls.py:24` | Objetivo obvio de escaneo automatizado. | identity-rules / security-rules |
| 9 | ~~Credencial real de un tercero expuesta~~ **[HECHO — A4]** Carpeta `lambda/` retirada del repositorio de trabajo. **Sigue pendiente, y es acción tuya, no mía**: (a) avisar a Comfama para rotar esa API key — sigue siendo válida y visible en el historial público de GitHub aunque el archivo ya no esté en la copia de trabajo; (b) decidir aparte si querés reescribir el historial de git para borrarla de los commits viejos (operación de alto impacto, force-push, no la hago sin tu aprobación explícita separada). | `lambda/` (ya no existe localmente); sigue en el historial de `origin/main` | Mientras no rotes la key con Comfama, sigue comprometida sin importar qué hagamos en este repo. | config-rules §2 |
| 10 | Parseo de `Decimal` sin `try/except` en un endpoint de pago → `decimal.InvalidOperation` sin capturar → 500 crudo. | `views_core.py:1386-1388` | Viola la regla del núcleo "ningún error se muestra crudo", en una vista que mueve dinero. | 00-CORE #9 |
| 11 | ~~El CI no era un gate real~~ **[HECHO — A4]** `bandit`/`safety` ya no corren con `\|\| true` (bandit bloquea en severidad media+, hoy en 0; safety bloquea salvo las 6 vulnerabilidades que solo se arreglan con Django 5.2.x, ver #14). Nuevo job `secrets-scan`. `quality-gate` ahora falla de verdad si `security` o `secrets-scan` fallan, no solo si fallan los tests. **Pendiente, no resuelto todavía**: `render.yaml` sigue con `autoDeploy: true` desconectado del pipeline — Render despliega igual aunque el CI falle. Arreglarlo requiere que generes un Deploy Hook desde el dashboard de Render y me lo des como secret de GitHub. | `.github/workflows/tests.yml`, `render.yaml:22` | El gate de calidad del código ya bloquea de verdad; falta conectar ese gate al momento del deploy. | release-rules §1 / dependencies-rules |
| 12 | Variables sin default (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) que tumban el arranque completo si faltan. | `settings.py:234-238` | El servicio entero no levanta, no es un 500 de una vista puntual. | config-rules |
| 13 | Funciones núcleo de negocio sin ningún test dedicado: `obtener_profile()`, `calcular_fechas_pago`, `determinar_estado_cuota_al_crear`. | `mi_app/utilities/decorators.py`, `mi_app/utils.py` | Cambiar cualquiera de estas sin red de tests es tocar dinero/permisos a ciegas. | testing-rules / integrity-rules |
| 14 | ~~Django 4.2.11 desactualizado~~ **[HECHO — A4]** Actualizado a `4.2.30`, la última de la rama LTS 4.2. Corrige 36 de las 42 vulnerabilidades reportadas por `safety`, incluida una **inyección SQL real (CVE-2025-57833)** que estaba sin parchear. Verificado sin regresiones: mismos 222 tests, mismos 8 failures/26 errors preexistentes (ruido de entorno ya conocido, no causados por esta actualización). Las 6 vulnerabilidades restantes (Information Disclosure / Header Injection) solo se corrigen subiendo a Django 5.2.15+, un salto de versión mayor que necesita su propio plan de migración — quedan en cajón 2 (#15). | `requirements.txt:1` | Era más grave de lo que reportó la auditoría A3 original (que lo calificó de "no urgente"): había una inyección SQL real sin corregir en un sistema P3. | dependencies-rules |

---

## Cajón 2 — Se arregla pronto, con plan y fecha

| # | Hallazgo | Archivo:línea | Por qué importa |
|---|---|---|---|
| 1 | Cálculos de interés/mora convierten a `float()` antes de operar, aunque los campos de BD son `DecimalField` correctos. | `models.py:590,600-604,634-647,838-885,1090-1109,1247-1279` | Riesgo real de redondeo en plata de clientes. |
| 2 | `Cliente`→`Prestamo`→`Cuota`→`Pago` todo en `CASCADE`, sin retención ni soft-delete definidos. | `models.py:517,685,932,1069,1326` | Borrar un cliente borra en cadena todo su historial financiero; alcanzable desde `/admin/`. |
| 3 | `Cuota`/`CuotaRapida` son ~95% el mismo modelo copy-pasteado (mismo `calcular_mora_diaria()` línea por línea). Causa raíz del bug de cajón 1 #1. | `models.py:675` y `:1151` | Un fix aplicado a un lado y no al otro es exactamente lo que ya pasó. Unificar o documentar por qué deben ser distintos. |
| 4 | Sin `SESSION_COOKIE_AGE`/`SESSION_EXPIRE_AT_BROWSER_CLOSE` explícitos — rige el default de Django (2 semanas). | `settings.py` | Sin decisión documentada sobre cuánto debe durar una sesión con dinero de terceros de por medio. |
| 5 | Dependencias sin pin de versión (todo salvo `Django` y `django-ratelimit`), sin lockfile. | `requirements.txt` | Dos despliegues en fechas distintas pueden instalar versiones distintas sin que nadie lo decida. |
| 6 | `Django==4.2.11` desactualizado dentro de su propia rama LTS (soportada hasta abril 2026), sin cadencia de actualización. | `requirements.txt:1` | No es urgente hoy, pero nadie lo está vigilando. |
| 7 | CI corre en Python 3.11/3.12; producción declara 3.10.12 en `runtime.txt`. Sin paridad de entorno. | `.github/workflows/tests.yml:15` vs `runtime.txt` | Un test puede pasar en CI y comportarse distinto en el runtime real. |
| 8 | Sin endpoint de healthcheck (`/health`, `/ping`). | `urls.py` (ausente) | Render solo detecta "vivo" por respuesta de puerto, no por la DB realmente accesible. |
| 9 | Sin runbook de incidentes/rollback/restauración. `DEPLOY.md` es genérico y no cumple esa función. | — | Si algo falla, el propio dueño tiene que improvisar el procedimiento en caliente. |
| 10 | Legado de PythonAnywhere sin limpiar, desalineado con Render (config MySQL generada por un script que ya no aplica). | `DEPLOY.md`, `PYTHONANYWHERE_COMANDOS.txt`, `prepare_production.py` | Confunde sobre cuál es el mecanismo de deploy vigente. |
| 11 | `UsuarioProfileAdmin` permite a cualquier `is_staff` con permiso Django cambiar el `rol` de otro usuario, sin control de auto-escalado. | `mi_app/admin.py:534` | Hoy no explotable (un solo admin), pero el hueco está listo si se da acceso de admin a alguien más. |
| 12 | Sin ciclo de vida formal de cuenta de operario (activar/desactivar) — depende del `UserAdmin` genérico de Django. | — | Funcional pero informal a 10 usuarios. |
| 13 | "Staging" existe solo en código (`ENVIRONMENT=staging`), nunca se desplegó realmente. | `settings.py`, `context_processors.py`, `.github/workflows/README.md:183` | Rama de código muerta que aparenta más madurez de la que hay. |
| 15 | Migración mayor pendiente: Django 5.2.15+ corrige las 6 vulnerabilidades restantes (Information Disclosure/Header Injection, no explotables críticamente hoy), pero 4.2→5.x puede traer cambios de comportamiento que necesitan probarse aparte. | `requirements.txt:1` | No se hace a la ligera en el mismo pase que otros arreglos — merece su propio ciclo de prueba. |
| 16 | Rama remota sin mergear `fix/production-readiness-17236091267996910219`, con commits de otra sesión de asistente de IA, que **borra `render.yaml` y `build.sh` completos** y reescribe `settings.py`. Nunca se fusionó a `main`. | rama en `origin` | No se tocó ni se borró. Hay que decidir con el dueño si se revisa por si tiene algo rescatable, o se elimina. |

---

## Cajón 3 — Se arregla al tocarlo (acotado a lo que rodea el cambio)

- Lógica de negocio inline en `views_core.py` (6129 líneas) en vez de vivir en `services/` — sistemático, no puntual (back-rules §6).
- Archivos sueltos y redundantes que el dueño ya pidió reorganizar: `lambda/` (se retira, ya decidido en A1), `$file` (basura), variantes redundantes de backup (`scripts/backup_local.py`, `backup_local_manager.py`, `backup_manager_local.py`, `backup_manager.py` — cuatro para lo mismo), scripts de parche puntual (`fix_interes.py`, `reparar_csv.py`, `auto_protect.py`, etc.), tests redundantes (`tests_alto_3_4.py`, `tests_alto_3_4_fixed.py`, `tests_alto_final.py`), y scripts sueltos sin conexión con la app (`scrip.py`, `generar_plantilla.py`, `debug_barra_progreso.py`, `abrir_web.bat`).
- Endpoints propios (`buscar_cliente`, `lista_clientes_api`, `api_cuota_mora_actual`) sin versionado ni contrato declarado (api-rules) — bajo, 10 usuarios internos.

---

## Cajón 4 — Propuesto para aceptar conscientemente (pendiente de que el dueño lo ratifique explícitamente)

| # | Qué no se va a arreglar | Motivo propuesto |
|---|---|---|
| 1 | git-rules: revisión de código por otra persona, ramas protegidas | Mantenedor único confirmado (`CONTEXTO.md`). Sustituto: autorevisión completa del diff antes de cada push — a adoptar como práctica formal en A5, no como regla incumplida. |
| 2 | Sin contrato/versionado formal en los endpoints internos (`buscar_cliente`, etc.) | 10 usuarios internos, ningún consumidor externo — el esfuerzo no se justifica hoy. |
| 3 | `notify-slack` del pipeline sin `SLACK_WEBHOOK_URL` configurado | Si el dueño no piensa usar Slack, se acepta como apagado a propósito; si sí lo quiere, pasa a cajón 1 (es la única alerta que el proyecto tiene diseñada). **Pendiente de tu decisión.** |

**Nota**: el backup roto para Postgres (cajón 1 #5) fue propuesto por uno de los audits como candidato a cajón 4, pero se mantiene en cajón 1 porque no existe todavía una aceptación consciente tuya del riesgo — si preferís aceptarlo así por ahora, decímelo y lo muevo con el motivo.

---

## Fuera de alcance de esta auditoría (anotado, no investigado a fondo)

- Front-rules (responsive, accesibilidad, estados de carga): requiere revisión visual en navegador, no solo lectura de templates.
- Contenido completo de `scripts/` (24 archivos): se inventariaron por nombre, no se leyó cada uno línea por línea.
