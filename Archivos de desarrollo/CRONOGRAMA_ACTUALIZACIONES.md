# 📅 CRONOGRAMA DE ACTUALIZACIONES - Agenda de Desarrollo

**Propósito:** Planificar qué se trabaja cuándo  
**Audiencia:** Lead técnico, Product manager, equipo  
**Frecuencia de actualización:** Al inicio de cada semana o iteración  

---

## 📊 VERSIONES PLANENADAS

### 🔴 v2.5 (ACTUAL - EN VIVO) - ✅ 70% COMPLETADO

| Feature | Componente | Status | ETA | Prioridad |
|---|---|---|---|---|
| ERROR #9 Backup hotfix | backup_manager | ✅ COMPLETED | 2026-02-20 | 🔴 |
| Reorganización proyecto | docs/ + scripts/ | ✅ COMPLETED | 2026-02-20 | 🔴 |
| Sistema documentos vivos | docs/sistemas/ | ✅ COMPLETED | 2026-02-20 | 🔴 |

---

### 🟠 v2.6 (PRÓXIMA - NEXT SPRINT)

**Target Release:** 2026-03-03 (10 días)  
**Scope:** Resolver E#3 y decide si E#4  

#### SPRINT 1 - PRÓXIMA SEMANA (2026-02-24 → 2026-03-03)

##### TASK 1: ERROR #3 - LIMPIEZA DE DATOS REPORTERÍA
**Prioridad:** 🔴 CRÍTICA  
**Esfuerzo:** 4-6 horas  
**Asignado a:** [Dev principal]  

**Subtareas:**
- [ ] Auditoria BD: Buscar registros huérfanos
  - [ ] Cuotas sin cliente
  - [ ] Clientes sin préstamos
  - [ ] Reportes inconsistentes
- [ ] Crear script de limpieza: `management/commands/cleanup_orphaned_data.py`
- [ ] Crear backup: `backup --label="pre-cleanup"`
- [ ] Ejecutar limpieza local
- [ ] Tests: Verificar reportería post-limpieza
- [ ] Documentos: CHANGELOG + DASHBOARD + ESTADO_COMPONENTES

**Done By:** 2026-02-26  
**Tests:** 5+ tests en `test_cleanup_orphaned.py`

---

##### TASK 2: ERROR #7 - INTERÉS COMPUESTO
**Prioridad:** 🔴 CRÍTICA  
**Esfuerzo:** 3-5 horas  
**Asignado a:** [Dev secundario]  
**Bloqueado por:** E#3 (Limpieza) ← Desbloquea ~2026-02-26

**Subtareas:**
- [ ] Cambiar fórmula en `utils.py`:
  - [ ] Actual: `amount * interest_rate`
  - [ ] Nuevo: `amount * (1 + interest_rate) ^ periods`
- [ ] Migraciones: ¿Recalcular cuotas viejas? (decision)
- [ ] Tests: Verificar fórmula en casos limite
- [ ] Reporte: Re-test "Interés Mensual"
- [ ] Documentos: ADR nuevo + CHANGELOG

**Done By:** 2026-02-28  
**Tests:** 10+ cases en `test_compound_interest.py`

---

##### TASK 3: TESTING & QA
**Prioridad:** 🟠 ALTA  
**Esfuerzo:** 2 horas  

- [ ] Crear integration tests: E#3 + E#7 juntos
- [ ] Regression tests: Full suite (453 tests)
- [ ] Performance: ¿Reportes más rápidos post-limpieza?
- [ ] Datos realesz en local DB

**Done By:** 2026-03-01

---

**Sprint Summary:**
```
2026-02-24: E#3 desarrollo
2026-02-25: E#3 testing + fix bugs
2026-02-26: E#3 completado, E#7 comienza
2026-02-27: E#7 desarrollo + fixing
2026-02-28: E#7 completado, testing
2026-03-01: Regression suite full
2026-03-02: Bugfixes finales
2026-03-03: RELEASE v2.6 con E#3 + E#7 ✅
```

**Version status:** v2.5 → v2.6 = 7/10 errores completados (70%)

---

### 🟡 v2.7 (Post-Sprint 1)

**Target Release:** 2026-03-17 (2 semanas after v2.6)  
**Scope:** Resolver E#4, E#5, E#6  

#### SPRINT 2 - SEMANA DE MARZO (2026-03-03 → 2026-03-17)

| Error | Tipo | Esfuerzo | Prioridad | Bloqueadores |
|---|---|---|---|---|
| E#4 | Préstamo rápido | 4h | 🟡 MEDIUM | None |
| E#5 | Lista negra | 3h | 🟡 MEDIUM | None |
| E#6 | Etiquetación | 4h | 🟡 MEDIUM | None |

**Sprint plan:**
- Día 1-2: E#4 (Préstamo + cuotas en un form)
- Día 2-3: E#5 (is_blacklisted field + validación)
- Día 3-5: E#6 (Tags M2M + búsqueda)
- Día 5-6: Testing + bugfixes
- Día 7: Release

**Version status:** v2.6 (70%) → v2.7 (100%) = PROYECTO COMPLETADO ✅

---

## 🗓️ ROADMAP ANUAL

```
FEBRERO (Current)
├─ 2026-02-20: v2.5 (50% done)
├─ 2026-02-20: Sistema documentos vivos ✅
├─ 2026-02-20: ERROR #9 hotfix ✅
└─ 2026-03-03: v2.6 target (70%)

MARZO
├─ 2026-02-24→03-03: E#3 + E#7
├─ 2026-03-03: v2.6 release
├─ 2026-03-17: v2.7 target (100%)
└─ 2026-03-17: Proyecto completado ✅

ABRIL+
├─ Mantenimiento
├─ Optimización
├─ Refactorización (ej: E#DEBT-001 grandes vistas)
└─ Features nuevas (si usuario pide)
```

---

## ⏰ HITOS IMPORTANTES

### 🎯 HITO 1: Sistemas críticos reparados
**Fecha:** 2026-02-20  
**Completado:** ✅
- ✅ ERROR #9 - Backups
- ✅ ERROR #8 - Permisos
- ✅ Documentación viva
**Impacto:** Proyecto estable + rastreable

### 🎯 HITO 2: Datos limpios + Interés correcto
**Fecha:** 2026-03-01 (planned)
- 🔵 ERROR #3 - Limpieza
- 🔵 ERROR #7 - Interés compuesto
**Impacto:** Reportería confiable

### 🎯 HITO 3: PROYECTO 100% COMPLETADO
**Fecha:** 2026-03-17 (planned)
- 🔵 ERROR #4 - Préstamo rápido
- 🔵 ERROR #5 - Lista negra
- 🔵 ERROR #6 - Etiquetación
**Impacto:** ALL FEATURES DONE, proyecto listo para producción

### 🎯 HITO 4+: Post-completion
**Fecha:** 2026-04-01+
- Mantenimiento
- Refactorización deuda técnica
- Features adicionales (si usuario pide)

---

## 📊 DISTRIBUCIÓN DE TIEMPO POR ERROR

| Error | Estimado | Real | % Total Proyecto |
|---|---|---|---|
| E#1 | 3h | ~5h | ~8% |
| E#2 | 1h | ~1h | ~2% |
| E#8 | 5h | ~6h | ~10% |
| E#9 | 1h | ~2h | ~3% |
| E#3 | 5h | TBD | ~8% |
| E#7 | 4h | TBD | ~7% |
| E#4 | 4h | TBD | ~7% |
| E#5 | 3h | TBD | ~5% |
| E#6 | 4h | TBD | ~7% |
| E#10 | 2h | ~2h | ~3% |
| Docs/Org | 8h | ~20h | ~33% |
| **TOTAL** | **40h** | **~36h+** | **100%** |

*Nota: Documentación/reorganización tomó más tiempo de lo esperado (pero vale la pena)*

---

## 📅 CALENDARIO DE SESIONES

```
SEMANA 1 (FEB 17-23)
├─ Sesión A: E#1, E#2, initial setup
├─ Sesión B: E#8 Permisos + Auditoría
└─ Sesión C: E#9 Hotfix + Reorganización

SEMANA 2 (FEB 24-MAR 2) 🔵 PRÓXIMO
├─ Sesión D: E#3 Limpieza [2h]
├─ Sesión E: E#3 Testing + E#7 Inicio [2h]
├─ Sesión F: E#7 Completado [2h]
└─ Sesión G: Regression + v2.6 Release [1h]

SEMANA 3 (MAR 3-9)
├─ Sesión H: E#4 Préstamo rápido [2h]
├─ Sesión I: E#5 Lista negra [1.5h]
├─ Sesión J: E#6 Etiquetación [2h]
└─ Sesión K: Testing de integradores [1.5h]

SEMANA 4 (MAR 10-16)
├─ Sesión L: Bugfixes finales [1h]
├─ Sesión M: Documentación final [1h]
└─ Sesión N: v2.7 RELEASE + Deploy [1h]

MARZO 17: 🎉 PROYECTO 100% COMPLETADO
```

---

## 🎯 CRITERIOS DE ÉXITO POR SPRINT

### v2.6 Success Criteria:
- [ ] E#3: Cleanup ejecutado, 0 orphaned records
- [ ] E#7: Interés compound correcto en 100% cuotas
- [ ] Tests: 453 → ??? (expected 500+)
- [ ] Reportería: Números verificables en auditoría
- [ ] Documentación: CHANGELOG + DASHBOARD actualizados

### v2.7 Success Criteria:
- [ ] E#4: Form combinado funciona, 10+ tests
- [ ] E#5: Blacklist previene préstamos, funciona filter
- [ ] E#6: Tags M2M versionado, búsqueda por tag
- [ ] Tests: Total 550+
- [ ] Proyecto: 10/10 ERRORES RESUELTOS ✅

---

## 📝 ACTUALIZAR ESTE ARCHIVO

### Al inicio de cada sesión:
- [ ] Actualizar Sprint actual con progreso
- [ ] Si fallas algo: mover a próxima semana
- [ ] Si completas algo: marcar ✅ con fecha

### Ejemplo de entrada de sesión:

```
### Sesión N - 2026-03-XX
Duración: 2.5h
Trabajó en: E#4 + E#5
Completado: E#4 form + tests (12 test cases)
Bloqueado: E#5 (descubrió que tags M2M requiere migration más compleja)
Para próxima: E#5 refactor + E#6
Documentación: CHANGELOG actualizado
```

---

## 🚀 DEPLOYMENT SCHEDULE

### Producción (Hostinger)
- **v2.5:** Deployed 2026-02-20 22:00 UTC
- **v2.6:** Planned 2026-03-03 14:00 UTC
- **v2.7:** Planned 2026-03-17 15:00 UTC

### Backup antes de cada Deploy
```bash
python manage.py backup --label="pre-v2.6-release"
```

### Monitor post-deploy (primeras 2h)
- [ ] Logs Clean
- [ ] Endpoints respondiendo
- [ ] Performance normal

---

## 🤝 REUNIONES PLANEADAS

### Standup Diario (Cuando hay sesión activa)
**Tiempo:** 10 min  
**Preguntas:**
- ¿Qué hice ayer?
- ¿Qué hago hoy?
- ¿Hay bloqueadores?

### Sprint Review (At end of Sprint)
**Fecha:** 2026-03-03, 19:00 UTC  
**Agenda:**
- Demo de E#3 + E#7
- Métricas: Tests, performance, coverage
- Feedback usuario

### Sprint Planning (Before next Sprint)
**Fecha:** 2026-03-03, 20:00 UTC  
**Agenda:**
- Backlog priorities
- Story pointing (E#4, E#5, E#6)
- Team capabilities

---

**Próxima actualización:** 2026-02-24 (inicio SPRINT 1)  
**Revisión anual:** 2026-04-01
