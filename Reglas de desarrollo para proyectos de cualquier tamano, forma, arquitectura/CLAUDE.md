# Trabajar sobre este repositorio

> Este archivo aplica **solo a este repo** — el que contiene las plantillas madre. No se copia a los proyectos generados; para eso está [`plantilla-CLAUDE.md`](plantilla-CLAUDE.md).

## Qué es esto

Un conjunto de reglas de desarrollo, genérico y reutilizable. Aquí **no se construye software**: se escriben y se mantienen las reglas con las que otros proyectos se construirán.

La consecuencia práctica más importante:

**No rellenes los marcadores.** `[STACK]`, `[BASE DE DATOS]`, `[BREAKPOINTS]` están así a propósito. Se especializan en la copia que vive dentro de cada proyecto real, generada en la Fase 3 del planteamiento o la Fase A5 de la adopción. "Arreglarlos" aquí rompe la utilidad del repo.

## Convenciones al editar reglas

1. **Toda regla lleva su porqué.** Una regla sin motivo se cumple literalmente y se incumple en espíritu; y nadie sabe si se puede borrar cuando parece excesiva. Si además viene de un caso real, el caso va pegado en una línea.
2. **Referencias cruzadas siempre a sección, nunca a número de regla.** Se escribe `[[data-rules]] §5 Backups y recuperación`, no `[[data-rules]] #26`.

   *(El caso: al insertar una regla en `api-rules` se corrió la numeración y quedaron inválidas 66 referencias de otros archivos, en un repo de veintitantos archivos. Los números se mueven; los nombres de sección no.)*
3. **Un tema, un archivo dueño.** El mapa de propiedad está en [`reglas/README.md`](reglas/README.md). En los demás archivos el tema aparece como **puntero**, nunca como copia — dos copias divergen.
4. **Marcado de perfil**: sin marca = aplica desde P0; `[P1]`/`[P2]`/`[P3]` = aplica desde ese perfil en adelante.
5. **`00-CORE.md` no crece.** Es la única regla estructural del conjunto: para meter algo hay que sacar algo. Un núcleo de seis páginas es exactamente el problema que el núcleo resuelve.
6. **Numeración correlativa por archivo**, continua entre secciones. Al insertar una regla en medio hay que renumerar lo que sigue.

## Al añadir un archivo de reglas nuevo

Tres sitios que hay que tocar además del archivo, o el archivo nace huérfano y nadie lo abrirá nunca:

1. `reglas/README.md` — el índice y el **mapa de propiedad**.
2. `reglas/01-DISPARADORES.md` — al menos una fila que lleve a él. Un archivo al que no apunta ningún disparador es un archivo que no existe en la práctica.
3. `00-planteamiento-protocol.md` (Fase 3) y `01-adopcion-protocol.md` (Fase A5) — la lista de qué se genera y en qué perfil.

Y si la regla es mecanizable, línea en `reglas/02-AUTOMATIZABLE.md`.

## Verificación antes de dar por cerrado un cambio

Estas comprobaciones existen porque las tres han fallado ya:

```bash
# 1. Enlaces internos que no corresponden a ningún archivo
grep -rho '\[\[[A-Za-z0-9-]*\]\]' --include=*.md . | sort -u | tr -d '[]' \
  | while read n; do [ -f "reglas/$n.md" ] || echo "ROTO: $n"; done

# 2. Referencias numéricas residuales (deben ser a sección)
grep -rn '\]\] #[0-9]' --include=*.md .

# 3. Numeración rota dentro de cada archivo
for f in reglas/*.md; do awk -v F="$f" '/^[0-9]+\. /{n=$1+0; if(n<=p) print F" L"NR": "n" tras "p; p=n}' "$f"; done
```

La 3 avisa de dos falsos positivos conocidos y correctos: la lista de prioridades de `evolution-rules` §5 y la lista final de `99-EJEMPLO.md`, que son listas ordenadas independientes.

**Cuidado con las sustituciones masivas con `sed`/`printf`**: un `\1` en una cadena de `printf` se interpreta como carácter de control y se come el carácter siguiente. Ya pasó, en 65 sitios a la vez. Si haces un reemplazo en lote, verifica una muestra **y** busca caracteres de control antes de dar nada por bueno.

## Tono

Las reglas se escriben en imperativo impersonal ("se valida", "no se commitea"), en español, y explicando el coste real de incumplirlas. Nada de "es recomendable" ni "sería bueno": si no es obligatorio, no es una regla — es un recordatorio, y va en la sección de recordatorios.
