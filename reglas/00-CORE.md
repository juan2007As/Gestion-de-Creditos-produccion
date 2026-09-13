# CORE — Las reglas que aplican a todo (Gestión de Créditos)

> **Este es el único archivo que se lee entero, siempre, en cada sesión de trabajo.** El resto de `reglas/` es referencia: se consulta cuando la tabla de [[01-DISPARADORES]] dice que toca.
>
> Perfil de este proyecto: **P3** (maneja dinero real y datos personales de clientes — cédula, teléfono, historial financiero). Ver `CONTEXTO.md`.

## Antes de tocar nada

1. **Entender antes de actuar.** Si la solicitud es ambigua, se pregunta; no se asume.
2. **Mirar el código real**, no responder desde conocimiento genérico. `views_core.py` tiene 6000+ líneas — no asumir dónde vive algo, buscarlo.
3. **Consultar [[01-DISPARADORES]]**: mirar qué toca este cambio y abrir los archivos que correspondan.
4. **Buscar quién más lo usa** antes de modificar, mover, renombrar o borrar algo existente — con búsqueda real, no de memoria.
5. **Clasificar el radio del cambio**:

| Radio | Qué es | Antes | Al cerrar |
|---|---|---|---|
| **Local** | Un archivo, sin dependientes, reversible. | Se ejecuta directo. | Puertas 18-20. En silencio. |
| **Módulo** | Afecta a otros archivos del mismo módulo. | Se explica el plan. | Las 5 puertas. |
| **Cruzado** | Cruza módulos, o toca `views_core.py` desde varias vistas a la vez. | Se explica **y** se confirma. | Las 5 puertas, dichas. |
| **Parada** | Cae en la lista de abajo. | Se pregunta, siempre. | Las 5 puertas + constancia escrita en `DEUDA-TECNICA.md` o `CONTEXTO.md`. |

**Nivel de autonomía acordado con el dueño: Consultivo.** Se analiza, se propone y se espera confirmación antes de ejecutar — en todo, no solo en lo de radio módulo/cruzado. Ver [[ai-rules]] §10.

## Mientras se construye

6. **Toda entrada externa se valida en el servidor.**
7. **Toda acción verifica autorización de rol/permiso** (`@require_rol`/`@require_permission`) — este proyecto **no** aísla por operario (decisión de negocio: con hasta 10 personas, cualquier operario ve/edita/paga cualquier cliente a propósito). No reintroducir un chequeo de "propiedad" sin que el dueño lo pida explícitamente otra vez.
8. **Ningún secreto** en el código, el repositorio, un log, una URL ni el frontend. Ya hubo un caso real: una API key de una integración ajena (Comfama) vivía en `lambda/` — se retiró, pero sigue en el historial de git hasta que se decida reescribirlo.
9. **Ningún error se silencia y ningún error se muestra crudo.** Al usuario, un mensaje entendible; al log, el detalle. Caso real ya encontrado: `pagar_cuota_especifica` deja pasar un `Decimal` inválido sin capturar → 500 crudo (`DEUDA-TECNICA.md` cajón 1).
10. **Un error no se convierte en un valor vacío.**
11. **Nada a medias sin decirlo.** Si se toma un atajo, se registra en `DEUDA-TECNICA.md`.
12. **Dinero: `Decimal` siempre, nunca `float`.** Ya hay un bug real de esto en producción (`Cuota.total_a_pagar()`, ver `DEUDA-TECNICA.md` cajón 1 #1) causado por convertir a `float` antes de operar. No repetir el patrón en código nuevo.

## Las paradas obligatorias

> Se para y se pregunta, siempre, sin importar el nivel de autonomía acordado ni la prisa que haya.

13. **Algo irreversible**: borrar o transformar datos de producción, reescribir historial de git ya publicado, publicar una API que otros consumirán.
14. **Producción**: cualquier operación difícil de deshacer — y nunca sin confirmar que hay backup **reciente y verificado** (`.github/workflows/backup.yml` lo prueba a diario; confirmar que la última corrida pasó antes de tocar producción).
15. **Dinero**: cálculo de interés, mora, cuotas, saldos, cualquier cosa que cambie cuánto le cobra el sistema a un cliente.
16. **Datos personales nuevos**: empezar a recoger una categoría que antes no se recogía.
17. **Cambio de alcance o de producto**: si lo que se pide se desvía de `CONTEXTO.md`, se señala antes de construirlo.
18. **Bucle**: si el mismo problema falla dos veces con el mismo enfoque, se para y se replantea con el dueño.

## Antes de decir "está hecho"

> Las 5 puertas. Si falta una, la tarea está *funcionando*, no *terminada*.

19. **Seguridad**: no se abrió ningún hueco de autorización, validación ni exposición de datos.
20. **No rompe lo existente**: se comprobaron los dependientes y siguen funcionando (`python manage.py test mi_app` — hoy hay 8 failures/25 errors preexistentes conocidos, documentados en `DEUDA-TECNICA.md`; un cambio no debe sumar más de los que ya había).
21. **Verificado, no supuesto**: los tests se corrieron y pasan, o se probó de verdad.
22. **Rastro**: si es una acción sensible, deja registro en `HistorioCambios`/`AuditLog`; si puede fallar en producción, hay forma de enterarse (hoy no la hay del todo — ver `DEUDA-TECNICA.md` cajón 1 #6).
23. **Contexto al día**: si este cambio deja `CONTEXTO.md`, `DEUDA-TECNICA.md` o alguna regla desactualizada, se corrige en el mismo cambio.

## Cómo se habla

24. **Verdad antes que complacencia.**
25. **Explicar el porqué**, no solo el qué. Con varias opciones válidas, recomendación clara, no lista neutra.
26. **Distinguir lo verificado de lo supuesto.**

---

**Si solo se recuerda una cosa:** nada se cambia de forma aislada, nada se da por hecho sin verificarlo, y nada se decide en silencio — y en este proyecto en particular, ningún cálculo de dinero se toca sin usar `Decimal` y sin un test que lo cubra.
