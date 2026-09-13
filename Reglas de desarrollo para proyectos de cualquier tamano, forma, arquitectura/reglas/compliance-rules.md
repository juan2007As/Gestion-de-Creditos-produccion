# Reglas de Privacidad, Cumplimiento y Obligaciones Legales

> Perfil mínimo del archivo: **P2** (desde que hay datos de personas reales que no son tú). En **P3** aplica entero y es prioritario.
>
> **Aviso:** esto son reglas de ingeniería para no incumplir por descuido, no asesoramiento legal. Cuando hay dinero, salud, menores o datos biométricos de por medio, la decisión final es de un profesional del derecho — el trabajo de la IA es asegurarse de que el sistema **pueda** cumplir y de que nadie descubra tarde que no puede.
>
> El motivo de tener esto escrito: casi todo lo de aquí es **imposible o carísimo de añadir después**. Un sistema que no sabe qué datos personales tiene ni dónde están no puede borrarlos aunque quiera.

## 1. Inventario: saber qué tienes

1. **[P2]** Existe un inventario de datos personales: **qué** se recoge, **dónde vive** cada dato (tabla, caché, índice de búsqueda, logs, backups, y cada sistema de terceros), **para qué** se usa, **quién** puede leerlo y **cuánto tiempo** se guarda.
2. **[P2]** El inventario se actualiza **en el mismo cambio** que añade un campo personal nuevo. Si se deja para después, no se hace, y el inventario deja de ser fiable — que es lo mismo que no tenerlo.
3. **[P2]** Los datos personales están **marcados en el código o en el modelo** (anotación, convención de nombre, tipo). Si distinguir un campo personal de uno que no lo es requiere leer todo el proyecto, ninguna regla de este archivo es aplicable en la práctica.
4. **[P3]** Se distinguen las **categorías especiales** (salud, biometría, origen étnico, religión, orientación sexual, ideología, condenas) porque tienen requisitos mucho más estrictos y a menudo la respuesta correcta es simplemente **no almacenarlas**.

## 2. Minimización y propósito

5. **[P2]** **No se recoge un dato "por si acaso sirve más adelante".** Cada dato personal almacenado tiene un propósito concreto y actual. Lo que no se tiene no se puede filtrar, no hay que protegerlo, no hay que borrarlo y no hay que justificarlo.
6. **[P2]** Se prefiere el dato menos identificativo que resuelva el problema: un rango de edad en vez de la fecha de nacimiento, un país en vez de la dirección exacta, un hash en vez del identificador.
7. **[P2]** Usar un dato para algo distinto de aquello para lo que se recogió es una **decisión nueva**, no una optimización. Los datos de facturación no se usan para marketing porque estaban a mano.
8. **[P3]** Anonimización y seudonimización no son lo mismo: seudonimizar (sustituir el nombre por un identificador) sigue siendo dato personal si existe la tabla que lo revierte. Anonimizar de verdad es irreversible — y hay que comprobar que no se puede reidentificar cruzando campos.

## 3. Consentimiento y transparencia

9. **[P2]** Cuando el consentimiento es la base para tratar un dato, se **registra**: qué aceptó exactamente el usuario, **cuándo**, y **qué versión** del texto legal estaba vigente. Un booleano `acepto_terminos = true` no demuestra nada.
10. **[P2]** Los textos legales (términos, privacidad, cookies) están **versionados** y se conserva cada versión histórica, porque hay que poder demostrar qué se aceptó en su momento.
11. **[P2]** El consentimiento se puede **retirar** con la misma facilidad con la que se dio, y retirarlo tiene efecto real en el sistema, no solo en un campo de la base de datos.
12. **[P2]** Nada de casillas premarcadas, nada de agrupar en un solo "acepto" consentimientos para finalidades distintas (usar el servicio, recibir marketing, ceder datos a terceros son cosas separadas).
13. **[P2]** Las cookies y trazadores no esenciales **no se cargan antes** de obtener el consentimiento. El banner que pregunta después de haber cargado el analítico es incumplimiento con interfaz bonita.

## 4. Derechos del usuario: implementados, no prometidos

14. **[P2]** El sistema puede, **para un usuario concreto y en un plazo razonable**:
    - **Acceder / exportar**: entregar todos sus datos en un formato legible y portable.
    - **Rectificar**: corregir datos erróneos.
    - **Borrar**: eliminarlo de verdad, con las excepciones legales documentadas.
    - **Oponerse / limitar**: dejar de usar sus datos para una finalidad concreta sin cerrar la cuenta.
15. **[P2]** Si estas operaciones requieren que un desarrollador escriba consultas a mano cada vez, no están implementadas — son un favor que alguien hace mientras tenga tiempo, y fallan justo cuando llegan varias a la vez.
16. **[P2]** **El borrado cruza sistemas.** Borrar al usuario de tu base de datos no lo borra del proveedor de pagos, del de email marketing, del almacenamiento de archivos, del índice de búsqueda, de las cachés, de los logs ni de los backups. Está escrito qué pasa en **cada uno** de esos sitios, y quién lo ejecuta.
17. **[P2]** Los **backups** son la excepción honesta: normalmente no se pueden editar. La solución aceptada es documentar que los datos persisten en backups hasta que expira su retención, y garantizar que **una restauración no resucita** datos que se habían borrado.
18. **[P2]** Está definido qué se **conserva** pese a una solicitud de borrado y por qué: facturas por obligación fiscal, registros de auditoría por obligación de trazabilidad ([[audit-rules]]), datos necesarios para defenderse legalmente. Y en esos casos se conserva **solo lo imprescindible**, no la cuenta entera.
19. **[P2]** Borrar a un usuario no debe romper la integridad de lo que dejó (pedidos, facturas, mensajes). Se decide de antemano: anonimizar el autor conservando el contenido, o borrar ambos. Ver [[data-rules]].

## 5. Retención

20. **[P2]** Cada categoría de dato tiene un **plazo de retención declarado** y un proceso automático que lo aplica. Sin proceso automático, la retención declarada es una intención: en la práctica todo se guarda para siempre.
21. **[P2]** La retención también aplica a **logs, backups, cachés y exportaciones generadas**. Un log con direcciones IP y correos guardado indefinidamente es un almacén de datos personales que nadie está vigilando.
22. **[P2]** Un archivo exportado (informe, CSV de clientes) que queda en un bucket sin caducidad es una fuga esperando a ocurrir: las exportaciones caducan y se borran.

## 6. Terceros y transferencias

23. **[P2]** Existe una lista de **todos los terceros que tocan datos de tus usuarios**: hosting, base de datos, analítica, email, pagos, soporte, monitorización, y cualquier API de IA a la que se envíe contenido de usuario. Cada uno necesita su contrato de tratamiento de datos.
24. **[P2]** Añadir un servicio de terceros que va a recibir datos personales **no es una decisión técnica menor**: se decide explícitamente con el usuario, igual que una decisión difícil de revertir ([[evolution-rules]] §4 Definición de "hecho").
25. **[P2]** Está documentado **dónde se procesan y almacenan** los datos geográficamente, porque la residencia de datos puede ser un requisito legal o contractual, y cambiarla después implica migrar de proveedor.
26. **[P3]** Enviar contenido de usuario a un servicio de IA de terceros es una transferencia de datos: se declara, se consiente cuando corresponde, y se comprueba si el proveedor entrena con ello. Ver [[ai-rules]].

## 7. Ámbitos con reglas propias

27. **[P3]** **Pagos**: los datos de tarjeta **nunca tocan tus servidores**. Se usa la tokenización del proveedor (campos alojados por él). El momento en que el número de tarjeta pasa por tu código, aunque no lo guardes, es el momento en que entras en el alcance completo de PCI-DSS. No se registra jamás el número completo ni el CVV, ni siquiera temporalmente en un log.
28. **[P3]** **Menores de edad**: si el producto puede ser usado por menores, hay requisitos adicionales de consentimiento parental y restricciones de publicidad y perfilado. Si no se quieren asumir, hay que impedir activamente su registro, no limitarse a prohibirlo en los términos.
29. **[P3]** **Salud, biometría y datos financieros**: se asume el marco más estricto aplicable y se consulta con un profesional antes de diseñar el modelo de datos, no después de construirlo.
30. **[P3]** **Decisiones automatizadas** que afecten significativamente a una persona (denegar un crédito, cerrar una cuenta, moderar contenido) deben ser explicables y tener una vía de revisión humana.
31. **[P2]** **Accesibilidad**: en muchos contextos es una obligación legal, no una mejora opcional. Ver [[front-rules]].
32. **[P2]** **Comunicaciones comerciales**: consentimiento previo, remitente identificable, y baja funcionando en un clic. Un enlace de baja roto es una infracción, no un bug menor.

## 8. Brechas de seguridad

33. **[P2]** Existe un procedimiento escrito de brecha, porque los plazos son **cortos** (72 horas para notificar a la autoridad en el RGPD) y **empiezan cuando se detecta**, no cuando se arregla.
34. **[P2]** El procedimiento define: quién decide que esto es una brecha, cómo se evalúa el alcance (qué datos, de cuántas personas), quién notifica a la autoridad, cuándo hay que avisar a los afectados, y quién habla públicamente.
35. **[P2]** La capacidad de **determinar el alcance** depende directamente de [[audit-rules]]: sin rastro de accesos no se puede saber qué se llevaron, y entonces hay que asumir lo peor y notificar el máximo.
36. **[P2]** Todo incidente con datos personales se documenta aunque se concluya que no requiere notificación — la decisión de no notificar también hay que poder justificarla.
37. **[P2]** Existe una vía para que alguien de fuera **reporte una vulnerabilidad** (contacto público o `security.txt`) y un compromiso de responder. Sin ella, quien encuentre un fallo lo publicará o lo venderá.

## Antes de dar por cerrada cualquier tarea que toque datos personales

- ¿Este dato nuevo es personal? ¿Está en el inventario, marcado, y con retención definida?
- ¿De verdad hace falta guardarlo, o lo estoy recogiendo por si acaso?
- Si mañana este usuario pide que lo borren todo, ¿este dato desaparecería de **todos** los sitios donde acaba de quedar copiado?
- ¿Este dato está saliendo hacia algún tercero que no está en la lista?
- ¿Acaba este dato en un log, en una URL, en un email o en una exportación sin caducidad?
- **[P3]** ¿Hay algún punto por el que pase un número de tarjeta completo?
