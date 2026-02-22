# 🔗 MATRIZ TRANSVERSAL DE CAMBIOS - Impacto Cruzado

**Propósito:** Entender cómo un cambio en un módulo afecta OTRO módulo  
**Audiencia:** Senior devs, arquitectos, QA  
**Frecuencia:** Actualizar cuando nuevos módulos se agregan  

---

## 🗺️ DEPENDENCIAS ENTRE COMPONENTES

### ➡️ Cuando cambias VIEWS.PY

```
views.py (4103 líneas - NÚCLEO)
    ↓
├─→ models.py (Modelos/BD)
├─→ forms.py (Validación)
├─→ utils.py (Helpers)
├─→ templates/ (Renderizado)
├─→ admin.py (Panel administrativo)
├─→ permissions.py (Roles - CRÍTICO desde E#8)
└─→ backup_manager.py (Sistema de respaldos - CRÍTICO desde E#9)

⚠️ IMPACTO: ALTO - Revisión completa de permisos + respaldos
```

### ➡️ Cuando cambias MODELS.PY

```
models.py (Esquema BD)
    ↓
├─→ migrations/ (Versionado histórico)
├─→ views.py (Queries + Validación)
├─→ forms.py (Campos del formulario)
├─→ admin.py (Interface admin)
├─→ tests/ (Fixtures)
└─→ utils.py (Funciones de cálculo)

⚠️ IMPACTO: CRÍTICO - Crear migration, revisar datos existentes
```

### ➡️ Cuando cambias FORMS.PY

```
forms.py (Validación frontend)
    ↓
├─→ views.py (Procesa datos)
├─→ templates/ (Renderiza HTML)
│   └─→ JavaScript / Validación JS
└─→ models.py (Valida contra BD)

⚠️ IMPACTO: MEDIO - Revisar templates que usan este form
```

### ➡️ Cuando cambias PERMISSIONS.PY (E#8)

```
permissions.py (Roles/Permisos - SISTEMA CRÍTICO)
    ↓
├─→ views.py (48 decoradores aplicados)
├─→ admin.py (Panel administrativo)
├─→ models.py (User, Group, Permission models)
└─→ templates/ (Mostrar/ocultar UI según rol)

⚠️ IMPACTO: CRÍTICO - Auditar todos los 48 endpoints protegidos
✅ AUDITORÍA: 53 tests en test_roles_permisos.py (PASSING)
```

### ➡️ Cuando cambias BACKUP_MANAGER.PY (E#9)

```
backup_manager.py (Sistema de respaldos)
    ↓
├─→ views.py (3 endpoints: create/restore/list)
├─→ admin.py (Interface admin)
└─→ models.py (Tabla de respaldos)

🔴 HISTORIA: Importación incorrecta rota en 2026-02-20
✅ ARREGLADO: Cambiar import path
⚠️ IMPACTO: 3 endpoints quedaron 100% rotos
```

### ➡️ Cuando cambias TEMPLATETAGS

```
templatetags/ (Filtros personalizados)
    ↓
└─→ templates/ (Todos los .html que usan custom tags)

⚠️ IMPACTO: MEDIO - Buscar en templates por {% tag %}
```

---

## 📊 MATRIZ CRUZADA DE COMPONENTES

| Si cambias... | Afecta a... | Severidad | Validación |
|---|---|---|---|
| models.py | views, forms, admin, migrations | 🔴 CRÍTICA | Crear migration, revisar tests |
| views.py | templates, forms, models, permissions | 🔴 CRÍTICA | Revisión de permisos, tests de endpoint |
| forms.py | templates, views, models | 🟠 ALTA | Validar templates, probar form |
| permissions.py | views (48 decoradores), admin, templates | 🔴 CRÍTICA | Auditar todos endpoints, 53 tests |
| backup_manager.py | views (3 endpoints), admin, models | 🔴 CRÍTICA | Tests backup_system.py |
| templates/ | views, forms, JavaScript | 🟠 ALTA | Revisar elementos interactivos |
| utils.py | views, forms, models | 🟡 MEDIA | Buscar referencias de función |
| admin.py | models, permissions, templates | 🟡 MEDIA | Probar panel admin |
| templatetags/ | templates que los usan | 🟡 MEDIA | Buscar en templates |
| migrations/ | models, BD | 🔴 CRÍTICA | Probar migrate/rollback |

---

## 🔍 BÚSQUEDAS PARA IMPACTO

### Para encontrar impacto de cambio en `backup_manager`:
```python
# En views.py buscar:
grep "backup_manager\|create_backup\|restore_backup" views.py
# Resultado esperado: Líneas 3792, 3818, 3841
```

### Para encontrar impacto de cambio en `permissions`:
```python
# Buscar decoradores aplicados:
grep "@.*permission\|@login_required\|@role_required" views.py
# Resultado esperado: 48 decoradores
```

### Para encontrar impacto de cambio en formulario:
```html
<!-- En templates buscar el form: -->
grep "<form" templates/*.html | grep "NombreForm"
```

---

## 🎯 CAMBIOS TÍ PICOS Y SU CASCADA

### ESCENARIO 1: Agregar campo a Préstamo (models.py)
```
1. Agregar en models.Prestamo
2. Crear migration: python manage.py makemigrations
3. Run migration: python manage.py migrate
4. Actualizar forms.PrestamoForm
5. Actualizar template: crear_prestamo.html
6. Actualizar views: prestar_create (si necesita)
7. Actualizar admin.PrestamoAdmin
8. TESTS: Crear fixture con nuevo campo
9. Commit: "FEAT: Add [field] to Préstamo model"
```

### ESCENARIO 2: Cambiar permiso de endpoint (permissions.py E#8)
```
1. Cambiar en permissions.py (crear nuevo rol o permisos)
2. Actualizar decorador en views.py
3. AUDIT: Validar no hay otros endpoints con misma lógica
4. TEST: Ejecutar test del endpoint con nuevo permiso
5. ADMIN: Asegurar rol existe en BD
6. Commit: "CHORE: Update permission for [endpoint]"
```

### ESCENARIO 3: Reparar bug en backup_manager.py (COMO E#9)
```
1. Identificar import incorrecto
2. Cambiar import path en views.py
3. TEST: Ejecutar test_backup_system.py
4. VALIDATE: Probar 3 endpoints: create, restore, list
5. Commit: "FIX: Correct import path for backup_manager"
```

---

## 🚨 CAMBIOS DE ALTO RIESGO

### 🔴 CRÍTICO - Requiere pre-comunicación:
- [ ] Cambios en models.Migration (puede romper BD)
- [ ] Cambios en permissions.py (afecta 48 endpoints)
- [ ] Cambios en backup_manager.py (datos críticos)
- [ ] Cambios en forms de negocio (validación)

### 🟠 ALTO - Requiere auditoría:
- [ ] Cambios en views.py (núcleo de aplicación)
- [ ] Cambios en utils.py (funciones usadas en múltiples sitios)
- [ ] Cambios en models (esquema)

### 🟡 MEDIO - Requiere testing:
- [ ] Cambios en templates
- [ ] Cambios en forms
- [ ] Cambios en TypeScript/JavaScript

---

## 📝 CHECKLIST ANTES DE CAMBIOS DE ALTO RIESGO

```markdown
## CAMBIO DE ALTO RIESGO: [DESCRIPCIÓN]

- [ ] Leí MATRIZ_TRANSVERSAL_CAMBIOS.md
- [ ] Identificué componentes afectados: [LISTA]
- [ ] Creé branch nuevo: git checkout -b feature/[nombre]
- [ ] Realicé cambios en [ARCHIVO]
- [ ] Busqué referencias con grep: [RESULTADOS]
- [ ] Actualicé componentes dependientes: [LISTA]
- [ ] Ejecuté tests relevantes: [RESULTADO]
- [ ] Commit: "TIPO: Descripción breve"
- [ ] PR/MR: Describí impacto completo
```

---

## 📌 ACTUALIZACIONES

**Última actualización:** 2026-02-20  
**Próxima revisión:** Cuando se agreguen nuevos módulos  

**Historial de cambios a esta matriz:**
- 2026-02-20: Agregado backup_manager.py + permissions.py (E#8, E#9)
