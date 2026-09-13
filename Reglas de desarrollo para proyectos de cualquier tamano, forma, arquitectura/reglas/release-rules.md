# Reglas de Integración Continua y Despliegue

> Perfil mínimo del archivo: **P1**. Las reglas marcadas `[P2]`/`[P3]` aplican desde ese perfil.
>
> [[environments-rules]] define la jerarquía entre entornos y quién manda. Este archivo define **el mecanismo**: cómo el código pasa de una rama a producción sin que nadie tenga que acordarse de hacer bien doce pasos a mano.

## 1. Puerta de calidad automatizada

1. **[P1]** Antes de poder integrar un cambio, un pipeline automático ejecuta como mínimo: formateo y linter, comprobación de tipos, tests ([[testing-rules]]), build, **escaneo de secretos** ([[config-rules]] §2 Secretos) y **auditoría de vulnerabilidades de dependencias** ([[dependencies-rules]]).
2. **[P1]** Estas comprobaciones se ejecutan **en el pipeline, no solo en local**. Lo que solo corre en la máquina de alguien no corre.
3. **[P1]** Un pipeline en rojo bloquea la integración. Si el equipo se acostumbra a mergear en rojo, el pipeline deja de significar nada y se puede borrar.
4. **[P1]** Un test que falla de forma intermitente se arregla o se retira; **no se reintenta hasta que pase**. Reintentar convierte el pipeline en un generador de ruido que oculta fallos reales. Ver [[testing-rules]].
5. **[P2]** El pipeline no tiene acceso a secretos de producción salvo en el paso de despliegue, y esos secretos están restringidos a ejecuciones desde la rama principal — nunca accesibles desde una rama de una contribución externa.

## 2. Artefacto y trazabilidad

6. **[P2]** **Se despliega exactamente el mismo artefacto que se probó.** No se recompila entre staging y producción: una recompilación puede traer una dependencia distinta y estar desplegando algo que nadie ha ejecutado nunca.
7. **[P2]** El artefacto es inmutable y está etiquetado con el commit exacto del que salió. Desde cualquier entorno se puede responder "¿qué versión y qué commit hay aquí?".
8. **[P1]** La configuración cambia entre entornos; el artefacto no. Lo que varía se inyecta según [[config-rules]].

## 3. Despliegue

9. **[P1]** El despliegue es un **procedimiento reproducible**, no una secuencia de comandos que solo una persona recuerda. Aunque sea un script de tres líneas, está escrito y en el repositorio.
10. **[P2]** **Nadie despliega a producción a mano desde su portátil** cuando hay más de una persona en el proyecto. El despliegue lo hace el pipeline desde una rama concreta, y queda registrado quién lo disparó.
11. **[P1]** **Todo despliegue tiene camino de vuelta conocido de antemano.** Se piensa antes de desplegar, no cuando ya está ardiendo. Ver [[environments-rules]] §Ningún entorno inferior toca el mundo real.
12. **[P2]** La estrategia de despliegue es proporcional al proyecto y está decidida: reinicio simple con breve corte, rolling, blue/green o canary. Sobre-ingeniería aquí cuesta tanto como sub-ingeniería.
13. **[P2]** Durante un despliegue progresivo **conviven la versión antigua y la nueva**. Todo cambio debe ser compatible con la versión inmediatamente anterior durante ese periodo: contratos de API ([[api-rules]]), formato de mensajes en colas, y esquema de datos.
14. **[P2]** Se evita desplegar antes de un fin de semana o de un periodo sin nadie disponible, salvo que sea un arreglo urgente — no por superstición, sino porque el coste de un fallo es el tiempo hasta que alguien puede atenderlo.
15. **[P2]** Tras el despliegue se **observa activamente** durante un rato (errores, latencia, métricas de negocio). Un despliegue no termina cuando el pipeline pone la marca verde; termina cuando se ha comprobado que el sistema real sigue bien.

## 4. Migraciones y despliegue

16. **[P1]** El orden entre migración de base de datos y despliegue de código está decidido explícitamente, nunca implícito.
17. **[P2]** Los cambios de esquema destructivos siguen el patrón **expandir → migrar → contraer**, repartido en varios despliegues:
    1. **Expandir**: añadir lo nuevo sin quitar lo viejo. El código antiguo sigue funcionando.
    2. **Migrar**: desplegar el código que usa lo nuevo, y trasladar los datos existentes.
    3. **Contraer**: eliminar lo antiguo, solo cuando ya no hay nada que lo use.

    Renombrar una columna en un solo paso rompe a todas las instancias antiguas que sigan vivas durante el rollout.
18. **[P2]** Las migraciones de **datos** (mover, transformar, rellenar) se separan de las migraciones de **esquema**, y las masivas se ejecutan por lotes con posibilidad de pausa — no en una transacción única que bloquee la tabla durante media hora. Ver [[data-rules]].
19. **[P2]** Un rollback de código **no revierte automáticamente una migración de datos**. Antes de desplegar, está claro si este cambio se puede revertir de verdad o solo hacia adelante.

## 5. Versionado y registro de cambios

20. **[P1]** El proyecto tiene un esquema de versionado declarado (versionado semántico salvo justificación) y cada versión desplegada es identificable.
21. **[P2]** Existe un **changelog** de lo que entra en cada versión, escrito para quien lo va a usar, no un volcado de los mensajes de commit.
22. **[P2]** Toda versión desplegada en producción está en el control de versiones y se puede reconstruir. Nunca hay un "parche que se aplicó directo en el servidor" que no exista en el repositorio: eso desaparece en el siguiente despliegue y reintroduce el bug que arreglaba.

## 6. Revisión de código

> Las reglas de revisión y de protección de la rama viven en [[git-rules]] §Revisión de código y §Ramas. Aquí solo lo que es propio del proceso de release:

23. **[P2]** El pipeline en verde es requisito para mergear, no una recomendación: es lo que convierte la revisión humana en una segunda capa en vez de en la única.
24. **[P2]** Un cambio urgente puede saltarse el proceso, pero **deja constancia** de que se saltó y se revisa después. Lo que no puede pasar es que "urgente" se convierta en el camino habitual — si la vía rápida se usa cada semana, el proceso normal está mal diseñado y es el proceso lo que hay que arreglar.

## 7. Clientes que no puedes actualizar

> Aplica a móvil, escritorio, extensiones de navegador, SDKs que otros integran y dispositivos. Cambia lo suficiente como para tener sección propia: **la regla 11 de este archivo —"todo despliegue tiene camino de vuelta"— aquí es falsa.** Una versión instalada en el teléfono de alguien no se revierte, y publicar el arreglo puede tardar días si hay revisión de tienda de por medio.

25. **[P1]** La consecuencia inmediata: **el coste de un error se multiplica y la verificación previa vale más que el rollback.** Lo que en un servicio se arregla en diez minutos, aquí se arrastra semanas.
26. **[P1]** Existe un **interruptor remoto** (feature flag servido desde el servidor, [[config-rules]] §3) para apagar una funcionalidad rota sin publicar una versión nueva. Es el único "rollback" real que existe en este paradigma, y por eso toda funcionalidad de riesgo nace detrás de uno.
27. **[P1]** **El servidor mantiene compatibilidad con las versiones de cliente que siguen vivas**, no solo con la última. Todo cambio de contrato se evalúa contra la versión más antigua soportada ([[api-rules]] §2).
28. **[P1]** Está declarada la **versión mínima soportada** y el mecanismo para forzar la actualización cuando haga falta (aviso, bloqueo suave, bloqueo duro). Sin este mecanismo, la compatibilidad hacia atrás es para siempre — y eso es una decisión que nadie tomó conscientemente.
29. **[P2]** El despliegue es **progresivo** cuando la plataforma lo permite (publicación por porcentaje), y se observan errores y valoraciones antes de completarlo.
30. **[P2]** Los **datos locales del cliente** tienen su propia migración, y esa migración corre en dispositivos que pueden llevar cinco versiones de retraso: debe funcionar saltando versiones intermedias, y no puede asumir conexión.
31. **[P2]** Está decidido qué hace la aplicación **sin conexión** y cómo se resuelven los conflictos al sincronizar — quién gana, y si el usuario se entera ([[data-rules]] §9).
32. **[P2]** Los diagnósticos no llegan solos: se instrumenta el cliente para saber qué versiones están vivas y qué falla en ellas, porque no hay acceso al entorno donde ocurre ([[observability-rules]]).

## Antes de dar por cerrado cualquier cambio en el proceso de release

- ¿Este cambio es compatible con la versión anterior mientras conviven durante el despliegue?
- ¿Se puede revertir este despliegue? ¿Y la migración de datos que lleva dentro?
- ¿El pipeline realmente valida lo que creo que valida, o hay un paso que se salta en silencio?
- ¿Hay algo aplicado en producción que no exista en el repositorio?
- ¿Alguien que no sea yo podría desplegar y revertir esto siguiendo lo que está escrito?
