# ✅ CHECKLIST DE DEPLOYMENT - Verificaciones Pre-Producción

**Propósito:** Garantizar que los cambios son seguros antes de ir a producción  
**Audiencia:** DevOps, QA, Lead técnico  
**Cuándo usar:** Antes de ANY cambio a producción  

---

## 📋 FASE 1: VERIFICACIONES LOCALES (Local Development)

Ejecutar completamente ANTES de hacer commit:

### ✅ Código & Tests
- [ ] `pytest` - Todos los tests pasan (453/453 ✅)
- [ ] `python manage.py check` - Django validation OK
- [ ] Sem9ntic check con Pylance/mypy (sin errores)
- [ ] `pylint` o similar - Sin warnings mayores
- [ ] `black` o similar - Código formateado

### ✅ Migraciones
- [ ] `python manage.py makemigrations --check` - Cambios detectados?
- [ ] Si hay cambios: `python manage.py migrate --plan` - Plan OK?
- [ ] Test rollback: `python manage.py migrate <prev>` then forward (ONLY IF new migration)
- [ ] `python manage.py migrate` on fresh DB - ¿Funciona desde cero?

### ✅ Static Files
- [ ] `python manage.py collectstatic --dry-run` - Cambios detectados?
- [ ] Si cambios: Esperar a fase 2

### ✅ Git & Commits
- [ ] `git status` - Nada pendiente?
- [ ] `git diff --staged` - Cambios esperados?
- [ ] Commit message: "TYPE: Brief description"
- [ ] Log: `git log --oneline -5` - Último commit es el tuyo?

---

## 📋 FASE 2: CAMBIOS DOCUMENTADOS

Antes de push a rama main/master:

### ✅ Documentación Sincronizada
- [ ] `CHANGELOG_DETALLADO.md` - Agregada entrada
- [ ] `DASHBOARD_PROYECTO.md` - Métricas actualizadas
- [ ] `ESTADO_COMPONENTES.md` - Status de componentes actualizado
- [ ] `DEUDA_TECNICA.md` - Si cambio introduce deuda o resuelve deuda

### ✅ Matriz de Cambios
- [ ] Leí `MATRIZ_TRANSVERSAL_CAMBIOS.md`
- [ ] Identifiqué componentes afectados
- [ ] Verifiqué que no hay dependencias rotas
- [ ] Si cambio afecta >2 módulos: ✅ Auditoría manual

### ✅ Decisiones Técnicas (Si aplica)
- [ ] ¿Este cambio es decisión arquitectónica? 
  - SI: → `REGISTRO_DECISIONES_TECNICAS.md` - Agregar ADR-XXX
  - NO: → Continuar

---

## 📋 FASE 3: TESTING COMPLETO

LOCAL FINAL:

### ✅ Smoke Tests (Quick)
```bash
python manage.py runserver
# Visitar página principal: ¿Carga?
# Intentar login: ¿Funciona?
# Intentar crear cliente: ¿Funciona?
# Intentar crear préstamo: ¿Funciona?
```

### ✅ Regression Tests
```bash
pytest tests/
# ¿Todo pasando? 453/453?
```

### ✅ Feature Tests (Si hay feature nueva)
```bash
# Testear feature específica
pytest tests/test_nuevo_feature.py -v
```

### ✅ Performance Check
```bash
# ¿Queries están optimizadas?
# ¿Carga tarda <2 segundos?
# ¿Reportes generan en <30 segundos?
```

### ✅ Security Check
- [ ] Verificar permisos en endpoint nuevo (si lo hay)
- [ ] ¿Es endpoint protegido? @login_required o @role_required?
- [ ] Si toca permisos: Auditoría 48 endpoints (ver ADR-003)
- [ ] ¿SQL injection posible? (especialmente en búsqueda)

---

## 📋 FASE 4: STAGING (Si existe)

Si tienes ambiente staging previamente a producción:

### ✅ Deploy a Staging
- [ ] `git push origin staging` (o similar)
- [ ] CI/CD pipeline ejecuta (si existe)
- [ ] Smoke tests en staging pasando
- [ ] QA hace testing manual
- [ ] Performance OK en staging

### ✅ Monitoreo
- [ ] Error logs limpios (sin Exceptions)
- [ ] Performance metrics normales
- [ ] DB queries count normal

---

## 📋 FASE 5: PRODUCCIÓN

ANTES DE PROD:

### ⚠️ PRE-DEPLOYMENT
- [ ] Backup de BD en producción: `python manage.py backup` (o manual)
- [ ] Comunicación enviada si es cambio importante
- [ ] Equipo standby en caso de rollback
- [ ] Fecha/hora de deployment anotada en CHECKLIST

### ✅ DEPLOYMENT
- [ ] `git push origin main` (o similar)
- [ ] CI/CD o deployment manual ejecuta
- [ ] Migrations ejecutan: `python manage.py migrate`
- [ ] Static files recolectados: `python manage.py collectstatic`
- [ ] Servidor Django reinicia
- [ ] Gunicorn/nginx verifican status

### ✅ POST-DEPLOYMENT
- [ ] Visitar app en producción: ¿Carga?
- [ ] Intentar feature nuevas: ¿Funciona?
- [ ] Logs limpios (no Exceptions)
- [ ] Performance normal (monitoreo)
- [ ] No hay 500 errors en error logs

### ⚠️ ROLLBACK PLAN (Si falla)
- [ ] `git revert <commit>` si cambio roto
- [ ] `python manage.py migrate <prev_migration>` si migration rota
- [ ] Restore BD desde backup si data corrupta
- [ ] Notificar equipo

---

## 🎯 CHECKLIST RÁPIDA POR TIPO DE CAMBIO

### 🔹 Si cambias MODELS (schema change):
```
- [ ] FASE 1: Todos los tests ✅
- [ ] Crear migration: makemigrations
- [ ] Test rollback de migration
- [ ] FASE 2: CHANGELOG + DASHBOARD + DEUDA_TECNICA
- [ ] FASE 3: Smoke tests + regression
- [ ] FASE 4: Staging tests (si existe)
- [ ] FASE 5: Backup BD → Deploy → Verify
```

### 🔹 Si cambias VIEWS/PERMISSIONS:
```
- [ ] FASE 1: Todos los tests ✅
- [ ] MATRIZ_TRANSVERSAL_CAMBIOS: Verificar impacto
- [ ] Auditoría de permisos (si aplica)
- [ ] FASE 2: CHANGELOG + DASHBOARD
- [ ] FASE 3: Smoke tests + security check
- [ ] FASE 5: Deploy
```

### 🔹 Si cambias TEMPLATES/CSS:
```
- [ ] FASE 1: Tests ✅
- [ ] Collectstatic: python manage.py collectstatic
- [ ] FASE 2: CHANGELOG
- [ ] FASE 3: Visual check en diferentes browsers
- [ ] FASE 5: Deploy → Verify CSS loads
```

### 🔹 Si cambias CRITICAL SYSTEM (Backup, Permissions, etc):
```
- [ ] FASE 1: Tests ✅✅✅ con cobertura
- [ ] MATRIZ_TRANSVERSAL_CAMBIOS: Full audit
- [ ] REGISTRO_DECISIONES_TECNICAS: ADR si es importante
- [ ] DEUDA_TECNICA: Notar si introduce riesgos
- [ ] FASE 2: CHANGELOG + DASHBOARD + ESTADO_COMPONENTES
- [ ] FASE 3: Full testing suite
- [ ] FASE 4: Staging complete testing
- [ ] FASE 5: Backup → Deploy con comunicación → Full verify
```

---

## 📊 TABLA DE VERIFICACIONES POR SEVERIDAD

| Severidad | Fases Requeridas | Tiempo Estimado |
|---|---|---|
| 🟢 TRIVIAL (typo) | 1 + 5 | 5 min |
| 🟡 MINOR (UI improvement) | 1 + 2 + 3 + 5 | 20 min |
| 🟠 MAJOR (nuevo feature) | 1 + 2 + 3 + 4 + 5 | 1-2 horas |
| 🔴 CRITICAL (cambio de DB o permissions) | 1 + 2 + 3 + 4 + 5 + rollback plan | 3+ horas |

---

## 💾 REGISTRO DE DEPLOYMENTS

Cuando COMPLETE un deployment, agregar entrada aquí:

### ✅ Deployment: [FECHA] - [TIPO]

**Cambios:** [Qué se deployo]  
**Testeado en:** Local + Staging (si aplicó)  
**Deployed a:** Production  
**Hora:** HH:MM UTC  
**Status:** ✅ Success / 🔴 Rolled back  
**Verificaciones completadas:** [X fases de arriba]  
**Notas:** [Algo importante?]  

**Ejemplo:**
```
### ✅ Deployment: 2026-02-20 - HOTFIX

Cambios: ERROR #9 backup_manager import path
Testeado en: Local (5 tests passed)
Deployed a: Production
Hora: 14:30 UTC
Status: ✅ Success - All 3 endpoints working
Verificaciones: Fases 1,2,3,5 complete
Notas: Hotfix rápido, 3 endpoints vuelven a funcionar
```

---

## 🚨 PROBLEMAS COMUNES & SOLUCIONES

### Problema: Tests pasan local pero fallan en producción

**Causas comunes:**
- Diferencia en versiones (Python, Django, libs)
- Datos diferentes en BD con vs sin migraciones
- Paths absolutos vs relativos

**Solución:**
- Test en environment idéntico a prod
- Usar Docker si es posible
- Verificar versions en requirements.txt

### Problema: Deploy es lento o times out

**Causas:**
- DB migration tarda demasiado
- Collectstatic es lento
- Network latency

**Solución:**
- Hacer migrations en modo no-blocking
- Pre-test TODAS las migrations localmente
- Usar CDN para static files

### Problema: Rollback no funciona

**Causas:**
- Migration rollback no reversible
- Data schema incompatible

**Solución:**
- Ver DEBT-004 (Rollback testing)
- Mantener backup BD de antes de deploy

---

## 📌 IMPORTANTE

> **NUNCA SKIPEAR FASE 2 (Documentación)**
> 
> Si skippeas documentación, la próxima sesión perderá contexto.
> SIEMPRE actualiza:
> 1. CHANGELOG_DETALLADO.md
> 2. DASHBOARD_PROYECTO.md
> 3. Documento específico del cambio

> **SIEMPRE HAZ BACKUP ANTES DE PROD**
> 
> Si algo falla, es tu línea de defensa.

---

**Proxima actualización:** Cuando haya nuevo tipo de cambio o nuevo deployment
