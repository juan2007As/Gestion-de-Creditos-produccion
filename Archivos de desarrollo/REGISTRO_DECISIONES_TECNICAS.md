# 🎯 REGISTRO DE DECISIONES TÉCNICAS (ADR - Architectural Decision Records)

**Propósito:** Documentar CADA decisión arquitectónica importante y POR QUÉ se tomó  
**Audiencia:** Architects, senior devs, futuros mantenedores  
**Formato:** MADR (Markdown Architecture Decision Records)  

---

## ADR-001: Usar Django como Framework Web

**Estado:** ✅ ACCEPTED  
**Fecha:** Inicio del Proyecto (2025)  
**Contexto:**  
Se necesitaba un framework Python para:
- Gestión de préstamos y clientes
- Panel administrativo robusto
- ORM integrado

**Decisión:**  
Usar Django 6.0.2 over FastAPI, Flask o Django REST

**Alternativas Consideradas:**
- FastAPI: Más rápido pero requiere más configuración custom
- Flask: Micro-framework, muy minimal, requería mucho código custom
- Django REST Framework: Similar, Django es suficiente para requisitos

**Impacto:**
- ✅ Ventajas: Admin integrado, ORM poderoso, seguridad built-in
- ⚠️ Consecuencias: Más "pesado", pero estable para producción

**Relacionado:** ESTADO_COMPONENTES.md → Django 6.0.2

---

## ADR-002: SQLite para Desarrollo Local, PostgreSQL para Producción

**Estado:** ✅ ACCEPTED  
**Fecha:** Fase inicial (2025)  
**Contexto:**  
Ambiente de desarrollo vs producción necesitan diferentes DB

**Decisión:**  
- Local: SQLite (simple, sin instalación)
- Producción (Hostinger): PostgreSQL (escalable)

**Alternativas:**
- MySQL: Similar a PostgreSQL, más restrictivo
- MongoDB: NoSQL, no apto para relaciones complejas (préstamos/cuotas)
- SQLite everywhere: Simple pero no escala en producción

**Impacto:**
- ✅ Rápido desarrollo local
- ✅ Producción escalable
- ⚠️ Requires migration script si algo es incompatible

**Notas:** Migraciones son compatibles Django ↔ PostgreSQL

---

## ADR-003: Role-Based Permissions System (ERROR #8)

**Estado:** ✅ IMPLEMENTED (2026-02-15)  
**Fecha:** 2026-02-15  
**Contexto:**  
Necesidad de controlar acceso a endpoints según rol del usuario:
- Admin: Todo
- Gestor: Créar préstamos, listar clientes
- Usuario: Solo ver sus propios préstamos

**Decisión:**  
Implementar sistema de roles con Django's built-in User/Group/Permission
- Crear 3 roles: Admin, Gestor, Usuario
- Decoradores custom: @role_required
- 48 decoradores aplicados en views.py

**Alternativas:**
- Django Guardian: Más complejo, permissions a nivel de objeto
- Roles manuales en BD: Frágil, no escalable
- Auth externa (OAuth): Overkill para proyecto local

**Impacto:**
- ✅ Sistema seguro, auditable
- ✅ 53 tests confirman funcionamiento
- ⚠️ Todos los endpoints DEBEN tener decorador
- ⚠️ CRÍTICO: Cambios futuros en permisos afectan 48 lugares

**Archivo:** [permissions.py](../../../mi_app/permissions.py)  
**Auditoría:** [AUDITORIA_PROFUNDA_FINAL.md](../../archivos/AUDITORIA_PROFUNDA_FINAL.md)

---

## ADR-004: Centralized Backup System (ERROR #9)

**Estado:** ✅ IMPLEMENTED (2026-02-20)  
**Fecha:** 2026-02-20  
**Contexto:**  
Necesidad de respaldar BD de forma segura y recuperable

**Decisión:**  
- Crear módulo backup_manager.py independiente
- 3 endpoints: create_backup, restore_backup, list_backups
- Stored en media/backups/
- Usar .sql dumps + JSON metadata

**Alternativas:**
- Respaldos automáticos via cron: Complejo de configurar
- Respaldos mentales: No es viable
- Cloud-based (S3): Dependencia externa

**Impacto:**
- ✅ Recuperación de desastres posible
- ✅ Trazabilidad completa
- ⚠️ CRÍTICO: Import path error rompió todo (2026-02-20)
- ⚠️ FIX: Cambiar `from backup_manager` → `from mi_app.backup_manager`

**Validación:** test_backup_system.py - 5/5 tests PASSING

---

## ADR-005: Template Tags Para Filtros Personalizados

**Estado:** ✅ IMPLEMENTED  
**Fecha:** Mid-project (2026)  
**Contexto:**  
Necesidad de filtros reutilizables en templates (ej: formatear moneda)

**Decisión:**  
Usar Django template tags en `templatetags/`
- Registrar filtros `@register.filter`
- Usar en templates con `{% load custom_tags %}{{ value|my_filter }}`

**Alternativas:**
- Lógica en views.py y pasar contexto: Verbose
- Filter en JavaScript: Menos performante
- Custom template language: Overkill

**Impacto:**
- ✅ Templates limpios
- ✅ Reutilización fácil
- ⚠️ Cambios en filtro afectan todos templates que lo usen

---

## ADR-006: Dark Mode via SCSS + localStorage

**Estado:** ✅ IMPLEMENTED (E#10 COMPLETED)  
**Fecha:** 2026  
**Contexto:**  
Usuarios piden opción dark mode

**Decisión:**  
- CSS variables para colores
- SCSS genera dos temas: light.css + dark.css
- localStorage guarda preferencia usuario
- JavaScript cambia tema dinámicamente

**Alternativas:**
- Prefers-color-scheme CSS: No permite override usuario
- Tailwind dark mode: Cambiaría todo el CSS
- Color picker JS: Más complejo

**Impacto:**
- ✅ UX mejorada
- ✅ Usuarios pueden elegir tema
- ⚠️ Dos CSS files a mantener

---

## ADR-007: Excel Export via openpyxl (ERROR #1 FIXED)

**Estado:** ✅ FIXED (was E#1BUG)  
**Fecha:** Inicio  
**Contexto:**  
Necesidad de exportar datos a Excel

**Decisión:**  
Usar librería openpyxl para crear XLSX files
- Formateo automático (1 = entero, $1.23 = currency)
- Headers coloreados
- Ancho de columna automático

**Contexto de BUG:**  
Import incorrecto causaba que exportación fallara

**Impacto:**
- ✅ Exportación a Excel funcionando 100%
- ✅ Formateo profesional
- ⚠️ Archivos grandes pueden ser lentos

**Validación:** test_fixes.py (general)

---

## ADR-008: Favor Composition Over Inheritance en Models

**Estado:** ✅ FOLLOWED  
**Fecha:** Architectural guideline  
**Contexto:**  
Mantener models simples y DRY

**Decisión:**  
- Models muy específicos a su dominio (Prestamo, Cuota, Cliente)
- Comportamiento reutilizable en utils.py (functions)
- Herencia solo para casos claros (ej: AbstractUser)

**Alternativas:**
- Herencia múltiple: Complejidad, diamond problem
- Mixins: Útiles pero overuse causa confusión

**Impacto:**
- ✅ Código legible
- ✅ Menor acoplamiento
- ✅ Tests más aislados

---

## ADR-009: Migrations Solo para Cambios de Esquema, No Data

**Estado:** ✅ FOLLOWED  
**Fecha:** Directiva BD  
**Contexto:**  
Evitar data migrations que pueden fallar en producción

**Decisión:**  
- Migraciones para struct (add field, modify column)
- Data changes via management command o manual
- Nunca data migration en migration file

**Alternativas:**
- Data migrations: Más automático pero frágil
- Manual SQL: Requeridor error

**Impacto:**
- ✅ Migraciones confiables
- ✅ Reducido riesgo de downtime
- ⚠️ Data cleanup requiere steps extra

---

## ADR-010: Centralized Documentation System (NUEVO - 2026-02-20)

**Estado:** ✅ IMPLEMENTED  
**Fecha:** 2026-02-20  
**Contexto:**  
Proyecto perdía contexto entre sesiones. Documentación no se actualizaba.

**Decisión:**  
Crear 10 "living documents" en `docs/sistemas/`:
1. DASHBOARD_PROYECTO.md - Estado actual
2. CHANGELOG_DETALLADO.md - Cambios históricos
3. MANIFEST_ACTUALIZACION.md - Qué actualizar cuándo
4. MATRIZ_TRANSVERSAL_CAMBIOS.md - Impacto cruzado
5. ESTADO_COMPONENTES.md - Versiones/status
6. REGISTRO_DECISIONES_TECNICAS.md - Este archivo (ADR)
7. DEUDA_TECNICA.md - Bugs/TODOs conocidos
8. CHECKLIST_DEPLOYMENT.md - Pre-prod checks
9. INDICE_BUGS_POR_COMPONENTE.md - Tracking bugs
10. CRONOGRAMA_ACTUALIZACIONES.md - Schedule

**Razón:**  
- Evitar "¿qué pasó la sesión pasada?" syndrome
- Mantener contexto histórico
- Facilitar onboarding de nuevos devs
- Auditabilidad completa

**Alternativas:**
- Wiki externo: Difícil mantener sincronizado
- Issue tracker solo: Incompleto para decisiones
- Nada (caos actual): No viable para proyecto creciente

**Impacto:**
- ✅ Contexto SIEMPRE disponible
- ✅ Decisiones documentadas
- ✅ Fácil auditoría
- ⚠️ Requiere disciplina para actualizar
- ⚠️ CRÍTICO: Agregar a REGLAS_DESARROLLO.md como obligatorio

**Aplicado en:**
- [REGLAS_DESARROLLO.md](../REGLAS_DESARROLLO.md) - PARTE 4 nueva
- [MANIFEST_ACTUALIZACION.md](MANIFEST_ACTUALIZACION.md) - Checklist de actualización

---

## 📋 PENDIENTES PARA DOCUMENTAR

- ADR-011: Arquitectura de respuestas API (cuando se implemente E#?)
- ADR-012: Estrategia de caching (cuando se necesite)
- ADR-013: Logging centralized (cuando se implemente)

---

## 📌 CÓMO USAR ESTE ARCHIVO

### Para Buscar Decisión:
1. Ctrl+F palabra clave
2. Leer el ADR relevante
3. Entender impacto

### Para Agregar Nuevo ADR:
1. Copiar formato template
2. Escribir contexto, decisión, alternativas
3. Documentar impacto
4. Notar en CHANGELOG_DETALLADO.md
5. Ver REGISTRO_DECISIONES_TECNICAS.md en línea de MANIFEST_ACTUALIZACION.md

### Template para Nuevo ADR:

```markdown
## ADR-XXX: [Título]

**Estado:** PROPOSED | ACCEPTED | DEPRECATED  
**Fecha:** YYYY-MM-DD  
**Contexto:**  
[Qué problema / situación existía]

**Decisión:**  
[Qué se decidió hacer]

**Alternativas:**  
- Alt 1: [Por qué no]
- Alt 2: [Por qué no]

**Impacto:**
- ✅ Ventaja 1
- ✅ Ventaja 2
- ⚠️ Trade-off 1

**Relacionado:**  
[Links a otros ADRs o docs]
```

---

**Próxima revisión:** Cuando próximas decisiones arquitectónicas se tomen
