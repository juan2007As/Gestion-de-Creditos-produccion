# Reglas de Integración Continua y Despliegue (Gestión de Créditos)

> Paradigma: servicio que el dueño despliega y controla (Render). No aplica la sección de "clientes que no puedes actualizar" (móvil/SDK) — se omite.

## 1. Puerta de calidad automatizada — estado real tras la Fase A4

1. El pipeline (`.github/workflows/tests.yml`) ejecuta: tests (job `tests`, matrix Python 3.10/3.12), linting (no bloqueante salvo errores de sintaxis), `bandit` (bloqueante, severidad media+), `safety` (bloqueante, con 6 CVEs de Django 5.2.x ignoradas explícitamente hasta esa migración mayor), y `secrets-scan` (bloqueante).
2. `quality-gate` depende de `tests`, `linting`, `security` y `secrets-scan`, y falla de verdad si `tests`, `security` o `secrets-scan` fallan — corregido en la Fase A4 (antes solo miraba `tests`).
3. **Resuelto**: `render.yaml` tiene `autoDeploy: false`. El job `deploy` en `tests.yml` llama al Deploy Hook de Render (`secrets.RENDER_DEPLOY_HOOK_URL`) solo si `quality-gate` pasó y solo en push a `main`. Si el secret falta, el job falla con un mensaje explícito en vez de fallar en silencio.
4. Un test intermitente se arregla o se retira, no se reintenta a ciegas — los tests E2E ya están marcados `|| true` a propósito (necesitan Selenium, no configurado), documentado, no oculto.

## 2. Artefacto y despliegue

5. El despliegue es reproducible: `build.sh` + `render.yaml`, en el repositorio, no comandos sueltos que solo el dueño recuerda.
6. **Camino de vuelta**: Render permite volver a un deploy anterior por su propio mecanismo. Con solo 2 migraciones y sin patrón expandir/migrar/contraer documentado, un rollback de código después de una migración de datos no tiene camino de vuelta pensado — evaluarlo caso a caso antes de una migración grande.
7. Tras cada despliegue, revisar el Log de Render un momento — no hay observabilidad automática todavía (ver [[observability-rules]]).

## 3. Migraciones y despliegue

8. El orden migración↔código: `build.sh` intenta `migrate` en el build; si la DB no está lista, falla en silencio (`|| echo AVISO`) y el deploy sigue igual. Esto ya causó el 500 de login investigado al inicio de esta adopción — riesgo real, no teórico.
9. Antes de cualquier migración sobre producción: confirmar que `.github/workflows/backup.yml` corrió exitosamente y restauró (ver [[data-rules]] §5).

## 4. Legado a limpiar

10. `PYTHONANYWHERE_COMANDOS.txt` (autogenerado por `prepare_production.py`) y `DEPLOY.md` son de una plataforma de despliegue que ya no se usa (decisión deliberada del dueño: Render por facilidad/tier gratis). `prepare_production.py` genera config de MySQL, desalineada con `settings.py` (que solo soporta Postgres en producción). Deuda cajón 3 — limpiar al tocar despliegue de nuevo.
11. Existe una rama sin mergear (`fix/production-readiness-...`, de otra sesión de IA) que borra `render.yaml`/`build.sh` — no se toca sin decisión explícita del dueño.

## Antes de dar por cerrado cualquier cambio en el proceso de release

- ¿El pipeline realmente valida lo que creo que valida?
- ¿Se puede revertir este despliegue? ¿Y la migración de datos que lleva dentro?
- ¿Hay algo aplicado en producción que no exista en el repositorio?
- ¿La última corrida de `backup.yml` pasó antes de tocar producción?
