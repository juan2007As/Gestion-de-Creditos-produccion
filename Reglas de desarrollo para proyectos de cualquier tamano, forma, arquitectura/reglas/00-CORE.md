# CORE — Las reglas que aplican a todo

> **Este es el único archivo que se lee entero, siempre, en cada sesión de trabajo.** El resto de `reglas/` es referencia: se consulta cuando la tabla de [[01-DISPARADORES]] dice que toca.
>
> Aquí no hay nada nuevo. Es la destilación de lo que aplica a cualquier cambio, en cualquier proyecto, de cualquier perfil. Si una regla de aquí choca con otra de un archivo de referencia, gana la de aquí.

## Antes de tocar nada

1. **Entender antes de actuar.** Si la solicitud es ambigua, se pregunta; no se asume. Reformular lo que se ha entendido es más rápido que construir lo que no era.
2. **Mirar el código real**, no responder desde conocimiento genérico. Si hay acceso al proyecto y no se ha mirado, la respuesta no vale.
3. **Consultar [[01-DISPARADORES]]**: mirar qué toca este cambio y abrir los archivos que correspondan. Son treinta segundos y es lo que evita la mitad de los fallos.
4. **Buscar quién más lo usa** antes de modificar, mover, renombrar o borrar algo existente — con búsqueda real, no de memoria. Y recordar que la búsqueda no encuentra los usos que llegan desde fuera del repositorio ([[integrity-rules]]).
5. **Clasificar el radio del cambio**, porque de esto depende todo lo demás:

| Radio | Qué es | Antes | Al cerrar |
|---|---|---|---|
| **Local** | Un archivo, sin dependientes, reversible. | Se ejecuta directo. | Puertas 18, 19 y 20. En silencio. |
| **Módulo** | Afecta a otros archivos del mismo módulo. | Se explica el plan. | Las 5 puertas. |
| **Cruzado** | Cruza módulos, front↔back, o toca una integración. | Se explica **y** se confirma. | Las 5 puertas, dichas. |
| **Parada** | Cae en la lista de abajo. | Se pregunta, siempre. | Las 5 puertas + constancia escrita. |

**El rigor es el mismo en los cuatro; lo que cambia es la ceremonia.** Un cambio local cumple las puertas igual, solo que sin anunciarlo. Aplicar el ritual completo a un cambio de una línea es la vía más rápida a que el usuario pida saltarse el proceso — y entonces se pierde también donde importaba. Ante la duda entre dos radios, se aplica el mayor.

## Mientras se construye

6. **Toda entrada externa se valida en el servidor.** El cliente valida por comodidad del usuario; el servidor valida porque el cliente miente.
7. **Toda acción verifica autorización sobre el recurso concreto**, no solo que haya sesión. "¿Puede *este* usuario hacer *esto* sobre *este* recurso?"
8. **Ningún secreto** en el código, en el repositorio, en un log, en una URL ni en el frontend.
9. **Ningún error se silencia y ningún error se muestra crudo.** Al usuario, un mensaje entendible; al log, el detalle.
10. **Un error no se convierte en un valor vacío.** Devolver una lista vacía o un nulo cuando la operación falló cambia un fallo ruidoso por corrupción silenciosa.
11. **Nada a medias sin decirlo.** Si se toma un atajo, se dice que es un atajo, y se registra en `DEUDA-TECNICA.md`.

## Las paradas obligatorias

> Se para y se pregunta, siempre, sin importar el nivel de autonomía acordado ni la prisa que haya. Ver [[ai-rules]] §10.

12. **Algo irreversible**: borrar o transformar datos de producción, cambiar de proveedor, publicar una API que otros consumirán, enviar comunicaciones masivas.
13. **Producción**: cualquier operación que la toque de forma difícil de deshacer — y nunca sin confirmar que hay backup **reciente y verificado**.
14. **Dinero**: cobros, reembolsos, precios, saldos, facturación.
15. **Datos personales nuevos**: empezar a recoger una categoría que antes no se recogía.
16. **Cambio de alcance o de producto**: si lo que se pide se desvía del planteamiento acordado, se señala antes de construirlo.
17. **Bucle**: si el mismo problema falla dos veces con el mismo enfoque, se para y se replantea con el usuario. No hay tercer intento a ciegas.

## Antes de decir "está hecho"

> Las 5 puertas. Si falta una, la tarea está *funcionando*, no *terminada*, y esa diferencia se comunica. Detalle y recordatorios adicionales en [[evolution-rules]] §4.

18. **Seguridad**: no se abrió ningún hueco de autorización, validación ni exposición de datos.
19. **No rompe lo existente**: se comprobaron los dependientes y siguen funcionando.
20. **Verificado, no supuesto**: los tests se corrieron y pasan, o se probó de verdad. "Debería funcionar" no es una verificación.
21. **Rastro**: si es una acción sensible, deja registro; si puede fallar en producción, hay forma de enterarse.
22. **Contexto al día**: si este cambio deja `CONTEXTO.md` o alguna regla desactualizada, se corrige en el mismo cambio.

## Cómo se habla

23. **Verdad antes que complacencia.** Si la idea del usuario tiene un problema, se dice directamente y con la alternativa en la mano. Nunca se valida algo por cortesía: el valor de estar de acuerdo depende de que el desacuerdo sea posible.
24. **Explicar el porqué**, no solo el qué. Y cuando hay varias opciones válidas, presentarlas con su coste real y una recomendación clara — no una lista neutra.
25. **Distinguir lo verificado de lo supuesto.** "Lo he comprobado" y "creo que sí" no se dicen igual.

---

**Si solo se recuerda una cosa de todo el conjunto de reglas:** nada se cambia de forma aislada, nada se da por hecho sin verificarlo, y nada se decide en silencio.
