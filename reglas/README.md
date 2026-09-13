# Índice de Reglas — Sistema de Gestión de Créditos

> Este directorio gobierna el desarrollo de este proyecto en concreto. Generado en la **Fase A5** del protocolo de adopción (ver `../01-adopcion-protocol.md` y `../CONTEXTO.md`). A diferencia de las plantillas madre, aquí los archivos están **especializados**: nombres reales, decisiones reales, deuda real.

## Perfil de este proyecto: **P3**

Maneja dinero real (préstamos, cuotas, pagos, mora) y datos personales sensibles de clientes (cédula, teléfono, historial financiero) — aunque solo lo operen ~10 personas internamente. El perfil lo determina qué pasa si falla, no el tamaño del equipo. Confirmado en `CONTEXTO.md`.

## Cómo se usa esto (las tres capas)

| Capa | Archivo | Cuándo |
|---|---|---|
| **1. Núcleo** | [[00-CORE]] | **Siempre.** Se lee entero en cada sesión. |
| **2. Enrutamiento** | [[01-DISPARADORES]] | **Antes de cada tarea.** |
| **3. Referencia** | El resto de este directorio | Cuando la capa 2 lo indica. |
| **Transversal** | `02-AUTOMATIZABLE.md` (heredado de la plantilla madre — ver `../Reglas de desarrollo.../reglas/02-AUTOMATIZABLE.md`) | Ya se recorrió completo en la Fase A4; el resultado está en `DEUDA-TECNICA.md`. |

## Los archivos de este proyecto

| Archivo | Estado | Responde a |
|---|---|---|
| [[ai-rules]] | Generado | Cómo se comporta la IA en este proyecto — nivel de autonomía: **Consultivo**. |
| [[integrity-rules]] | Generado | Impacto cruzado — crítico dado que `views_core.py` concentra casi toda la lógica. |
| [[evolution-rules]] | Generado | Deuda técnica, Definition of Done, aprendizaje de fallos reales ya vividos. |
| [[git-rules]] | Generado | Mantenedor único — el sustituto de revisión por pares es releer el diff entero. |
| [[security-rules]] | Generado | Estado real: login sin rate-limit, admin sin MFA — ver `DEUDA-TECNICA.md`. |
| [[data-rules]] | Generado | Dinero en `Decimal`, backup con restauración probada, concurrencia en pagos. |
| [[identity-rules]] | Generado | RBAC real (`Rol`/`Permiso`), sin aislamiento por operario (decisión de negocio). |
| [[config-rules]] | Generado | Secretos, variables de entorno, escaneo ya activo. |
| [[release-rules]] | Generado | CI/CD real: qué bloquea, qué falta conectar (Render ↔ pipeline). |
| [[observability-rules]] | Generado | Estado real: sin alertas todavía (decisión explícita de diferirlo). |
| [[operations-rules]] | Generado | Backup, mantenimiento, bus factor de 1. |
| [[compliance-rules]] | Generado | Datos personales de clientes, retención sin definir todavía. |
| [[dependencies-rules]] | Generado | Lockfile real, Django parcheado, deuda de migración mayor pendiente. |
| architecture-rules | *(pendiente de generar)* | Se genera la primera vez que se planifique una refactorización real de `views_core.py`. |
| back-rules | *(pendiente de generar)* | Se genera al tocar validación/transacciones de forma significativa fuera de lo ya cubierto en data-rules. |
| front-rules | *(pendiente de generar)* | No se auditó UI en navegador en esta adopción — se genera antes del primer cambio visual serio. |
| api-rules | *(pendiente de generar)* | Los endpoints internos (`buscar_cliente`, etc.) no tienen contrato formal todavía; se genera si se agregan consumidores externos. |
| testing-rules | *(pendiente de generar)* | Hay 221 tests reales; se genera cuando se planifique subir cobertura de forma dedicada. |
| audit-rules | *(pendiente de generar)* | El rastro (`HistorioCambios`/`AuditLog`) ya se auditó dentro de data-rules §5; archivo propio si crece la necesidad. |

## Mapa de propiedad: un tema, un dueño

| Tema | Dueño | Aparece como puntero en |
|---|---|---|
| Autorización por rol/permiso | [[identity-rules]] | security, git |
| Autenticación y sesiones | [[identity-rules]] | security |
| Secretos: manejo y escaneo | [[config-rules]] | security, git, operations |
| Dinero y tiempo | [[data-rules]] §2 | 00-CORE |
| Concurrencia en pagos | [[data-rules]] §3 | 00-CORE |
| Backups y restauración | [[data-rules]] §5 | operations |
| Migraciones | [[data-rules]] §4 | release |
| Pipeline y puertas de calidad | [[release-rules]] | git, dependencies |
| Prioridad bajo presión | [[evolution-rules]] §5 | 00-CORE |
| Paradas obligatorias / autonomía | [[ai-rules]] §10 | 00-CORE |

## Dónde este conjunto no llega todavía

- No se auditó front-end en navegador real (responsive, accesibilidad) — pendiente.
- `architecture-rules`, `back-rules`, `api-rules`, `testing-rules`, `audit-rules` quedan como filas pendientes en [[01-DISPARADORES]]: se generan la primera vez que el proyecto entra de lleno en ese dominio, con el caso real delante, en vez de escribirse en abstracto ahora.

## Regla sobre estas reglas

1. Un archivo que miente sobre el proyecto es peor que no tener archivo. Si algo deja de aplicar, se corrige en el momento en que se detecta.
2. [[00-CORE]] no crece — si algo nuevo merece estar ahí, se saca otra cosa.
3. Cuando el dueño dé una instrucción operacional puntual, se identifica su archivo dueño y se escribe ahí.
4. Cuando aparezca un tipo de tarea recurrente que no está en [[01-DISPARADORES]], se añade la fila.
