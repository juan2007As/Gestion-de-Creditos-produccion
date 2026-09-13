# Prompts listos para usar

## Antes de nada: llevar las reglas al proyecto

La IA tiene que poder **leer** las reglas. Dos formas:

**A) Copiarlas dentro del proyecto** (recomendado — viajan con el repo y sobreviven a que cambies de máquina o de herramienta):

```bash
# desde la raíz del proyecto destino
cp -r "/c/Users/sarit/Downloads/Reglas de desarrollo para proyectos de cualquier tamano, forma, arquitectura/reglas" .
cp "/c/Users/sarit/Downloads/Reglas de desarrollo para proyectos de cualquier tamano, forma, arquitectura/01-adopcion-protocol.md" .
cp "/c/Users/sarit/Downloads/Reglas de desarrollo para proyectos de cualquier tamano, forma, arquitectura/plantilla-CLAUDE.md" .
```

**B) Dejarlas donde están** y darle la ruta absoluta a la IA. Funciona si la herramienta puede leer fuera del directorio del proyecto. En ese caso, sustituye en el prompt la mención a `./reglas/` por la ruta completa.

---

## 1. Prompt de arranque (el principal)

> Copiar y pegar tal cual en la primera sesión, con el proyecto abierto.

```
Vamos a adoptar en este proyecto un conjunto de reglas de desarrollo que ya
tengo escrito. Está en `./reglas/` y el procedimiento a seguir está en
`./01-adopcion-protocol.md`.

Léelos primero, empezando por `reglas/README.md` (el índice y los perfiles),
`reglas/00-CORE.md` y `01-adopcion-protocol.md`. Después entra en MODO
ADOPCIÓN y sigue ese protocolo por fases.

Reglas de esta sesión, importantes:

1. NO modifiques ni una línea de código en las fases A0 a A3. Son de
   inventario y auditoría. Si arreglas cosas sobre la marcha, la auditoría
   no termina nunca y el diff se vuelve irrevisable.
2. PARA al final de cada fase y espérame. No encadenes fases sin mi visto
   bueno.
3. Investiga el código tú mismo antes de preguntarme. Buena parte de lo que
   necesitas está ahí. Pregúntame solo lo que no se puede deducir leyendo:
   cuántos usuarios reales hay, si pagan, quién tiene los accesos, qué está
   desplegado y dónde.
4. No juzgues el código existente. Descríbeme el riesgo concreto, no la
   calidad de quien lo escribió (que fui yo). "Cualquiera con cuenta puede
   leer los pedidos de otro cambiando el ID en la URL" me sirve; "hay
   problemas graves de seguridad" no.
5. Sé concreto y no alarmista. Y si algo no lo sabes, dilo en vez de
   suponerlo.

Empieza por la FASE A0 (inventario de la realidad). Cuando la tengas,
descríbeme el proyecto de vuelta con lo que hayas encontrado —incluido lo
que creas que yo no sé— y espera mi confirmación antes de seguir.
```

---

## 2. Prompt corto

> Para cuando ya conoces el flujo y no quieres tanta instrucción.

```
Lee `reglas/README.md`, `reglas/00-CORE.md` y `01-adopcion-protocol.md`, y
entra en MODO ADOPCIÓN sobre este proyecto.

Empieza por la Fase A0. No toques código hasta la Fase A4, y para al final
de cada fase a esperar mi aprobación.
```

---

## 3. Prompt para retomar en otra sesión

> La adopción no cabe en una sola sesión. Este es el de continuación.

```
Seguimos con la adopción de reglas de este proyecto.

Lee `CONTEXTO.md`, `DEUDA-TECNICA.md` y `01-adopcion-protocol.md` para
situarte, dime en qué fase nos quedamos según lo que encuentres escrito, y
continúa desde ahí. Mismas condiciones: una fase por vez, y me esperas al
final de cada una.
```

---

## 4. Prompt para el día a día (una vez adoptadas)

Normalmente **no hace falta**: para eso está el `CLAUDE.md` que genera la Fase A5, que se carga solo. Úsalo solo si tu herramienta no carga nada automáticamente, o si notas que la IA se ha olvidado del conjunto a mitad de una conversación larga:

```
Antes de seguir: relee `reglas/00-CORE.md` y `reglas/01-DISPARADORES.md`,
y mira qué disparadores aplican a lo que vamos a hacer ahora.
```

---

## Qué deberías obtener al terminar

| Fase | Resultado |
|---|---|
| **A0** | Una descripción del proyecto tal como es de verdad, no como se cuenta. |
| **A1** | `CONTEXTO.md` con el planteamiento reconstruido y las decisiones que se ven en el código. |
| **A2** | El perfil (P0-P3) asignado y justificado. |
| **A3** | `DEUDA-TECNICA.md` poblado, con los huecos repartidos en los cuatro cajones. |
| **A4** | Las comprobaciones automáticas mínimas en marcha (escaneo de secretos, backup probado, registro de errores, pipeline). |
| **A5** | `reglas/` especializado con lo que el proyecto **hace**, y el `CLAUDE.md` que lo carga todo solo. |

## Señales de que algo va mal

- **Empieza a arreglar código en la Fase A1.** Recuérdale el punto 1 del prompt.
- **La auditoría A3 sale con 200 puntos y sin prioridad.** Falta repartirlos en los cuatro cajones; pídeselo, y en particular el cajón 4 (lo que se acepta y se escribe).
- **Las reglas generadas en A5 describen un proyecto ideal** en vez del tuyo. Es el fallo más probable de todo el proceso: pídele que reescriba describiendo lo que hay hoy, con las reglas incumplidas marcadas como `PENDIENTE`.
- **Te pregunta cosas que están en el código.** Punto 3 del prompt.
