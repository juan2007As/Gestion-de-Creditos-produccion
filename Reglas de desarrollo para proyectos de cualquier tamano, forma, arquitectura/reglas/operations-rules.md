# Reglas de Operación, Incidentes y Continuidad

> Perfil mínimo del archivo: **P2**. En P1 aplican solo las secciones 1 y 5 (health checks y accesos).
>
> [[environments-rules]] gobierna cómo llega el código a producción. [[observability-rules]] gobierna cómo te enteras de que algo va mal. **Este archivo gobierna qué haces cuando ya está roto** — y todo lo que hay que tener preparado *antes* para que ese momento no sea una improvisación.

## 1. Estado del sistema

1. La aplicación expone un **health check** y está definido qué significa "sano" en este proyecto concreto: no basta con "el proceso responde". Se distingue:
   - **liveness**: el proceso está vivo (si no, reiniciarlo).
   - **readiness**: puede atender tráfico (dependencias críticas accesibles). Si no, sacarlo del balanceador, no reiniciarlo.
2. El health check **no debe depender de todo**: si comprueba cinco integraciones externas, la caída de la menos importante saca el servicio entero de servicio.
3. **[P2]** Existe una forma de responder en menos de un minuto a: ¿está funcionando?, ¿desde cuándo?, ¿qué versión está desplegada?, ¿qué desplegó el último cambio?

## 2. Runbook: los procedimientos escritos

4. **[P2]** Existe un runbook escrito y accesible (no en la cabeza de nadie) que cubre al menos:
   - cómo desplegar y **cómo revertir**;
   - cómo reiniciar cada componente;
   - **cómo restaurar un backup**, con los pasos reales, no "restaurar el backup";
   - cómo poner el sistema en modo mantenimiento o degradado;
   - cómo rotar cada credencial;
   - a quién avisar según el tipo de problema (proveedor de hosting, de pagos, responsable del dato).
5. **[P2]** Un procedimiento del runbook que nunca se ha ejecutado es una hipótesis, no un procedimiento. Los críticos (restauración, rollback) se **ensayan** al menos una vez, y se anota cuándo se ensayaron por última vez.
6. **[P2]** El runbook se actualiza cuando el sistema cambia. Un runbook obsoleto es peor que ninguno: da falsa confianza justo cuando no hay tiempo de descubrir que miente.

## 3. Incidentes

7. **[P2]** Están definidos los **niveles de severidad** con criterios concretos y observables, no subjetivos. Por ejemplo: SEV1 el servicio no funciona o hay pérdida/exposición de datos; SEV2 una funcionalidad principal está rota o degradada para muchos usuarios; SEV3 fallo acotado con solución alternativa.
8. **[P2]** **Mitigar primero, entender después.** Durante un incidente el objetivo es restaurar el servicio (revertir, desactivar un flag, escalar recursos). La causa raíz se investiga cuando el usuario ya no está sufriendo. Esto es la excepción explícita a la regla de "entender la causa raíz antes de parchear" de [[ai-rules]] §3 Cero pereza — y en cuanto el incidente se cierra, la regla vuelve a aplicar.
9. **[P2]** Durante un incidente hay **una sola persona coordinando** y decidiendo. Dos personas tocando producción a la vez sin coordinación han causado más daño que muchos incidentes originales.
10. **[P2]** Todo lo que se toca durante un incidente se **anota mientras pasa** (hora y acción). La memoria reconstruye mal, y ese registro es la base del postmortem y de la auditoría.
11. **[P2]** **Comunicación al usuario**: está definido a partir de qué severidad se comunica, por qué canal y quién lo hace. El silencio durante una caída hace más daño a la confianza que la caída.
12. **[P3]** Si el incidente implica datos personales, se activa el procedimiento de brecha de [[compliance-rules]] **en paralelo**, no después — los plazos legales corren desde que se detecta, no desde que se arregla.

## 4. Postmortem

13. **[P2]** Todo incidente grave (SEV1/SEV2) tiene un postmortem escrito en los días siguientes, con: qué pasó, cronología, impacto real medido, causa raíz, por qué no se detectó antes, y **acciones concretas con responsable**.
14. **[P2]** El postmortem es **sin culpa**. La pregunta no es quién se equivocó, sino qué permitió que un error individual llegara a producción. Un postmortem que busca culpables garantiza que el siguiente incidente se oculte.
15. **[P2]** Las acciones del postmortem son tareas reales con dueño y prioridad, o van a `DEUDA-TECNICA.md` según [[evolution-rules]]. Un postmortem sin acciones ejecutadas es un ritual.
16. **[P2]** "Tener más cuidado" y "recordar hacer X" no son acciones válidas. Las acciones válidas cambian el sistema: una validación, una alerta, un test, un paso automatizado — o una regla nueva en su archivo dueño, que es la vía de [[evolution-rules]] §8 Aprender de los fallos. Toda pregunta de postmortem termina en una de esas dos formas: **automatizar** ([[02-AUTOMATIZABLE]]) o **enrutar** ([[01-DISPARADORES]]). Confiar en la memoria de alguien no es ninguna de las dos.

## 5. Accesos y bus factor

17. **[P1]** Existe un **inventario de accesos**: qué servicios usa el proyecto (hosting, dominio, base de datos, pagos, email, repositorio, DNS, monitorización), quién tiene acceso a cada uno y con qué nivel.
18. **[P1]** **Ninguna cuenta crítica depende de una sola persona.** Si solo una persona puede entrar al proveedor de dominio o al de pagos, un accidente, unas vacaciones o una salida del equipo pueden dejar el proyecto muerto sin que nadie pueda hacer nada. Esto se resuelve antes de que sea urgente, porque cuando es urgente ya no tiene solución.
19. **[P1]** Las cuentas críticas se registran a nombre de la **organización**, no de la cuenta personal de alguien.
20. **[P2]** MFA activo en todo servicio crítico, con los códigos de recuperación guardados en un lugar seguro y **conocido por más de una persona**.
21. **[P2]** **Offboarding**: cuando alguien deja el proyecto, existe una lista de qué revocar, y se ejecuta el mismo día. Se revocan también los tokens personales, las claves SSH y las sesiones activas, no solo la cuenta principal.
22. **[P2]** Revisión periódica de accesos: quién tiene qué y si todavía lo necesita. Los permisos solo suben si nadie los revisa.
23. **[P2]** El acceso directo a producción (base de datos, consola) está restringido, es excepcional, requiere justificación y queda auditado (ver [[audit-rules]] §2 Qué se audita siempre).

## 6. Continuidad: lo que caduca en silencio

24. **[P1]** Existe una lista de **cosas que caducan** y quién las vigila, con aviso anticipado: dominio, certificados TLS, tarjeta de pago del proveedor cloud, tokens y claves de terceros, licencias, y las versiones de runtime/base de datos que llegan a fin de soporte.
25. **[P1]** Las renovaciones críticas están automatizadas donde se puede (certificados, renovación de dominio) y **monitorizadas siempre** — la automatización también falla, y falla en silencio.
26. **[P2]** Está pensado y escrito qué pasa si desaparece una dependencia externa crítica: el proveedor de pagos, el de email, el de hosting. No hace falta tener el plan implementado; hace falta que no sea la primera vez que se piensa el día que ocurre.
27. **[P2]** Backups, restauración probada y objetivos **RPO/RTO**: la regla completa vive en [[data-rules]] §5. Aquí solo su consecuencia operativa — el tiempo que tardó la última restauración de prueba **es** el RTO real del proyecto, por mucho que el documento diga otra cosa.

## 7. Alertas y guardia

28. **[P2]** **Toda alerta tiene una acción asociada.** Si al recibirla la respuesta correcta es "no hacer nada", esa alerta se corrige o se borra. Las alertas ruidosas entrenan al equipo a ignorarlas, y el día que una importa también se ignora.
29. **[P2]** Se alerta sobre **síntomas que sufre el usuario** (errores, latencia, operaciones que no completan), no solo sobre causas técnicas (CPU, memoria). Un servidor al 90% de CPU que sirve todo correctamente no es una emergencia.
30. **[P2]** Está claro **quién responde** fuera de horario y por qué canal llega el aviso. Si la respuesta es "nadie", entonces está aceptado explícitamente que una caída nocturna dura hasta la mañana — y eso es una decisión legítima, pero tomada, no descubierta.
31. **[P3]** Los objetivos de servicio (SLO) están escritos y se miden, y si hay compromiso contractual con clientes (SLA), el SLO interno es más estricto que el SLA externo.

## 8. Mantenimiento planificado

32. **[P2]** Las tareas de mantenimiento recurrentes están identificadas y calendarizadas: actualización de dependencias ([[dependencies-rules]]), rotación de secretos ([[config-rules]]), revisión de accesos, purga de datos según retención ([[compliance-rules]]), prueba de restauración de backups ([[data-rules]]), y limpieza de feature flags muertos.
33. **[P2]** El mantenimiento no es "lo que se hace cuando sobra tiempo". Nunca sobra tiempo: si no está calendarizado, no se hace, y el sistema se degrada hasta que la degradación se convierte en incidente.
34. **[P2]** Las ventanas de mantenimiento con impacto para el usuario se anuncian con antelación y se hacen en el horario de menor uso real, medido, no supuesto.

## Antes de dar por cerrada cualquier tarea con impacto operativo

- Si esto falla a las 3 de la madrugada, ¿alguien se entera, y sabría qué hacer sin llamarme?
- ¿Este componente nuevo está en el runbook y en el inventario de accesos?
- ¿He introducido alguna dependencia que caduque o que dependa de una sola persona?
- ¿La alerta que acabo de crear tiene una acción concreta, o es solo ruido nuevo?
- Tras este incidente, ¿hay una acción concreta que impida que vuelva a pasar, o solo buena intención?
