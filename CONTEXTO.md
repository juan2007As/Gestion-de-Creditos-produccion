# CONTEXTO.md — Sistema de Gestión de Créditos

> Generado en **Fase A1 del protocolo de adopción** (`01-adopcion-protocol.md`). Es reconstrucción arqueológica: el planteamiento existió, nunca se escribió. Cada bloque marca si es **[RECONSTRUCCIÓN]** (inferido leyendo el código, pendiente de que el dueño lo desmienta si hace falta) o **[CONFIRMADO]** (dicho explícitamente por el dueño en esta sesión).

## Qué es el producto

**[RECONSTRUCCIÓN, aproximada — el dueño no la confirma al 100%, dice "te acercas mucho pero no digo que sí tal cual"]**

Un sistema interno para que el dueño y hasta ~10 operarios/gerentes administren una operación propia de préstamos/créditos: alta de clientes, otorgar préstamos con cuotas (quincenal/mensual), registrar pagos, calcular mora, mantener un scoring/etiqueta de cliente (BUENO/MEDIO/MALO/SIN_HISTORIAL) y una lista negra. Los clientes finales (deudores) no tienen acceso al sistema — solo lo operan las ~10 personas autorizadas.

## Quién lo usa **[CONFIRMADO]**

- Máximo 10 personas de momento (operarios/gerentes/admin), uso interno.
- El dueño (Juan Carlos) es la **única persona que sostiene y administra el código y la lógica** — no hay equipo, no hay bus factor que repartir.

## Perfil asignado: **P3** **[CONFIRMADO — Fase A2 cerrada]**

El perfil no lo determina el tamaño (10 usuarios es poco) sino qué pasa si falla: el sistema maneja **dinero real** (montos de préstamo, cuotas, pagos, mora) y **datos personales sensibles** (cédula, teléfono, historial financiero) de los clientes de la operación de crédito — que no son los 10 operarios, son terceros cuyos datos están en juego. Encaja con el ejemplo textual del protocolo ("un script de 300 líneas que mueve las nóminas es P3"). Ante la duda se elige el perfil más alto.

## Ruta y paradigma

- **Ruta A** — producto con interfaz (paneles web server-rendered con Django templates).
- **Paradigma** — servicio que el propio dueño despliega y controla (Render). No aplica ninguno de los paradigmas especiales (cliente no actualizable, producto de datos/ML, on-premise).

## Nivel de autonomía acordado

**Pendiente de fijar formalmente** en `reglas/ai-rules.md` (Fase A5). De momento rige lo que pidió el dueño al iniciar la adopción: ninguna fase se encadena sin su aprobación explícita, y durante las Fases A0-A3 no se toca código.

## Decisiones estructurales encontradas en el código, y su motivo **[CONFIRMADO por el dueño]**

| # | Decisión visible en el código | Motivo real | Tipo |
|---|---|---|---|
| 1 | RBAC propio (`Rol`/`Permiso`/`RolPermiso`/`UsuarioProfile`) en vez de los permisos nativos de Django | Sugerido por una IA de asistencia previa; el dueño lo califica como "decisión tonta", sin motivo técnico sólido detrás | **Accidente histórico** — no se toca ahora, se revisa en A3 si migrar a permisos nativos compensa el esfuerzo |
| 2 | "Préstamos rápidos" como modelos paralelos (`PrestamoRapido`/`CuotaRapida`/`PagoPrestamoRapido`) en vez de un tipo/flag dentro de `Prestamo` | Es un producto de crédito genuinamente propio y distinto (decisión deliberada), pero el dueño sospecha que **la implementación está mal hecha** | **Decisión deliberada de negocio + posible bug/mala implementación** → entra en la pista paralela de revisión de lógica que pidió el dueño |
| 3 | Solo 2 migraciones para 17 modelos con historia evidente (RBAC, scoring, lista negra, préstamos rápidos) | Misma causa que la decisión 1: intervención de una IA previa sin buen criterio | **Accidente histórico.** Riesgo concreto a verificar en A3: si la base de Postgres de producción en Render fue creada bajo un historial de migraciones distinto al que hoy vive en el repo, un `migrate` puede fallar por desajuste de estado — **posible relación directa con el 500 de login ya investigado** |
| 4 | Carpeta `lambda/` con integración a Comfama (API key real incluida) viviendo en este mismo repositorio | No pertenece al producto — el dueño confirma que **se va del repo** | **Ajeno / cadáver a remover.** Se suma a un pedido más amplio del dueño: reorganizar el repo y sacar archivos sueltos (además de `lambda/`: `$file`, scripts de la raíz sin uso, variantes redundantes de backup y de tests ya detectadas en A0) |
| 5 | Migración de PythonAnywhere a Render como plataforma de despliegue | Decisión pragmática y deliberada: facilidad y tier gratuito | **Decisión deliberada.** Todo lo que quedó de PythonAnywhere (`DEPLOY.md`, `PYTHONANYWHERE_COMANDOS.txt`, `prepare_production.py` generando config de MySQL) es legado a limpiar, no una alternativa viva |

## Qué NO es este proyecto

**[RECONSTRUCCIÓN — el dueño todavía no confirmó ni corrigió estos tres puntos, quedan abiertos]**

- No tiene pasarela de pago real integrada: los pagos se registran manualmente, no se cobran de forma automática.
- No es multi-tenant: es una sola operación de crédito, no varias empresas compartiendo el sistema.
- No tiene app móvil ni expone una API pública consumida por terceros (la única integración externa tipo API es `lambda/`, que se está retirando por ajena al producto).

## Encargo adicional del dueño, transversal a toda la adopción **[CONFIRMADO]**

Además de auditar cumplimiento de las reglas de proceso (seguridad, backups, deuda técnica, arquitectura), el dueño pidió expresamente revisar **lógica de negocio e incoherencias reales entre frontend y backend** — bugs funcionales, no solo higiene de proceso. Se lleva como pista separada y se cruza con `DEUDA-TECNICA.md` en el cajón que corresponda (cajón 1 si hay dinero real de por medio).

## Limitación operativa detectada, no resuelta todavía

Este directorio de trabajo **no es un repositorio git activo** (no existe carpeta `.git`; es una copia/extracción del repo real de GitHub). Cualquier limpieza de archivos que se haga aquí más adelante (Fase A3/A4) no tiene red de seguridad local vía `git revert` — hay que decidir antes de borrar nada si se trabaja contra un clon real conectado a `juan2007As/Gestion-de-Creditos-produccion` o si esta copia se sincroniza manualmente después.
