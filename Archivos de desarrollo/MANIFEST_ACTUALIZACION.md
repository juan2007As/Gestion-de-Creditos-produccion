# 📋 MANIFEST DE ACTUALIZACIÓN - Qué Actualizar Cuándo

**Propósito:** Ser la "checklist maestra" de qué documentos actualizar en cada escenario  
**Audiencia:** TODOS los desarrolladores  
**Frecuencia:** ANTES de cada sesión, DESPUÉS de cada cambio, ANTES de cada commit  

---

## 🟢 ACTUALIZAR CADA SESIÓN DE TRABAJO

**OBLIGATORIO - No saltarse:**

### 1️⃣ Al INICIAR sesión:
- [ ] Leer: `DASHBOARD_PROYECTO.md` (5 min)
  - ¿Cuál es el estado actual?
  - ¿Qué errores están pendientes?
  
- [ ] Leer: `CHANGELOG_DETALLADO.md` (5 min)
  - ¿Qué cambios se han hecho recientemente?
  - ¿Hay breaking changes?

- [ ] Leer: `DEUDA_TECNICA.md` (5 min)
  - ¿Hay algo que evitar?
  - ¿Hay workarounds que aplicar?

### 2️⃣ DURANTE la sesión (cada cambio importante):
- [ ] Actualizar: `CHANGELOG_DETALLADO.md`
  - Agregar sección con el cambio que hiciste
  - Incluir fecha, severidad, impact

- [ ] Actualizar: `ESTADO_COMPONENTES.md`
  - Si tocaste algún componente, actualiza su status
  - Versión, fecha última revisión

### 3️⃣ Antes de cada COMMIT:
- [ ] Leer: `MATRIZ_TRANSVERSAL_CAMBIOS.md`
  - ¿Mi cambio afecta otras partes?
  - ¿Hay dependencias?

- [ ] Actualizar: `CHECKLIST_DEPLOYMENT.md`
  - Marcar qué se verificó
  - Notar cualquier nueva prueba

- [ ] Actualizar: `DASHBOARD_PROYECTO.md`
  - Cambiar métricas si aplica
  - Actualizar status general

- [ ] Actualizar: `CHANGELOG_DETALLADO.md`
  - AGREGAR ENTRADA FINAL del cambio

- [ ] **EJECUTAR GIT COMMIT**

### 4️⃣ Cuando termina la sesión:
- [ ] Actualizar: `DASHBOARD_PROYECTO.md` (última fila)
  - "Última sesión completada: [fecha]"
  - Stock de lo que se hizo

---

## 🟠 ACTUALIZAR CUANDO...

### ...Agregas una decisión arquitectónica
**Documento:** `REGISTRO_DECISIONES_TECNICAS.md`
- Qué se decidió
- Por qué se decidió
- Alternativas consideradas
- Impacto futuro

**Ejemplo:**
```
## ADR-004: Usar SQLite3 local (2026-02-20)
**Decisión:** SQLite para desarrollo local, PostgreSQL para producción
**Alternativas:** MongoDB (no), MySQL (posible)
**Impacto:** Migraciones futuras requerirán script
```

### ...Descubres un bug o limitación
**Documento:** `DEUDA_TECNICA.md`
- Qué es el problema
- Severidad
- Workaround (si existe)
- Quién lo creó
- Cuándo arreglarlo

### ...Completas un error/feature
**Documentos a actualizar:**
1. `DASHBOARD_PROYECTO.md` - Cambiar contador E#X de pendiente a completado
2. `CHANGELOG_DETALLADO.md` - Agregar entrada con detalles
3. `INDICE_BUGS_POR_COMPONENTE.md` - Cambiar status

### ...Necesitas una checklist para deploy
**Documento:** `CHECKLIST_DEPLOYMENT.md`
- Agregar verificación nueva
- Documentar quién la verifica
- Cuándo falló y cómo se arregló

---

## 🔵 TABLAS DE FRECUENCIA

### Documento → Cuándo actualizar

| Documento | Frecuencia | Responsable | Crítico |
|-----------|-----------|-------------|---------|
| DASHBOARD_PROYECTO.md | Al terminar sesión | Dev | ✅ |
| CHANGELOG_DETALLADO.md | ANTES de commit | Dev | ✅ |
| MANIFEST_ACTUALIZACION.md | Cuando cambian procesos | Lead | ⚠️ |
| MATRIZ_TRANSVERSAL_CAMBIOS.md | Cuando agregamos módulos | Architect | ⚠️ |
| ESTADO_COMPONENTES.md | Cada cambio técnico | Dev | ⚠️ |
| REGISTRO_DECISIONES_TECNICAS.md | Decisiones importante | Lead | ✅ |
| DEUDA_TECNICA.md | Cuando descubres bugs | Dev | ⚠️ |
| CHECKLIST_DEPLOYMENT.md | Antes de producción | QA/Lead | ✅ |
| INDICE_BUGS_POR_COMPONENTE.md | Cuando cierras bug | Dev | ⚠️ |
| CRONOGRAMA_ACTUALIZACIONES.md | Planificación semanal | Lead | ⚠️ |

---

## 💡 TIPS PRÁCTICOS

### Actualizar rápido (3 minutos):
1. Abrir DASHBOARD_PROYECTO.md
2. Cambiar 2-3 líneas de status
3. Git add + commit

### Actualizar correctamente (10 minutos):
1. CHANGELOG → agregar cambios
2. ESTADO_COMPONENTES → verificar si algo cambió
3. DASHBOARD → actualizar métricas
4. Commit

### Ritual de sesión completa (30 minutos):
1. Inicio: Leer Dashboard + Changelog (5 min)
2. Trabajo: Cambios (20 min)
3. Fin: Actualizar docs + Commit (5 min)

---

## ⚠️ REGLA DE ORO

> **ANTES de hacer git commit, tu sesión NO está completa hasta actualizar mínimo:**
> 1. CHANGELOG_DETALLADO.md ✅
> 2. DASHBOARD_PROYECTO.md ✅
> 3. El documento específico del cambio (ESTADO_COMPONENTES, REGISTRO_DECISIONES, etc) ✅

**Si no actualizaste estos 3, tu commit está INCOMPLETO.**

---

## 🎯 FLUJO INTEGRADO

```
[INICIO SESIÓN]
    ↓
[LEER: Dashboard + Changelog + DeudaTécnica]
    ↓
[TRABAJAR: Cambios, tests, fixes]
    ↓
[ACTUALIZAR: Changelog durante el trabajo]
    ↓
[ANTES COMMIT: Matriz, Checklist, Dashboard]
    ↓
[COMMIT: Todo junto]
    ↓
[FIN SESIÓN: Dashboard.md = última actualización]
```

---

## 📌 CHECKLIST RÁPIDA PARA COPIAR/PEGAR

```markdown
## SESIÓN [FECHA]

- [ ] Leí DASHBOARD_PROYECTO.md
- [ ] Leí CHANGELOG_DETALLADO.md
- [ ] Leí DEUDA_TECNICA.md
- [ ] Hice cambios en [ARCHIVO] por razón [RAZÓN]
- [ ] Actualicé CHANGELOG_DETALLADO.md
- [ ] Actualicé DASHBOARD_PROYECTO.md
- [ ] Actualicé [DOC ESPECÍFICA] si aplica
- [ ] Ejecuté tests: [X/X PASSED]
- [ ] Commit: "TIPO: Descripción"
- [ ] ✅ SESIÓN COMPLETA
```

**Próxima revisión:** Mensual o cuando cambie la estructura del proyecto
