# Protocolo de Adopción (proyecto que ya existe)

> Este archivo se coloca en la raíz de un proyecto **que ya está escrito** — con o sin usuarios, con o sin documentación, con o sin las buenas prácticas de `reglas/`.
> Cuando una IA lea este archivo, debe entrar en **MODO ADOPCIÓN** y seguir este protocolo antes de tocar nada.
>
> Su hermano es [`00-planteamiento-protocol.md`](00-planteamiento-protocol.md), que gobierna los proyectos nuevos. La diferencia es sustancial: allí se **diseña** la realidad; aquí se **descubre**, y casi siempre es peor de lo que nadie dice.

## Regla de oro

**Primero entender lo que hay, después decidir qué se cambia.** La tentación de llegar a un proyecto existente y empezar a "arreglarlo" según las reglas es el error más caro que se puede cometer aquí: rompe cosas que funcionaban por motivos que nadie recuerda, consume el presupuesto de confianza del usuario, y deja el proyecto peor que antes pero con mejor estilo.

Corolario, y es el que más cuesta respetar: **el código que ya existe no se juzga.** Se hizo con la información, el tiempo y la presión que había. Lo único que importa es qué riesgo tiene hoy y qué se hace al respecto.

---

## FASE A0 — Inventario de la realidad

Antes de opinar sobre nada, averiguar qué es esto de verdad. Se investiga en el código y en la infraestructura, no se pregunta todo al usuario: buena parte no lo sabrá, y otra parte creerá saberlo y estará desactualizada.

1. **Qué es y qué hace**: stack real, arquitectura real, módulos y responsabilidades tal como están, no como debieron ser.
2. **Dónde vive**: qué hay desplegado, en qué entornos, quién lo hospeda, qué servicios de terceros consume, qué dominios y certificados.
3. **Quién lo usa**: ¿usuarios reales? ¿cuántos? ¿pagan? ¿hay datos de personas? ¿de qué tipo? Esto determina el perfil, y el perfil determina todo lo demás.
4. **Qué lo sostiene**: ¿hay tests? ¿corren? ¿hay pipeline? ¿hay backups, y alguien los ha restaurado alguna vez? ¿hay logs? ¿hay alertas? ¿alguien se entera si se cae?
5. **Quién sabe de esto**: quién lo mantiene, quién tiene los accesos, y qué se pierde si esa persona desaparece.
6. **Qué está vivo y qué es cadáver**: código muerto, features apagadas, integraciones que ya no se usan, ramas abandonadas. Marcar dudas, no borrar nada todavía.

Criterio de salida: la IA puede describir el proyecto de vuelta al usuario y este confirma "sí, así es" — incluidas las partes que el usuario no sabía.

---

## FASE A1 — Reconstruir el contexto hacia atrás

El equivalente a la Fase 0 del protocolo de planteamiento, pero arqueológico: el planteamiento existió, solo que nunca se escribió.

1. Reconstruir con el usuario: qué problema resuelve el producto, para quién, y qué lo distingue.
2. **Qué NO es este proyecto** (alcance negativo) — sigue siendo tan valioso como el alcance positivo, y en un proyecto existente además explica por qué no se hicieron cosas que parecen obvias.
3. Identificar las **decisiones estructurales que se ven en el código** y preguntar por su motivo: por qué esta base de datos, por qué esta separación, por qué esta integración. Las que nadie recuerda se anotan como *"decisión sin motivo documentado"* — eso es información, no un vacío: significa que se puede reconsiderar sin miedo a romper una razón oculta.
4. Distinguir tres cosas que en un proyecto existente se confunden constantemente: lo que es **decisión deliberada**, lo que es **accidente histórico**, y lo que es **bug que nadie ha notado**. Se tratan distinto.
5. Escribir `CONTEXTO.md` con todo lo anterior, marcando explícitamente lo que es reconstrucción y lo que es confirmación del usuario.

Criterio de salida: existe `CONTEXTO.md` y el usuario lo aprueba como memoria del proyecto.

---

## FASE A2 — Asignar perfil

Se elige el perfil **P0-P3** de [`reglas/README.md`](reglas/README.md) **según la realidad actual, no según la intención original ni el tamaño del código**.

El error típico aquí es asignar perfil bajo porque el proyecto "es pequeño" o "empezó como un experimento". El perfil no lo determina el tamaño: lo determina **qué pasa si falla**. Un script de 300 líneas que mueve las nóminas es P3. Una aplicación de 80.000 líneas sin usuarios reales es P0.

Se escribe en `CONTEXTO.md` con su justificación.

---

## FASE A3 — Auditoría de huecos

Se recorre el conjunto de reglas que activa el perfil y se anota, **sin arreglar nada todavía**, qué se cumple y qué no. La disciplina de no arreglar durante la auditoría es lo que hace que la auditoría termine.

El resultado es `DEUDA-TECNICA.md` poblado desde el primer día — que es su estado natural en un proyecto existente, y no una señal de que algo se hizo mal.

Cada hueco se clasifica en uno de cuatro cajones, **por orden de urgencia**:

### Cajón 1 — Se arregla ya, antes de tocar nada más
Lo que no se puede reconstruir hacia atrás o lo que tiene riesgo activo:

- Secretos en el repositorio o en el historial → **revocar primero** ([[config-rules]] §2).
- Huecos de autorización: recursos accesibles cambiando un ID, endpoints sin comprobación, paneles de administración expuestos.
- **Ausencia de backup, o backup que nunca se ha restaurado.** Sin esto, cualquier otro trabajo se hace sin red.
- Envío de correos, cobros o notificaciones reales desde entornos que no son producción.
- Dependencias con vulnerabilidad conocida y explotable, o fuera de soporte.
- Ausencia total de registro de errores: si nadie se entera de que algo falla, todo lo demás es a ciegas.
- **[P2]** Ausencia de rastro de auditoría en acciones sensibles. El rastro que no se escribió ayer no existe nunca; cuanto más tarde se empiece, más historia se pierde para siempre.

### Cajón 2 — Se arregla pronto, con plan y fecha
Riesgo real pero no inmediato: falta de tests en lo crítico, migraciones no versionadas, configuración sin validar, ausencia de pipeline, accesos que dependen de una sola persona, retención de datos personales sin definir.

### Cajón 3 — Se arregla al tocarlo (regla del explorador, acotada)
Lo que no justifica una campaña propia pero no debe empeorar: estilo, estructura, nombres, cobertura de tests de zonas secundarias, textos hardcodeados.

**Acotada quiere decir acotada**: al tocar un archivo se deja mejor que como se encontró, pero el arreglo se limita a lo que rodea al cambio. Un fix de tres líneas no arrastra un refactor de trescientas — eso convierte cada tarea en impredecible y hace imposible revisar el diff.

### Cajón 4 — Se acepta conscientemente y se escribe
Cosas que están mal según las reglas y que **no se van a arreglar**, con el motivo: coste desproporcionado, se va a reescribir esa parte, el riesgo real es bajo, o simplemente no compensa.

Este cajón es tan importante como el primero. Una deuda aceptada y escrita es una decisión; una deuda ignorada es una trampa. Y sin este cajón, la auditoría produce una lista de 200 puntos que nadie mira nunca.

---

## FASE A4 — Puesta al día de la mecánica

Se recorre [`reglas/02-AUTOMATIZABLE.md`](reglas/02-AUTOMATIZABLE.md) y se decide línea por línea: ya está / se implementa ahora / se acepta como deuda con motivo.

En un proyecto existente el orden que más rinde por esfuerzo invertido suele ser este, y conviene respetarlo:

1. **Escaneo de secretos** — barato, y encuentra cosas el primer día.
2. **Backup con restauración probada** — porque todo lo que viene después se apoya en poder deshacer.
3. **Registro de errores y una alerta mínima** — dejar de trabajar a ciegas.
4. **Pipeline con los tests que ya existan**, aunque sean pocos. Un pipeline con tres tests que corre siempre vale más que cincuenta tests que nadie ejecuta.
5. **Tests de autorización** sobre los recursos principales. Casi siempre aparece algo.
6. **Validación de configuración al arrancar** — convierte fallos futuros lejanos en un fallo inmediato y obvio.

---

## FASE A5 — Generar las reglas del proyecto

Se sigue el mismo escalonado que la Fase 3 del protocolo de planteamiento: **núcleo ahora, dominios según lo que el proyecto ya tiene, resto en diferido.** Con la ventaja de que aquí no hay que adivinar qué dominios toca el proyecto — la Fase A0 ya lo inventarió.

Se genera siempre: `CONTEXTO.md`, el **enganche de carga** (`CLAUDE.md` o equivalente, copiado de `plantilla-CLAUDE.md`), `DEUDA-TECNICA.md` ya poblado por la Fase A3, `reglas/README.md`, `reglas/00-CORE.md`, `reglas/01-DISPARADORES.md` con todas las filas, y `ai-rules`, `integrity-rules`, `evolution-rules`, `git-rules`, `security-rules` y `data-rules`.

Los demás, según lo que el inventario haya encontrado. Los que el proyecto todavía no tiene quedan como fila pendiente en los disparadores.

Y tres diferencias respecto a un proyecto nuevo, que son la esencia de esta fase:

1. **Se especializan con lo que el proyecto ya hace**, no con lo que debería hacer. Si la autenticación usa tokens en `localStorage`, `identity-rules` describe eso y anota la contramedida que le corresponde — no describe la solución ideal que nadie ha implementado. Un archivo de reglas que describe un proyecto imaginario es exactamente el problema que estas reglas intentan evitar.
2. **Cada regla que hoy no se cumple queda marcada** como `PENDIENTE` con referencia a su entrada en `DEUDA-TECNICA.md`. Así la regla existe, es visible, y no se confunde con algo ya resuelto.
3. **La tabla de disparadores se llena con las tareas reales de este proyecto**, con sus nombres: sus integraciones, sus módulos delicados, esa parte que todo el mundo sabe que hay que tocar con cuidado. Ahí es donde el conocimiento que hoy vive en la cabeza de alguien pasa a estar escrito — y es probablemente lo más valioso que produce todo este protocolo.

Criterio de salida: el usuario revisa y aprueba `CONTEXTO.md`, `reglas/`, `DEUDA-TECNICA.md` y el plan de los cajones 1 y 2.

---

## FASE A6 — Desarrollo continuo

A partir de aquí el proyecto entra en el mismo régimen que uno nuevo: [`reglas/00-CORE.md`](reglas/00-CORE.md) siempre, [`reglas/01-DISPARADORES.md`](reglas/01-DISPARADORES.md) antes de cada tarea, y la Fase 4 del protocolo de planteamiento.

Con dos reglas propias de un proyecto adoptado:

1. **Las reglas se aplican íntegramente al código nuevo desde el primer día.** No hay periodo de gracia para lo que se escribe a partir de ahora: si no, la deuda sigue creciendo mientras se paga la antigua, y nunca se converge.
2. **Al código antiguo se le aplican cuando se toca**, según el cajón 3. Nadie tiene que arreglar el pasado entero antes de poder trabajar.

---

## Reglas de comportamiento durante TODO el protocolo

- **No juzgar el código existente**, ni en el tono ni en los comentarios. Se describe el riesgo, no la calidad de quien lo escribió — que muy posiblemente sea el propio usuario.
- **No arreglar durante la auditoría.** Anotar y seguir. Si se arregla sobre la marcha, la auditoría no termina nunca y el diff se vuelve irrevisable.
- **Ser concreto con el riesgo, no alarmista.** "Cualquiera con una cuenta puede leer los pedidos de los demás cambiando el ID en la URL" es útil. "Hay problemas graves de seguridad" no lo es, y además invita a ignorarlo.
- **No prometer una reescritura.** La respuesta a un proyecto con deuda casi nunca es reescribirlo; es priorizarla. Si de verdad hace falta reescribir algo, eso es una decisión de producto con su propio planteamiento, no una conclusión de una auditoría técnica.
- Todo lo que salga de este protocolo queda **escrito en archivos**, no dicho en conversación.
