# Reglas de Evolución y Actualización

> El planteamiento inicial (Fase 0-3) construye los cimientos. Este archivo gobierna cómo el proyecto crece sobre esos cimientos sin perder coherencia, sin acumular deuda invisible, y sin desviarse del producto que se aprobó — para que cada actualización futura sea tan sencilla como la primera pieza.

## 1. El planteamiento original es el ancla, no un documento muerto

1. Toda feature nueva se contrasta contra `CONTEXTO.md` antes de construirse: ¿esto encaja con el problema y usuario que definimos en la Fase 0, o es una desviación? Si es una desviación, no se rechaza automáticamente, pero se señala explícitamente como tal y se decide junto al usuario si el planteamiento original se actualiza o si la feature se descarta/pospone.
2. Ninguna feature se da por "planteada" solo porque el usuario la pidió en una frase — pasa por una mini versión del protocolo de la Fase 0 (entender, reformular, confirmar) antes de diseñarse, proporcional a su tamaño: una feature grande merece su propio mini-mock y mini-definición de datos; una pequeña puede resolverse en la conversación misma.

## 2. Revisión periódica de contexto (evita el drift silencioso)

3. Cada cierto número de features/cambios significativos (orientativo: cada 5-10, o cuando se sienta que el proyecto "ya no se parece tanto" al planteamiento original), se hace una revisión completa de `CONTEXTO.md` y de los archivos de `reglas/` para detectar si algo quedó desactualizado — no solo parchear el documento tras cada cambio puntual (regla existente en [[ai-rules]] §5 Contexto siempre vivo), sino auditar el conjunto de vez en cuando.
4. Si en esa revisión se detecta que una regla ya no aplica, se contradice con otra, o el stack/arquitectura documentado ya no es el real, se corrige ahí mismo — un archivo de reglas que miente sobre el proyecto es peor que no tener archivo.

**El conjunto de reglas también se mide.** Exigir métricas al producto y no tener ninguna sobre uno mismo es la contradicción más fácil de cometer. En cada revisión se responden tres preguntas, y las respuestas se escriben:

- **¿Se está usando?** ¿Se consultó [[01-DISPARADORES]] antes de las tareas, o se trabajó de memoria? Si nadie lo abre, el problema no es la disciplina: la tabla no está enrutando y hay que arreglarla o simplificarla.
- **¿Qué se saltó y por qué?** Una regla que se salta repetidamente está mal escrita, es desproporcionada para este proyecto, o debería estar automatizada. Se corrige la regla, no se insiste en la disciplina.
- **¿Qué falló que ninguna regla previó?** Esta es la que alimenta la sección 8. Es la única de las tres que hace crecer el conjunto en la dirección correcta.

## 3. Registro de deuda técnica (nada de atajos invisibles)

5. Todo atajo tomado conscientemente ("por ahora así, se arregla después", un TODO, un hack temporal) se registra en un archivo `DEUDA-TECNICA.md` en la raíz — con qué se hizo, por qué, y qué implicaría arreglarlo bien. No queda solo como comentario suelto en el código que nadie vuelve a mirar.
6. Antes de tomar un atajo nuevo, se avisa al usuario explícitamente de que se está tomando y por qué (tiempo, complejidad, incertidumbre) — no se decide en silencio.
7. La deuda técnica registrada se revisa en la misma cadencia que la revisión de contexto (punto 3) — preguntar si alguna ya vale la pena pagar.

## 4. Definición de "hecho" (Definition of Done) por feature

Una checklist larga bajo presión se ejecuta como ritual o se salta entera. Por eso la Definition of Done tiene dos niveles con **fuerza distinta**: cinco puertas que bloquean, y unos recordatorios que se revisan y se pueden diferir dejando constancia.

### Las 5 puertas (bloquean el cierre, sin excepción)

Estas son las mismas de [[00-CORE]]. Si falta una, la feature está **funcionando** pero no **terminada**, y esa diferencia se comunica al usuario en vez de reportarla como cerrada. No se negocian con el plazo: lo que se negocia es el plazo.

8. **Seguridad**: no se abrió ningún hueco de autorización, de validación ni de exposición de datos ([[security-rules]], [[identity-rules]]).
9. **No rompe lo existente**: se buscaron los dependientes de verdad y siguen funcionando ([[integrity-rules]]).
10. **Verificado, no supuesto**: los tests se corrieron y pasan, o se probó de verdad. Y existe al menos un test que falla si esto se rompe en el futuro, incluida la comprobación de autorización si toca datos de un usuario ([[testing-rules]]).
11. **Rastro**: si puede fallar en producción, hay forma de enterarse ([[observability-rules]]); **[P2]** si contiene acciones sensibles, dejan registro en el mismo cambio ([[audit-rules]]) — nunca en una tarea posterior, porque esa tarea no llega.
12. **Nada oculto**: todo atajo tomado está dicho y registrado en `DEUDA-TECNICA.md`.

### Recordatorios (se revisan; se pueden diferir dejando constancia)

Se recorren al cerrar, y lo que quede pendiente se registra como deuda con su motivo. No bloquean, pero tampoco desaparecen.

13. Cumple las reglas aplicables de [[front-rules]] y/o [[back-rules]] (estados completos, responsive, paginación, transacciones, idempotencia).
14. `CONTEXTO.md` refleja lo que este cambio añade o modifica del planteamiento.
15. **[P2]** Si añade datos personales: están inventariados, con retención definida y cubiertos por el borrado ([[compliance-rules]]).
16. **[P2]** Si añade configuración: validada al arrancar y presente en `.env.example` ([[config-rules]]).
17. **[P2]** Si añade una dependencia: evaluada y con el lockfile al día ([[dependencies-rules]]).
18. La documentación que este cambio deja mintiendo (contrato de API, README, diagrama) está corregida.

> **Dos filtros, no uno.** Por **perfil del proyecto** (ver [[README]]): en P0/P1 los puntos marcados `[P2]` no aplican. Y por **radio del cambio** ([[00-CORE]] §5): un cambio local cumple las tres primeras puertas y se cierra sin ceremonia; uno cruzado o irreversible las cumple todas y además lo dice. Cumplir es obligatorio en los dos casos; anunciarlo, no.

## 4bis. Revisión del perfil del proyecto

19. El perfil (P0-P3) elegido en la Fase 2 **se revisa** en cada auditoría periódica del punto 3. Un proyecto sube de perfil cuando cambia la realidad, no cuando alguien lo decide: aparecen usuarios reales que no conoces, entra dinero, entran datos personales de terceros, o el sistema pasa a ser algo cuya caída tiene consecuencias.
20. Subir de perfil **no se hace en silencio**: se comunica al usuario qué reglas se activan a partir de ahora y qué hay pendiente de poner al día. Ese desfase se registra en `DEUDA-TECNICA.md` como cualquier otro atajo, porque eso es exactamente lo que es.
21. Es más barato empezar en el perfil alto que subir después. Auditoría, aislamiento entre tenants, inventario de datos personales y trazabilidad son **muy caros de retrofitear**: el sistema no puede borrar lo que no sabe que tiene.

## 5. Prioridad bajo presión de tiempo

Cuando un plazo real fuerza a no poder cumplir todo al 100% (no puede haber test completo, no da tiempo a explicar cada detalle, etc.), el orden de lo que NUNCA se sacrifica es:

1. **Seguridad** ([[security-rules]], [[identity-rules]]) — nunca se recorta. Un hueco de autorización no se arregla después: se explota antes.
2. **Integridad y no perder datos** ([[integrity-rules]], [[data-rules]]) — nunca se recorta. Incluye tener backup verificado antes de cualquier operación irreversible.
3. **[P2] Trazabilidad y obligaciones legales** ([[audit-rules]], [[compliance-rules]]) — nunca se recorta, por un motivo distinto a los anteriores: **no se puede reconstruir hacia atrás**. Un rastro que no se escribió en su momento no existe nunca más, y un plazo legal incumplido no se recupera trabajando el fin de semana. Todo lo demás en esta lista se puede pagar tarde; esto no.
4. **Funcionalidad correcta del camino principal** (que la feature haga lo que promete en su caso de uso central).
5. **[P2] Poder detectar que ha fallado** ([[observability-rules]]) — se puede reducir a lo mínimo, pero no a cero: entregar algo que puede romperse sin que nadie se entere es entregar un problema futuro sin fecha.
6. **Cobertura de test** — se puede reducir a lo crítico (autorización y lógica de negocio principal), documentando qué quedó sin cubrir en `DEUDA-TECNICA.md`.
7. **Pulido de UI/UX en casos extremos, refactor cosmético, documentación exhaustiva** — lo primero en ceder, siempre y cuando se registre como pendiente.

Esta jerarquía se comunica al usuario cuando se activa ("por el tiempo, voy a priorizar X y Y, dejando Z pendiente en deuda técnica") — nunca se aplica en silencio.

**Lo que nunca es un atajo aceptable, por mucha prisa que haya:** desactivar la verificación de certificados, saltarse la comprobación de autorización, commitear un secreto "temporalmente", ejecutar un cambio irreversible en producción sin backup verificado, o desplegar algo que envíe correos reales desde un entorno de pruebas. Estas no se negocian con el plazo: se negocia el plazo.

## 6. Cambios reversibles vs irreversibles (transversal a todo el proyecto)

22. Antes de cualquier decisión, clasificarla: ¿es fácilmente reversible (se puede deshacer sin costo real) o difícil/imposible de revertir?
23. Las decisiones difíciles de revertir siempre se confirman explícitamente con el usuario antes de ejecutar, con el motivo de por qué son de ese tipo — nunca se asume autorización implícita para estas aunque el resto del flujo esté en modo autónomo.
24. Cuentan como difíciles de revertir, como mínimo: borrar o transformar datos de producción; cambiar de proveedor de pagos, de identidad o de base de datos; publicar una API que terceros van a consumir ([[api-rules]] §2 Cambios y compatibilidad); enviar comunicaciones masivas a usuarios reales; empezar a recoger una categoría nueva de datos personales ([[compliance-rules]] §6 Terceros y transferencias); y elegir dónde se alojan los datos geográficamente.

## 7. Mantenimiento recurrente (lo que nunca es urgente hasta que es un incidente)

25. **[P2]** La lista de tareas recurrentes y su cadencia vive en [[operations-rules]] §8. Lo que aporta este archivo es el motivo por el que se incumple: **nadie las pide, no aportan valor visible, y compiten con features que sí lo aportan.** Por eso no basta con listarlas — hay que planificarlas como cualquier feature, con su hueco real.
26. **[P2]** "Cuando haya tiempo" significa nunca. La factura del mantenimiento diferido no desaparece: se acumula y se paga entera, de golpe, el día del incidente — y ese día cuesta varias veces lo que habría costado repartida.

## 8. Aprender de los fallos (cómo estas reglas mejoran con el uso)

> Un conjunto de reglas escrito razonando qué es correcto sale liso y ligeramente genérico. Las reglas que de verdad se cumplen son las que tienen filo, y el filo lo da un caso real: *"nunca X — pasó en marzo y costó dos días"* se recuerda; *"conviene evitar X"* se lee y se olvida.
>
> Esta sección es el mecanismo por el que el conjunto deja de envejecer y empieza a mejorar. **Sin esto, las reglas solo pueden crecer desde fuera (lo que el usuario pida) y nunca desde dentro (lo que el proyecto enseñe).**

27. **Todo fallo con causa raíz no trivial cierra con una pregunta**, además del arreglo y del test de regresión: *¿había una regla que habría evitado esto?* Aplica a bugs que llegaron a producción, incidentes, y a cualquier "esto se rompió y no lo vio venir nadie". Solo hay tres respuestas posibles y cada una lleva a una acción distinta:

| Respuesta | Qué significa | Qué se hace |
|---|---|---|
| **Sí, y no se siguió** | Problema de aplicación, no de contenido. Escribir la regla otra vez no arregla nada. | Ver si es mecanizable ([[02-AUTOMATIZABLE]]). Si lo es, se automatiza. Si no, se añade fila en [[01-DISPARADORES]] para que aparezca en el momento en que hacía falta. |
| **Sí, pero era ambigua o genérica** | La regla existía y no mordía. | Se **afila con este caso concreto**, en su archivo dueño. |
| **No había** | Hueco real. | Se escribe, en el archivo dueño, con el caso que la motivó. |

28. **La regla nueva lleva su caso pegado, en una línea.** No un documento de incidente: una frase entre paréntesis o un inciso. Es lo que la separa de una recomendación abstracta, y lo que hace que alguien dentro de dos años entienda por qué existe antes de borrarla por parecer excesiva.
29. La regla nueva va a su **archivo dueño** (ver el mapa de propiedad de [[README]]), y si corresponde se le añade fila en [[01-DISPARADORES]] y línea en [[02-AUTOMATIZABLE]]. Una regla que solo existe en su archivo y no aparece en el momento de trabajar es una regla que nadie va a leer.
30. **No todo fallo merece una regla, y decidir que no también se escribe.** Si el caso es irrepetible, si el coste de cumplir la regla supera al del fallo, o si ya está cubierto por una regla existente que sí se siguió, se anota la decisión de **no** escribirla y por qué. Sin esta válvula, el conjunto crece por acumulación hasta volverse inaplicable — que es exactamente el fallo que las tres capas de navegación intentan evitar.
31. Cuando el fallo fue un incidente, esta pregunta **es** una de las acciones del postmortem ([[operations-rules]] §4), y cumple su exigencia de que las acciones cambien el sistema en vez de pedir más cuidado.
32. La misma pregunta aplica en positivo: si algo salió especialmente bien porque alguien hizo algo que no está escrito en ningún sitio, eso también es una regla que falta.

## Checklist de cierre de cualquier ciclo de trabajo (sprint, sesión larga, o hito)

- ¿El planteamiento en `CONTEXTO.md` sigue reflejando la realidad del proyecto?
- ¿Hay deuda técnica acumulada que ya vale la pena revisar?
- ¿Todas las features cerradas en este ciclo cumplen la Definition of Done de este archivo?
- ¿Alguna decisión irreversible se tomó sin confirmación explícita? (no debería haber pasado)
- ¿El perfil del proyecto sigue siendo el correcto, o la realidad ya lo ha subido?
- **[P2]** ¿Hay mantenimiento recurrente vencido (dependencias, backups sin probar, accesos sin revisar)?
- ¿Falló algo este ciclo que ninguna regla previó? ¿Se escribió la regla, o se decidió explícitamente no escribirla? (sección 8)
- ¿Alguna regla se saltó repetidamente? Eso es un defecto de la regla, no del equipo.
