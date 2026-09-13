# Reglas de Seguridad (Gestión de Créditos)

> Perfil **P3**. Archivos hermanos: [[identity-rules]] (quién eres y qué puedes tocar), [[config-rules]] (secretos), [[dependencies-rules]] (código de terceros).
>
> Django ya cubre buena parte de esto por defecto (CSRF, escapado de templates, ORM parametrizado). Este archivo se centra en lo que Django **no** hace solo, y en el estado real de este proyecto.

## Principios no negociables

1. **Ningún secreto en el código ni el repositorio.** Ya hubo un caso real (API key de Comfama en `lambda/`) — ver [[config-rules]] §2.
2. **Toda entrada de usuario es hostil hasta que se demuestre lo contrario.** Validar en el servidor, nunca confiar solo en el formulario. Caso real ya encontrado: `pagar_cuota_especifica` parsea `Decimal(request.POST.get(...))` sin `try/except` → 500 crudo con datos de un pago (`DEUDA-TECNICA.md` cajón 1 #10).
3. **Autenticación y autorización son cosas distintas** — este proyecto usa `@login_required` + `@require_rol`/`@require_permission` ([[identity-rules]]). Recordar: no hay aislamiento por operario (decisión de negocio), pero sí debe haber rol/permiso correcto en cada vista nueva.
4. **Contraseñas nunca en texto plano** — Django hash por defecto (PBKDF2), no tocar eso.
5. **HTTPS siempre en producción** — ya configurado (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` en `settings.py`).
6. **Principio de menor privilegio.**

## Estado real de este proyecto (Fase A4/A5)

| Punto | Estado |
|---|---|
| Escaneo de secretos en pre-commit y CI | ✅ Activo desde la Fase A4 |
| Rate limiting en `login_view` | ✅ `@ratelimit(key='ip', rate='5/m', method='POST', block=True)` |
| `/admin/` con MFA o restricción adicional | ❌ Ruta por defecto, solo usuario+contraseña (cajón 1 #8) |
| Cabeceras de seguridad (`CSP`, `HSTS`, `X-Content-Type-Options`) | Parcial — `SECURE_*` de Django activos, sin `Content-Security-Policy` explícita |
| SAST (bandit) en el pipeline | ✅ Bloqueante desde la Fase A4 (severidad media+) |
| Escaneo de dependencias vulnerables (safety) | ✅ Bloqueante desde la Fase A4; Django parcheado de 42 a 6 CVEs conocidas |
| MFA en GitHub/Render | No verificado desde aquí — pendiente que el dueño lo confirme en cada dashboard |

## Validación de entrada

7. **Consultas parametrizadas siempre** — el ORM de Django ya lo hace; no usar `.raw()`/`extra()` con texto concatenado.
8. **Asignación masiva**: los `ModelForm` (`ClienteForm`, `PrestamoForm`) ya declaran campos explícitos — no cambiar a volcar `request.POST` directo sobre un modelo.
9. **Límites en listas**: `lista_clientes_api` devuelve todos los clientes sin paginar — no urgente hoy (10 usuarios, volumen bajo), pero no repetir el patrón en endpoints nuevos (`DEUDA-TECNICA.md` cajón 3).

## Archivos subidos por el usuario (importación de Excel)

10. `importar_excel` recibe archivos de clientes — validar tipo real (no solo extensión `.xlsx`) y tamaño máximo antes de procesarlos con `openpyxl`/`pandas`.
11. El archivo no se guarda con el nombre que envía el usuario si se persiste en disco.

## Sesiones y CSRF

12. CSRF ya activo vía middleware de Django (`CsrfViewMiddleware`) — no desactivar en ninguna vista nueva.
13. `SESSION_COOKIE_AGE`/`SESSION_EXPIRE_AT_BROWSER_CLOSE` no están definidos explícitamente — rige el default de Django (2 semanas). Deuda cajón 2, ver `DEUDA-TECNICA.md`.

## Superficie de red

14. La base de datos (Postgres en Render) no está expuesta más allá de lo que Render gestiona — no abrir el puerto públicamente "para debuggear".
15. El panel de admin y `/admin/` necesitan capa adicional (MFA, restricción por IP) antes de considerarse cerrado este punto — ver tabla de arriba.

## Cuando algo va mal

16. Un secreto expuesto se considera comprometido aunque "solo lo vimos nosotros": se revoca primero (avisar al proveedor si es de un tercero, como Comfama) y se limpia después.
17. Un fallo de seguridad detectado con datos de clientes de por medio se trata como incidente — ver [[operations-rules]].

## Antes de dar por cerrada cualquier tarea con superficie de seguridad

- ¿Hay algún dato sensible expuesto en logs, errores o URLs?
- ¿Se validó la entrada en el servidor?
- ¿Se verificó rol/permiso a nivel de vista, no solo que hay sesión?
- ¿Algún secreto quedó hardcodeado por accidente?
- ¿Qué es lo peor que puede hacer aquí un operario autenticado pero descuidado (no necesariamente malicioso, dado que no hay aislamiento entre ellos)?
