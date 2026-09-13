# PLANTILLA — enganche de carga de las reglas

> **Instrucciones para quien genera el proyecto (no forman parte del archivo final):**
>
> Copia el contenido de debajo de la línea a la raíz del proyecto, con el nombre del archivo que tu herramienta carga automáticamente en cada sesión:
>
> | Herramienta | Archivo |
> |---|---|
> | Claude Code | `CLAUDE.md` |
> | Codex / agentes que siguen el estándar | `AGENTS.md` |
> | Cursor | `.cursorrules` |
> | Otra | el que esa herramienta lea sola, sin que nadie se lo pida |
>
> Si tu herramienta no carga ningún archivo automáticamente, este contenido va al principio de cada sesión a mano. **No es opcional:** sin este enganche, las tres capas de atención dependen de que la IA se acuerde de ir a buscarlas — que es exactamente lo que el diseño intenta evitar.
>
> Rellena `[NOMBRE DEL PROYECTO]`, `[Pn]` y `[NIVEL]` con los valores reales antes de guardarlo.

---

# [NOMBRE DEL PROYECTO]

## Antes de responder a nada, lee estos dos archivos

1. **`reglas/00-CORE.md`** — las reglas que aplican a todo. Una página. Se lee entera, siempre.
2. **`reglas/01-DISPARADORES.md`** — la tabla de enrutamiento. Se consulta **antes de empezar cada tarea** para saber qué más hay que abrir.

Y **`CONTEXTO.md`** para saber qué es este proyecto, qué decisiones se tomaron y por qué.

Si la conversación se ha alargado y ya no tienes el núcleo delante, vuelve a leerlo antes de seguir. No trabajes de memoria sobre las reglas.

## Datos del proyecto

- **Perfil:** `[Pn]` — determina qué reglas aplican. Ver `reglas/README.md`.
- **Nivel de autonomía:** `[NIVEL]` (consultivo / supervisado / autónomo). Ver `reglas/ai-rules.md` §10.
- **Deuda técnica conocida:** `DEUDA-TECNICA.md`.

## Lo que nunca se salta, sea cual sea el nivel de autonomía

Se para y se pregunta ante: algo **irreversible**, cualquier operación difícil de deshacer sobre **producción** (y nunca sin backup verificado), **dinero**, empezar a recoger una **categoría nueva de datos personales**, un **cambio de alcance** respecto a lo acordado, o el mismo problema fallando **dos veces** con el mismo enfoque.

## Cómo se aplican las reglas

**El rigor va en el trabajo, no en la respuesta.** Las reglas se cumplen siempre; se mencionan solo cuando cambian lo que recibes, cuando bloquean algo, o cuando preguntas. No se enumeran los chequeos que salieron bien. Lo que sí se dice siempre es lo que quedó pendiente.

La ceremonia es proporcional al radio del cambio: un cambio local se hace y se reporta en una frase; uno cruzado o irreversible se explica y se confirma antes.

## Si falta un archivo de reglas

Los archivos de `reglas/` se generan **cuando el proyecto llega a ese dominio**, no todos por adelantado. Si un disparador apunta a un archivo que todavía no existe, ese es el momento: se genera entonces —especializado, con el caso real delante— y se avisa. No se sigue adelante sin él ni se improvisa el dominio de memoria.
