# Reglas de Observabilidad y Manejo de Errores (Gestión de Créditos)

> **Estado real, decisión explícita del dueño**: hoy no hay registro de errores que sobreviva ni ninguna alerta. Se decidió diferirlo, no implementarlo en la Fase A4 — sigue como deuda cajón 1 en `DEUDA-TECNICA.md`, con la decisión de *cuándo* ya tomada, no el riesgo reducido.

## 1. Manejo de errores

1. Ningún error se muestra crudo al usuario — `DEBUG=False` en producción ya lo garantiza a nivel de Django, pero hay excepciones puntuales sin capturar (ej. `pagar_cuota_especifica`, `views_core.py:1386-1388`, un `Decimal` inválido revienta sin `try/except`). Al tocar una vista, capturar y devolver un mensaje entendible.
2. **Un error no se convierte en un valor vacío.** No devolver una lista vacía o un `None` cuando la operación de negocio falló.

## 2. Logs — estado real

3. `settings.py` define `LOGGING` solo en producción, escribiendo a `logs/django_error.log` (`FileHandler`, nivel `ERROR`). **Render usa filesystem efímero en el plan gratuito** — ese archivo probablemente no sobrevive a un redeploy/restart, y Render solo captura stdout/stderr en su panel de Logs, no un `FileHandler` a disco.
4. Nunca contraseñas, tokens o cédulas completas en logs — el middleware de auditoría (`mi_app/auditoria.py`) ya excluye `password`/`csrfmiddlewaretoken` del payload capturado; no aflojar eso al tocarlo.

## 3. Cuando se decida implementar esto (queda como referencia, no como tarea abierta ahora)

5. La opción más simple y ya evaluada con el dueño: `mail_admins` nativo de Django al primer 500 (reutiliza el `EMAIL_HOST` que ya está configurado, cero cuentas nuevas).
6. La opción más completa: Sentry (plan free), requiere que el dueño cree la cuenta y pase el DSN — la IA deja el código listo, no crea la cuenta.
7. Job de mantenimiento (`auto_mantenimiento.py`) no tiene monitoreo de "última ejecución exitosa" — si deja de correr, nadie se entera (silencio, no error). Si se implementa observabilidad, esto entra primero.

## Antes de dar por cerrada una tarea que puede fallar en producción

- Si esto falla en producción hoy, ¿me entero yo, o solo si un operario se queja? (Hoy: solo si se queja.)
- ¿El mensaje que ve el usuario es claro, o se cuela un error técnico crudo?
- ¿Hay algún catch silencioso que debería al menos loguear?
