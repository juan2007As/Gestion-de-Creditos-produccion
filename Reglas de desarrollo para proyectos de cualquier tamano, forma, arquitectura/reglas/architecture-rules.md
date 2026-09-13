# Reglas de Arquitectura

> Plantilla base. Al generarse para un proyecto real, reflejar la arquitectura concreta elegida en la Fase 2 (monolito modular, microservicios, serverless, etc.) con un diagrama o descripción de módulos/servicios reales.

## Principios no negociables

1. **La arquitectura debe justificarse por el tamaño real del proyecto, no por moda.** Un proyecto pequeño con microservicios es tan un error como un proyecto masivo forzado en un monolito sin módulos claros. Cualquier propuesta de cambio arquitectónico se justifica contra necesidad real, no "porque así se hace ahora".
2. **Límites de módulo/servicio explícitos y respetados.** Cada módulo tiene una responsabilidad clara documentada. Un módulo no accede directamente a las tablas internas de otro — pasa por su interfaz/API pública.
3. **Dependencias en una sola dirección donde sea posible.** Evitar dependencias circulares entre módulos — si aparecen, es señal de que el límite de responsabilidad está mal trazado y hay que replantearlo, no forzarlo con un parche.
4. **Configuración fuera del código.** Secrets, URLs de entorno, feature flags: nunca hardcodeados — siempre vía variables de entorno o sistema de configuración, con un `.env.example` documentado.
5. **Un solo lugar de verdad para cada tipo de dato o regla de negocio.** Si una regla de validación o cálculo se necesita en dos sitios, se extrae a un lugar compartido — no se duplica "por rapidez".

## Evolución de la arquitectura

6. Todo cambio estructural grande (nuevo servicio, cambio de base de datos, cambio de patrón de comunicación) se documenta como decisión en `CONTEXTO.md` con el motivo — para que dentro de 6 meses se entienda por qué se hizo así.
7. Antes de añadir una nueva dependencia externa (librería, servicio de terceros), evaluar: ¿resuelve algo que no se puede resolver razonablemente sin ella?, ¿está mantenida?, ¿qué pasa si desaparece?
8. Preferir composición y módulos simples sobre abstracciones genéricas tempranas ("por si acaso se necesita para otra cosa"). Una abstracción se introduce cuando ya hay 2-3 casos reales que la piden, no antes.
9. **[P2]** Una arquitectura no se elige solo por cómo funciona, sino por **cuánto cuesta operarla y quién va a hacerlo**. Diez servicios necesitan diez despliegues, diez conjuntos de logs, diez cadenas de alertas y trazado distribuido para depurar cualquier cosa. Si el equipo no puede sostener esa carga, la arquitectura correcta es otra ([[operations-rules]]).
10. **[P2]** Cada frontera de servicio o de proceso es una llamada que puede fallar, tardar o llegar dos veces. Toda comunicación entre componentes que cruce la red se diseña con timeout, reintento y comportamiento definido ante fallo ([[api-rules]] sección 4).
11. **[P2]** Está declarado qué componentes son **críticos** (si caen, el producto no funciona) y cuáles permiten degradación. Sin esa distinción, todo se trata igual y nada se protege bien.
12. **[P2]** El coste de infraestructura es una restricción de diseño desde el principio, no un descubrimiento de la primera factura.

## Documentación y conocimiento

13. El `README` permite a alguien nuevo **levantar el proyecto y ejecutar los tests** sin preguntarle nada a nadie. Si hace falta un paso que solo alguien conoce, ese paso falta en el README, y se comprueba de verdad en una máquina limpia de vez en cuando.
14. **[P1]** Las decisiones estructurales se registran con su **motivo y las alternativas descartadas** (en `CONTEXTO.md` o en documentos de decisión). Dentro de seis meses, "por qué no se hizo de la otra forma" es más valioso que "qué se hizo": sin ese registro, alguien deshará la decisión sin saber qué problema resolvía.
15. **[P1]** Existe un diagrama mínimo actualizado de los componentes reales y cómo se comunican. Un diagrama desactualizado se corrige o se borra; no se deja mintiendo.
16. **[P2]** Ningún conocimiento crítico vive únicamente en la cabeza de una persona. Ver [[operations-rules]] sección 5.

## Antes de aprobar un cambio arquitectónico

- ¿Este cambio resuelve un problema real y actual, o es especulativo?
- ¿Qué módulos/servicios existentes se ven afectados?
- ¿Introduce una dependencia circular o un acoplamiento nuevo no deseado?
- ¿Quedó documentada la decisión y el motivo?
- **[P2]** ¿Quién va a operar esto, y tiene la capacidad de hacerlo?
- **[P2]** ¿Qué pasa cuando esta nueva pieza falle o esté lenta?
