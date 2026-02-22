# 🎯 TESTING INTERACTIVO - ORIENTACIÓN INICIAL

**Fecha:** 21 de Febrero de 2026  
**Estado:** Listo para comenzar testing

---

## 📁 Archivos Creados

```
pruebas_humano/
├── DATOS_PRUEBA_CLIENTE.xlsx          ← Excel con 1 cliente, 3 préstamos
└── GUIA_TESTING_COMPLETA.md           ← Este archivo (12 pasos completos)
```

## ✅ Qué Está Listo

1. **Excel de Importación**: `DATOS_PRUEBA_CLIENTE.xlsx`
   - Cliente: Juan Carlos Pérez (1234567890)
   - 3 filas (3 préstamos para el mismo cliente)
   - Montos: $500k, $750k, $300k
   - Interés: 15% todos
   - Cuotas: 2, 3, 1 respectivamente

2. **Guía Completa**: `GUIA_TESTING_COMPLETA.md`
   - 12 PASOS detallados de testing
   - Desde LOGIN hasta LIST NEGRA
   - Verificaciones específicas en cada paso
   - Comandos SQL y Python para debugging

---

## 🚀 CÓMO PROCEDER AHORA

### Opción A: Testing Manual Paso a Paso (RECOMENDADO)

1. **Abre** la guía: `pruebas_humano/GUIA_TESTING_COMPLETA.md`
2. **Sigue PASO 1**: Preparación y Login
3. **Sigue PASO 2**: Importación Excel
4. **Continúa secuencialmente** hasta PASO 12

**Tiempo estimado:** 60-90 minutos para completar todos los pasos

### Opción B: Testing Interactivo con Ajustes Dinámicos

**Tu flujo:**
1. Dime qué quieres prueba/ajustar:
   - "Agrega mora a Cuota #2"
   - "Cambia la tasa de interés"
   - "Crea un pago de $100,000"
   - "Muestra el scoring del cliente"
   - etc.

2. Yo ejecutaré los cambios en la BD/Sistema
3. Veremos el resultado juntos
4. Documentaré lo que funcionó/falló

**Tiempo estimado:** Variable, según tu necesidad

---

## ❓ ¿QUÉ HAGO PRIMERO?

### Si quieres ir PASO A PASO (máxima coverage):
👉 **Sigue la guía en orden** 
- PASO 1: Login
- PASO 2: Importar Excel
- PASO 3: Ver Cliente
- (y así sucesivamente...)

### Si quieres TESTING DINÁMICO (ajustes reales):
👉 **Cuéntame QUÉ quieres probar:**

Ejemplos:
- "Importa el Excel y muéstrame cómo quedó"
- "Registra un pago de $100,000 a la primera cuota"
- "Muéstrame qué pasa con la mora después de 10 días"
- "Agrega el cliente a lista negra manualmente"
- "Genera un reporte de morosidad"
- "Cambia el rating del cliente de SIN_HISTORIAL a BUENO"
- "Exporta los datos a Excel"
- "Crea un nuevo préstamo de $1,000,000 para el mismo cliente"

---

## 📊 RESUMEN DE FUNCIONALIDADES A VALIDAR

```
✓ AUTENTICACIÓN
✓ IMPORTACIÓN EXCEL
✓ GESTIÓN DE CLIENTES
✓ CREACIÓN DE PRÉSTAMOS
✓ GENERACIÓN DE CUOTAS
✓ CÁLCULO DE MORA
✓ REGISTRO DE PAGOS (Completo, Parcial, con Mora)
✓ VALIDACIONES
✓ REPORTES
✓ EXPORTACIÓN
✓ BÚSQUEDA Y FILTROS
✓ ANÁLISIS Y SCORING
✓ LISTA NEGRA
✓ RESPONSIVE DESIGN
✓ INTEGRIDAD DE DATOS
```

---

## 🎯 TÚ DECIDES EL RUMBO

**Yo estoy listo para:**

1. ✅ Guiar paso a paso por la guía (si quieres máximo orden)
2. ✅ Hacer cambios dinámicos en la BD (si quieres testing real)
3. ✅ Combinar: Seguir guía pero con ajustes interactivos
4. ✅ Debugging y análisis de cualquier error que encuentres

**¿Cuál prefieres?**

---

*Documento generado automáticamente para orientación de testing*
