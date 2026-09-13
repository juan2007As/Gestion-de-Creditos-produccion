# Reglas de Observabilidad y Manejo de Errores

> Sin esto, los bugs se descubren cuando el usuario se queja, no antes.
>
> Perfil mínimo: **P0** para la sección 1. Las reglas marcadas `[P1]`/`[P2]`/`[P3]` aplican desde ese perfil (ver [[README]]).
>
> Este archivo cubre **enterarse de que algo va mal**. Qué hacer cuando ya va mal está en [[operations-rules]]. El rastro de quién hizo qué, que es otra cosa, está en [[audit-rules]].

## 1. Manejo de errores

1. Todo error inesperado se loguea con contexto suficiente para diagnosticarlo sin tener que reproducirlo a ciegas (qué operación, qué usuario/recurso, qué input relevante — sin datos sensibles, ver [[security-rules]]).
2. Distinguir siempre entre error esperado (validación fallida, recurso no encontrado — se maneja con respuesta clara al usuario) y error inesperado (bug, fallo de infraestructura — se loguea con severidad alta y se investiga).
3. El usuario final nunca ve un stack trace ni un mensaje técnico crudo — ve un mensaje entendible; el detalle técnico va al log. Junto al mensaje se le da el **identificador de correlación** para que pueda reportarlo y sea localizable en un segundo ([[audit-rules]] §4 Trazabilidad de extremo a extremo).
4. Ninguna excepción se atrapa y se silencia sin registrar nada ("catch vacío") — si se decide ignorar un error, se documenta explícitamente por qué es seguro ignorarlo.
5. **Un error atrapado y convertido en un valor vacío es peor que un error.** Devolver una lista vacía, un `null` o un valor por defecto cuando la operación falló convierte un fallo ruidoso en corrupción silenciosa que aparece semanas después y en otro sitio.
6. **[P1]** Un error que se registra en cada petición es un error que ya nadie lee. El log de errores debe estar razonablemente limpio; si no, la señal se pierde en el ruido.

## 2. Logs

7. **[P1]** Logs **estructurados** (clave-valor, normalmente JSON), no cadenas de texto concatenadas. Un log que solo se puede leer con los ojos no se puede filtrar, agregar ni alertar.
8. **[P1]** Niveles usados con criterio y consistente en todo el proyecto: `debug` para desarrollo, `info` para hitos de negocio, `warn` para lo anómalo pero manejado, `error` para lo que requiere atención humana. Todo en `info` es lo mismo que nada.
9. **[P1]** Todo log lleva el **`correlation_id`** de la operación, para poder reconstruir una petición completa a través de servicios, colas y jobs.
10. **[P1]** Los logs no salen por la salida estándar sin más en producción: van a un destino consultable, con búsqueda por campo y por rango de tiempo. Un log que hay que descargar por SSH y leer con `grep` no se usa el día que hace falta.
11. Nunca contienen contraseñas, tokens, números de tarjeta ni datos sensibles completos (enmascarar cuando haga falta loguear referencia a ellos). Ver [[security-rules]] y [[compliance-rules]].
12. **[P2]** Los logs tienen **retención definida y coste vigilado**. Son una factura recurrente y, si contienen datos personales, también una obligación legal ([[compliance-rules]] §5 Retención).

## 3. Métricas

13. **[P2]** Se miden como mínimo, por endpoint o por operación: **tasa de errores**, **latencia** (con percentiles, no solo la media — la media esconde el 5% de usuarios que lo está pasando mal) y **volumen**.
14. **[P2]** Se miden **métricas de negocio**, no solo técnicas: registros completados, pagos exitosos y fallidos, operaciones principales del producto. El motivo: **un fallo de negocio puede no producir ningún error técnico.** Si los registros caen a cero porque el formulario dejó de enviar, ningún servidor se queja y todos los gráficos técnicos están en verde.
15. **[P2]** Se mide cada **dependencia externa** por separado: latencia y tasa de error por proveedor. Sirve para saber de quién es el problema antes de discutirlo, y para detectar una degradación antes de que se convierta en caída.
16. **[P2]** Se miden los **recursos que se agotan**: pool de conexiones a base de datos, profundidad de las colas, espacio en disco, memoria. Estos no fallan progresivamente, fallan de golpe cuando llegan al límite.
17. **[P2]** Los trabajos en segundo plano y las tareas programadas se instrumentan igual que los endpoints: cuándo se ejecutaron por última vez, cuánto tardaron, cuántas fallaron. **Un job que dejó de ejecutarse no genera ningún error** — el silencio es el síntoma, y hay que alertar sobre el silencio.

## 4. Alertas

18. **[P2]** Toda alerta tiene una acción asociada y un destinatario real. Ver [[operations-rules]] §7 Alertas y guardia para el detalle.
19. **[P2]** Se alerta sobre síntomas del usuario, no solo sobre causas técnicas.
20. **[P2]** Fallos de integraciones externas (pagos, email, APIs de terceros) alertan — estos fallan más de lo que se asume y no deben fallar en silencio.
21. **[P3]** Se alerta también sobre **ausencia de actividad esperada** (no llegaron pagos en dos horas, el job nocturno no corrió, dejaron de entrar webhooks). Es la clase de fallo que más tarda en detectarse.

## 5. Trazas y diagnóstico

22. **[P2]** El `correlation_id` se propaga a servicios, colas, jobs y llamadas salientes ([[audit-rules]] §4 Trazabilidad de extremo a extremo). Sin eso, la mitad del sistema es una caja negra en cuanto la operación sale del ciclo petición-respuesta.
23. **[P2]** Existe un lugar único donde mirar primero cuando algo va mal, y está escrito en el runbook ([[operations-rules]]). Buscar en cinco herramientas distintas durante un incidente es tiempo de caída.
24. **[P3]** Trazado distribuido cuando hay varios servicios: sin él, "está lento" es imposible de atribuir.

## 6. Coste y privacidad de la propia observabilidad

25. **[P2]** La observabilidad tiene coste (almacenamiento, ingesta, herramienta) y se vigila como cualquier otro gasto. Un log de depuración activado por error en producción puede multiplicar la factura en un día.
26. **[P2]** Las herramientas de monitorización de terceros reciben datos de tus usuarios: entran en la lista de terceros de [[compliance-rules]] §6 Terceros y transferencias, y se configuran para no capturar contenido sensible de formularios ni cuerpos de petición completos.

## Antes de dar por cerrada una tarea que puede fallar en producción

- Si esto falla en producción, ¿quedaría registro suficiente para diagnosticarlo?
- ¿El mensaje que ve el usuario final es claro y no expone detalles internos?
- ¿Hay algún catch silencioso que debería al menos loguear?
- ¿Hay algún error convertido en valor vacío que va a corromper algo más adelante?
- **[P2]** Si esto deja de funcionar del todo, ¿me entero yo antes que el usuario, o solo si alguien se queja?
- **[P2]** ¿Este proceso en segundo plano avisa si deja de ejecutarse, o solo si falla?
