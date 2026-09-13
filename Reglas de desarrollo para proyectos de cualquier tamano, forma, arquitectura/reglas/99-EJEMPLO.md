# Ejemplo trabajado — una feature de principio a fin

> Apéndice, no una capa. Se lee una vez para entender **cómo se usa el conjunto**, y se vuelve a él cuando algo no encaja.
>
> El caso está elegido a propósito: **una petición que parece trivial y no lo es.** La mayoría de los fallos serios no entran por features que dan miedo — entran por las que nadie miró dos veces.

---

## La petición

> *"Añádeme un botón para exportar mis clientes a CSV."*

Proyecto de ejemplo: SaaS de gestión, perfil **P2**, con organizaciones (multi-tenant), nivel de autonomía **supervisado**.

---

## Paso 1 — Consultar [[01-DISPARADORES]] (30 segundos)

Se busca por lo que se va a hacer. Encajan cuatro filas:

| Fila | Abre |
|---|---|
| Exportar, descargar o listar en masa | identity §4 · compliance §5 · audit §2 |
| Devolver una lista de cosas | api §1 · data §6 |
| Tocar algo en un sistema multi-organización | identity §5 · testing |
| Construir una pantalla o componente | front-rules |

Y como el CSV se genera y se sirve como archivo, también aplica `security-rules` §Archivos subidos en su parte de servido de archivos.

**Sin este paso**, lo natural es escribir un endpoint que consulta la tabla, la vuelca a CSV y la devuelve. Funciona. Y tiene, como mínimo, cinco problemas.

## Paso 2 — Lo que aparece al leer, y que el usuario no pidió

Ninguna de estas preguntas es invento: cada una sale directa de una regla concreta.

1. **¿Quién puede exportar?** Poder ver un cliente no es poder descargar los 40.000 ([[identity-rules]] §4). El acceso masivo se autoriza aparte del individual. → *Hace falta un permiso nuevo, y hay que decidir qué roles lo tienen.*
2. **¿Solo sus clientes?** La consulta tiene que llevar el filtro de organización, y de forma que sea imposible olvidarlo ([[identity-rules]] §5). → *Aquí es donde una exportación se convierte en fuga entre clientes.*
3. **¿Cuántas filas?** Un volcado sin límite bloquea la base de datos y agota la memoria del servidor ([[data-rules]] §6 Rendimiento y salud de la base de datos). → *Por encima de cierto tamaño, esto no puede ser síncrono.*
4. **¿Esto es dato personal?** Un CSV de clientes lo es, entero. Sale del sistema, se descarga y viaja ([[compliance-rules]] §1 Inventario: saber qué tienes). → *Y si se genera un archivo temporal, tiene que caducar ([[compliance-rules]] §5 Retención).*
5. **¿Queda registro?** La exportación de datos personales se audita siempre: quién, cuándo, cuántos registros ([[audit-rules]] §2 Qué se audita siempre). → *El día que alguien pregunte "¿quién se llevó nuestra base de clientes?", esta es la única respuesta posible.*
6. **¿Dónde se sirve el archivo?** Con URL firmada y caducidad, no desde una ruta pública adivinable ([[security-rules]] §Archivos subidos por el usuario, punto 29).

De un botón han salido: un permiso, un filtro obligatorio, una decisión de arquitectura (síncrono o no), una entrada de inventario, un evento de auditoría y una caducidad.

## Paso 3 — Lo que se le dice al usuario

Aquí es donde se aplica [[ai-rules]] §11 Cómo se aplican las reglas sin volver el proceso insoportable. **No se le entrega la lista anterior.** Se le llevan solo las decisiones que le pertenecen, en su idioma:

> Lo hago. Tres cosas que necesito decidir contigo, porque cambian el resultado:
>
> 1. **¿Quién puede exportar?** Ahora mismo cualquiera que vea clientes podría descargarlos todos. Sugiero limitarlo a administradores de la organización — descargar la base entera es una acción de otra categoría que ver una ficha.
> 2. **Si son más de ~5.000 clientes**, la descarga inmediata puede tumbar la aplicación. Propongo: hasta ese número, descarga directa; por encima, se genera en segundo plano y avisamos por email con un enlace que caduca a las 24 h.
> 3. **Voy a registrar quién exporta y cuántos registros**, y el enlace caducará. Es una descarga de datos personales de tus clientes y conviene poder responder por ella.
>
> Lo demás lo resuelvo yo.

Tres preguntas, no doce. Lo que no cambia la decisión del usuario **no se le consulta**: el filtro de organización, la URL firmada y la paginación interna se hacen y ya está.

## Paso 4 — Clasificar el radio ([[00-CORE]] §Antes de tocar nada)

Toca back, front, permisos y auditoría: es **cruzado**. Además el punto 2 —el límite y el modo asíncrono— es una decisión de producto. Por tanto: se explica el plan **y** se confirma antes de ejecutar. Que es exactamente lo que hizo el mensaje anterior.

No es una parada obligatoria: no hay nada irreversible, ni dinero, ni una categoría nueva de datos personales (los clientes ya estaban).

## Paso 5 — Construir

Nada sorprendente si los pasos anteriores se hicieron. En orden: permiso nuevo denegado por defecto → consulta con filtro de organización en la capa transversal → paginación interna al generar → evento de auditoría en la misma transacción, no después → archivo con URL firmada y caducidad → estados de carga y error en el botón ([[front-rules]]) → si hay modo asíncrono, job idempotente con alerta si deja de ejecutarse ([[back-rules]] §Trabajo asíncrono).

## Paso 6 — Las 5 puertas ([[evolution-rules]] §4 Definición de "hecho")

| Puerta | Cómo se cumple aquí |
|---|---|
| **Seguridad** | Permiso comprobado, filtro de organización aplicado, archivo no accesible sin firma. |
| **No rompe** | Permiso nuevo: nadie lo tiene todavía, así que no cambia el acceso de nadie existente ([[integrity-rules]], caso "cambiar quién puede hacer algo"). |
| **Verificado** | Tests corridos. Y el que importa: **un usuario de la organización A no obtiene ni una fila de la B** ([[testing-rules]] §Lo que casi nunca se testea). |
| **Rastro** | Evento de auditoría con actor, número de registros y momento. Alerta si el job asíncrono deja de correr. |
| **Nada oculto** | Si se dejó fuera la caducidad automática del archivo por tiempo, va a `DEUDA-TECNICA.md` y se dice. |

## Paso 7 — Al cerrar

En una frase: *"Listo. Exporta solo administradores, con registro de quién y cuántos. Por encima de 5.000 va en segundo plano. El borrado automático de los archivos viejos quedó pendiente, lo anoté en la deuda."*

**No se enumeran las puertas superadas ni los archivos de reglas consultados.** Lo que se dice es lo que quedó fuera.

---

## Lo que este ejemplo enseña

1. **El disparador hace el trabajo pesado.** Las preguntas del paso 2 no salieron de ser cuidadoso: salieron de abrir cuatro archivos durante medio minuto.
2. **Rigor por dentro, brevedad por fuera.** Doce consideraciones internas, tres preguntas al usuario, una frase al cerrar.
3. **El test de aislamiento es el que salva.** De todo lo anterior, el que evita el fallo más caro —enseñarle a un cliente los datos de otro— es una prueba automática de veinte líneas.
4. **Casi todo era invisible desde la petición.** "Un botón de exportar" no menciona permisos, ni tenants, ni auditoría, ni caducidad. Por eso el conjunto de reglas existe: no para las tareas que ya dan miedo, sino para las que no lo dan.

## El mismo caso en otros perfiles

- **P0** (prototipo personal): consulta, CSV, descarga. Sin permisos, sin auditoría, sin caducidad. Nada de lo anterior aplica y exigirlo sería absurdo.
- **P1** (herramienta interna): filtro correcto, límite de filas y un registro básico de quién exportó. Sin URL firmadas ni proceso asíncrono.
- **P3** (datos de salud o financieros): todo lo del P2, más justificación registrada de por qué se exporta, aviso al responsable de datos, posible cifrado del archivo y retención más estricta.

**El mismo botón, cuatro implementaciones legítimas.** Eso es lo que hacen los perfiles, y es lo que permite que un mismo conjunto de reglas sirva a un proyecto de fin de semana y a uno regulado.
