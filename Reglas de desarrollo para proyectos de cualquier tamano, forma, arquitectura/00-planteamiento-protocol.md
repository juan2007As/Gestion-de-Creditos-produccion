# Protocolo de Planteamiento Inicial

> Este archivo se coloca en la raíz de un proyecto NUEVO, antes de escribir una sola línea de código.
> Cuando una IA lea este archivo, debe entrar en **MODO PLANTEAMIENTO** y seguir este protocolo sin saltarse fases.

## Regla de oro

No se escribe código de producción hasta que las Fases 1 y 2 estén cerradas y el usuario haya dado su aprobación explícita en cada una. "Planteamiento largo pero correcto" le gana siempre a "rápido pero ambiguo".

---

## FASE 0 — Entendimiento de la idea

Antes de proponer nada, la IA debe:

1. Pedir al usuario que describa la idea en sus propias palabras (aunque sea desordenado).
2. Reformulársela de vuelta con sus propias palabras para confirmar que entendió — no seguir si hay ambigüedad.
3. Identificar: quién es el usuario final, qué problema resuelve, qué lo hace distinto de alternativas existentes, y qué NO es este proyecto (alcance negativo — igual de importante que el positivo).
4. No sugerir stack, arquitectura ni funcionalidades todavía. Esta fase es solo escucha y clarificación.

Criterio de salida: el usuario confirma "sí, entendiste la idea".

---

## FASE 0.5 — Elegir la ruta del protocolo

No todo proyecto tiene interfaz de usuario. Antes de entrar en la Fase 1 se decide por cuál de estas tres rutas va el planteamiento — decidirlo mal hace que la Fase 1 sea un trámite vacío o que se salte por completo, que es lo que suele pasar.

| Ruta | Cuándo | Qué es la Fase 1 |
|---|---|---|
| **A — Producto con interfaz** | Alguien va a usar esto mirando una pantalla: web, app, panel. | La Fase 1 tal como está escrita abajo: mock navegable primero. |
| **B — Sistema sin interfaz** | API pública o interna, pipeline de datos, CLI, servicio de infraestructura, integración, bot, worker. | La Fase 1B: contrato y consumidores. |
| **C — Mixto** | Tiene interfaz **y** consumidores programáticos (lo más común en cuanto un producto crece). | Ambas, empezando por la que tenga al usuario más importante. |

En la ruta B, el error equivalente a "diseñar el backend antes que el frontend" es **diseñar la implementación antes que el contrato**. El principio se conserva: primero lo que ve quien lo consume, después cómo se construye por dentro.

### El paradigma de ejecución (segunda pregunta, igual de importante)

La ruta define **la forma**; el paradigma define **dónde corre y quién controla las actualizaciones**. Y eso invalida supuestos de fondo del conjunto de reglas, así que se decide aquí y se escribe en `CONTEXTO.md`.

| Paradigma | Supuesto que rompe | Qué hay que decidir en el planteamiento |
|---|---|---|
| **Servicio que tú despliegas** (web, API, worker) | Ninguno. Es el caso para el que está escrito el conjunto. | — |
| **Cliente que no puedes actualizar** (móvil, escritorio, extensión, SDK, dispositivo) | "Todo despliegue tiene camino de vuelta": **falso**. Una versión instalada no se revierte, y vas a tener clientes de hace años vivos. | Versión mínima soportada y cómo se fuerza; compatibilidad hacia atrás del servidor; interruptor remoto para apagar una funcionalidad rota sin publicar; datos locales y sincronización; qué pasa sin conexión. Ver [[release-rules]] §7 y [[api-rules]] §2. |
| **Producto de datos o de modelos** (ML, analítica, pipelines) | "Mismo código, mismo resultado": **falso**. El comportamiento depende de datos que cambian solos. | Qué se versiona además del código (modelo, datos de entrenamiento, features); cómo se reproduce un resultado del pasado; cómo se detecta que el modelo se ha degradado; qué es un fallo silencioso aquí (una predicción mala no lanza excepciones). |
| **Ejecución en casa del cliente** (on-premise, autoalojado) | "Producción es una y la controlas tú": **falso**. Hay tantas producciones como clientes, con versiones distintas. | Cómo se diagnostica sin acceso; cómo se actualiza; qué configuración puede tocar el cliente; qué datos puedes ver y cuáles no. |

Si el proyecto cae fuera de estos cuatro (juego, embebido, hardware), se dice explícitamente: el conjunto de reglas cubre bien la parte de servidor, datos y proceso de trabajo, y **no cubre** lo específico de ese dominio. Eso se anota como límite conocido en `CONTEXTO.md`, no se disimula.

---

## FASE 1B — Contrato y consumidores (ruta B; sustituye a la Fase 1)

La IA actúa como **diseñadora de interfaces de programación y asesora de producto**, no como programadora todavía.

1. Identificar **quién consume esto**: qué sistemas, escritos por quién, con qué capacidad de adaptarse a un cambio. Un consumidor que no controlas convierte cualquier cambio futuro en negociación ([[api-rules]]).
2. Proponer 2-3 formas distintas de exponer la funcionalidad (estilo de API, granularidad de operaciones, síncrono contra asíncrono, quién consulta a quién) con su trade-off explicado **en términos de quien lo consume**, no técnicos.
3. Construir el equivalente al mock: un **contrato ejemplo real y ejecutable** — peticiones y respuestas concretas con datos de ejemplo, o el esquema de los mensajes y eventos. No una descripción en prosa: algo contra lo que el usuario pueda decir "aquí falta un campo".
4. Recorrer los **casos de uso reales de punta a punta** sobre ese contrato, incluidos los de error: qué pasa cuando falla, cuando el dato no existe, cuando llega dos veces, cuando llega en desorden.
5. Definir las **garantías** que se prometen, porque son tan parte del contrato como los campos: ¿qué latencia?, ¿qué volumen?, ¿entrega al menos una vez o como mucho una vez?, ¿qué se garantiza si el proceso se cae a la mitad?
6. Explicitar qué datos y qué operaciones internas implica todo esto (sin diseñar el interior todavía) — esto alimenta la Fase 2.

Criterio de salida: el usuario aprueba el contrato y los casos de uso como base del proyecto.

---

## FASE 1 — Frontend / Diseño (ruta A; PRIMERO, antes que nada de backend)

La IA actúa como **diseñador UI/UX y asesor de producto**, no como programador todavía.

1. Proponer 2-3 enfoques visuales/de flujo distintos (no uno solo — dar de dónde elegir), explicando el trade-off de cada uno en términos de usuario, no técnicos.
2. Construir un mock navegable real (HTML/artifact interactivo, no descripción en texto) de las pantallas/vistas clave, con datos de ejemplo.
3. Iterar sobre el mock con el usuario: cada cambio se discute, se explica el porqué de una sugerencia, y se ajusta.
4. Definir en esta fase: mapa de pantallas/rutas, estados vacíos/carga/error de cada vista, breakpoints responsive objetivo, y el lenguaje visual (no necesariamente colores exactos, pero sí principios: denso vs espacioso, cuántos niveles de jerarquía, etc.)
5. Explicitar qué funcionalidades del front implican qué datos/acciones del back (sin diseñar el back todavía) — esto alimenta la Fase 2.

Criterio de salida: el usuario aprueba el mock y el mapa de pantallas como base visual del proyecto.

---

## FASE 2 — Backend / Arquitectura (basado en lo que salió de la Fase 1)

> **Esta fase puede devolver a la Fase 1, y eso no es un fallo del proceso: es el proceso funcionando.**
>
> Si al diseñar el interior se descubre que algo aprobado en la Fase 1 es inviable, desproporcionadamente caro, o obliga a un modelo de datos que va a doler durante años, **se vuelve a la Fase 1 con el problema concreto y con 2-3 alternativas** que conserven la intención de producto. Lo que no se hace nunca: construirlo a la fuerza porque "ya estaba aprobado", ni cambiarlo por lo bajo en la implementación y que el usuario se entere al verlo.
>
> Un mock aprobado es un acuerdo sobre la intención, no un contrato inmutable. Lo que sí es inmutable es que el cambio se decide con el usuario.

1. A partir de las funcionalidades visibles en el front, listar TODAS las funcionalidades reales necesarias (explícitas + las que el usuario no mencionó pero se derivan del front — ej. si hay login, hace falta recuperación de contraseña, verificación de email, etc. Sugerirlas, no asumirlas silenciosamente).
2. Proponer stack con opciones y trade-offs reales (no la moda del momento) — considerar: tamaño esperado del proyecto, quién lo va a mantener, presupuesto/infra disponible, tiempo de vida esperado.
3. Proponer arquitectura (monolito/microservicios/serverless/etc.) justificando por qué encaja con el tamaño y necesidades reales del proyecto — sobre-ingeniería es tan mala como sub-ingeniería.
4. Modelar entidades de datos principales y sus relaciones.
5. Definir integraciones externas necesarias (pagos, auth, email, storage, etc.).
6. Cada decisión de esta fase se presenta como pregunta o sugerencia con opciones, nunca como hecho consumado.

### 2.1 — Elegir el perfil del proyecto (obligatorio antes de cerrar la fase)

Se decide junto al usuario el perfil **P0 / P1 / P2 / P3** definido en [`reglas/README.md`](reglas/README.md), y se escribe en `CONTEXTO.md` con su justificación. El perfil determina qué reglas se aplican y cuáles serían sobre-ingeniería para este proyecto concreto.

Ante la duda entre dos perfiles se elige **el más alto**: subir de perfil a mitad del proyecto es caro (auditoría, aislamiento entre tenants e inventario de datos personales son muy difíciles de retrofitear), bajar es gratis.

### 2.2 — Preguntas operacionales que el usuario no va a plantear por su cuenta

Antes de cerrar la fase, la IA pregunta activamente por lo que no es visible desde el frontend pero determina si el proyecto es viable a medio plazo. El usuario no tiene por qué saber que estas preguntas existen — es trabajo de la IA sacarlas ([[ai-rules]] §7 Preguntar proactivamente):

- **Usuarios y permisos**: ¿hay más de un tipo de usuario? ¿quién puede ver o hacer qué? ¿hay administradores? ¿el soporte necesitará entrar como un usuario? ([[identity-rules]])
- **Organizaciones**: ¿un usuario pertenece a una empresa/equipo? Si sí, el aislamiento entre organizaciones es una decisión de arquitectura, no un filtro añadido después.
- **Datos personales**: ¿qué datos de personas se van a guardar? ¿hay menores, salud, datos financieros? ¿de qué países son los usuarios? ([[compliance-rules]])
- **Dinero**: ¿hay cobros? ¿suscripciones? ¿reembolsos? ¿facturación con obligaciones fiscales?
- **Rastro**: ¿va a hacer falta responder "quién cambió esto"? ¿ante un cliente, ante un auditor? ([[audit-rules]])
- **Pérdida y caída**: ¿cuántos datos sería aceptable perder en el peor caso? ¿cuánto tiempo puede estar caído sin que sea un problema serio? ([[operations-rules]])
- **Terceros**: ¿qué servicios externos hacen falta? ¿qué pasa con el producto si uno de ellos falla o desaparece?
- **Quién lo mantiene**: ¿una persona, un equipo? ¿quién responde si se cae un domingo? Esto cambia la arquitectura recomendada tanto como el número de usuarios.
- **Entornos**: ¿hará falta un entorno de pruebas separado de producción?
- **Ciclo de vida**: ¿qué pasa cuando un usuario se da de baja? ¿qué pasa con lo que creó?

Criterio de salida: el usuario aprueba stack, arquitectura, perfil y lista de funcionalidades.

---

## FASE 3 — Generación de artefactos del proyecto

> **Principio de esta fase: se genera lo que el proyecto ya tiene, no todo por si acaso.**
>
> Generar veinte archivos de reglas antes de escribir una línea de código produce, casi siempre, archivos genéricos con los nombres cambiados: la especialización se hace en abstracto, sin un caso real delante, y en el momento de más fatiga del proceso. Además cuesta un contexto enorme que hace falta para construir.
>
> Así que se genera el **núcleo** ahora, y cada archivo de dominio **la primera vez que el proyecto llega a ese dominio**. Es la misma lógica que [[architecture-rules]] aplica a las abstracciones: se introducen cuando hay un caso real que las pide, no antes.

### 3.1 — El núcleo, siempre y en cualquier perfil

Sin esto, el resto no se aplica: solo se archiva.

- `CONTEXTO.md` — la idea, el planteamiento completo, el **perfil**, la **ruta y el paradigma** de la Fase 0.5, el **nivel de autonomía** acordado, y las decisiones tomadas con su porqué.
- `CLAUDE.md` (o el archivo que cargue tu herramienta) — copiado de [`plantilla-CLAUDE.md`](plantilla-CLAUDE.md) y rellenado. **Es el enganche que hace que las reglas se carguen solas**; sin él todo depende de que alguien se acuerde de mirar.
- `DEUDA-TECNICA.md` — vacío al empezar, se llena según [[evolution-rules]].
- `reglas/README.md` — índice, perfil vigente y mapa de propiedad de temas.
- `reglas/00-CORE.md` — adaptado al proyecto, y **corto**: si crece, deja de cumplir su función.
- `reglas/01-DISPARADORES.md` — **con todas las filas**, incluidas las que apuntan a archivos que todavía no existen (ver 3.3), más las propias del proyecto: sus integraciones, sus tipos de tarea recurrentes.
- `reglas/ai-rules.md` — comportamiento, nivel de autonomía y tono de aplicación.
- `reglas/integrity-rules.md` — impacto cruzado.
- `reglas/evolution-rules.md` — Definition of Done, deuda técnica, prioridad bajo presión y aprendizaje desde los fallos.
- `reglas/git-rules.md`

### 3.2 — Los dominios que el proyecto ya tiene

Salen directamente de las respuestas de la Fase 2, no de una lista fija. Se genera el archivo de cada dominio que el proyecto toca **desde el primer día**:

| Se genera ahora si… | Archivo |
|---|---|
| Hay interfaz de usuario (ruta A o C) | `front-rules.md` |
| Hay servidor, lógica de negocio o base de datos | `back-rules.md` · `data-rules.md` |
| Se expone o consume alguna API, o hay integraciones | `api-rules.md` |
| Se guarda cualquier cosa de cualquier persona | `security-rules.md` (siempre) · `identity-rules.md` (si hay cuentas) |
| Hay decisiones de estructura que justificar | `architecture-rules.md` |
| Se va a escribir algún test (es decir, siempre salvo P0 desechable) | `testing-rules.md` |
| Hay configuración o algún secreto | `config-rules.md` |
| Se instala alguna dependencia | `dependencies-rules.md` |

**Piso mínimo innegociable, sea cual sea el perfil:** `security-rules`, `data-rules` y `git-rules` se generan siempre. Son las que hay que cumplir desde el primer commit, y las únicas cuyo incumplimiento no se puede arreglar retroactivamente.

**En P2 y P3 se añaden también ahora**, porque no se pueden reconstruir hacia atrás y retrofitearlas es un rediseño: `audit-rules.md`, `compliance-rules.md`, `operations-rules.md`, `environments-rules.md`, `release-rules.md`, `observability-rules.md`.

### 3.3 — Los demás: generación en diferido

El resto queda **listado en `reglas/01-DISPARADORES.md` con su fila correspondiente, pero sin archivo todavía**. La fila lleva la marca `(pendiente de generar)`.

Cuando una tarea active un disparador que apunta a un archivo inexistente, **ese es el momento**: se genera antes de continuar, se avisa al usuario de que el proyecto acaba de entrar en un dominio nuevo, y se especializa con el caso real delante.

Tres ventajas concretas frente a generarlo todo al principio:
1. Sale **especializado de verdad**, porque hay un caso concreto que lo motiva en vez de una plantilla en abstracto.
2. No se paga el contexto por adelantado.
3. El archivo nace cuando el proyecto ya tiene forma, nombres y decisiones reales que meterle dentro.

Lo que **no** puede pasar: seguir adelante sin generarlo, o improvisar el dominio de memoria. La fila del disparador existe precisamente para que ese momento no pase desapercibido.

### 3.4 — Verificación de la Fase 3 (no se cierra sin esto)

La IA repasa cada archivo generado y confirma en voz alta:

1. **No queda ningún marcador sin resolver** (`[STACK]`, `[BASE DE DATOS]`, `[BREAKPOINTS]`, `[NIVEL]`, etc.).
2. Cada archivo menciona **nombres reales** del proyecto: sus módulos, sus entidades, sus proveedores. Un archivo que podría pertenecer a cualquier proyecto no está especializado.
3. Las reglas de perfil superior al elegido se han eliminado, o conservan su marca `[Pn]` visible para que se sepa que están dormidas a propósito.
4. Ninguna regla generada contradice a otra ni contradice una decisión de `CONTEXTO.md`.
5. Las decisiones concretas de la Fase 2 (dónde vive el token, quién es la fuente de verdad de cada dato, qué se audita, qué pasa si cae cada tercero) están escritas en su archivo, no solo en la conversación.
6. **El enganche de carga existe y nombra correctamente los archivos** — se comprueba abriendo el `CLAUDE.md` generado, no suponiéndolo.
7. **Los disparadores cubren los dominios diferidos**, con su marca de pendiente. Un dominio diferido sin fila es un dominio que se va a olvidar.

`reglas/02-AUTOMATIZABLE.md` se recorre aquí línea por línea, decidiendo para cada una: **ya está / se implementa ahora / se acepta como deuda con motivo**. Ninguna línea se queda sin decisión, y lo que quede como deuda se escribe en `DEUDA-TECNICA.md`.

Criterio de salida: el usuario revisa y aprueba lo generado. A partir de aquí empieza el desarrollo real, gobernado por estas reglas.

---

## FASE 4 — Desarrollo continuo y actualizaciones (vive mientras el proyecto vive)

Esta fase no tiene un "criterio de salida" — es el modo permanente de trabajo una vez cerrado el planteamiento inicial. Cada feature, fix o cambio nuevo:

1. Se contrasta contra `CONTEXTO.md` (¿sigue alineado con el planteamiento original?).
2. Sigue el ciclo de análisis → sugerencia → decisión conjunta de [[ai-rules]].
3. Pasa el chequeo de impacto cruzado de [[integrity-rules]] antes de tocar algo existente.
4. Se considera "terminado" solo cuando cumple la Definition of Done de [[evolution-rules]], filtrada por el perfil del proyecto.
5. Cada cierto número de cambios (ver [[evolution-rules]]), se audita el conjunto de `reglas/` y `CONTEXTO.md` para que no queden desactualizados — y se revisa si el **perfil del proyecto sigue siendo el correcto**. Un proyecto que empezó como P1 y ya tiene usuarios de pago es P2, y las reglas que eso activa se ponen al día o se registran como deuda.

Esto es lo que hace que el proyecto pueda crecer indefinidamente sin que el planteamiento inicial se "pierda" con el tiempo.

---

## Reglas de comportamiento durante TODO el protocolo

- Nunca avanzar de fase sin aprobación explícita del usuario.
- Si el usuario pide saltarse una fase, advertir el riesgo concreto de hacerlo (no bloquear, pero sí dejar constancia).
- Priorizar verdad y practicidad sobre complacencia: si una idea del usuario tiene un problema técnico o de producto, decirlo directamente con la alternativa.
- Todo output de este protocolo debe quedar escrito en archivos, no solo dicho en conversación — el planteamiento debe sobrevivir a que se cierre la sesión.
