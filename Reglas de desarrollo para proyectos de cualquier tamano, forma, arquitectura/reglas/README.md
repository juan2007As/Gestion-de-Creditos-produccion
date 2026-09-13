# Índice de Reglas

> Este directorio es el conjunto de reglas que gobierna el desarrollo del proyecto.
>
> **En este repo son plantillas madre deliberadamente genéricas**, pensadas para servir a proyectos de cualquier tipo, tamaño y arquitectura. La especialización ocurre en la **copia** que se genera dentro de cada proyecto real — en la Fase 3 del [protocolo de planteamiento](../00-planteamiento-protocol.md) o en la Fase A5 del [protocolo de adopción](../01-adopcion-protocol.md). Los marcadores tipo `[STACK]` que quedan aquí son intencionados: **no se rellenan en este repo.**

## Cómo se usa esto (las tres capas)

El conjunto es grande a propósito: cubre lo que hace falta para operar un sistema de verdad. Pero nadie aplica trescientas reglas por tarea. Por eso está organizado en capas de atención, y **saltarse este orden es la forma habitual de que un conjunto de reglas exista sin aplicarse**:

| Capa | Archivo | Cuándo |
|---|---|---|
| **1. Núcleo** | [[00-CORE]] | **Siempre.** Una página. Es lo único que se lee entero en cada sesión. |
| **2. Enrutamiento** | [[01-DISPARADORES]] | **Antes de cada tarea.** Dice qué archivo abrir según lo que se va a hacer. Treinta segundos. |
| **3. Referencia** | El resto de este directorio | Cuando la capa 2 lo indica, o al planificar. |
| **Transversal** | [[02-AUTOMATIZABLE]] | Al montar el proyecto y en cada auditoría: qué reglas debe verificar una máquina en vez de la memoria de alguien. |
| **Apéndice** | [[99-EJEMPLO]] | Una vez, al principio: una feature recorriendo el conjunto entero de principio a fin. |

---

## Perfiles de proyecto

No todos los proyectos necesitan lo mismo. Un prototipo personal con auditoría inmutable y RPO/RTO documentados es tan un error como una plataforma de pagos sin ellos. Por eso cada regla lleva marcado el **perfil mínimo** en el que aplica.

| Perfil | Qué es | Ejemplo |
|---|---|---|
| **P0** | Personal / prototipo / demo. Sin usuarios reales, sin datos de terceros, se puede tirar y rehacer. | Un script, un experimento, un portfolio. |
| **P1** | Interno o con pocos usuarios conocidos. Hay datos que dolería perder, pero no hay obligación legal ni terceros afectados. | Herramienta interna del equipo, side project con 20 usuarios. |
| **P2** | Producto con usuarios reales que no conoces. Alguien confía sus datos y su trabajo al sistema. Caerse tiene consecuencias. | SaaS, app pública, marketplace. |
| **P3** | Datos sensibles, dinero o regulación. Un fallo tiene consecuencias legales, financieras o sobre la salud/seguridad de personas. | Pagos, salud, menores, datos biométricos, sector financiero. |

**Los perfiles son acumulativos**: P2 incluye todo lo de P1 y P0.

### Convención de marcado

- Una regla **sin marca** aplica siempre, desde P0.
- Una regla marcada **`[P2]`** aplica desde P2 en adelante (y por tanto también en P3).
- Un archivo entero puede llevar un perfil mínimo en su cabecera.

### Cómo se elige el perfil

Se decide en la **Fase 2** del planteamiento (o en la **Fase A2** de adopción), junto al usuario, y se escribe en `CONTEXTO.md`.

**El perfil no lo determina el tamaño del código: lo determina qué pasa si falla.** Un script de 300 líneas que mueve nóminas es P3; una aplicación de 80.000 líneas sin usuarios reales es P0.

Ante la duda entre dos perfiles, **se elige el más alto**: subir de perfil a mitad del proyecto es caro (retrofitear auditoría, aislamiento entre tenants o inventario de datos personales es un rediseño), bajar es gratis.

El perfil se **revisa** en cada auditoría periódica de [[evolution-rules]]: un proyecto que empezó como P1 y ya tiene 500 usuarios de pago es P2, le guste a quien le guste.

---

## Los archivos

### Navegación
| Archivo | Responde a |
|---|---|
| [[00-CORE]] | ¿Qué aplica a absolutamente todo lo que haga? |
| [[01-DISPARADORES]] | Voy a hacer X — ¿qué tengo que leer antes? |
| [[02-AUTOMATIZABLE]] | ¿Qué debería estar comprobando una máquina en vez de mi memoria? |
| [[99-EJEMPLO]] | ¿Cómo se ve todo esto aplicado a una feature real? |

### Cómo se trabaja
| Archivo | Responde a |
|---|---|
| [[ai-rules]] | Cómo se comporta la IA: analizar antes de actuar, verdad sobre complacencia, nivel de autonomía. |
| [[integrity-rules]] | ¿Este cambio rompe algo más? Protocolo de impacto cruzado. |
| [[evolution-rules]] | Cómo crece el proyecto sin perder coherencia: deuda técnica, Definition of Done, qué se sacrifica bajo presión. |
| [[git-rules]] | Control de versiones, commits, ramas, revisión de código. |

### Cómo se construye
| Archivo | Responde a |
|---|---|
| [[architecture-rules]] | Límites de módulos, dependencias, cuándo abstraer, documentación. |
| [[front-rules]] | UI, estados, responsive, accesibilidad, i18n. |
| [[back-rules]] | Validación, transacciones, rendimiento, trabajo asíncrono. |
| [[api-rules]] | Contratos, versionado, deprecación, integraciones, webhooks, reconciliación. |
| [[data-rules]] | Modelo, migraciones, backups, concurrencia, dinero y tiempo. |
| [[testing-rules]] | Qué se testea, con qué profundidad, y qué no. |

### Quién puede hacer qué, y quién lo hizo
| Archivo | Responde a |
|---|---|
| [[identity-rules]] | Usuarios, sesiones, permisos, multi-tenancy, ciclo de vida de cuenta. |
| [[security-rules]] | Que no te roben ni rompan nada. |
| [[audit-rules]] | ¿Quién hizo qué, cuándo y desde dónde? Rastro inmutable. |
| [[compliance-rules]] | Obligaciones legales sobre datos personales, pagos y menores. |

### Cómo vive en producción
| Archivo | Responde a |
|---|---|
| [[environments-rules]] | Local / test / staging / producción y el flujo entre ellos. |
| [[config-rules]] | Configuración, secretos y feature flags. |
| [[release-rules]] | CI/CD, despliegue, versionado, rollback. |
| [[dependencies-rules]] | Librerías de terceros y cadena de suministro. |
| [[observability-rules]] | Logs, métricas, errores: enterarse antes que el usuario. |
| [[operations-rules]] | Mantenimiento, incidentes, continuidad, accesos. |

---

## Mapa de propiedad: un tema, un dueño

Muchos temas tocan varios archivos. Para que no diverjan con el tiempo, **cada tema tiene un archivo canónico**: ahí vive la regla completa. En los demás archivos aparece como **puntero**, nunca como copia. Si alguien necesita cambiar una regla, la cambia en su dueño y el resto sigue siendo válido.

| Tema | Dueño | Aparece como puntero en |
|---|---|---|
| Autorización y permisos | [[identity-rules]] §4 | security, back, front, testing, api |
| Autenticación y sesiones | [[identity-rules]] §1-§3 | security |
| Multi-tenancy | [[identity-rules]] §5 | data, testing, back |
| Secretos: manejo y rotación | [[config-rules]] §2 | security, git, operations |
| Validación de entrada | [[security-rules]] §Validación | back, front, api |
| Contratos y cambios rompedores | [[api-rules]] §1-§2 | back, integrity, front |
| Idempotencia y reintentos | [[api-rules]] §3 | back, testing, data |
| Backups y restauración | [[data-rules]] §5 | environments, operations |
| Concurrencia | [[data-rules]] §3 | back |
| Dinero y tiempo | [[data-rules]] §2 | front, back |
| Migraciones | [[data-rules]] §4 | release, integrity |
| Borrado de un usuario y sus datos | [[compliance-rules]] §4 | identity, data |
| Retención de datos | [[compliance-rules]] §5 | data, observability, audit |
| Trabajo asíncrono, colas y jobs | [[back-rules]] §Trabajo asíncrono | observability, api |
| Rastro de acciones sensibles | [[audit-rules]] | identity, compliance, operations, config |
| Alertas | [[operations-rules]] §7 | observability |
| Pipeline y puertas de calidad | [[release-rules]] §1 | git, testing, dependencies, security |
| Prioridad bajo presión | [[evolution-rules]] §5 | 00-CORE |
| Paradas obligatorias / autonomía | [[ai-rules]] §10 | 00-CORE |

---

## Dónde este conjunto no llega

Decirlo importa: un conjunto de reglas que aparenta cubrirlo todo hace que nadie busque en otro sitio lo que le falta.

Está escrito asumiendo **un servicio que tú despliegas y controlas**, con base de datos y usuarios. Sobre esa base, la Fase 0.5 del planteamiento identifica tres paradigmas donde algunos supuestos de fondo **dejan de ser ciertos**, y qué hay que decidir en cada uno: clientes que no puedes actualizar (móvil, escritorio, SDK), productos de datos y modelos, y ejecución en casa del cliente. Lo específico de esos paradigmas está cubierto en parte ([[release-rules]] §7, [[api-rules]] §2), no del todo.

Y hay dominios donde este conjunto **solo cubre la mitad genérica** — el proceso de trabajo, los datos, la seguridad, la operación — y no lo propio del oficio: videojuegos, sistemas embebidos, hardware, tiempo real estricto, cálculo científico. En esos casos se dice explícitamente en `CONTEXTO.md` y se busca la referencia específica del dominio. No se disimula el hueco.

## Regla sobre estas reglas

1. Un archivo de reglas que miente sobre el proyecto es peor que no tener archivo. Si una regla ya no aplica o se contradice con otra, se corrige en el momento en que se detecta — no "cuando haya tiempo".
2. Al generarse para un proyecto real, los archivos se **especializan**: nombres de servicios reales, stack real, decisiones reales. Un archivo generado que sigue diciendo `[STACK]` no está terminado. (En este repo madre sí se quedan genéricos, a propósito.)
3. **[[00-CORE]] no crece.** Es la única regla estructural del conjunto: si una regla nueva parece merecer estar en el núcleo, hay que sacar otra. Un núcleo de seis páginas es exactamente el problema que el núcleo resuelve.
4. Cuando el usuario dé una instrucción operacional puntual ("producción siempre manda", "nunca toques la tabla X sin avisar"), no se trata como anécdota: se identifica a qué archivo pertenece y se escribe ahí (ver [[ai-rules]] §7 Preguntar proactivamente).
5. Cuando aparezca un tipo de tarea recurrente que no está en [[01-DISPARADORES]], se añade la fila. Esa tabla es el índice vivo: si no crece con el proyecto, deja de enrutar.
6. Si un tema que afecta al proyecto no tiene casa en ningún archivo, se propone crear la sección o el archivo — y se le asigna dueño en el mapa de propiedad.
