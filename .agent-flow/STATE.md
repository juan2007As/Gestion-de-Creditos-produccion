# Estado operativo

> **2026-10-13, actualizacion final**: commit `62aa360` pusheado a `origin/main` (ver HISTORY.md para el detalle completo del commit, la verificacion de backup previa, y el hallazgo de que `origin` no tiene rama `master`). CI/CD en curso o recien terminado en GitHub Actions -- pendiente de que la duena confirme que el pipeline y el deploy en Render quedaron en verde.


- Tarea: Plan de acción de seguridad completo (auditoría "desde base de datos hasta protección general", 2026-10-13) -- Tier 0, Tier 1 y Tier 2, más 2 hallazgos menores encontrados de paso. Detalle completo de cada punto en HISTORY.md.
- Objetivo: cerrar los huecos de infiltración/exposición de datos confirmados por auditoría, sin tocar producción ni dinero.
- Estado: **terminado**. Todo lo acordado está implementado y verificado (resumen completo en el mensaje final al dueño). Los últimos 2 puntos tocados hoy (DEUDA-TECNICA #22bis/#22ter) resultaron, tras verificar, NO ser bugs reales:
  - **#22bis (ratelimit de backup sin block=True)**: RETRACTADO. Se verificó con un test (desactivando el cambio temporalmente) que `django-ratelimit==4.1.0` (el instalado) ya tiene `block=True` como default -- las 3 vistas de backup SIEMPRE bloquearon bien. Se dejó `block=True` explícito de todas formas (no hace daño, documenta intención), pero no corregía ningún hueco real.
  - **#22ter (emoji en logger.warning)**: severidad corregida. Se verificó con una prueba aislada (`python -I`, logger fuera de Django/colorama) que `logger.warning()` con emoji NO revienta como sí lo hace `print()` -- el módulo `logging` de Python atrapa el error de codificación internamente (`Handler.handleError()`) y nunca propaga la excepción. El riesgo real era más chico de lo que se documentó inicialmente: el mensaje se habría perdido/reemplazado por un aviso genérico en vez de crashear. Se quitó el emoji igual (gratis, mejora la señal en logs).
  - Ambas correcciones de severidad están documentadas explícitamente en `DEUDA-TECNICA.md` #22bis/#22ter como autocorrecciones -- se presentaron inicialmente como "hallazgos nuevos" sin haberlos verificado todavía, y se corrigieron el mismo día al intentar implementar el fix.
- Editor activo: ninguno.
- Última confirmación humana del editor: "Vamos con esos dos hallazgos, lo otro queda anotado" -- confirmando arreglar #22bis/#22ter.
- Archivos tocados en este último paso: `mi_app/views_core.py` (`block=True` explícito en 3 `@ratelimit` de backup), `mi_app/utilities/middleware.py` (emoji quitado de `logger.warning` en `RateLimitMiddleware`), `mi_app/tests/test_backup_rapido_ratelimit.py` (nuevo, 3 tests), `mi_app/tests/test_ratelimit_middleware_logging.py` (nuevo, 1 test), `DEUDA-TECNICA.md` (#19/#22bis/#22ter corregidos).
- Verificación final: suite completa en 346 tests, 7 failures + 16 errors + 3 skipped -- exactamente el baseline histórico conocido, cero regresiones introducidas por ningún cambio de toda la sesión.
- Intentos fallidos: 0 (las 2 autocorrecciones no fueron intentos fallidos de implementación -- el código se implementó bien a la primera; lo que se corrigió fue la severidad/certeza de la documentación del hallazgo, verificando antes de dar algo por bueno).
- Bloqueo: ninguno.
- Nada commiteado todavía (convención del proyecto: solo se commitea cuando el dueño lo pide explícitamente).
- **Con esto se da por cerrado TODO el plan de acción de seguridad de esta sesión** (Tier 0 + Tier 1 + Tier 2 + los 2 hallazgos menores). Pendientes que NO son parte de este plan, a criterio del dueño para otra sesión:
  - Vigilar el primer deploy real con los cambios de #5 (sslmode), #6 (HSTS) y #20 (CSP) antes de darlos por confirmados en producción viva.
  - Subir gradualmente `SECURE_HSTS_SECONDS` en despliegues futuros (hoy en 1 hora, deliberadamente conservador).
  - CSP estricto (sin `'unsafe-inline'`) requeriría un refactor aparte de ~15 templates para sacar scripts/estilos/handlers inline.
  - Resto de `DEUDA-TECNICA.md` cajón 2 (versión de Django, pin de dependencias, healthcheck, runbook, legado de PythonAnywhere, etc.) -- deuda técnica general, no hallazgos de la auditoría de seguridad, nunca se acordó abordarla en este plan.

Estados permitidos: pendiente / en progreso / pausado / bloqueado / terminado.
Editor permitido: Codex / Claude Code / ninguno.
