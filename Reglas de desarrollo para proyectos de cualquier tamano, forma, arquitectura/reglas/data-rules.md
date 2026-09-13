# Reglas de Datos

> Distinto de seguridad: seguridad es "que no te roben los datos"; esto es "que los datos tengan sentido, sean consistentes, no se corrompan y no se pierdan".
>
> Perfil mínimo: **P0**. Las reglas marcadas `[P1]`/`[P2]`/`[P3]` aplican desde ese perfil (ver [[README]]).

## 1. Modelo de datos

1. Todo modelo de datos define explícitamente qué campos son obligatorios, qué formato/rango es válido, y qué pasa con valores nulos — no dejarlo implícito en el comportamiento del ORM.
2. Las relaciones entre entidades reflejan la realidad del negocio (uno-a-uno, uno-a-muchos, muchos-a-muchos) — no forzar una relación más simple de lo que es solo por comodidad inicial, si eso va a requerir un rediseño doloroso pronto.
3. **Las invariantes se garantizan en la base de datos, no solo en el código.** Unicidad, claves foráneas, `NOT NULL` y restricciones de valor se declaran en el esquema. El código se salta con una condición de carrera, un script de mantenimiento o una segunda instancia del servicio; el esquema no.
4. Datos derivados/calculados no se duplican como fuente de verdad si se pueden calcular — si se cachean por rendimiento, se documenta cómo se mantienen sincronizados y qué los invalida.
5. Se define explícitamente qué pasa al borrar una entidad que otras referencian (cascada, restricción, soft-delete) — nunca dejarlo "a ver qué hace la base de datos por defecto" sin haberlo decidido.
6. **[P1]** Las entidades con ciclo de vida (pedido, suscripción, ticket, cuenta) tienen una **máquina de estados explícita**: los estados posibles están enumerados y las transiciones válidas declaradas y verificadas. Sin esto acabas con un pedido "reembolsado" que vuelve a "pendiente de pago" porque llegó un evento tarde.
7. Un campo con significado múltiple ("este texto a veces es un código y a veces un comentario") es un error de modelado, no un ahorro de columna.

## 2. Los dos temas que siempre se hacen mal

8. **Dinero nunca en coma flotante.** Se usa decimal exacto o enteros de la unidad mínima (céntimos). `0.1 + 0.2` no da `0.3`, y ese error se acumula factura a factura hasta que un cliente lo detecta antes que tú.
9. **Todo importe lleva su moneda.** Un número suelto es una futura pérdida. Y nunca se suman importes de monedas distintas sin conversión explícita, con la tasa y la fecha de conversión guardadas.
10. **Todo instante se almacena en UTC**, con tipo de dato consciente de zona horaria. La conversión a hora local ocurre solo en presentación.
11. Se distingue un **instante** (cuándo ocurrió algo: UTC) de una **fecha civil** (un cumpleaños, un día festivo: no tiene hora ni zona) de una **hora local futura** (una cita a las 9:00 en Madrid: hay que guardar la zona, porque el cambio de horario mueve el instante).
12. El cambio de horario existe: hay días de 23 y de 25 horas, y horas locales que ocurren dos veces o ninguna. "Sumar 24 horas" no es "mañana a la misma hora".
13. Codificación Unicode completa en toda la cadena (base de datos, conexión, aplicación). Los nombres de personas llevan tildes, eñes, apellidos compuestos y emojis, y no se validan con reglas inventadas sobre qué "parece" un nombre real.

## 3. Concurrencia

14. **[P1]** Dos peticiones simultáneas son el caso normal, no el excepcional. El patrón "leer, comprobar en el código, escribir" es una condición de carrera: entre la comprobación y la escritura cabe otra petición entera.
15. **[P1]** La unicidad se garantiza con una restricción de la base de datos, no comprobando antes si existe.
16. **[P1]** Cuando dos usuarios pueden editar lo mismo, se decide explícitamente entre bloqueo optimista (versión del registro; el segundo recibe un conflicto) y el último gana. "El último gana" es una opción válida si se ha elegido; es un bug si se ha descubierto.
17. **[P1]** Los contadores y saldos se actualizan en la base de datos de forma atómica, nunca leyendo el valor a la aplicación y escribiendo el resultado.
18. **[P2]** Las transacciones se mantienen cortas y **nunca contienen llamadas de red a terceros**: una transacción abierta esperando a una API externa bloquea filas y agota el pool de conexiones.

## 4. Migraciones

19. Los cambios de esquema (agregar/quitar/renombrar campos, cambiar tipos) se hacen vía **migraciones versionadas**, nunca editando la base de datos directamente a mano en producción.
20. Toda migración se prueba primero sobre una copia con **volumen y forma realistas**, no sobre una base vacía. Una migración que tarda 40 ms con 100 filas puede bloquear una tabla media hora con 10 millones.
21. **[P1]** Se separa la migración de **esquema** (cambiar la estructura) de la migración de **datos** (mover o transformar contenido). Se despliegan y se revierten distinto.
22. **[P1]** Las migraciones de datos masivas se ejecutan **por lotes**, con posibilidad de pausar y reanudar, y son **reejecutables sin duplicar efectos** por si se cortan a la mitad.
23. **[P2]** Los cambios destructivos siguen el patrón expandir → migrar → contraer de [[release-rules]] §4 Migraciones y despliegue. Renombrar una columna en un solo paso rompe a toda instancia antigua que siga viva durante el despliegue.
24. **[P1]** Antes de una migración irreversible sobre producción se confirma que existe un backup **reciente y verificado** ([[environments-rules]] §Ningún entorno inferior toca el mundo real).

## 5. Backups y recuperación

25. **[P1]** Existe una política de backup declarada: qué se respalda, con qué frecuencia, cuánto se retiene, y dónde se guarda — en una ubicación **separada** de los datos originales y del mismo proveedor de acceso, o un compromiso de la cuenta se lleva también los backups.
26. **[P1]** **Un backup que nunca se ha restaurado no es un backup, es una suposición.** La restauración se prueba de verdad, con periodicidad, y se anota cuándo se probó por última vez y cuánto tardó. Esa cifra es tu RTO real.
27. **[P2]** Están escritos el **RPO** (cuántos datos es aceptable perder) y el **RTO** (cuánto tiempo es aceptable estar caído). Sin esos dos números, la política de backup no se puede evaluar. Ver [[operations-rules]] §6 Continuidad: lo que caduca en silencio.
28. **[P2]** Los backups se cifran y su acceso está restringido: contienen exactamente lo mismo que la base de datos de producción, incluidos todos los datos personales.
29. **[P2]** La retención de backups se coordina con la retención legal de [[compliance-rules]]: un backup eterno es un almacén de datos personales que nadie está vigilando.
30. **[P1]** Un backup no sustituye a un histórico. Si el negocio necesita saber cómo estaba un registro hace tres meses, eso se modela ([[audit-rules]]), no se resuelve restaurando un backup.

## 6. Rendimiento y salud de la base de datos

31. **[P1]** Los índices se crean por una razón concreta (una consulta real que los necesita), y se sabe cuáles existen. Cada índice acelera lecturas y frena escrituras: ni ninguno ni todos.
32. **[P1]** Ninguna consulta de una pantalla o endpoint depende de un escaneo completo de una tabla que va a crecer sin límite.
33. **[P1]** Se detectan y corrigen las consultas N+1: son el problema de rendimiento más común y el más invisible en desarrollo, donde hay 10 filas.
34. **[P2]** Se monitorizan las consultas lentas y el uso del pool de conexiones ([[observability-rules]]). Una consulta que degrada al crecer los datos no avisa: simplemente un día ya no responde.
35. **[P2]** Los procesos pesados de lectura (informes, exportaciones, analítica) no compiten con el tráfico de usuarios: réplica de lectura, ventana horaria o límites explícitos.
36. **[P2]** Los archivos grandes (imágenes, adjuntos, vídeos) no se guardan en la base de datos: van a almacenamiento de objetos y en la base queda la referencia.

## 7. Operar sobre datos reales

37. **[P1]** **Nunca un `UPDATE` o `DELETE` sin `WHERE` en producción.** Todo script que modifique datos se ejecuta primero como `SELECT` para ver exactamente cuántas y cuáles filas va a tocar, dentro de una transacción, y con backup confirmado.
38. **[P1]** El acceso directo a la base de datos de producción es excepcional, justificado y auditado ([[operations-rules]] §5 Accesos y bus factor). Todo cambio hecho a mano queda registrado, porque si no, es un cambio que no existe en ningún sitio y desaparece en el siguiente despliegue.
39. **[P1]** **Los datos de producción no se copian a otros entornos sin anonimizar.** Ver [[environments-rules]] y [[compliance-rules]]. Un volcado de producción en el portátil de alguien es una brecha de datos esperando a un robo de portátil.
40. **[P1]** Las semillas y datos de prueba son sintéticos. Nunca PII real, nunca emails ni teléfonos reales de personas — un entorno de pruebas que envía un correo a un cliente real es un incidente.

## 8. Privacidad, retención y borrado

41. **[P1]** Identificar qué datos son personales/sensibles y documentar cuánto tiempo se retienen y bajo qué justificación. El detalle está en [[compliance-rules]].
42. **[P1]** Si el proyecto lo requiere (usuarios reales, no solo demo), soft-delete o anonimización en vez de borrado físico inmediato para datos con valor de auditoría.
43. **[P1]** Si se usa soft-delete, **todas** las consultas deben excluir lo borrado por defecto, de forma que no filtrar sea difícil, no solo desaconsejado. Un registro borrado que reaparece en una lista es peor que no haberlo borrado.
44. **[P2]** El borrado de un usuario cruza sistemas: base de datos, cachés, índices de búsqueda, almacenamiento de archivos, logs, colas y terceros. Está escrito qué pasa en cada uno ([[compliance-rules]] §4 Derechos del usuario: implementados, no prometidos).
45. **[P2]** Está decidido qué ocurre con el contenido de un usuario borrado (anonimizar el autor y conservar el contenido, o borrar ambos) — y esa decisión no puede romper la integridad de facturas ni de registros contables.

## 9. Cuando el dato vive en más de un sitio

46. **[P2]** Para cada entidad que existe también fuera del sistema (proveedor de pagos, CRM, ERP, índice de búsqueda) está declarado **quién es la fuente de verdad** y qué gana en un conflicto. Ver [[api-rules]] §6 Reconciliación.
47. **[P2]** Toda copia (caché, índice, vista materializada, réplica) tiene una estrategia de invalidación explícita y un desfase máximo aceptable. Una caché sin invalidación definida sirve datos obsoletos indefinidamente, y nadie sabe desde cuándo.
48. **[P2]** Existe forma de **detectar la desincronización** y de reconstruir la copia desde la fuente de verdad. Ver la regla de reconciliación de [[api-rules]] §6 Reconciliación.

## Antes de dar por cerrado un cambio de modelo de datos

- ¿Qué pasa con los datos existentes al aplicar este cambio? ¿Necesitan migración de datos, no solo de esquema?
- ¿Qué pasa si se borra esta entidad? ¿Se decidió explícitamente el comportamiento en cascada?
- ¿Este dato nuevo es sensible? ¿Está cubierto por [[security-rules]] y [[compliance-rules]]?
- ¿Esta invariante está garantizada por la base de datos, o solo por una condición en el código?
- ¿Qué pasa si dos peticiones hacen esto exactamente a la vez?
- ¿Esta migración se ha probado con volumen real, o solo con una tabla vacía?
- ¿Hay un backup reciente y verificado antes de esta operación irreversible?
- ¿Este dato acaba copiado en algún otro sitio que ahora hay que mantener sincronizado?
