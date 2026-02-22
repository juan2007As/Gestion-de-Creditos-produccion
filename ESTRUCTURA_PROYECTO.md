# Estructura del Proyecto - Gestor de Préstamos

Estructura organizada del proyecto (actualizada Feb 2026).

---

## Raíz

```
proyecto_john/
├── manage.py              # Punto de entrada Django
├── requirements.txt       # Dependencias
├── .env.example           # Plantilla variables entorno
├── DEPLOY.md              # Guía de despliegue
├── ESTRUCTURA_PROYECTO.md # Este archivo
│
├── proyecto_john/         # Configuración Django (settings, urls, wsgi)
├── mi_app/                # Aplicación principal
├── scripts/               # Scripts de utilidad
│   ├── audit/             # Auditorías (antes audit_scripts/)
│   └── tools/             # Herramientas de desarrollo
├── tests/                 # Tests a nivel proyecto
├── docs/                  # Documentación
├── config/                # Configuración (gunicorn, etc.)
│
├── "plan y accion/"       # Reglas y planes de desarrollo
├── "Archivos de desarrollo/"  # Docs técnicos
├── pruebas_humano/        # Material testing manual
│   ├── scripts/           # Scripts de verificación (paso 10, etc.)
│   └── DATOS_PRUEBA_CLIENTE.xlsx
└── backups/               # Copias de seguridad (no versionadas)
```

---

## mi_app/

| Carpeta/Archivo | Descripción |
|-----------------|-------------|
| `models.py` | Modelos de datos |
| `views_core.py` | Vistas principales |
| `views/` | Paquete de vistas |
| `auth_views.py` | Login, register |
| `api_views.py` | APIs búsqueda |
| `forms.py` | Formularios |
| `urls.py` | Rutas |
| `services/` | Lógica de negocio |
| `utilities/` | Decoradores, middleware |
| `management/commands/` | Comandos manage.py |
| `tests/` | **Todos los tests** (unitarios, integración, alto) |
| `templates/` | Plantillas HTML |
| `static/` | CSS, JS |

---

## Ejecutar tests

```bash
# Todos los tests
python manage.py test mi_app

# Con pytest
pytest mi_app/tests/ -v
```

---

## Cambios recientes (reorganización)

- Scripts sueltos de raíz → `pruebas_humano/scripts/`
- Tests de mi_app → `mi_app/tests/`
- audit_scripts/ → `scripts/audit/`
