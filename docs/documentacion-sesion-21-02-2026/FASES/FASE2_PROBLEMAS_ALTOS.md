# 🟠 FASE 2: PROBLEMAS ALTOS (40 horas)

**Estado:** Pendiente  
**Timeline:** 1-2 semanas  
**Impact:** Mejoras significativas en UX  
**Score Target:** 9.5 → 9.7/10  

---

## 📋 TABLA DE PROBLEMAS FASE 2

| # | Problema | Prioridad | Horas | Impacto | Status |
|---|----------|-----------|-------|---------|--------|
| **ALTO #1** | Búsqueda Dropdown en Reportes | 🟠 ALTO | 2h | UX mediocre | ❌ PENDING |
| **ALTO #2** | Input Moneda UI (Responsive) | 🟠 ALTO | 2h | Mobile UX | ❌ PENDING |
| **ALTO #3** | Importación Excel Mejorada | 🟠 ALTO | 3h | Data integrity | ❌ PENDING |
| **ALTO #4** | Mora en Tiempo Real (AJAX) | 🟠 ALTO | 3h | Data freshness | ❌ PENDING |
| | | | **10h** | | |

---

## ❌ ALTO #1: Búsqueda Dropdown NO FUNCIONA en Reportes

**Prioridad:** 🟠 ALTO  
**Impacto:** Reportes menos útiles  
**Dificultad:** ⭐ FÁCIL  
**Tiempo:** 2 horas  

### Problema Actual:
```html
<!-- en reporte_prestamos.html -->
<select name="cliente" id="cliente-search">
  <!-- Dropdown funciona para SELECCIONAR cliente -->
  <!-- PERO NO filtra los préstamos en la tabla abajo -->
</select>

<table id="prestamos-table">
  <!-- Muestra TODOS los préstamos -->
  <!-- Usuario debe scrollear y buscar manualmente -->
</table>
```

### Lo que debe pasar:
1. Usuario selecciona cliente en dropdown → ✅
2. Tabla se filtra automáticamente → ❌ NO PASA AHORA
3. Solo muestra préstamos de ese cliente → ❌ NO PASA AHORA

### Solución:
```javascript
// Agregar event listener al dropdown
$("#cliente-search").on("change", function() {
    const clienteId = $(this).val();
    
    if (clienteId) {
        $("#prestamos-table tbody tr").hide();
        $(`#prestamos-table tbody tr[data-cliente="${clienteId}"]`).show();
    } else {
        $("#prestamos-table tbody tr").show();
    }
});
```

### Files a modificar:
- `mi_app/templates/reportes/reporte_prestamos.html`
- `mi_app/static/js/reportes.js` (crear o actualizar)

---

## ❌ ALTO #2: Inputs de Moneda NO SON Responsive

**Prioridad:** 🟠 ALTO  
**Impacto:** UX mediocre especialmente en móvil  
**Dificultad:** ⭐ FÁCIL  
**Tiempo:** 2 horas  

### Problema Actual:
```html
<!-- ACTUAL (mala UX) -->
<input type="number" style="width: 50px;" name="monto" />
<!-- En móvil: campo muy pequeño, difícil de usar -->
<!-- Sin indicación clara que es DINERO -->
```

### Referencia en código:
- `mi_app/templates/forms/` - múltiples templates
- `mi_app/forms.py` - campos de MontoField

### Solución:
```html
<!-- CORRECTO (bootstrap) -->
<div class="input-group mb-3">
    <span class="input-group-text">$</span>
    <input type="number" 
           class="form-control" 
           name="monto"
           step="0.01"
           min="0"
           placeholder="0.00">
    <span class="input-group-text">COP</span>
</div>
```

### Beneficios:
- ✅ Responsive automático (Bootstrap)
- ✅ Claramente es dinero ($)
- ✅ Muestra moneda (COP)
- ✅ Mejor UX en móvil

### Files a modificar:
- `mi_app/templates/clientes/crear_cliente.html`
- `mi_app/templates/prestamos/crear_prestamo.html`
- `mi_app/templates/cuotas/registrar_pago.html`
- Otros templates con inputs de moneda

---

## ❌ ALTO #3: Importación Excel Incompleta

**Prioridad:** 🟠 ALTO  
**Impacto:** Posible pérdida de datos sin feedback  
**Dificultad:** ⭐⭐ MEDIA  
**Tiempo:** 3 horas  

### Problemas Actuales:

#### Problema 1: Error en 1 fila = TODO se cancela
```python
# ACTUAL (views.py - importar_excel):
def importar_excel(request):
    try:
        for row in excel_data:
            cliente = Cliente.objects.create(...)  # Si fila 10 falla
            # TODO se cancela, filas 1-9 se pierden ❌
    except Exception:
        return error()
```

**Debería ser:**
- Importar filas válidas: 95 OK ✅
- Reportar inválidas: 5 con error ❌
- Mostrar resumen al usuario

#### Problema 2: NO valida estructura
```python
# ACTUAL: 
# Si Excel tiene columnas faltantes → crash silencioso

# DEBERÍA:
# Verificar que existan: cedula, nombre, teléfono, etc.
# Si falta → error claro antes de empezar
```

#### Problema 3: Sin feedback de qué falló
```python
# ACTUAL:
# Usuario: "¿Por qué falló la importación?"
# Sistema: "Error" (sin detalles)

# DEBERÍA:
# "Fila 5: Cédula duplicada"
# "Fila 12: Teléfono inválido"
# "Fila 20: Email sin @"
```

### Solución:
```python
def importar_excel(request):
    errores = []
    exitosos = 0
    
    # Validar estructura primero
    columnas_requeridas = ['cedula', 'nombre', 'telefono', 'email']
    if not all(col in excel_headers for col in columnas_requeridas):
        return error("Faltan columnas requeridas: " + str(columnas_requeridas))
    
    # Procesar cada fila
    for idx, row in enumerate(excel_data, 1):
        try:
            # Validar
            if not validar_cedula(row['cedula']):
                errores.append(f"Fila {idx}: Cédula inválida")
                continue
            
            # Crear (sin transacción global)
            cliente = Cliente.objects.create(...)
            exitosos += 1
            
        except Exception as e:
            errores.append(f"Fila {idx}: {str(e)}")
    
    # Retornar resumen
    return {
        'exitosos': exitosos,
        'errores': errores,
        'total': len(excel_data)
    }
```

### Files a modificar:
- `mi_app/views.py` - función `importar_excel()`
- `mi_app/services/excel_import.py` (crear si no existe)
- `mi_app/templates/importar_excel.html`

---

## ❌ ALTO #4: Mora NO se actualiza en Tiempo Real

**Prioridad:** 🟠 ALTO  
**Impacto:** Usuario ve datos desactualizados  
**Dificultad:** ⭐⭐ MEDIA  
**Tiempo:** 3 horas  

### Problema Actual:
```
14:00 → Usuario abre "Detalle Cuota Vencida"
        Mora mostrada: $15.00 (calculada)

14:30 → Usuario aún viendo la MISMA página
        Mora = $15.00 (SIGUE IGUAL)
        
PERO en realidad:
        Mora debería ser: $15.30 (+$0.30 en 30 min)
        Usuario ve data INCORRECTA ❌
```

### Por qué pasa:
- Mora se calcula cuando carga la página
- NO se recalcula mientras página está abierta
- Usuario ve información "stale"

### Solución:

#### Opción 1: AJAX Refresh cada 30 segundos
```javascript
// Actualizar mora automáticamente
setInterval(function() {
    $.ajax({
        url: '/api/cuota/{id}/mora-actual/',
        method: 'GET',
        success: function(data) {
            $("#mora-display").text("$" + data.mora);
            $("#updated-at").text("Actualizado hace " + data.tiempo_atras);
        }
    });
}, 30000); // Cada 30 segundos
```

#### Opción 2: WebSocket Real-Time
```javascript
// Si necesita más real-time (cada segundo)
const ws = new WebSocket('ws://tuserver/mora-updates/');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    $("#mora-display").text("$" + data.mora);
};
```

### Files a modificar:
- `mi_app/views.py` - crear endpoint `/api/cuota/{id}/mora-actual/`
- `mi_app/templates/cuotas/detalle_cuota.html`
- `mi_app/static/js/mora-realtime.js` (crear)

---

## 📊 RESUMEN FASE 2

```
ALTO #1: Dropdown Reportes        2h  ⭐ FÁCIL
ALTO #2: Input Moneda UI          2h  ⭐ FÁCIL
ALTO #3: Excel Import Mejorada    3h  ⭐⭐ MEDIA
ALTO #4: Mora Tiempo Real         3h  ⭐⭐ MEDIA
──────────────────────────────────────────────
TOTAL:                           10h  

Impacto UX: SIGNIFICATIVO ↑↑↑
Impacto Score: +0.2 (9.5 → 9.7)
```

---

## 🎯 Orden Recomendado

1. **ALTO #1** (2h) - Fácil, rápido win ✅
2. **ALTO #2** (2h) - Fácil, mejora UX ✅
3. **ALTO #3** (3h) - Media, importante data ⏳
4. **ALTO #4** (3h) - Media, real-time ⏳

**Timeline:** 1-2 semanas (si trabajas 5-10h/día)

---

## ✅ Pre-requisitos antes de FASE 2

```
✅ FASE 1 (CRÍTICAs #1-10) COMPLETADA
✅ Sistema en producción
✅ Tests base en place
✅ Performance optimizado
✅ Datos consistentes
✅ Seguridad implementada

Ya puedes comenzar FASE 2
```

---

## 📝 Documentos de Referencia

- `PROBLEMAS_PRIORIZADO_COMPLETO.md` (líneas 700+)
- `plan y accion/PLAN_EJECUCION_DETALLADO.md` (sección FASE 2)

---

**¿Comenzamos con ALTO #1? 🚀**
