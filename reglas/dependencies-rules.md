# Reglas de Dependencias (Gestión de Créditos)

> `requirements.txt` es el lockfile de este proyecto (no hay contenedores, no hay imágenes que fijar por separado).

## 1. Antes de añadir una dependencia

1. Evaluar antes de instalar: ¿resuelve algo real?, ¿está mantenida?, ¿qué arrastra? Caso real ya identificado: `Pillow` y las tres dependencias de `google-auth-*` estaban declaradas sin uso real en `mi_app/` (las de Google solo las usa `scripts/backup_manager.py`, fuera del path de la app desplegada) — `Pillow` se retiró en la Fase A4 por no tener ni un solo uso en todo el repo.
2. **Nunca instalar un nombre de paquete sin verificar que es el proyecto real** — especialmente relevante trabajando con asistencia de IA.

## 2. Fijado de versiones — ya resuelto en la Fase A4

3. **`requirements.txt` tiene TODAS las versiones fijadas** desde la Fase A4 (antes solo `Django` y `django-ratelimit` lo estaban). Cualquier dependencia nueva se agrega con `==versión`, nunca sin pin.
4. Runtime fijado en `runtime.txt` (Python 3.10.12) — mantener el CI corriendo al menos una vez contra esa misma versión (ya corregido: matrix incluye 3.10).

## 3. Vulnerabilidades y actualización

5. Escaneo automático activo desde la Fase A4: `safety check` bloqueante en CI.
6. **Django 4.2.11 → 4.2.30** en la Fase A4: corrigió 36 de 42 CVEs conocidas, incluida una inyección SQL real (CVE-2025-57833) sin parchear. Las 6 restantes solo se corrigen subiendo a Django 5.2.15+ — salto de versión mayor, requiere su propio plan de migración y pruebas (`DEUDA-TECNICA.md` cajón 2 #15), no se hace de pasada.
7. Django 4.2 LTS sigue soportado — no está fuera de soporte, pero no tiene cadencia de actualización calendarizada. Revisar con `safety check -r requirements.txt` cada cierto tiempo (ver [[operations-rules]] §6 Mantenimiento).
8. Una actualización mayor (como el eventual salto a Django 5.x) se hace sola, no mezclada con otros cambios, para saber qué rompió qué si algo rompe.

## Antes de añadir o actualizar cualquier dependencia

- ¿Comprobé que el paquete existe y es el correcto?
- ¿Tiene versión fijada en `requirements.txt`?
- ¿Corrí `python manage.py test mi_app` después de actualizar? (mismo resultado esperado: sin regresiones sobre los 8 failures/25 errors preexistentes ya documentados)
- ¿Esta dependencia nueva se usa de verdad en `mi_app/`, o solo en un script suelto de `scripts/`?
