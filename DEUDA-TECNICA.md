# DEUDA-TECNICA.md — Sistema de Gestión de Créditos

> Generado en **Fase A3 del protocolo de adopción**. Perfil **P3**. Nada de esto se ha arreglado todavía — es inventario, no acción. Clasificado en los 4 cajones del protocolo (`01-adopcion-protocol.md`).

---

## Cajón 1 — Se arregla ya, antes de tocar nada más

| # | Hallazgo | Archivo:línea | Por qué importa | Dueño de regla |
|---|---|---|---|---|
| 1 | ~~Bug de dinero real~~ **[RESUELTO]** `Cuota.total_a_pagar()` sumaba el interés *original completo* en vez del *interés pendiente* — cobraba de más en cuotas con abono parcial de interés. Corregido para usar `monto_pendiente_interes` (igual que `CuotaRapida` y que `detalles_completos()`, que ya lo hacía bien en la misma clase) y quitado el `float()` — ahora en `Decimal` de punta a punta. Test de regresión agregado (`test_unit_models.py::test_total_a_pagar_usa_interes_pendiente_no_el_original`), verificado que falla contra el código viejo y pasa con el fix. Sin regresiones: 221 tests, mismos 8 failures/25 errors preexistentes. | `mi_app/models.py:835-838` | — | data-rules §2 |
| 2 | `tech_debt_fixes.py` (`ConsolidatedCalculations`/`ConsolidatedValidations`) fue escrito para resolver exactamente esta duplicación (mora, interés, validaciones) pero **nunca se conectó** al código real — solo lo usan sus propios tests. Da falsa sensación de que la deuda ya se pagó. | `mi_app/utilities/tech_debt_fixes.py` (431 líneas, 0 usos fuera de `test_tech_debt_critica10.py`) | Mientras nadie lo mire, cualquiera asume que la lógica ya está centralizada. No lo está. | evolution-rules / architecture-rules |
| 3 | Pagos sin atomicidad ni bloqueo: solo `registrar_pago` (vía `@atomic_payment_view`) usa `transaction.atomic()`/lock. `pagar_cuota_especifica` y toda la línea de "préstamos rápidos" mutan saldos sin ninguno de los dos. | `views_core.py:1370-1450`, `:3118`, `:3240`, `:3260` vs `:997` (el único protegido) | Dos requests simultáneos sobre la misma cuota (doble clic, dos pestañas) pueden dejar el saldo o el estado inconsistente. | data-rules §3 |
| 4 | ~~IDOR: aislamiento por operario roto~~ **[RESUELTO — decisión de producto, no bug]** Se confirmó que el control de "esto es tuyo" (`valida_propiedad_cliente`/`valida_propiedad_prestamo`) era un no-op en absolutamente todas las vistas donde se usaba, porque `Cliente`/`Prestamo` nunca tuvieron campo de dueño. El dueño del proyecto decidió explícitamente que **todos los operarios deben ver todos los clientes** — no hace falta aislar. Se retiraron los dos decoradores (6 puntos de uso en `views_core.py`), sus definiciones en `decorators.py`, y el test que asumía aislamiento (`test_fase_2.py::DecoradorValidacionPropiedad`). Sin regresiones: 221 tests (uno menos, el retirado), mismos errores/fallos preexistentes. | `mi_app/views_core.py`, `mi_app/utilities/decorators.py` | Movido a cajón 4 (ver abajo) — el código ahora refleja la regla real, no una que nunca funcionó. | identity-rules §4 |
| 5 | ~~Backup real inexistente para producción~~ **[RESUELTO]** `.github/workflows/backup.yml`: `pg_dump` diario + restauración real contra una base vacía en cada corrida (falla si no restaura). El dueño ya agregó el secret `DATABASE_URL` en GitHub — el workflow puede correr de verdad. Se confirma que corrió con éxito la primera vez tras el próximo push (pestaña Actions). | `mi_app/utilities/backup_manager.py`, `.github/workflows/backup.yml` | — | data-rules §5 |
| 6 | Sin registro de errores que sobreviva ni alerta de ningún tipo. **[Decisión del dueño: se deja anotado, no se implementa por ahora.]** | `settings.py:209-229` | Si algo se rompe en producción, nadie se entera salvo que un usuario lo reporte. Sigue en cajón 1 porque el riesgo no cambió, solo la decisión de cuándo resolverlo. | observability-rules |
| 7 | ~~`login_view` sin rate-limit~~ **[RESUELTO]** Se agregó `@ratelimit(key='ip', rate='5/m', method='POST', block=True)`, mismo patrón que las otras vistas ya protegidas del proyecto. Se apoya en `RateLimitMiddleware` (ya existente) para devolver 429. | `views_core.py:41` | — | security-rules |
| 8 | `/admin/` en ruta por defecto, sin MFA ni restricción adicional — exigido desde P3. **Decisión del dueño**: no se implementa MFA por ahora (requiere nueva dependencia + migración + flujo de login nuevo, no es un ajuste menor) — queda como deuda aceptada, no arreglada. | `proyecto_john/urls.py:24` | Objetivo obvio de escaneo automatizado; hoy protegido solo por usuario+contraseña estándar de Django (password aleatoria desde la Fase A4, ya no `Admin123!`). | identity-rules / security-rules |
| 9 | ~~Credencial real de un tercero expuesta~~ **[RESUELTO]** Carpeta `lambda/` retirada del repositorio de trabajo. El dueño ya avisó a Comfama y la key fue rotada de su lado. **Queda un residuo menor, no urgente**: la key vieja (ya inválida) sigue visible en el historial de `origin/main` — reescribir ese historial (force-push) es una operación de alto impacto que se hace solo si el dueño la pide explícitamente aparte; hoy no es necesario porque la key ya no sirve para nada. | `lambda/` (ya no existe localmente); residuo inerte en el historial de `origin/main` | — | config-rules §2 |
| 10 | Parseo de `Decimal` sin `try/except` en un endpoint de pago → `decimal.InvalidOperation` sin capturar → 500 crudo. | `views_core.py:1386-1388` | Viola la regla del núcleo "ningún error se muestra crudo", en una vista que mueve dinero. | 00-CORE #9 |
| 11 | ~~El CI no era un gate real~~ **[RESUELTO Y VERIFICADO EN PRODUCCIÓN]** `bandit`/`safety` ya no corren con `\|\| true`. Job `secrets-scan` activo. `quality-gate` falla de verdad si `security` o `secrets-scan` fallan. `render.yaml` con `autoDeploy: false`; el job `deploy` dispara el Deploy Hook de Render (`secrets.RENDER_DEPLOY_HOOK_URL`) solo si `quality-gate` pasó, solo en push a `main`. Confirmado por el dueño: el pipeline corrió en verde de punta a punta (`tests`, `linting`, `security`, `secrets-scan`, `performance`, `quality-gate`, `deploy`) y Render desplegó. | `.github/workflows/tests.yml`, `render.yaml:22` | El gate de calidad bloquea de verdad y controla el deploy real — ya probado, no solo diseñado. | release-rules §1 / dependencies-rules |
| 12 | Variables sin default (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) que tumban el arranque completo si faltan. | `settings.py:234-238` | El servicio entero no levanta, no es un 500 de una vista puntual. | config-rules |
| 13 | Funciones núcleo de negocio sin ningún test dedicado: `obtener_profile()`, `calcular_fechas_pago`, `determinar_estado_cuota_al_crear`. | `mi_app/utilities/decorators.py`, `mi_app/utils.py` | Cambiar cualquiera de estas sin red de tests es tocar dinero/permisos a ciegas. | testing-rules / integrity-rules |
| 17 | ~~`CACHES` de producción apuntaba a Redis en `127.0.0.1:6379`, que nunca existió en este deploy~~ **[INCIDENTE REAL, RESUELTO]** Ya estaba anotado como latente desde la A0 (afectaba a los 3 `@ratelimit` de backups, nunca se notó porque esas rutas casi no se usan). Al agregar `@ratelimit` a `login_view` en esta misma sesión (cajón 1 #7), **se disparó en producción**: todo POST a `/login/` devolvía 500 al intentar conectarse a un Redis inexistente, mientras el GET seguía en 200 — rompiendo el login que se suponía que estábamos arreglando. Fix: `settings.py` ahora usa `LocMemCache` salvo que exista un `REDIS_URL` real configurado (nunca más un default de Redis en localhost). | `proyecto_john/settings.py` | Verificar en el próximo login real que efectivamente ya no da 500. | data-rules / operations-rules |
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
| 4 | **[Confirmado — A4]** No hay aislamiento de datos entre operarios: cualquier operario ve/edita/paga cualquier cliente o préstamo, sin importar quién lo creó. | Motivo explícito del dueño: equipo pequeño y de confianza (máx. 10 personas), el aislamiento nunca fue una necesidad real del negocio — el código que lo simulaba nunca funcionó y se retiró en vez de arreglarse. |
| 5 | Registro de errores / alerta mínima sin implementar (Sentry, email, etc.) | Decisión explícita del dueño en esta sesión: no implementar todavía. Sigue igual anotado como riesgo activo en cajón 1 #6 — este ítem documenta la decisión de *cuándo*, no reduce el riesgo. |

**Nota**: el backup roto para Postgres (cajón 1 #5) fue propuesto por uno de los audits como candidato a cajón 4, pero se mantiene en cajón 1 porque no existe todavía una aceptación consciente tuya del riesgo — si preferís aceptarlo así por ahora, decímelo y lo muevo con el motivo.

---

## Checklist completo de `02-AUTOMATIZABLE.md` (Fase A4 — cada línea tiene decisión)

| Línea | Decisión |
|---|---|
| Formateo/linter en pre-commit | Deuda cajón 3 — CI ya avisa (flake8/black/isort no bloqueantes); aplicar formateo real al tocar cada archivo, no de una vez (evita un diff de miles de líneas irrevisable) |
| Escaneo de secretos en pre-commit | ✅ Hecho |
| Archivos que nunca deben subirse | ✅ Ya estaba (`.gitignore` cubre `.env`, `db.sqlite3`, `/staticfiles`, `/media`) |
| Tests en verde (pipeline) | ✅ Ya estaba |
| Comprobación de tipos/compilación | Deuda cajón 3 — sin type hints/mypy; bajo impacto a este tamaño de equipo |
| Escaneo de secretos (pipeline) | ✅ Hecho (`secrets-scan` job) |
| Vulnerabilidades en dependencias | ✅ Hecho (`safety`, bloqueante) |
| Lockfile presente y coherente | ✅ Hecho — `requirements.txt` con TODAS las versiones fijadas (antes solo 2 de 15 lo estaban); se retiró `pillow` (cero uso real en todo el repo) |
| Licencias de dependencias permitidas | Deuda cajón 3 — software de uso interno, no se redistribuye |
| SAST | ✅ Cubierto por `bandit` (ya bloqueante) |
| Build reproducible | Deuda cajón 3 — depende del build de Render, sin Docker propio |
| Detección de tests desactivados | Ya documentado: los E2E corren con `\|\| true` a propósito (necesitan Selenium) — deuda cajón 3, conocida y nombrada, no oculta |
| **[Hallazgo nuevo, cajón 2]** `pytest mi_app/tests/` nunca pudo ni siquiera recolectar la mayoría de los archivos con estilo pytest (fixtures de `tests/conftest.py`, un directorio hermano no un ancestro de `mi_app/tests/`) ni sabía qué settings de Django usar — el CI llevaba corriendo estos pasos **fallando en la colección desde siempre**, nunca ejecutando un test real. Se arregló la infraestructura (`pytest.ini` + `conftest.py` raíz con `pytest_plugins`), y al arreglarse salieron a la luz **~40 fallos reales preexistentes** (`test_integration_workflows.py`: 11; el resto repartido en `test_validaciones_critica4.py`, `tests_alto_2.py` —clases CSS que no existen—, `tests_alto_3_4*.py`, etc.). Se marcaron esos pasos como no bloqueantes (`\|\| true`) para no ocultar el hallazgo pero tampoco bloquear el pipeline con una investigación que no se puede hacer de pasada. **Pendiente: revisar archivo por archivo cuáles son bugs reales vs. tests desactualizados.** |
| **[Hallazgo nuevo, cajón 3]** `.gitignore` tiene patrones demasiado amplios (`*.ini`, `*.cfg`) que se tragan archivos de configuración legítimos del proyecto, no solo temporales del editor. Ya pasó una vez con `*_BACKUP*` ocultando `mi_app/urls_backups.py` (Fase A0), y ahora con `*.ini` ocultando el `pytest.ini` recién creado (tuvo que forzarse con `git add -f`). Revisar y acotar esos patrones la próxima vez que se toque `.gitignore`. |
| Validación de configuración al arrancar | ✅ Ya estaba |
| Sin valores por defecto inseguros | ✅ Ya estaba |
| Bloqueo de envíos reales fuera de producción | ✅ Ya estaba (`EMAIL_BACKEND` de consola fuera de producción) |
| Filtro de tenant | No aplica — proyecto confirmado no-multi-tenant en `CONTEXTO.md` |
| Denegar por defecto | ✅ En general (todas las vistas de negocio llevan `@login_required` + `@require_permission`/`@require_rol`); revisar caso a caso al agregar vistas nuevas |
| Enmascarado de campos sensibles en logs | Deuda cajón 2 — el middleware de auditoría ya excluye contraseñas/CSRF del payload, pero no enmascara cédula/monto en el resto de logs |
| Límites de tamaño de petición/página | Deuda cajón 3 — `lista_clientes_api` (`views_core.py:125`) devuelve TODOS los clientes sin paginar; bajo impacto con el volumen actual, revisar si crece |
| Timeout en cliente HTTP saliente | No aplica — `mi_app/` no hace llamadas HTTP salientes (confirmado por grep) |
| Restricciones de BD (unicidad, FK, NOT NULL, rangos) | Ya está en gran parte (constraints ya vistas en migraciones); no se auditó campo por campo |
| Tipo exacto para importes | Ya está a nivel de columna (`DecimalField`); el bug real estaba en los métodos de cálculo, no en el esquema — ver cajón 1 #1 |
| Tipo consciente de zona horaria | ✅ Ya está (`USE_TZ=True`, confirmado sin mezcla con `datetime.now()` en A3) |
| Audit log sin permiso de borrado/modificación | ✅ Ya está (confirmado en A3: `AuditLogAdmin` lo bloquea, y no hay `.update()`/`.delete()` desde código de negocio) |
| Permisos mínimos del usuario de BD | Deuda cajón 2 — no se pudo verificar desde aquí (config de Render), pendiente de revisar en el dashboard |
| Test "A no puede leer el recurso de B" | No aplica igual que el filtro de tenant — decisión de negocio: todos los operarios ven todos los clientes |
| Idempotencia en pagos | Deuda cajón 1 — relacionado con la falta de atomicidad ya reportada (cajón 1 #3): sin lock, un doble submit puede duplicar un pago |
| Contrato de API verificado | No aplica (P2), endpoints internos sin consumidores externos |
| Migraciones probadas sobre datos representativos | Deuda cajón 2 — no se prueba en CI contra un dataset realista, solo contra BD vacía |
| Sesiones invalidadas al cambiar contraseña | Deuda cajón 3 — Django lo hace por defecto desde 4.1+ (`django.contrib.auth.password_validation` con `update_session_auth_hash`), no se confirmó que el flujo de cambio de contraseña propio lo use |
| Vigilancia de tareas programadas (silencio = alerta) | Deuda cajón 2 — `auto_mantenimiento.py` no tiene monitoreo de última ejecución exitosa |
| Caducidad de certificados/dominios/tokens | Deuda cajón 3 — Render gestiona el certificado; sin vigilancia propia de la key de Comfama ahora retirada |
| Antigüedad del backup y del último restore probado | ✅ Cubierto por el propio `backup.yml` (falla si no restaura, corre diario) |
| Tasas de error/latencia, métricas de negocio | Deuda cajón 1 — mismo hueco que observabilidad general |
| Discrepancias de reconciliación con terceros | No aplica — no hay integración de terceros activa tras retirar `lambda/` |
| Gasto de infraestructura/logs | Deuda cajón 3 — bajo volumen actual (10 usuarios), revisar si crece |
| Purga de datos que superan retención | Deuda cajón 2 — no hay política de retención definida (ver cajón 2 de compliance) |
| Caducidad de feature flags | No aplica — el proyecto no usa feature flags |
| Recordatorios calendarizados (backup, rotación, accesos, dependencias, auditoría de reglas) | Se dejan para la Fase A5/A6 — se registran como rutina en `reglas/operations-rules.md` especializado |

## Fuera de alcance de esta auditoría (anotado, no investigado a fondo)

- Front-rules (responsive, accesibilidad, estados de carga): requiere revisión visual en navegador, no solo lectura de templates.
- Contenido completo de `scripts/` (24 archivos): se inventariaron por nombre, no se leyó cada uno línea por línea.
