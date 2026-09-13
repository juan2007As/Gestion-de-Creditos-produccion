# Reglas de Auditoría y Trazabilidad

> Perfil mínimo del archivo: **P2**. En P1 basta con auditar cambios de permisos y borrados; en P0 no aplica.
>
> **No es lo mismo que [[observability-rules]].** Los logs sirven para que tú diagnostiques un fallo, son ruidosos, se rotan y se borran. El audit log sirve para responder ante un cliente, un auditor o un juez a la pregunta "¿quién hizo esto y cuándo?". Son sistemas distintos, con retención distinta y permisos distintos. Mezclarlos hace que ninguno de los dos sirva.

## 1. Principios no negociables

1. **El audit log es de solo-añadir (append-only).** No se edita, no se borra por registros sueltos, no se "corrige". Si un registro es erróneo, se añade otro que lo explique.
2. **Quien administra el sistema no puede borrar el rastro de lo que hizo.** El audit log vive en un almacén con permisos propios (tabla sin permiso de DELETE/UPDATE para la aplicación, servicio externo, o almacenamiento inmutable). Un rastro que el atacante puede limpiar no es un rastro.
3. **Escribir la auditoría es parte de la operación, no un efecto secundario opcional.** Si la operación se confirma y la auditoría no, se ha perdido el rastro; el diseño debe hacer que eso sea imposible o al menos detectable y alertado.
4. **Nunca se registra el dato sensible en sí, sino la referencia y el hecho.** Se audita "usuario X cambió la contraseña de Y", nunca la contraseña. Se audita "se exportaron 3.200 registros de clientes", no los registros. Ver [[security-rules]].
5. Si una acción no se puede reconstruir después leyendo el audit log, esa acción no está terminada.

## 2. Qué se audita siempre

6. **Identidad**: inicio y cierre de sesión, intentos fallidos de autenticación, bloqueo de cuenta, alta y baja de MFA, cambio de contraseña y de email.
7. **Permisos**: concesión, revocación y modificación de cualquier rol o permiso. Quién lo otorgó y sobre quién.
8. **Acciones de administración**: cualquier operación hecha desde un panel de administración o con privilegios elevados, incluida la **impersonación** (ver [[identity-rules]] §6 Impersonación y acceso de soporte).
9. **Datos sensibles**: acceso, modificación y **exportación**. En P3, también la simple lectura de registros con datos personales por parte de personal interno.
10. **Borrados y operaciones irreversibles**: qué se borró, quién y cuándo. Un borrado sin rastro es indistinguible de una pérdida de datos.
11. **Cambios de configuración** del sistema: feature flags, límites, integraciones, credenciales, parámetros de negocio (precios, comisiones, cuotas). Ver [[config-rules]].
12. **Operaciones financieras**: cobros, reembolsos, cambios de plan, aplicación de descuentos, ajustes manuales de saldo. Estas se auditan siempre, sin excepción, desde el primer día.
13. **[P3]** Acceso directo a la base de datos de producción por parte de una persona, con la justificación asociada.

## 3. Qué contiene cada registro

14. Un registro de auditoría sin alguno de estos campos está incompleto:
    - **Quién**: identificador del actor. Si hubo impersonación o una acción automatizada en nombre de alguien, se registran **ambos**: el actor real y el actor efectivo.
    - **Qué**: el tipo de acción, con un código estable y enumerado (no un texto libre que cambie con cada refactor).
    - **Sobre qué**: tipo y identificador del recurso afectado.
    - **Cuándo**: marca de tiempo en **UTC**, con precisión suficiente para ordenar eventos del mismo segundo.
    - **Desde dónde**: IP de origen y agente/cliente, cuando exista.
    - **Resultado**: si la acción tuvo éxito o fue denegada. **Los intentos denegados se auditan igual que los exitosos** — son la señal temprana de un ataque.
    - **Correlación**: el `correlation_id` de la petición, para poder cruzarlo con [[observability-rules]].
15. En cambios de datos se registra el **antes y el después** de los campos modificados, no solo "se actualizó el registro". Sin el valor anterior, el rastro no permite reconstruir nada ni deshacer nada.
16. Los códigos de acción son **estables en el tiempo**. Renombrar un tipo de evento rompe la historia: se añade uno nuevo y se deja de usar el viejo, no se reescribe.

## 4. Trazabilidad de extremo a extremo

17. Toda petición entrante recibe (o genera) un **`correlation_id`** que se propaga a: los logs de la aplicación, las llamadas a otros servicios internos, los mensajes que se encolan, los jobs que se disparan a raíz de ella, y el registro de auditoría.
18. Ese identificador se devuelve al cliente en la respuesta de error, para que un usuario pueda reportar "me falló con el código X" y sea localizable en un segundo. Un identificador opaco no filtra información y ahorra horas de soporte.
19. Una operación asíncrona (cola, job, webhook) arrastra el `correlation_id` de la operación que la originó. Sin eso, la mitad del sistema es una caja negra en cuanto algo sale del ciclo petición-respuesta.

## 5. Retención, acceso y consulta

20. La retención del audit log se define explícitamente y es **más larga** que la de los logs de aplicación. Cuando hay obligación legal o contractual, la define esa obligación, no la comodidad. Ver [[compliance-rules]].
21. Quién puede **leer** el audit log está restringido y definido — contiene por diseño el mapa completo de la actividad del sistema.
22. **[P3]** Leer el audit log también se audita.
23. El audit log debe ser **consultable en la práctica**, no solo existir: se puede filtrar por actor, por recurso y por rango de fechas sin escribir código nuevo. Un rastro que hace falta un desarrollador y dos horas para consultar no sirve el día que hace falta de verdad.
24. Los backups del audit log siguen las mismas reglas de [[data-rules]], incluida la verificación de restauración.

## 6. Relación con el resto del sistema

25. Auditoría y logs se escriben en **destinos distintos**. Un log de depuración no debe poder inundar ni desplazar al rastro de auditoría.
26. El audit log **no es la fuente de verdad del negocio**. Si el estado actual de una entidad solo se puede reconstruir leyendo la auditoría, falta modelar el estado en [[data-rules]] (o se está haciendo event sourcing, que es una decisión de arquitectura consciente y no un accidente).
27. Un cambio que añade una acción sensible nueva añade su evento de auditoría **en el mismo commit**. No en una tarea posterior, porque esa tarea no llega nunca.

## Antes de dar por cerrada cualquier tarea con superficie de auditoría

- Si mañana un cliente pregunta "¿quién borró/cambió esto?", ¿podría responderle con datos y no con suposiciones?
- ¿Esta acción sensible nueva registra actor real, recurso, momento y resultado?
- ¿Se está registrando algún dato sensible en claro dentro del propio rastro?
- ¿El intento **denegado** de esta acción también deja registro?
- ¿El `correlation_id` sobrevive hasta el final de la operación, incluida su parte asíncrona?
