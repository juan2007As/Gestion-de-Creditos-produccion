# Qué verifica una máquina y qué juzga una persona

> La disciplina se erosiona. En la conversación cuarenta, con prisa, se cumple lo que una máquina comprueba y se olvida el resto. Por eso el conjunto de reglas separa explícitamente las dos categorías:
>
> - **Reglas mecanizables**: tienen una respuesta objetiva y repetible. **Deben** convertirse en una comprobación automática. Confiar en que alguien se acuerde es aceptar que un día no se acuerde.
> - **Reglas de juicio**: requieren entender el problema. No se automatizan; se sostienen con checklists y con revisión.
>
> **Regla que gobierna este archivo:** una regla mecanizable que todavía no está mecanizada **es deuda técnica** y se registra como tal en `DEUDA-TECNICA.md` ([[evolution-rules]] §3). No es "algo que estaría bien tener": es una regla que hoy no se está cumpliendo de forma fiable, aunque parezca que sí.

## El principio de diseño detrás de todo esto

Casi todo el conjunto de reglas se cumple por **autorreporte**: quien trabaja dice que corrió los tests, que buscó los dependientes, que comprobó la autorización. Nada lo verifica. Ese es el techo estructural de cualquier conjunto de reglas, y no se supera con más reglas ni con más disciplina.

**Cuanta más Definition of Done viva en la máquina y menos en el autorreporte, menos depende todo de que quien trabaja sea escrupuloso precisamente el día que tiene prisa.** De ahí salen dos consecuencias que conviene tener presentes:

1. **Dónde invertir**: entre escribir una regla nueva y automatizar una que ya existe, casi siempre rinde más lo segundo. Una regla escrita compite por la atención; una comprobación automática no necesita atención.
2. **Qué hacer cuando una puerta se salta por olvido**: la respuesta correcta nunca es "tener más cuidado" ([[operations-rules]] §4). Es mover esa puerta a esta lista, o —si no se puede— hacer que aparezca en [[01-DISPARADORES]] justo en el momento en que hace falta.

Corolario incómodo pero útil: **una regla que no se puede automatizar ni enrutar, y que depende solo de que alguien se acuerde, hay que asumir que se incumplirá alguna vez.** Si el coste de ese incumplimiento es inaceptable, el problema no está en la regla — está en el diseño del sistema, que permite que ese fallo sea posible.

## Cómo se usa

En la **Fase 3** del planteamiento (o en la **Fase A4** de adopción) se recorre este archivo y se decide, para cada línea, una de tres cosas: **ya está**, **se implementa ahora**, o **se acepta como deuda con motivo**. Lo que quede en la tercera categoría se escribe. Ninguna línea se queda sin decisión.

---

## 1. Bloqueo antes de commitear (pre-commit)

Barato, inmediato, y evita que el problema entre siquiera al historial.

| Comprueba | Regla que hace cumplir |
|---|---|
| Formateo y linter | [[architecture-rules]], convenciones del proyecto |
| **Escaneo de secretos** | [[config-rules]] §2 · [[git-rules]] §Secretos y el historial |
| Archivos que nunca deben subirse (`.env`, builds, volcados) | [[git-rules]] |

> El escaneo de secretos es el único de esta lista que es innegociable en cualquier perfil, incluido P0: el historial de Git es permanente y un secreto commiteado ya está comprometido.

## 2. Bloqueo antes de integrar (pipeline)

| Comprueba | Regla que hace cumplir | Perfil |
|---|---|---|
| Tests en verde | [[testing-rules]] | P0 |
| Comprobación de tipos / compilación | [[back-rules]], [[front-rules]] | P0 |
| Escaneo de secretos (otra vez, por si se saltó el pre-commit) | [[config-rules]] §2 | P0 |
| **Vulnerabilidades conocidas en dependencias** | [[dependencies-rules]] §3 | P1 |
| Lockfile presente y coherente | [[dependencies-rules]] §2 | P0 |
| Licencias de dependencias dentro de la lista permitida | [[dependencies-rules]] §5 | P2 |
| Análisis estático de seguridad (SAST) | [[security-rules]] §Seguridad del propio desarrollo | P2 |
| Build reproducible del artefacto que se desplegará | [[release-rules]] §2 | P2 |
| Detección de tests desactivados o marcados como omitidos | [[testing-rules]] | P1 |

> Con el criterio de [[release-rules]] §1: está decidido de antemano **qué severidad bloquea y qué solo avisa**. Un pipeline que bloquea por todo se acaba desactivando.

## 3. Comprobaciones en el propio código (fallo rápido)

Las más valiosas del archivo: no dependen de que nadie ejecute nada.

| Comprueba | Regla que hace cumplir | Perfil |
|---|---|---|
| **Validación de configuración al arrancar** — si falta una variable, la aplicación no arranca | [[config-rules]] §1 | P0 |
| **Sin valores por defecto inseguros** — un secreto sin definir es un fallo de arranque, no un valor genérico | [[config-rules]] §1 | P0 |
| **Bloqueo de envíos reales fuera de producción** — implementado en el punto de envío, no como advertencia en un documento | [[environments-rules]] §Ningún entorno inferior toca el mundo real | P1 |
| **Filtro de tenant imposible de olvidar** — capa transversal, RLS, o conexión por tenant | [[identity-rules]] §5 | P2 |
| **Denegar por defecto** — un endpoint sin autorización declarada no se sirve, en vez de servirse abierto | [[identity-rules]] §4 | P1 |
| Enmascarado automático de campos sensibles en logs | [[security-rules]] · [[observability-rules]] §2 | P1 |
| Límites de tamaño de petición y de página aplicados globalmente | [[api-rules]] §1 · [[security-rules]] §Validación de entrada | P1 |
| Timeout por defecto en el cliente HTTP saliente | [[api-rules]] §4 | P1 |

## 4. Comprobaciones en la base de datos

Lo que el esquema garantiza no se puede saltar con una condición de carrera ni con un script de mantenimiento.

| Comprueba | Regla que hace cumplir | Perfil |
|---|---|---|
| Restricciones de unicidad, claves foráneas, `NOT NULL`, rangos válidos | [[data-rules]] §1 | P0 |
| Tipo exacto para importes (nunca coma flotante) | [[data-rules]] §2 | P0 |
| Tipo consciente de zona horaria para instantes | [[data-rules]] §2 | P0 |
| Audit log sin permiso de borrado ni modificación para la aplicación | [[audit-rules]] §1 | P2 |
| Permisos mínimos del usuario de base de datos de la aplicación | [[security-rules]] §Principios | P1 |

## 5. Tests que hacen cumplir una regla

Estos no prueban una funcionalidad: prueban que una regla del conjunto sigue viva.

| Test | Regla que hace cumplir | Perfil |
|---|---|---|
| **El usuario A no puede leer ni modificar el recurso de B** — por cada tipo de recurso | [[testing-rules]] §Lo que casi nunca se testea · [[identity-rules]] §4 | P1 |
| **Aislamiento entre organizaciones** | [[identity-rules]] §5 | P2 |
| **Idempotencia**: ejecutar dos veces produce un solo efecto | [[api-rules]] §3 | P1 |
| Contrato de API verificado contra su documentación | [[api-rules]] §1 | P2 |
| Migraciones aplicadas sobre datos representativos, y revertidas si se declaran reversibles | [[data-rules]] §4 | P2 |
| Las sesiones se invalidan al cambiar la contraseña | [[identity-rules]] §2 | P1 |

## 6. Vigilancia continua (nadie tiene que acordarse)

| Comprueba | Regla que hace cumplir | Perfil |
|---|---|---|
| Última ejecución exitosa de cada tarea programada — **alerta por el silencio** | [[back-rules]] §Trabajo asíncrono · [[observability-rules]] §3 | P1 |
| Profundidad de la cola de fallidos | [[back-rules]] §Trabajo asíncrono | P2 |
| Caducidad de certificados, dominios, tarjetas y tokens de terceros | [[operations-rules]] §6 | P1 |
| Antigüedad del último backup **y del último restore probado** | [[data-rules]] §5 | P1 |
| Tasa de errores y latencia por endpoint y por proveedor externo | [[observability-rules]] §3 | P2 |
| Métricas de negocio (registros, pagos) — un fallo de negocio no genera error técnico | [[observability-rules]] §3 | P2 |
| **Discrepancias de reconciliación con terceros** | [[api-rules]] §6 | P2 |
| Gasto de infraestructura y de logs | [[back-rules]] §Rendimiento · [[observability-rules]] §6 | P2 |
| Vulnerabilidades nuevas en dependencias ya instaladas | [[dependencies-rules]] §3 | P1 |
| Purga automática de datos que superan su retención | [[compliance-rules]] §5 | P2 |
| Caducidad de feature flags | [[config-rules]] §3 | P2 |

## 7. Recordatorios calendarizados

No son automatizables en el sentido de "una máquina lo decide", pero sí en el de "una máquina lo recuerda". Sin fecha en un calendario, no ocurren. Ver [[operations-rules]] §8 y [[evolution-rules]] §7.

- Prueba real de restauración de un backup.
- Rotación de secretos.
- Revisión de accesos y de permisos concedidos.
- Actualización de dependencias y revisión de versiones fuera de soporte.
- Auditoría del conjunto de `reglas/` y de `CONTEXTO.md`, con revisión del perfil.
- Limpieza de feature flags y de deuda técnica vencida.

---

## Lo que NO se automatiza (y por qué importa saberlo)

Estas reglas no tienen comprobación mecánica posible, y pretender lo contrario da una falsa sensación de cobertura. Se sostienen con las checklists de [[00-CORE]] y con revisión humana:

- **Si el cambio resuelve el problema real** o solo hace desaparecer el síntoma.
- **Si la arquitectura es proporcional** al proyecto, o es sobre-ingeniería.
- **Si el radio de impacto se evaluó de verdad** — un pipeline no sabe qué olvidaste buscar.
- **Si el modelo de datos refleja el negocio** o lo fuerza a caber.
- **Si la decisión es reversible** y si merece confirmación explícita.
- **Si lo que se dice al usuario es cierto** o es lo que suena bien decir.
- **Si el mensaje de error es entendible** para quien lo va a leer.
- **Si esta funcionalidad debería existir.**

La cobertura de tests, por cierto, pertenece a esta lista y no a las anteriores: es una **señal**, no un objetivo. Un 90% de cobertura sobre tests que no comprueban nada es peor que un 50% sobre lo que importa, porque además da confianza ([[testing-rules]]).
