# Reglas de Integridad (Impacto Cruzado)

> El principio central: nada se cambia de forma aislada. Todo cambio se evalúa por su efecto en el resto del sistema antes de ejecutarse.

## Protocolo obligatorio antes de cualquier cambio no trivial

1. **Buscar todos los usos/dependientes** del elemento que se va a tocar (función, componente, endpoint, tabla, tipo/interfaz, variable de entorno) antes de modificarlo — con búsqueda real en el código, no por memoria o suposición.
2. **Clasificar el cambio** por su radio de impacto:
   - Local (un archivo, sin dependientes externos) → se puede ejecutar directo.
   - Módulo (afecta a otros archivos dentro del mismo módulo) → se explica el plan antes de ejecutar.
   - Cruzado (afecta a otro módulo, al front desde el back o viceversa, o a una integración externa) → se explica el plan Y se confirma con el usuario antes de ejecutar, salvo que ya esté explícitamente autorizado.
3. **Explicar el plan en términos concretos**: "esto va a cambiar X, lo cual usan Y y Z, así que también voy a actualizar Y y Z" — no un aviso vago de "esto puede tener efectos secundarios".
4. Tras el cambio, **verificar que los dependientes siguen funcionando** (tests, o revisión manual si no hay tests para esa parte) antes de dar la tarea por cerrada.

## Casos específicos de alto riesgo (requieren el protocolo completo siempre)

5. Cambiar la forma/contrato de una API (request/response) — revisar todos los consumidores.
6. Cambiar el esquema de datos (columnas, tipos, relaciones) — revisar todas las queries y migraciones relacionadas.
7. Renombrar o mover archivos/módulos — revisar todos los imports.
8. Cambiar una variable de entorno o config compartida — revisar todo lugar que la lea.
9. Cambiar un componente de UI muy reutilizado (botón base, layout, card) — revisar todas las pantallas donde aparece, no solo la que motivó el cambio.
10. Eliminar código "que parece no usarse" — confirmar con búsqueda real que no tiene referencias antes de borrar, y explicar qué se borra y por qué. Ojo: la búsqueda en el código no encuentra los usos que llegan por nombre dinámico, desde otro repositorio, desde una tarea programada, desde un webhook de un tercero o desde un panel de administración. Antes de borrar algo que parece muerto, se comprueba también si tiene tráfico real.
11. **Cambiar una regla de negocio, un precio o un cálculo** — revisar qué pasa con los datos ya creados bajo la regla anterior. Lo ya calculado normalmente **no se recalcula**: se conserva el valor que se aplicó en su momento ([[config-rules]] §4 Parámetros de negocio).
12. **Cambiar el formato de un mensaje de cola o de un evento** — durante un despliegue conviven productores y consumidores de dos versiones ([[back-rules]] §Trabajo asíncrono: colas, jobs y tareas programadas).
13. **Cambiar quién puede hacer algo** (roles, permisos, visibilidad) — revisar a quién se le abre y a quién se le cierra el acceso con este cambio, incluidos los usuarios ya existentes, y comprobar que no queda nadie bloqueado ni nadie viendo de más ([[identity-rules]]).
14. **Añadir un campo a una respuesta de API** — comprobar que no expone datos que ese consumidor no debería ver ([[api-rules]] §1 Forma del contrato).
15. **Tocar algo que produce dinero o datos legales** (facturación, impuestos, contratos, retención) — el radio de impacto incluye lo ya emitido, no solo lo futuro.

## Lo que la búsqueda en el código no encuentra

16. El chequeo de dependientes no se limita al repositorio actual. También hay que considerar: otros repositorios y clientes móviles, integraciones de terceros que consumen la API, webhooks configurados fuera, tareas programadas, paneles de administración, informes y consultas guardadas, y la propia documentación. Si algo de esto existe en el proyecto, forma parte de la búsqueda del punto 1.

## Señal de alarma

Si para responder "¿esto rompe algo más?" la única respuesta disponible es "no debería" sin haber buscado — eso es señal de que falta hacer el paso 1. No se asume seguridad, se verifica.
