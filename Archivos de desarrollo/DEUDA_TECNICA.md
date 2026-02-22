# 🔴 DEUDA TÉCNICA - Bugs Conocidos, TODOs, Workarounds

**Propósito:** Tracking de problemas conocidos que NO se van a resolver inmediatamente  
**Audiencia:** Todo el equipo  
**Frecuencia:** Actualizar cuando se descubre bug o se agrega workaround  

---

## 🔴 CRÍTICO - Resolver en próxima iteración

### DEBT-001: views.py es muy grande (4103 líneas)

**Severidad:** 🔴 CRÍTICA  
**Descubierto:** 2026-02-15  
**Creado por:** Code review anterior  
**Status:** PENDING

**Descripción:**
```
views.py tiene 4103 líneas de código
- Views de prestamos: 800+ líneas
- Views de clientes: 600+ líneas
- Views de reportes: 500+ líneas
- Views de admin: 400+ líneas
- Helpers inline: 1800+ líneas
```

**Problema:**
- Difícil de mantener
- Difícil de testear
- IDE ralentiza con archivos tan grandes
- Merge conflicts frecuentes

**Impacto Actual:**
- ⚠️ Desarrollo lento
- ⚠️ Errores potenciales

**Workaround:**
- Usar Ctrl+G para ir a línea específica
- Buscar con Ctrl+F en lugar de scroll

**Solución Propuesta:**
- Refactorizar en módulos:
  - `views/prestamos.py` (800 líneas)
  - `views/clientes.py` (600 líneas)
  - `views/reportes.py` (500 líneas)
  - `views/admin.py` (400 líneas)
  - `views/api.py` (api endpoints)
- Mantener `__init__.py` para imports

**Entrada en Git:**
```
git log --grep="DEBT-001\|refactor.*views"
```

---

### DEBT-002: Búsqueda de clientes no filtra por columna específica

**Severidad:** 🔴 CRÍTICA  
**Descubierto:** 2026-02-10  
**Bug Relacionado:** BUG #1C  
**Status:** PENDING → (Será E#? o no)

**Descripción:**
La búsqueda en `/clientes/` hace Q-object search en:
- nombre, apellido, cedula, email, telefono

Pero NO permite búsqueda por columna específica (ej: solo cedula)

**Problema:**
- Resultados innecesarios si usuario busca por cedula pero coincide nombre de otro
- UX confusa
- No hay input dropdown para seleccionar columna

**Impacto:**
- ⚠️ UX degradada
- ⚠️ Falsos positivos en búsqueda

**Workaround:**
- Usuario agrega más términos para ser específico
- Ej: Cedula + rol → más específico

**Solución:**
- Agregar `<select>` en template: "Buscar en columna: [nombre|cedula|email|etc]"
- Generar Q-object dinámico basado en selección
- O hacer búsqueda exact en cedula si no tiene espacios

**Priority:** MEDIA (Usable pero no óptimo)

---

## 🟠 ALTO - Arreglar en 1-2 semanas

### DEBT-003: Reportes de interés no include clientes activos correctamente

**Severidad:** 🟠 ALTA  
**Descubierto:** 2026-02-10  
**Relacionado:** ERROR #3, ERROR #7  
**Status:** PENDING

**Descripción:**
Reporte mensual de interés está linkeado a ERROR #3 (Limpieza) y ERROR #7 (Fórmula).

**Problemas:**
- Datos sucios en BD (clientes sin interés, cuotas sin cliente)
- Fórmula de interés antigua (no compuesta)
- Reportes generan números incorrectos

**Impacto:**
- ⚠️ Reportes no confiables
- ⚠️ Reportes lentos (queries complejas)
- ⚠️ Auditoría imposible

**Workaround:**
- Verificar datos a mano en admin panel
- Usar Excel export + manual verification

**Solución Completa:**
- E#3: Limpiar datos sucios
- E#7: Implementar interest_rate compuesto en model
- Retest reportes después de limpiar

---

### DEBT-004: DB migrations no tienen rollback tested

**Severidad:** 🟠 ALTA  
**Descubierto:** 2026-02-15  
**Status:** PENDING

**Descripción:**
Hemos creado 15+ migraciones, pero NUNCA hemos testeado:
```bash
python manage.py migrate --reverse
# ¿Funcionará rollback?
```

**Problema:**
- Si fallamos en producción, no sabemos si rollback va a funcionar
- Datos pueden quedar inconsistentes

**Impacto:**
- 🔴 CRÍTICO en producción
- ⚠️ Riesgo alto de downtime

**Workaround:**
- Nunca hacer rollback en producción (evitar problema)
- Mantener backup manual de BD antes de migrations

**Solución:**
- Test cada migration en sandbox:
  ```bash
  python manage.py migrate 0001
  python manage.py migrate --reverse 0000
  # Ver si datos OK
  python manage.py migrate forward de nuevo
  ```
- Documentar result en CHECKLIST_DEPLOYMENT.md

**Priority:** ALTA - Hacer antes de próximo deploy

---

## 🟡 MEDIUM - Arreglar en 2-3 semanas

### DEBT-005: JavaScript de dark mode puede optimizarse

**Severidad:** 🟡 MEDIA  
**Descubierto:** 2026-02-20  
**Status:** WONTFIX (Bajo priority)

**Descripción:**
Dark mode JS hace un fetch a localStorage en CADA página load.
No está minificado. Tiene console.log's de debug.

**Problema:**
- Página se carga 50ms más lento en primera visit (negligible pero detectable)
- Console polluted si abres DevTools

**Impacto:**
- Negligible para UX
- Código "sucio" pero funcional

**Workaround:**
- Nadie - ES ACEPTABLE

**Solución Propuesta:**
- Minify JS (webpack o gulp)
- Remover console.log's
- Caché agresivo del JS

**Priority:** LOW - No hace en próxima iteración

---

### DEBT-006: PDF export falla con caracteres especiales

**Severidad:** 🟡 MEDIA  
**Descubierto:** 2026-02-05  
**Status:** PENDING

**Descripción:**
Export a PDF falla si cliente tiene nombre con ñ, é, ö

**Error:**
```
UnicodeEncodeError: 'latin-1' codec can't encode character '\xf1' in position X
```

**Problema:**
- Usuarios con apellidos hispanohablantes no pueden exportar
- Workaround: Copiar nombre sin tildes manualmente

**Impacto:**
- ⚠️ BUG pero infrecuente
- UX mala para usuarios no-ASCII

**Workaround:**
- Usuario quita tildes antes de exportar
- O exporta a Excel (Excel soporta UTF-8)

**Solución:**
- Cambiar encoding de PDF a UTF-8
- libs: reportlab + utf-8-sig

**Priority:** MEDIA - Arreglar si hay tiempo

---

## 🟢 BAJO - OK para después

### DEBT-007: Admin panel no tiene búsqueda full-text

**Severidad:** 🟢 BAJO  
**Descubierto:** 2026-02-08  
**Status:** WONTFIX

**Descripción:**
Admin panel (django built-in) no tiene búsqueda en todos los campos.

**Problema:**
- Admin search limitado
- Usuarios administrativos deben ir a página pública

**Impacto:**
- BAJO - no impacta sistema crítico
- Admin UI podría ser mejor

**Workaround:**
- Ir a página de clientes pública (tiene búsqueda mejor)

**Solución:**
- Agregar `search_fields` en admin class
- Implementar elasticsearch (overkill)

**Priority:** BAJO - Nice-to-have

---

### DEBT-008: Sin logging centralizado

**Severidad:** 🟢 BAJO  
**Descubierto:** 2026-02-12  
**Status:** PENDING

**Descripción:**
Logs están dispersos:
- Algunos en django.log
- Algunos en console
- Algunos en tabla de auditoria
- Algunos en archivo de texto

**Problema:**
- Difícil debugging
- No hay trazabilidad centralizada

**Impacto:**
- BAJO - Sistema funciona
- Debug más lento

**Workaround:**
- Buscar en múltiples lugares si hay error

**Solución:**
- Usar `logging` module centralizado
- Configurar handlers: console + file + DB
- Implementar cuando sea necesario

**Priority:** BAJO - Si tiempo disponible

---

## 🔵 PENDIENTE - Decidir si es deuda o no

### DEBT-009: Tests podrían tener mejor coverage

**Severidad:** 🔵 TBD  
**Status:** PENDING

**Descripción:**
Tenemos 453 tests que pasan, pero ¿coverage real es 100%?

**Incertidumbre:**
- Nunca corrimos pytest con --cov flag
- Podrían haber ramas no testeadas

**Impacto:**
- TBD

**Workaround:**
- Nada

**Solución Propuesta:**
```bash
pytest --cov=mi_app --cov-report=html
# Ver qué branches faltan
```

**Priority:** MEDIUM - Investiga en próxima iteración

---

## 📊 TABLA RESUMEN DE DEUDA

| ID | Descripción | Severidad | Status | Creador | Workaround |
|---|---|---|---|---|---|
| DEBT-001 | views.py 4103 líneas | 🔴 | PENDING | Code Review | Ctrl+F |
| DEBT-002 | Búsqueda por columna | 🔴 | PENDING | Testing | Agregar términos |
| DEBT-003 | Reportes sin limpiar | 🟠 | PENDING | E#3/E#7 | Manual verification |
| DEBT-004 | Rollback migrations | 🟠 | PENDING | Deployment | Backup manual |
| DEBT-005 | Dark mode JS | 🟡 | WONTFIX | Audit | Acceptable |
| DEBT-006 | PDF Unicode | 🟡 | PENDING | User report | Use Excel |
| DEBT-007 | Admin search | 🟢 | WONTFIX | Nice-to-have | Use public page |
| DEBT-008 | Logging scattered | 🟢 | PENDING | Architecture | Multi-search |
| DEBT-009 | Coverage TBD | 🔵 | PENDING | TBD | N/A |

---

## 🎯 PRIORIZACIÓN PARA PRÓXIMAS SESIONES

### SESSION INMEDIATA (Próximas 2 horas):
- [ ] DEBT-004: Test rollback de migration
- [ ] DEBT-002: Investigar búsqueda (decide si es E#? o no)

### SESIÓN 2 (Próx 1-2 días):
- [ ] DEBT-001: Refactorizar views.py (consideración)
- [ ] DEBT-003: Es parte de E#3 + E#7 (lo harás aquí)

### SESIÓN 3 (Próx 1 semana):
- [ ] DEBT-006: Arreglar PDF Unicode
- [ ] DEBT-009: Coverage report

### SESIÓN 4+ (Cuando hay tiempo):
- [ ] DEBT-005: Minify JS (Low priority)
- [ ] DEBT-008: Logging centralizado

---

## 📝 ACTUALIZAR ESTE ARCHIVO

**Cuando descubres un bug:**
1. Agregar sección DEBT-00X
2. Describir: Severidad, workaround, impacto
3. Actualizar tabla resumen
4. NOTAR EN CHANGELOG_DETALLADO.md

**Cuando arreglas un bug:**
1. Cambiar status a RESOLVED
2. Quitar de tabla resumen (o mover a sección de archivo)
3. Notar en CHANGELOG_DETALLADO.md

**Ver también:** [CHANGELOG_DETALLADO.md](CHANGELOG_DETALLADO.md) para cambios históricos

---

**Última actualización:** 2026-02-20  
**Próxima revisión:** Cuando próxima deuda se descubra
