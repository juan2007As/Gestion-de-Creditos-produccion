# Reglas de Operación, Incidentes y Continuidad (Gestión de Créditos)

> Bus factor de 1 confirmado en `CONTEXTO.md`: el dueño es la única persona que sostiene y administra el proyecto. Varias reglas de esta plantilla asumen un equipo — se adaptan a lo que aplica de verdad con una sola persona, sin fingir un proceso de guardia que no existe.

## 1. Estado del sistema

1. **No existe health check** (`/health`, `/ping`). Render solo detecta "vivo" por respuesta de puerto, no por la DB realmente accesible. Deuda cajón 2.

## 2. Runbook

2. **No existe un runbook escrito.** `DEPLOY.md` es genérico y está desactualizado, no cumple esa función. Al menos debería cubrir: cómo revertir un deploy en Render, cómo restaurar el backup (`.github/workflows/backup.yml` documenta el mecanismo, falta un paso a paso en prosa), y a quién avisar si Comfama pregunta por la key retirada. Deuda cajón 2.

## 3. Incidentes

3. Con una sola persona operando, "coordinación entre varios" no aplica — pero **mitigar primero, entender después** sigue aplicando igual: si algo se rompe en producción, revertir/desactivar antes de investigar la causa raíz.
4. Anotar lo que se toca mientras se toca un incidente, aunque sea una sola persona — la memoria reconstruye mal incluso para uno mismo.

## 4. Accesos y bus factor

5. **Inventario de accesos real**: Render (hosting + DB), GitHub (repo), y el dashboard de Render como único punto de configuración de secretos. Todo hoy solo lo tiene el dueño — bus factor de 1, aceptado explícitamente, no es una deuda a "arreglar" salvo que el dueño quiera sumar a alguien.
6. MFA en GitHub y Render: no verificado desde esta adopción — el dueño debería confirmarlo directamente en cada dashboard.

## 5. Continuidad: lo que caduca en silencio

7. Certificado TLS: gestionado por Render automáticamente, no requiere vigilancia propia.
8. La API key de Comfama (ya retirada del código) no tiene vigilancia de caducidad — ya no aplica, salvo que se retome esa integración.
9. **RTO real de este proyecto**: lo que tarde en correr `.github/workflows/backup.yml` restaurando contra una base vacía — visible en la pestaña Actions de GitHub. Antes de la Fase A4 no existía ningún backup funcional para Postgres, así que el RTO real era "infinito".

## 6. Mantenimiento planificado

10. Tareas recurrentes conocidas: `auto_mantenimiento.py` (auto-tagging de lista negra, etiquetas de cliente, sincronización de estados de cuotas) — **no tiene monitoreo de última ejecución exitosa**, y no está confirmado si corre en algún cron real o si depende de que el dueño lo ejecute a mano. Deuda cajón 2.
11. Backup diario ya calendarizado (`backup.yml`, cron `0 7 * * *`).
12. Pendiente de calendarizar: revisión de accesos, rotación de `SECRET_KEY` si se sospecha compromiso, actualización de dependencias (recordatorio: `requirements.txt` ya tiene lockfile real desde la Fase A4, revisar cada tanto si hay CVEs nuevas con `safety check`).

## Antes de dar por cerrada cualquier tarea con impacto operativo

- Si esto falla a las 3 de la madrugada, ¿el dueño se entera, o solo si un operario se queja al día siguiente?
- ¿He introducido algo que dependa de un servicio externo sin plan de qué pasa si falla?
- ¿La última corrida de `backup.yml` pasó?
