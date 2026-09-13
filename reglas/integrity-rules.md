# Reglas de Integridad — Impacto Cruzado (Gestión de Créditos)

> Principio central: nada se cambia de forma aislada. Especialmente crítico aquí porque `mi_app/views_core.py` concentra 6000+ líneas de lógica de vistas — casi cualquier función se puede estar usando desde más de un sitio sin que se note a simple vista.

## Protocolo obligatorio antes de cualquier cambio no trivial

1. **Buscar todos los usos/dependientes** con `grep`/búsqueda real antes de modificar una función, decorador, modelo o variable de entorno.
2. **Clasificar el radio del cambio** (ver [[00-CORE]] §5): Local / Módulo / Cruzado.
3. **Explicar el plan en términos concretos**: "esto cambia X, que usan Y y Z".
4. Tras el cambio, **verificar que los dependientes siguen funcionando** — correr `python manage.py test mi_app` como mínimo (hoy hay 8 failures/25 errors preexistentes ya documentados en `DEUDA-TECNICA.md`; un cambio no debe sumar más).

## Casos específicos de alto riesgo en este proyecto

5. Cambiar la forma de un endpoint (`buscar_cliente`, `lista_clientes_api`, `api_cuota_mora_actual`) — aunque no tengan contrato formal, revisar el JS que los consume en los templates.
6. Cambiar el esquema de datos — revisar migraciones. Recordar: solo hay 2 migraciones para 17 modelos, y no está confirmado que el estado de la Postgres de Render coincida exactamente con este historial.
7. Renombrar o mover algo dentro de `views_core.py`, `services/` o `utilities/` — revisar todos los imports (`views/__init__.py` hace `from mi_app.views_core import *`, así que un renombrado ahí se propaga silenciosamente).
8. Cambiar una variable de entorno de `settings.py` — revisar `render.yaml`, `.env.example` y los tres archivos legado de PythonAnywhere que todavía la puedan referenciar.
9. **Cambiar una regla de negocio o un cálculo de dinero** (interés, mora, cuotas) — revisar qué pasa con préstamos ya creados bajo la regla anterior. Caso real ya encontrado: `Cuota.total_a_pagar()` y `CuotaRapida.total_a_pagar()` deberían calcular lo mismo y divergieron sin que nadie lo notara — exactamente el escenario que esta regla previene.
10. **Cambiar quién puede hacer algo** (`Rol`/`Permiso`/`RolPermiso`) — revisar a quién se le abre y a quién se le cierra el acceso, incluidos los usuarios que ya existen.
11. Eliminar código "que parece no usarse" — confirmar con búsqueda real. Ya hubo un caso de esto en la auditoría: los decoradores `valida_propiedad_cliente`/`valida_propiedad_prestamo` parecían protección real y eran un no-op; se retiraron solo tras confirmar con el dueño que la regla de negocio no existía.

## Lo que la búsqueda en el código no encuentra

12. El chequeo de dependientes no se limita a este repositorio. La carpeta `lambda/` (ya retirada) demostró que puede haber código relacionado fuera del control de Django. Si en el futuro se conecta algo externo de nuevo, se agrega a esta lista.

## Señal de alarma

Si para responder "¿esto rompe algo más?" la única respuesta es "no debería" sin haber buscado — falta el paso 1.
