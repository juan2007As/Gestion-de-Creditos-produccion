# Reglas de Backend

> Plantilla base. Al generarse para un proyecto real, especializar según [STACK], [BASE DE DATOS], [PATRÓN DE AUTENTICACIÓN] elegidos en la Fase 2.

## Principios no negociables

1. **Toda entrada externa se valida y sanitiza en el servidor**, sin excepción — nunca confiar en que el front ya validó. El front valida por UX; el back valida por seguridad e integridad de datos.
2. **Ningún endpoint sin control de autorización explícito.** No basta con "está autenticado" — hay que verificar que ese usuario específico puede hacer esa acción específica sobre ese recurso específico (evitar IDOR).
3. **Errores nunca exponen detalles internos** (stack traces, queries SQL, rutas de archivos) al cliente. Se loguean internamente con detalle (ver [[observability-rules]]) y se responden al cliente con mensajes genéricos y códigos de estado correctos.
4. **Idempotencia en operaciones críticas** (pagos, creación de recursos únicos) — una doble llamada por reintento de red no debe duplicar el efecto.
5. **Transacciones donde hay múltiples escrituras relacionadas.** Si una operación toca varias tablas/colecciones y puede fallar a la mitad, debe estar en una transacción o tener compensación explícita.
6. **Nada de lógica de negocio en el controlador/route handler.** Los handlers reciben la petición, delegan a la capa de servicio/dominio, y devuelven la respuesta. Esto facilita testear y evita duplicar reglas de negocio.

## Datos y contratos

7. Todo endpoint tiene un contrato explícito de entrada/salida (tipado, schema, u OpenAPI según el stack) — no "lo que devuelva el ORM tal cual".
8. Los cambios a un contrato de API existente son un evento de **impacto cruzado**: identificar y actualizar todos los consumidores (front, otros servicios, integraciones) antes de mergear (ver [[integrity-rules]]).
9. Migraciones de base de datos son reversibles siempre que sea posible, y nunca se ejecutan directamente en producción sin haberse probado antes.
10. Paginación obligatoria en cualquier endpoint que pueda devolver una lista sin límite natural.

## Rendimiento y escalabilidad razonada

11. No optimizar prematuramente para una escala que el proyecto no tiene ni va a tener pronto — pero sí evitar patrones que sean claramente O(n²) o hagan N+1 queries cuando la solución simple existe.
12. Operaciones lentas o externas (emails, llamadas a terceros, procesamiento pesado) van a segundo plano (colas/jobs), no bloquean la respuesta al usuario.
13. **[P2]** El coste de infraestructura es una restricción de diseño, no una sorpresa a fin de mes. Una consulta cara, un job que corre cada minuto o un log excesivamente verboso son decisiones con precio: se conocen y se vigilan con alertas de gasto ([[operations-rules]]).
14. **[P2]** Toda caché tiene declarado qué guarda, cuánto dura y **qué la invalida**. Una caché sin estrategia de invalidación sirve datos obsoletos indefinidamente y nadie sabe desde cuándo ([[data-rules]] §9 Cuando el dato vive en más de un sitio). Y la clave de caché incluye todo lo que distingue el resultado — incluido el usuario o el tenant, o acabarás sirviendo los datos de uno a otro.

## Trabajo asíncrono: colas, jobs y tareas programadas

> Todo lo que sale del ciclo petición-respuesta pierde el manejo de errores, la trazabilidad y la visibilidad que sí tiene un endpoint. Es donde los fallos se vuelven invisibles.

15. **[P1]** **Todo consumidor de una cola debe ser idempotente.** Las colas entregan "al menos una vez": un mensaje se va a procesar dos veces tarde o temprano, por un reintento o por un reinicio. Ver [[api-rules]] §3 Escritura segura y reintentos.
16. **[P1]** **No se asume orden de entrega** salvo que la cola lo garantice explícitamente (y suele costar rendimiento). El diseño debe tolerar que los eventos lleguen desordenados.
17. **[P1]** Un mensaje que falla repetidamente va a una **cola de fallidos** (dead letter queue) tras un número máximo de intentos, en vez de reintentarse eternamente bloqueando al resto. Y esa cola se **vigila**: llenarse en silencio es perder trabajo sin que nadie se entere.
18. **[P1]** Los reintentos usan backoff exponencial con jitter, nunca en bucle inmediato.
19. **[P1]** El mensaje lleva **identificadores, no objetos completos**. Un objeto serializado en la cola es una copia del estado de hace cinco minutos, y además ata el formato del mensaje a tu modelo de datos: al desplegar una versión nueva conviven mensajes con dos formatos distintos, y el consumidor tiene que entender ambos.
20. **[P1]** El mensaje arrastra el `correlation_id` de la operación que lo originó ([[audit-rules]] §4 Trazabilidad de extremo a extremo).
21. **[P1]** **Nada se encola dentro de una transacción sin resolver el desfase**: si la transacción se revierte, el mensaje ya salió y el consumidor busca un registro que no existe; si se encola después de confirmar, un fallo en medio pierde el mensaje. Se elige conscientemente cómo se resuelve.
22. **[P1]** **Una tarea programada que deja de ejecutarse no genera ningún error.** Se monitoriza su última ejecución exitosa y se alerta por el silencio ([[observability-rules]] §3 Métricas).
23. **[P1]** Las tareas programadas están protegidas contra la **ejecución duplicada** (al escalar a dos instancias, el cron corre dos veces) y contra el **solapamiento consigo mismas** cuando una ejecución tarda más que el intervalo.
24. **[P1]** Las tareas programadas se pueden ejecutar a mano y son **reejecutables sin duplicar efectos**, porque el día que fallan hay que relanzarlas.
25. **[P2]** Un job que procesa un lote grande registra su progreso y puede reanudarse; no empieza de cero tras un fallo al 90%.

## Antes de dar por terminada cualquier tarea de back

- ¿Está validada y sanitizada toda entrada externa?
- ¿Se verificó autorización, no solo autenticación, y sobre este recurso concreto?
- ¿Qué pasa si esta operación falla a la mitad? ¿Queda el sistema en estado inconsistente?
- ¿Este cambio de contrato rompe a algún consumidor existente? ([[api-rules]])
- ¿Los errores se manejan sin filtrar información sensible?
- ¿Qué pasa si dos peticiones idénticas llegan a la vez, o si el cliente reintenta?
- **[P1]** ¿Este trabajo asíncrono es idempotente, y me entero si deja de ejecutarse?
- ¿Esta acción sensible deja rastro en [[audit-rules]]?
