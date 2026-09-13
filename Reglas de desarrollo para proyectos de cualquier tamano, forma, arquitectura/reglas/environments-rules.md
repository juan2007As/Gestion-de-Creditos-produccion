# Reglas de Entornos (Local / Test / Staging / Producción)

> Principio central: **producción es la única fuente de verdad.** Todo lo demás (local, test, staging) es una aproximación al servicio de desarrollar con seguridad — nunca al revés.
>
> Perfil mínimo: **P0**. Las reglas marcadas `[P1]`/`[P2]`/`[P3]` aplican desde ese perfil (ver [[README]]). El mecanismo de despliegue está en [[release-rules]]; la configuración por entorno, en [[config-rules]].

## Jerarquía de entornos

1. Producción manda. Si hay una discrepancia entre lo que dice el código en local/staging y lo que realmente pasa en producción (datos, comportamiento, configuración), se investiga por qué producción difiere — no se asume que producción está "desactualizada" y se ignora.
2. Los datos fluyen en un solo sentido por defecto: de producción hacia entornos inferiores (anonimizados/sanitizados si son sensibles, ver [[security-rules]] y [[data-rules]]), nunca al revés. Nunca se sube a producción un dato, config o "arreglo rápido" que solo se probó y decidió en local sin pasar por el flujo normal.
3. Ningún cambio de configuración, esquema de datos o infraestructura se considera "hecho" hasta que está aplicado (o con plan claro de aplicarse) en producción — un fix que solo funciona en local no es un fix.
4. Si algo funciona en local/staging pero no en producción, el problema es del cambio, no del entorno de producción — se investiga la diferencia de entorno (variables, versiones, datos reales) como primera hipótesis.

## Diferencias esperadas y documentadas entre entornos

5. Toda diferencia intencional entre entornos (una API key de test vs real, un flag de debug activo solo en local, límites de rate distintos) se documenta explícitamente en `CONTEXTO.md` o en el `.env.example` — para que nunca se confunda con un bug.
6. Nunca debe haber diferencias de **lógica de negocio** entre entornos (si en local un descuento se calcula distinto que en producción, eso es un bug, no una feature de entorno).
7. **[P1]** **Paridad de entorno**: la versión del runtime, de la base de datos y de las dependencias es la misma en todos los entornos. La mayoría de los "en mi máquina funciona" son una diferencia de versión que nadie declaró.

## Ningún entorno inferior toca el mundo real

8. **[P1]** **Ningún entorno que no sea producción envía emails, SMS ni notificaciones a direcciones reales.** Se usa un capturador de correo, una lista blanca cerrada de destinatarios internos, o el modo de prueba del proveedor. Esta regla se implementa como un bloqueo técnico en el punto de envío, no como una advertencia en la documentación: es de los errores más frecuentes que existen, y el día que ocurre lo descubren tus clientes.
9. **[P1]** Lo mismo para todo efecto externo: cobros, envíos, publicaciones en redes, llamadas a APIs de terceros que hacen algo real. Los entornos inferiores usan siempre las credenciales de prueba del proveedor.
10. **[P1]** **Las credenciales de producción no existen en ninguna máquina de desarrollo.** Nadie "prueba una cosita rápida" apuntando a producción desde su portátil. Ver [[config-rules]] §2 Secretos.
11. **[P1]** Los datos que bajan de producción a entornos inferiores se **anonimizan antes de salir de producción**, no después de copiarlos. Un volcado con datos reales en el portátil de alguien ya es una brecha, aunque se anonimice más tarde. Ver [[data-rules]] §7 Operar sobre datos reales y [[compliance-rules]].
12. **[P2]** Los entornos inferiores no son públicos ni indexables, y tienen sus propias credenciales y aislamiento de red: un compromiso en staging no puede dar acceso a producción ([[security-rules]] §Superficie de red e infraestructura).

## Despliegues y cambios irreversibles

13. Todo cambio que toque producción de forma difícil de revertir (migración de datos, borrado, cambio de proveedor externo) se prueba primero en staging con datos representativos, y se confirma explícitamente con el usuario antes de aplicarlo en producción — ver el criterio de reversibilidad de [[evolution-rules]].
14. Backups o puntos de restauración se confirman que existen y son recientes antes de cualquier cambio riesgoso en producción — no se asume que "debe haber un backup". Y un backup que nunca se ha restaurado no cuenta ([[data-rules]] §5 Backups y recuperación).
15. Rollback: todo despliegue a producción debería tener un camino de vuelta conocido de antemano (versión anterior, migración reversible) — se piensa antes de desplegar, no después de que algo salga mal.
16. **[P2]** Un rollback de código no revierte una migración de datos. Antes de desplegar está claro si este cambio se puede deshacer de verdad o solo se puede arreglar hacia adelante ([[release-rules]] §4 Migraciones y despliegue).
17. **[P2]** Tras desplegar se **observa** el sistema real durante un rato antes de considerar el despliegue terminado ([[release-rules]] §3 Despliegue).

## Antes de dar por cerrado cualquier cambio que involucre entornos

- ¿Esto ya está validado contra el comportamiento/datos reales de producción, o solo contra una versión local idealizada?
- ¿Esta diferencia entre entornos es intencional y documentada, o es un descuido?
- ¿Si esto se despliega a producción y falla, hay forma clara de revertirlo?
- **[P1]** ¿Este código puede enviar algo al mundo real (email, cobro, notificación) desde un entorno que no es producción?
- **[P1]** ¿Estoy usando datos o credenciales reales fuera de producción?
