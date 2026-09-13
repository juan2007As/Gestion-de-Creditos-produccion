# Disparadores — Qué leer según lo que vas a hacer

> Las reglas no fallan por estar mal escritas, fallan porque nadie sabe que existen en el momento en que harían falta. Esta tabla es el enrutamiento: **se consulta antes de empezar cualquier tarea, no después**.
>
> Se busca por lo que se **va a hacer**, no por el tema al que pertenece — porque uno sabe que va a tocar un formulario, no sabe que eso es un asunto de cumplimiento normativo.
>
> Los enlaces apuntan a **secciones**, no a números de regla: los números se mueven en cuanto alguien inserta algo, los nombres de sección no.
>
> Las filas marcadas `[P2]` solo aplican desde ese perfil (ver [[README]]). [[00-CORE]] aplica siempre y no aparece aquí.

## Si una fila apunta a un archivo que no existe

Los archivos de reglas se generan **cuando el proyecto llega a ese dominio**, no todos por adelantado (Fase 3 del planteamiento, §3.3). Una fila marcada `(pendiente de generar)` significa que el proyecto todavía no había tocado ese terreno.

Que se active esa fila **es** el momento de generarlo: se escribe el archivo antes de continuar, especializado y con el caso real delante, y se avisa al usuario de que el proyecto acaba de entrar en un dominio nuevo. Después se quita la marca.

Lo que no se hace: seguir sin él, ni resolver el dominio de memoria. Esta tabla existe justamente para que ese momento no pase desapercibido.

## Construir

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Crear o cambiar un endpoint** | [[back-rules]] · [[api-rules]] §1 Forma del contrato · [[identity-rules]] §4 Autorización | ¿Puede este usuario acceder a **este** recurso, o solo comprobé que hay sesión? |
| **Cambiar la forma de una respuesta o petición** | [[api-rules]] §2 Cambios y compatibilidad · [[integrity-rules]] | ¿Qué consumidor se rompe con esto? ¿Los busqué de verdad, incluidos los de fuera del repo? |
| **Devolver una lista de cosas** | [[api-rules]] §1 · [[data-rules]] §6 Rendimiento | ¿Está paginada, y el tope lo impone el servidor? ¿Es un escaneo completo de una tabla que va a crecer? |
| **Exportar, descargar o listar en masa** | [[identity-rules]] §4 · [[compliance-rules]] §5 Retención · [[audit-rules]] §2 | Poder ver un cliente no es poder descargar los 40.000. ¿Está autorizado aparte? ¿El archivo generado caduca? |
| **Construir una pantalla o componente** | [[front-rules]] | ¿Estados vacío/carga/error? ¿Se ve con el texto más largo real? ¿Funciona solo con teclado? |
| **Escribir cualquier texto visible** | [[front-rules]] §Texto, idiomas y formatos | ¿Está en la capa de textos, o acabo de hardcodear algo que habrá que buscar en 200 archivos? |
| **Mostrar una fecha, una hora o un importe** | [[front-rules]] §Texto · [[data-rules]] §2 Los dos temas que siempre se hacen mal | UTC al guardar, zona del usuario al mostrar. Dinero jamás en coma flotante, y siempre con su moneda. |
| **Escribir lógica de negocio no trivial** | [[testing-rules]] | ¿Existe un test que **falle** si esto se rompe? ¿Lo comprobé rompiéndolo a propósito? |

## Datos

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Añadir o cambiar un campo / una tabla** | [[data-rules]] §1 Modelo · §4 Migraciones · [[integrity-rules]] | ¿Qué pasa con los datos que ya existen? ¿Hace falta migración de datos además de la de esquema? |
| **Guardar un dato nuevo de una persona** | [[compliance-rules]] §1 Inventario · §2 Minimización · [[data-rules]] §8 Privacidad | ¿De verdad hace falta guardarlo? Lo que no se tiene no se filtra, no se protege y no se borra. |
| **Declarar una regla de unicidad o una invariante** | [[data-rules]] §1 · §3 Concurrencia | ¿Está garantizada por la base de datos, o solo por un `if` que dos peticiones simultáneas se saltan? |
| **Tocar contadores, saldos, reservas o stock** | [[data-rules]] §3 Concurrencia · §2 | ¿Qué pasa si dos peticiones hacen esto exactamente a la vez? |
| **Borrar una entidad (o permitir borrarla)** | [[data-rules]] §1 · §8 · [[integrity-rules]] · [[audit-rules]] §2 | ¿Qué pasa con lo que la referencia? ¿Y con las copias en cachés, índices y terceros? |
| **Escribir un script que modifique datos** | [[data-rules]] §7 Operar sobre datos reales | Primero como `SELECT` para ver qué filas toca. Nunca sin `WHERE`. Backup verificado antes. |
| **Cachear algo** | [[back-rules]] §Rendimiento · [[data-rules]] §9 | ¿Qué la invalida? ¿La clave incluye al usuario o al tenant, o voy a servirle los datos de uno a otro? |

## Identidad y permisos

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Tocar login, registro, contraseña o sesión** | [[identity-rules]] §1-§3 · [[audit-rules]] §2 | ¿Esto revela si una cuenta existe? ¿Invalida las sesiones anteriores cuando debe? |
| **Añadir un rol, permiso o nivel de acceso** | [[identity-rules]] §4 · [[integrity-rules]] | ¿A quién se le abre y a quién se le cierra el acceso con esto, contando los usuarios que ya existen? |
| **Añadir un panel de administración o una acción de admin** | [[identity-rules]] §4 · §6 Impersonación · [[audit-rules]] §2 · [[security-rules]] §Superficie de red | ¿Queda registro de quién lo hizo? ¿Está expuesto a internet sin capa adicional? |
| **[P2] Tocar algo en un sistema multi-organización** | [[identity-rules]] §5 Multi-tenancy · [[testing-rules]] §Lo que casi nunca se testea | ¿Lleva el filtro de tenant, y es **imposible** escribir la consulta sin él? |

## Integraciones y trabajo asíncrono

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Llamar a un servicio externo** | [[api-rules]] §4 Llamadas salientes | ¿Tiene timeout? ¿Qué hace el sistema si el proveedor lleva cinco minutos caído? |
| **Integrar un proveedor nuevo** | [[api-rules]] §4 · [[compliance-rules]] §6 Terceros · [[dependencies-rules]] | ¿Va a recibir datos de nuestros usuarios? Entonces no es una decisión solo técnica. |
| **Recibir o emitir un webhook** | [[api-rules]] §5 Webhooks | ¿Verifico la firma? ¿Aguanta que llegue dos veces y en desorden? |
| **Escribir un job, un cron o un consumidor de cola** | [[back-rules]] §Trabajo asíncrono · [[observability-rules]] §3 Métricas | Un job que **deja de ejecutarse** no genera ningún error. ¿Alerto por el silencio? |
| **[P2] Guardar un estado que también vive en un tercero** | [[api-rules]] §6 Reconciliación · [[data-rules]] §9 | Si el webhook no llega, nadie se entera nunca. ¿Hay forma de detectar la desincronización? |
| **Aceptar archivos subidos por el usuario** | [[security-rules]] §Archivos subidos | ¿Desde dónde se sirven? Un SVG servido en tu dominio con sesión es XSS. |

## Configuración, dependencias y despliegue

| Vas a… | Abre | La pregunta que casi siempre se olvida |
|---|---|---|
| **Añadir una variable de entorno** | [[config-rules]] §1 Configuración · [[integrity-rules]] | ¿Está validada al arrancar y en `.env.example`, o alguien la descubrirá rota en tres semanas? |
| **Manejar un secreto o una credencial** | [[config-rules]] §2 Secretos · [[security-rules]] | ¿Puede acabar en un log, en una URL o en el bundle del frontend? |
| **Añadir un feature flag** | [[config-rules]] §3 Feature flags | ¿Tiene dueño y fecha de caducidad, o acabo de crear una rama de lógica eterna? |
| **Instalar una dependencia** | [[dependencies-rules]] §1 Antes de añadir | ¿Comprobé que ese paquete existe y es el que digo, o confié en el nombre? |
| **Desplegar** | [[release-rules]] · [[environments-rules]] | ¿Se puede revertir esto? ¿Y la migración de datos que lleva dentro? |
| **Trabajar en local contra datos o servicios reales** | [[environments-rules]] §Ningún entorno inferior toca el mundo real | ¿Esto puede enviar un email, un SMS o un cobro real desde un entorno de pruebas? |
| **Hacer commit** | [[git-rules]] | ¿He leído el diff entero, o estoy subiendo cosas que no he mirado? |

## Situaciones (no cambios de código)

| Estás en… | Abre | Lo primero |
|---|---|---|
| **Algo está roto en producción ahora mismo** | [[operations-rules]] §3 Incidentes | **Mitigar primero, entender después.** Y anotar lo que se toca, mientras se toca. |
| **Se ha filtrado un secreto** | [[config-rules]] §2 Secretos | **Revocar primero.** Limpiar el historial es lo último y no reduce el riesgo. |
| **[P2] Hay sospecha de acceso indebido a datos** | [[compliance-rules]] §8 Brechas · [[operations-rules]] §3 | El plazo legal corre desde que se **detecta**, no desde que se arregla. En paralelo, no después. |
| **Persigues un bug** | [[00-CORE]] §17 · [[testing-rules]] | Antes del arreglo, el test que reproduce el fallo — y que se comprueba que falla. |
| **Hay prisa y no da tiempo a todo** | [[evolution-rules]] §5 Prioridad bajo presión | Se negocia el plazo, no la seguridad ni el rastro. Y se dice en voz alta qué se está dejando fuera. |
| **Se rompió algo que ninguna regla previó** | [[evolution-rules]] §8 Aprender de los fallos | Además del arreglo y del test: ¿había una regla que lo habría evitado? Las tres respuestas posibles llevan a acciones distintas. |
| **Cierras un ciclo, sprint o hito** | [[evolution-rules]] §Checklist de cierre | ¿Sigue el perfil del proyecto siendo el correcto, o la realidad ya lo subió? |
| **Publicas para un cliente que no puedes actualizar** | [[release-rules]] §7 Clientes que no puedes actualizar | Aquí no hay rollback. ¿Está detrás de un interruptor remoto? |
| **Empiezas un proyecto nuevo** | [`00-planteamiento-protocol.md`](../00-planteamiento-protocol.md) | No se escribe código hasta cerrar las fases de planteamiento. |
| **Entras a un proyecto que ya existe** | [`01-adopcion-protocol.md`](../01-adopcion-protocol.md) | Primero entender qué hay de verdad; las reglas se adoptan, no se imponen de golpe. |

---

## Si nada de la tabla encaja

Entonces el cambio probablemente sea local y trivial, y basta con [[00-CORE]]. Pero antes de darlo por hecho, dos comprobaciones: **¿toca algo que otros usan?** y **¿toca dinero, datos de personas o producción?** Si alguna es que sí, no era trivial.

Y si aparece un tipo de tarea recurrente que no está en esta tabla, se añade la fila. Esta tabla es el índice vivo del conjunto: si no crece con el proyecto, deja de enrutar.
