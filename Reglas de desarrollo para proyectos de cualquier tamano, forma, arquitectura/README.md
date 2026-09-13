# Reglas de desarrollo

Un conjunto de reglas para plantear, construir y mantener proyectos de software **de cualquier tipo, tamaño y arquitectura** — no solo para que funcionen de cara al usuario, sino para que se puedan operar, auditar y sostener en el tiempo.

Está escrito para que lo lea una IA y trabaje con él, pero se entiende igual leyéndolo una persona.

---

## Las dos puertas de entrada

| Si vas a… | Empieza por |
|---|---|
| **Arrancar un proyecto nuevo** (no hay código todavía) | [`00-planteamiento-protocol.md`](00-planteamiento-protocol.md) |
| **Entrar a un proyecto que ya existe** (con o sin documentación) | [`01-adopcion-protocol.md`](01-adopcion-protocol.md) |

Ambos terminan en el mismo sitio: un proyecto con su `CONTEXTO.md`, su carpeta `reglas/` especializada, y su `DEUDA-TECNICA.md` viva.

## Qué hay dentro

- **[`reglas/`](reglas/)** — el conjunto completo. Empieza por [`reglas/README.md`](reglas/README.md), que es el índice.
- **[`plantilla-CLAUDE.md`](plantilla-CLAUDE.md)** — el archivo que se copia al proyecto generado para que las reglas se carguen solas en cada sesión. Sin esto, el resto depende de que alguien se acuerde de mirar.

## Cómo está organizado

Son ~1.900 líneas, y nadie aplica trescientas reglas por tarea. Por eso hay tres capas de atención:

1. **[`reglas/00-CORE.md`](reglas/00-CORE.md)** — una página. Lo único que se lee siempre.
2. **[`reglas/01-DISPARADORES.md`](reglas/01-DISPARADORES.md)** — tabla de enrutamiento: "vas a hacer X, lee Y". Se consulta antes de cada tarea.
3. **El resto** — referencia, se abre cuando la capa 2 lo indica.

Más dos transversales: [`02-AUTOMATIZABLE.md`](reglas/02-AUTOMATIZABLE.md) (qué debe verificar una máquina en vez de la memoria de alguien) y [`99-EJEMPLO.md`](reglas/99-EJEMPLO.md) (una feature real recorriendo el conjunto entero — el mejor sitio para empezar si quieres ver cómo se usa esto).

## Escala por perfil

Las mismas reglas no valen para un experimento de fin de semana y para una plataforma de pagos. Cada regla lleva marcado el perfil mínimo en el que aplica — **P0** prototipo, **P1** interno, **P2** producto con usuarios reales, **P3** datos sensibles o dinero. El perfil se elige al plantear el proyecto y **no lo determina el tamaño del código, sino qué pasa si falla**.

## Sobre este repositorio

Los archivos de `reglas/` son **plantillas madre deliberadamente genéricas**. Los marcadores tipo `[STACK]` que verás son intencionados: se rellenan en la copia que se genera dentro de cada proyecto real, nunca aquí.

Si vas a modificar las reglas en sí, lee antes [`CLAUDE.md`](CLAUDE.md) — recoge las convenciones del repo y los errores que ya se han cometido una vez.
