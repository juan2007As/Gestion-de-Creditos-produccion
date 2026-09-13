# Reglas de APIs, Contratos e Integraciones

> Perfil mínimo del archivo: **P1** para las secciones 1-3; **P2** en adelante para versionado formal y deprecación.
>
> [[back-rules]] gobierna cómo se construye un endpoint por dentro. Este archivo gobierna el **contrato**: lo que otros dan por hecho y que se rompe sin que te enteres. Un contrato roto no falla en tu código, falla en el de otro.

## 1. Forma del contrato

1. Todo endpoint tiene un contrato **explícito y declarado** de entrada y salida (tipos, schema, OpenAPI según el stack). Nunca "lo que devuelva el ORM tal cual": eso convierte cualquier cambio de columna en un cambio de API silencioso.
2. La documentación del contrato se **genera desde el código o se verifica contra él** de forma automática. Una documentación escrita a mano diverge en dos semanas y a partir de ahí miente, que es peor que no tenerla.
3. **Un único formato de error en todo el proyecto**, con:
   - un **código de error estable y enumerado** que el cliente pueda programar (`SALDO_INSUFICIENTE`), no un mensaje que cambie al corregir una tilde;
   - un mensaje legible para humanos;
   - el identificador de correlación (ver [[audit-rules]] §4 Trazabilidad de extremo a extremo);
   - los errores de validación por campo, cuando aplique.
4. Los códigos de estado HTTP se usan por su significado real: 400 no es lo mismo que 422, 401 (no sé quién eres) no es lo mismo que 403 (sé quién eres y no puedes). Devolver 200 con un cuerpo que dice "error" rompe a todo cliente que confíe en el estándar.
5. **Paginación obligatoria** en cualquier colección que pueda crecer sin límite natural, con un tope máximo por página aplicado en el servidor aunque el cliente pida más. Filtrado y ordenación siguen la misma convención en todos los endpoints.
6. Límite explícito de tamaño de petición y de profundidad/complejidad de consulta (especialmente en GraphQL o filtros anidados) — si no, un solo cliente puede tumbar el servicio sin proponérselo.
7. Las respuestas no exponen campos internos "porque estaban en el objeto": lo que sale se declara explícitamente. La fuga de datos por serialización automática es de las más frecuentes.

## 2. Cambios y compatibilidad

8. Está definido explícitamente qué es un cambio **rompedor** y qué no:
   - **No rompe**: añadir un endpoint, añadir un campo opcional en la entrada, añadir un campo en la salida.
   - **Rompe**: quitar o renombrar un campo, cambiar su tipo o formato, volver obligatorio un campo opcional, cambiar el significado de un valor, cambiar un código de estado o de error, endurecer una validación, cambiar el orden por defecto de una lista.
9. Un cambio rompedor en una API con consumidores es un evento de **impacto cruzado**: se identifican todos los consumidores y se actualizan antes de mergear (ver [[integrity-rules]]).
10. **Los clientes toleran campos nuevos que no conocen.** Si el frontend o una integración rompe porque llegó un campo extra, eso es un bug del cliente y se arregla — de lo contrario, la API queda congelada para siempre.
11. **[P2]** Versionado de API declarado desde el principio, aunque solo exista la v1. Añadir versionado después de tener consumidores es un rediseño.
12. **[P2]** Política de deprecación escrita: cuánto tiempo se mantiene lo antiguo, cómo se avisa (cabecera de deprecación, changelog, comunicación directa), y qué pasa al vencer el plazo. Sin plazo escrito, nada se retira nunca y se acumulan tres versiones vivas.
13. **[P3]** Una API pública consumida por terceros es una decisión **difícil de revertir** en el sentido de [[evolution-rules]] §6: se confirma explícitamente antes de publicarla.
14. **[P1]** Cuando el consumidor es un cliente que **no puedes actualizar** (móvil, escritorio, SDK integrado por otros), la compatibilidad deja de medirse contra "la versión actual del front" y pasa a medirse contra la **versión mínima soportada**, que está declarada. Sin ese número escrito, la respuesta a "¿esto rompe a alguien?" es indecidible y por defecto la compatibilidad se vuelve eterna. Ver [[release-rules]] §7.

## 3. Escritura segura y reintentos

15. **Idempotencia en toda operación de escritura crítica.** Una doble llamada por un reintento de red, un doble clic o un timeout no debe duplicar un cobro, un pedido ni un envío. Se resuelve con clave de idempotencia proporcionada por el cliente, o con una restricción de unicidad natural en base de datos.
16. Un timeout **no significa que la operación falló** — significa que no sabes si funcionó. El diseño debe permitir preguntar por el estado real o reintentar sin daño.
17. Las operaciones no idempotentes por naturaleza (enviar email, cobrar) se marcan explícitamente como tales y se protegen con registro previo del intento.

## 4. Llamadas salientes a terceros

18. **Toda llamada saliente lleva timeout explícito.** El valor por defecto de casi todas las librerías es "infinito" o "muy largo", y un tercero lento se convierte en tu caída: se agotan las conexiones y se cae todo, no solo lo que dependía de ese tercero.
19. Reintentos **solo en errores transitorios** (red, 5xx, 429), nunca en errores de cliente (4xx), con **backoff exponencial y jitter**. Reintentar en bucle cerrado convierte un fallo del proveedor en un ataque tuyo contra el proveedor.
20. **[P2]** Circuit breaker o degradación explícita para dependencias externas: qué hace el sistema cuando el proveedor lleva cinco minutos caído. "Se queda colgado" no es una respuesta aceptable.
21. Para cada integración externa está escrito **qué pasa si falla**: se degrada la funcionalidad, se encola para más tarde, o se rechaza la operación. Se decide antes, no durante el incidente.
22. Nunca se confía en que un tercero cumple su contrato: la respuesta de un proveedor se **valida** igual que la entrada de un usuario antes de usarla o guardarla.
23. Las credenciales de terceros se guardan y rotan según [[config-rules]], con el **mínimo scope** necesario.
24. **[P2]** Se registra latencia y tasa de error **por proveedor** (ver [[observability-rules]]) — para poder demostrar que la lentitud es suya y no tuya.
25. Ninguna llamada saliente se hace a una URL controlada por el usuario sin validación estricta de destino (SSRF, ver [[security-rules]]).

## 5. Webhooks

26. **Recibir**: se verifica la firma criptográfica del emisor antes de procesar nada. Un endpoint de webhook sin verificación de firma es un endpoint público de escritura para cualquiera que conozca la URL.
27. **Recibir**: el procesamiento es **idempotente** — los proveedores reenvían. Se guarda el identificador del evento y se descarta el duplicado.
28. **Recibir**: **no se asume orden de llegada.** El evento "pago confirmado" puede llegar antes que "pago creado". Se usa la marca de tiempo o el número de secuencia del evento y se descartan los eventos más antiguos que el estado actual.
29. **Recibir**: se responde rápido (aceptar y encolar) y se procesa aparte. Un webhook que tarda es un webhook que el proveedor reintenta, multiplicando el trabajo.
30. **Emitir**: se firman, se reintentan con backoff, se registra el resultado de cada entrega, y hay una forma de reenviar manualmente. El endpoint de destino es de un tercero: se valida que no apunte a la red interna.

## 6. Reconciliación (el fallo caro que casi nadie escribe)

31. **[P2]** Cuando un estado vive a la vez en tu sistema y en el de un tercero (pagos, suscripciones, inventario, envíos), existe un **proceso periódico de reconciliación** que compara ambos y reporta las discrepancias.
32. **[P2]** El motivo: el webhook que nunca llegó, el que llegó y falló al procesar, el timeout durante el cobro. El dinero se movió en el proveedor y tu base de datos no lo sabe. Sin reconciliación, eso no aparece en ningún log de error — simplemente no pasó nada, y lo descubre el cliente meses después.
33. **[P2]** Las discrepancias encontradas **alertan a una persona**, no se corrigen automáticamente sin criterio. Un ajuste automático mal diseñado sobre datos financieros hace más daño que la discrepancia.
34. **[P2]** Está definido **quién es la fuente de verdad de cada entidad** cuando la sincronización es bidireccional (tu sistema o el CRM/ERP/proveedor), y qué gana en un conflicto. Se decide en el planteamiento y se escribe en `CONTEXTO.md`, no en mitad del incidente.

## Antes de dar por cerrada cualquier tarea de API o integración

- ¿Este cambio rompe a algún consumidor existente según la definición del punto 8? ¿Los revisé todos de verdad?
- ¿Esta escritura es segura si el cliente la reintenta dos veces?
- ¿Esta llamada saliente tiene timeout, y está decidido qué pasa si el tercero está caído?
- ¿La documentación del contrato refleja este cambio, o acaba de quedarse mintiendo?
- ¿La respuesta expone algún campo interno que no debería salir?
- **[P2]** ¿Este estado compartido con un tercero tiene forma de detectar que se desincronizó?
