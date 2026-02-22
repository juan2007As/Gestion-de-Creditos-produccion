# 🐛 ÍNDICE DE BUGS POR COMPONENTE - Tracking Centralizado

**Propósito:** Saber instantáneamente qué bugs afectan qué componentes  
**Audiencia:** Todo el equipo  
**Frecuencia:** Actualizar cuando bug se descubre O se cierra  

---

## 🏗️ ESTRUCTURA POR COMPONENTE

En cada componente, bugs se categorizan como:
- 🔴 CRÍTICO: Función 100% rota
- 🟠 ALTO: Funciona pero con limitaciones mayoress
- 🟡 MEDIO: Funciona, problemas menores
- 🟢 BAJO: Cosmético o sin impacto actual
- 🔵 PENDIENTE CATEGORIZAR: Necesita triaging

---

## 📊 TODOS LOS BUGS ACTIVOS

### ERROR #1: IMPORTACIÓN EXCEL - ✅ RESUELTO
**Status:** ✅ COMPLETADO  
**Fecha resolución:** 2026-02-10  
**Componentes afectados:** `views.py`, `utils.py`

**Sub-bugs:**
1. 🔴 E#1A: Headers Excel incorrectos → ✅ FIXED
2. 🔴 E#1B: Encoding UTF-8 falla → ✅ FIXED
3. 🟡 E#1C: Búsqueda de columna específica → PENDIENTE (ver DEBT-002)

---

### ERROR #2: INTERÉS IMPORTADO - ✅ RESUELTO
**Status:** ✅ COMPLETADO  
**Fecha resolución:** 2026-02-10  
**Componentes afectados:** `models.py`, `utils.py`

**Descripción:** Interés no se aplicaba a cuotas importadas  
**Root cause:** Query no incluía campo interest_amount  

---

### ERROR #3: LIMPIEZA AUTOMÁTICA REPORTERÍA - 🔵 PENDIENTE
**Status:** 🔵 NO INICIADO  
**Prioridad:** 🔴 CRÍTICA  
**Componentes afectados:** `utils.py`, `management/commands/`, `models.py`

**Descripción:**  
Base de datos tiene registros "huérfanos":
- Cuotas sin cliente
- Clientes sin préstamos
- Reportes con datos inconsistentes

**Sub-bugs:**
- 🔴 Reportes retornan números incorrectos
- 🟠 Queries son lentos (busca en datos sucios)
- 🟡 Admin panel confuso con registro phantom

**Impacto:**
- CRÍTICO: Auditoría no confiable
- Reportería incorrecta
- Tests pueden tener falsos positivos

**Workaround:** Ver [DEUDA_TECNICA.md](DEUDA_TECNICA.md#debt-003)

---

### ERROR #4: PRÉSTAMO RÁPIDO CON CUOTAS - 🔵 PENDIENTE
**Status:** 🔵 NO INICIADO  
**Prioridad:** 🔠 MEDIA  
**Componentes afectados:** `forms.py`, `views.py`, `models.py`

**Descripción:**  
Usuario quiere crear préstamo + todas sus cuotas de una vez
Actualmente: Create prestamo → Ir a otra página → Crear cuotas manualmente

**Feature requerida:**
- Formulario combinado: Datos préstamo + tabla de cuotas
- Guardar todo en una transacción (todo o nada)
- Validar cuotas sumen a monto principal

**Sub-items:**
- 🔵 UI/Form combinado
- 🔵 Transacción atómica
- 🔵 Validación
- 🔵 Tests

---

### ERROR #5: LISTA NEGRA DE CLIENTES - 🔵 PENDIENTE
**Status:** 🔵 NO INICIADO  
**Prioridad:** 🟡 MEDIA  
**Componentes afectados:** `models.py`, `views.py`, `forms.py`

**Descripción:**  
Agregar campo `is_blacklisted` a Cliente:
- Si TRUE: No permite crear préstamos
- Admin puede togglear
- Reportería excluye estos clientes

**Sub-items:**
- 🔵 Migration: Agregar `is_blacklisted` boolean
- 🔵 Admin: Toggle UI
- 🔵 Validación en views: Prevenir préstamo si blacklisted
- 🔵 Reportes: Excluir

---

### ERROR #6: ETIQUETACIÓN DE CLIENTES - 🔵 PENDIENTE
**Status:** 🔵 NO INICIADO  
**Prioridad:** 🟡 MEDIA  
**Componentes afectados:** `models.py`, `forms.py`, `templates/`

**Descripción:**  
Agregar sistema de tags a clientes (ej: "VIP", "Moroso", "Nuevo")
- Many-to-many relationship: Cliente ↔ Tag
- Búsqueda/filtro por tag
- UI checkboxes en form

**Sub-items:**
- 🔵 Model: Tag, relationship M2M
- 🔵 Migration
- 🔵 Form: Checkboxes de tags
- 🔵 Búsqueda: Filtrar por tag
- 🔵 Template: Mostrar tags

---

### ERROR #7: REPORTE MENSUAL INTERÉS - 🔵 PENDIENTE
**Status:** 🔵 NO INICIADO  
**Prioridad:** 🔴 CRÍTICA  
**Componentes afectados:** `utils.py`, `views.py`, `management/commands/`

**Descripción:**  
Fórmula de interés actual es simple (interest_rate * monto)
Necesita ser compuesta: interest_rate^periods

**Sub-items:**
- 🔴 Formula: Implementar interés compuesto
- 🟠 Cuotas: Recalcular retroactivamente
- 🟠 Reportes: Verificar totales
- 🟡 Auditoría: Qué clientes fueron afectados

**Bloqueado por:** E#3 (Limpieza de datos)

---

### ERROR #8: ROLES Y PERMISOS - ✅ RESUELTO
**Status:** ✅ COMPLETADO  
**Fecha resolución:** 2026-02-15  
**Componentes afectados:** `permissions.py`, `views.py (48 decoradores)`, `admin.py`

**Descripción:**  
Implementar control de acceso basado en roles

**Sub-items:**
- ✅ E#8A: Crear Sistema de roles (3 roles: Admin, Gestor, Usuario) → ✅ DONE
- ✅ E#8B: Decoradores para proteger endpoints → ✅ DONE (48 aplicados)
- ✅ E#8C: Auditoría completa (53 tests) → ✅ DONE

**Validación:** [AUDITORIA_PROFUNDA_FINAL.md](../../archivos/AUDITORIA_PROFUNDA_FINAL.md)

---

### ERROR #9: SISTEMA DE RESPALDOS - ✅ RESUELTO
**Status:** ✅ COMPLETADO  
**Fecha resolución:** 2026-02-20  
**Componentes afectados:** `backup_manager.py`, `views.py (líneas 3792, 3818, 3841)`

**Descripción:**  
Sistema de backups completamente roto por import path incorrecto

**Root cause:** 
```python
# ANTES (INCORRECTO):
from backup_manager import create_backup  # ❌ NO ENCONTRADO

# DESPUÉS (CORRECTO):
from mi_app.backup_manager import create_backup  # ✅ FOUND
```

**Sub-items:**
- 🔴 E#9A: Import path error → ✅ FIXED (2026-02-20)
- ✅ E#9B: 3 endpoints reparados
- ✅ E#9C: 5 tests pasando

**Validación:** [test_backup_system.py](../../../tests/test_backup_system.py)

---

### ERROR #10: DARK MODE - ✅ RESUELTO
**Status:** ✅ COMPLETADO  
**Fecha resolución:** 2026-02-15 (aproximada)  
**Componentes afectados:** `templates/`, CSS, JavaScript

**Descripción:**  
Dark mode no aplicable/seleccionable

**Resultado:** ✅ Fully working (se puede seleccionar tema)

---

## 🔍 BÚSQUEDA RÁPIDA POR ESTATUSS

### ✅ RESUELTOS (5/10)
- [x] ERROR #1 - Excel import
- [x] ERROR #2 - Interés importado
- [x] ERROR #8 - Roles & Permissions
- [x] ERROR #9 - Backups (HOTFIX 2026-02-20)
- [x] ERROR #10 - Dark mode

### 🔵 PENDIENTES (5/10)
- [ ] ERROR #3 - Limpieza reportería (🔴 CRÍTICO)
- [ ] ERROR #4 - Préstamo rápido (🟡 MEDIO)
- [ ] ERROR #5 - Lista negra (🟡 MEDIO)
- [ ] ERROR #6 - Etiquetación (🟡 MEDIO)
- [ ] ERROR #7 - Interés compuesto (🔴 CRÍTICO)

---

## 🗂️ BÚSQUEDA POR COMPONENTE

### views.py (4103 líneas)
| Bug | Líneas | Status | Prioridad |
|---|---|---|---|
| E#8C: Decoradores | 10-4100 | ✅ 48 applied | DONE |
| E#9A: Backup imports | 3792,3818,3841 | ✅ FIXED | DONE |
| E#4: Préstamo rápido | TBD | 🔵 PENDING | 🟡 MEDIUM |

### models.py
| Bug | Impact | Status | Prioridad |
|---|---|---|---|
| E#3: Datos sucios | Migraciones | 🔵 PENDING | 🔴 CRITICAL |
| E#5: is_blacklisted | Add field | 🔵 PENDING | 🟡 MEDIUM |
| E#6: Tags M2M | Add relationship | 🔵 PENDING | 🟡 MEDIUM |

### utils.py
| Bug | Impact | Status | Prioridad |
|---|---|---|---|
| E#2: Interest apply | Fórmula | ✅ FIXED | DONE |
| E#3: Limpieza | Data cleanup | 🔵 PENDING | 🔴 CRITICAL |
| E#7: Interés compuesto | Fórmula | 🔵 PENDING | 🔴 CRITICAL |

### templates/
| Bug | Impact | Status | Prioridad |
|---|---|---|---|
| E#6: Tags checkboxes | UI | 🔵 PENDING | 🟡 MEDIUM |
| E#10: Dark mode | UI | ✅ DONE | DONE |

### forms.py
| Bug | Impact | Status | Prioridad |
|---|---|---|---|
| E#4: Préstamo + cuotas | New form | 🔵 PENDING | 🟡 MEDIUM |
| E#6: Tags selection | Add field | 🔵 PENDING | 🟡 MEDIUM |

---

## 🎯 PRIORIZACIÓN PARA PRÓXIMAS SESIONES

### SESIÓN INMEDIATA:
1. 🔴 E#3 (Limpieza) - Requiere auditoría de BD
2. 🔴 E#7 (Interés) - Bloqueado por E#3

### SESIÓN 2:
3. 🟡 E#4 (Préstamo rápido) - MEDIUM
4. 🟡 E#5 (Lista negra) - MEDIUM

### SESIÓN 3:
5. 🟡 E#6 (Etiquetación) - MEDIUM

---

## 📝 CÓMO ACTUALIZAR

### Cuando CIERRAS un bug:
1. Cambiar status a ✅
2. Agregar fecha resolución
3. Actualizar resumen
4. Commit: "FIX: Close ERROR #X"

### Cuando ABRES un bug:
1. Agregar sección ERROR #X
2. Describir: Status, prioridad, componentes
3. Agregar a tabla resumen
4. Notar en [CHANGELOG_DETALLADO.md](CHANGELOG_DETALLADO.md)

### Cuando descubres SUB-bug:
1. Agregar como E#XA, E#XB, etc.
2. Notar el bloqueador si existe

---

**Última actualización:** 2026-02-20  
**Próxima actualización:** Cuando próximo ERROR se resuelva o se descubra nuevo bug
