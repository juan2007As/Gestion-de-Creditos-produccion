# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema de Gestión de Créditos — a Django (Python) web application for financial credit management. Includes client management, loan creation, installment calculation, payment processing, financial reporting, Excel import/export, audit logging, and a blacklist system.

**Owner:** Juan Carlos (Colombia) — professional portfolio project.
**Production:** PythonAnywhere (`Gestion-de-Creditos`).

## Stack

- **Backend:** Django 4.2 (Python), django-crispy-forms + crispy-bootstrap5
- **Database:** SQLite (local/dev), PostgreSQL (production)
- **Frontend:** HTML/CSS/JS, Bootstrap, with server-rendered Django templates
- **Static files:** WhiteNoise in production
- **Key dependencies:** openpyxl (Excel I/O), pandas, psycopg2-binary, django-ratelimit, tabulate, Pillow

## Commands

```bash
# Development server
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py flush              # Wipe data, keep schema

# Testing — all tests live in mi_app/tests/
python manage.py test mi_app                         # All tests (Django runner)
pytest mi_app/tests/ -v                              # All tests (pytest)

# Environment config
python scripts/verificar_config.py                   # Verify active environment
python manage.py shell -c "from django.conf import settings; print(settings.ENVIRONMENT)"

# Clean database
python limpiar_db.py
python scripts/limpiar_bd.py
python scripts/restaurar_bd_vacia.py

# Production prep & maintenance
python manage.py collectstatic --noinput
python auto_mantenimiento.py                         # Scheduled: blacklist tagging, client labels, quota sync

# Create superuser (scripts at root)
python create_superuser.py
python setup_roles.py
```

## Architecture

### Environment system

Three environments controlled by the `ENVIRONMENT` env var: `local`, `staging`, `production`. Settings in `proyecto_john/settings.py` branch on this variable — DB engine (SQLite vs PostgreSQL), email backend, caching, security headers, logging, static file storage, and middleware all adapt automatically.

`.env` file (gitignored) holds secrets. Templates receive `LOCAL`, `PRODUCTION`, `STAGING`, `DEBUG`, `ENVIRONMENT`, and `CREDITS_CONFIG` via `mi_app/context_processors.py`.

Configuration templates live in `config/`: `local.env.example` and `pythonanywhere.env.example`.

### Project structure

Single Django app pattern — all functionality lives in `mi_app/`. The Django project config is `proyecto_john/` (settings, root URLConf, WSGI/ASGI).

```
mi_app/
├── models.py          # 17 models, ~2000 lines — the data core
├── views_core.py      # ~250KB, all view functions (re-exported via views/__init__.py)
├── views/             # Package that re-exports from views_core (ready for future split)
├── urls.py            # All app URL routes (~100 paths)
├── forms.py           # Django forms
├── services/          # Business logic layer (stateless service classes)
│   ├── prestamo_service.py, cuota_service.py, pago_service.py, cliente_service.py
│   ├── reportes.py, excel_validator.py, validaciones.py
├── utilities/         # Cross-cutting infrastructure
│   ├── decorators.py           # Role/permission decorators (@require_rol, @admin_required, etc.)
│   ├── middleware.py            # RateLimitMiddleware
│   ├── backup_manager.py       # Local backup management
│   ├── audit_decorator.py      # @registrar_cambio for audit logging
│   ├── audit_model.py          # AuditLog model helpers
│   ├── transaction_integrity.py
│   └── tech_debt_fixes.py
├── management/commands/        # Custom manage.py commands (cleanup, tagging, auditing, sync)
├── tests/                      # ~20 test files covering unit, integration, e2e, performance
├── templates/                  # Django templates (server-rendered)
├── static/                     # CSS/JS
└── signals.py                  # Django signals for real-time updates
```

### Data model (core entities)

- **Cliente** — Client with historical scoring fields (`total_prestado_historico`, `tasa_cumplimiento`, `dias_mora_promedio`, `etiqueta_cliente` [BUENO/MEDIO/MALO/SIN_HISTORIAL]). Rating is computed, not stored.
- **Prestamo** — Loan with `monto_total`, `interes`, `cuota_mensual`, `num_cuotas`, `tipo_pago` (QUINCENAL/MENSUAL), state machine (ACTIVO → EN_PROCESO → COMPLETADO / EN_MORA).
- **Cuota** — Installment with `monto`, `monto_pagado`, `fecha_pago_esperada`, paid status.
- **Pago** — Payment record tied to a Cuota.
- **PrestamoRapido / CuotaRapida / PagoPrestamoRapido** — Parallel models for "quick loans" (simpler loan product).
- **Configuracion** — Singleton app configuration (interest rates, limits).
- **Rol / Permiso / RolPermiso / UsuarioProfile** — Custom RBAC authorization system. Roles: ADMIN, GERENTE, OPERARIO.
- **HistorioCambios** — Audit trail of all data changes.
- **ListaNegra** — Client blacklist entries.
- **AuditoriaBackup / AuditLog** — Audit backup and request-level logging.

### Key architectural patterns

- **Service layer** in `mi_app/services/` — stateless classes with `@staticmethod` methods. Views delegate business logic here rather than inlining it.
- **RBAC via decorators** — Views are protected with `@require_rol`, `@require_permission`, `@admin_required`, `@gerente_o_admin` from `mi_app/utilities/decorators.py`. Each uses `@login_required` internally.
- **Audit middleware** (`mi_app/auditoria.AuditoriaRequestMiddleware`) logs every HTTP request. The `@registrar_cambio` decorator logs model changes to `HistorioCambios`.
- **Signals** (`mi_app/signals.py`) handle real-time client tagging, automatic scoring updates, and state synchronization.
- **Environment-conditional** everything: middleware, caching, email, DB, security settings, logging all branch on `ENVIRONMENT`.
- **Views as a package** — `mi_app/views/__init__.py` re-exports from `views_core.py`, designed to be split into modules (auth, clients, payments, reports) but not yet done.

### Maintenance commands (all in `mi_app/management/commands/`)

Key custom commands: `auto_tagging_lista_negra`, `auto_tagging_etiquetas`, `sincronizar_estados_cuotas`, `cleanup_prestamos_antiguos`, `corregir_totales_prestamo`, `reconciliar_finanzas`, `auditar_*` (multiple audit commands).

Run scheduled maintenance with `python auto_mantenimiento.py`, which chains the three most important commands.

### Excel import flow

Clients can be imported from Excel via `importar_excel` view → `mi_app/services/excel_validator.py`. Imported records are marked `importado_excel=True` on the Cliente model.

### Workflow: Local → Git → PythonAnywhere

Develop and test locally → push to GitHub (`git push origin main`) → pull on PythonAnywhere (`git pull origin main`) → migrate → reload web app.
