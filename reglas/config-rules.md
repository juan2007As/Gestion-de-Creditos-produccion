# Reglas de Configuración y Secretos (Gestión de Créditos)

> Este proyecto **no usa feature flags** (confirmado, `DEUDA-TECNICA.md`) — esa sección se omite. `CREDITS_CONFIG` (límites de monto, tasa de interés, etc.) son parámetros de negocio, no flags.

## 1. Configuración

1. **La configuración se valida al arrancar** — ya está: `SECRET_KEY`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` usan `config('X')` sin default en `settings.py`, y Django no arranca si faltan en producción.
2. Se lee centralizada en `proyecto_john/settings.py` vía `python-decouple` — no leer `os.environ` directo desde otro archivo.
3. **Ningún valor por defecto inseguro en producción** — ya está (el `SECRET_KEY` de desarrollo con default solo aplica en `ENVIRONMENT=local`).
4. `.env.example`, `config/local.env.example` y `config/pythonanywhere.env.example` deben actualizarse en el mismo commit que introduce una variable nueva. **Nota**: `config/pythonanywhere.env.example` es legado (genera config de MySQL, ya no aplica con Render+Postgres) — no agregar variables nuevas ahí, considerar retirarlo (`DEUDA-TECNICA.md` cajón 3).
5. El código no debe preguntar "¿en qué entorno estoy?" para decidir qué calcula (interés, mora) — solo para decidir a qué servicio conectarse. Ya se cumple: `ENVIRONMENT` decide DB/email/logging, no lógica de negocio.

## 2. Secretos

6. **Ningún secreto en el repositorio.** Caso real y activo: la API key de Comfama en `lambda/` (ya retirada del working tree, sigue en el historial de `origin/main` — ver [[git-rules]]).
7. **Escaneo automático activo desde la Fase A4**: `.pre-commit-config.yaml` (detect-secrets) + job `secrets-scan` en `.github/workflows/tests.yml`. Un hallazgo nuevo se audita (real o falso positivo) antes de forzar el commit — nunca con `--no-verify` sin mirar cuál de los dos es.
8. **Procedimiento ante filtración** (aplica ahora mismo a la key de Comfama):
   1. **Revocar primero** — avisar a Comfama para rotar la key. Acción del dueño, no de la IA.
   2. Emitir y desplegar la nueva (si la integración se retoma).
   3. Auditar qué se hizo con la key expuesta durante el periodo de exposición — no verificado en esta adopción.
   4. Limpiar el historial de git (force-push) — **último**, y solo con aprobación explícita separada; no reduce el riesgo si no se revocó antes.
9. Rotación periódica de `SECRET_KEY`/credenciales de DB/email: no hay proceso formal — aceptado como cajón 2 a este tamaño de equipo (rotar si se sospecha compromiso, no en calendario fijo).

## 3. Parámetros de negocio

10. `CREDITS_CONFIG` (`MAX_LOAN_AMOUNT`, `MIN_LOAN_AMOUNT`, `DEFAULT_INTEREST_RATE`, `MAX_PAYMENT_DAYS`) ya vive en configuración editable por entorno, no hardcodeada — correcto.
11. Cambiar `DEFAULT_INTEREST_RATE` no debe recalcular préstamos ya creados con la tasa anterior — verificar que los servicios de préstamo (`prestamo_service.py`) guardan la tasa aplicada en el momento, no la releen de `CREDITS_CONFIG` después.

## Antes de dar por cerrada cualquier tarea que toque configuración

- ¿Añadí una variable nueva? ¿Está en `.env.example`, validada al arrancar?
- ¿Hay algún secreto que pueda acabar en un log, una URL o una respuesta de error?
- ¿Quién más lee esta configuración que estoy cambiando? (`render.yaml`, los tres `.env.example`)
