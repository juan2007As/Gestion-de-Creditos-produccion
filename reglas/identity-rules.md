# Reglas de Identidad, Sesiones y Permisos (Gestión de Créditos)

> Este proyecto usa el sistema de autenticación nativo de Django + un RBAC propio (`Rol`/`Permiso`/`RolPermiso`/`UsuarioProfile`). El RBAC propio fue una decisión sin motivo técnico sólido (ver `CONTEXTO.md`) — no se reescribe solo por eso, pero tampoco se expande sin evaluar si los permisos nativos de Django ya alcanzarían.

## Decisión de negocio confirmada: sin aislamiento por operario

**Todos los operarios ven y editan todos los clientes/préstamos, a propósito.** No es un hueco de seguridad: es la regla real del negocio con hasta 10 usuarios de confianza (confirmado por el dueño en la Fase A3/A4). Los decoradores `valida_propiedad_cliente`/`valida_propiedad_prestamo` que simulaban lo contrario se retiraron porque además nunca funcionaron (`Cliente`/`Prestamo` no tienen campo de dueño). **No reintroducir un control de este tipo sin que el dueño lo pida explícitamente de nuevo.**

## 1. Autenticación

1. Se resuelve en un único punto: `mi_app.utilities.decorators.obtener_profile()` + el sistema de auth nativo de Django. No crear una segunda forma de "saber quién eres".
2. Contraseñas: hash nativo de Django (PBKDF2) — no tocar.
3. **Rate limiting en login: ya existe.** `login_view` (`views_core.py:41`) lleva `@ratelimit(key='ip', rate='5/m', method='POST', block=True)`.
4. **MFA en cuentas administrativas: decisión consciente de no implementar por ahora.** `/admin/` solo pide usuario+contraseña — aceptado como deuda (cajón 4), no es un descuido: es una cuenta única con password aleatoria fuerte, y MFA real es una feature no trivial (dependencia nueva, migración, flujo de login nuevo).

## 2. Sesiones

5. `SESSION_COOKIE_AGE`/`SESSION_EXPIRE_AT_BROWSER_CLOSE` sin definir explícitamente — rige el default de Django (2 semanas). Deuda cajón 2.
6. Las cookies de sesión ya llevan `SESSION_COOKIE_SECURE=True` en producción (`settings.py`).
7. Cambiar la contraseña debería invalidar sesiones existentes — no se confirmó si el flujo de cambio de contraseña de este proyecto lo hace (Django lo soporta nativamente vía `update_session_auth_hash`, pendiente de verificar que se use). Deuda cajón 3.

## 3. Autorización y modelo de permisos (RBAC real de este proyecto)

8. El modelo vive en `Rol`/`Permiso`/`RolPermiso` — tres roles: `ADMIN`, `GERENTE`, `OPERARIO`. Decoradores: `@require_rol`, `@require_permission`, `@require_any_permission`, `@admin_required`, `@gerente_o_admin`, `@no_operario_solamente` (`mi_app/utilities/decorators.py`).
9. `obtener_profile()` consulta la base en cada request (`get_or_create`) sin caché, y **crea automáticamente** un `UsuarioProfile` con rol `OPERARIO` por defecto si un usuario autenticado no tiene uno. Comportamiento silencioso a tener en cuenta al depurar permisos raros.
10. **Denegar por defecto**: toda vista de negocio nueva lleva `@login_required` + `@require_permission`/`@require_rol` explícito. Un endpoint sin ninguno de los dos se sirve abierto — ya pasó con `api_cuota_mora_actual` (`views_core.py:6093`), que solo tiene `@login_required`, sin `@require_permission`. Revisar si eso es intencional o deuda al tocarlo.
11. **Escalada de privilegios**: `UsuarioProfileAdmin` (`mi_app/admin.py:534`) permite a cualquier `is_staff` con permiso Django cambiar el `rol` de otro usuario, sin control de auto-escalado. No explotable hoy (un solo admin), pero si se da acceso de `/admin/` a un segundo operario, revisar esto primero. Deuda cajón 2.
12. **Autorización a nivel de recurso concreto** sigue aplicando para lo que SÍ varía por rol (ej. `@admin_required` en vistas de configuración) — la ausencia de aislamiento por operario es solo sobre "quién ve qué cliente", no sobre "quién puede hacer qué acción".

## 4. Ciclo de vida de la cuenta

13. No hay vista propia para activar/desactivar un operario — depende del `UserAdmin` genérico de Django (`is_active`). Deuda cajón 2, funcional pero informal a este tamaño de equipo.
14. El primer superusuario se crea por `build.sh` en cada deploy si no existe uno, con password generada al azar (ya corregido en la Fase A4 — antes era `Admin123!` fija).

## Antes de dar por cerrada cualquier tarea que toque identidad o permisos

- ¿Se comprobó `@require_permission`/`@require_rol` en la vista nueva, o solo `@login_required`?
- ¿Esta acción sensible queda registrada en `HistorioCambios`/`AuditLog`?
- ¿Estoy por reintroducir un control de "esto es tuyo" que el negocio ya descartó explícitamente?
- ¿Hay algún permiso nuevo abierto por defecto en vez de denegado por defecto?
