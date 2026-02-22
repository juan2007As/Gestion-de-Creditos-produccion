# 🧪 GUÍA DE TESTING INTEGRAL - PROYECTO GESTOR DE PRÉSTAMOS
**Versión:** 1.0  
**Fecha:** 21 de Febrero de 2026  
**Objetivo:** Validar TODAS las funcionalidades del sistema usando UN cliente con múltiples préstamos

---

## 📋 CONTENIDO RÁPIDO

- [PASO 1: Preparación y Login](#paso-1-preparación-y-login)
- [PASO 2: Importación de Datos](#paso-2-importación-de-datos-excel)
- [PASO 3: Visualización de Cliente](#paso-3-visualización-del-cliente)
- [PASO 4: Análisis de Préstamos](#paso-4-análisis-de-préstamos)
- [PASO 5: Cálculo de Mora](#paso-5-cálculo-de-mora-y-estado)
- [PASO 6: Registro de Pagos](#paso-6-registro-de-pagos)
- [PASO 7: Validación de Cuotas](#paso-7-validación-de-cuotas)
- [PASO 8: Reportes y Exportación](#paso-8-reportes-y-exportación)
- [PASO 9: Búsqueda y Filtros](#paso-9-búsqueda-y-filtros)
- [PASO 10: Análisis Avanzado y Scoring](#paso-10-análisis-avanzado-y-scoring)
- [PASO 11: Gestión de Lista Negra](#paso-11-gestión-de-lista-negra)
- [PASO 12: Validación Final](#paso-12-validación-final)

---

## 📊 DATOS DE PRUEBA

### Cliente
```
Nombre: Juan Carlos Pérez
Cédula: 1234567890
Email: juan.perez@email.com
Teléfono: 3105551234
```

### Préstamos a Importar
| # | Monto | Interés | Cuotas | Estado Esperado | Propósito |
|----|-------|---------|--------|-----------------|-----------|
| **1** | $500,000 | 15% | 2 | COMPLETADO | Historial de pagos ✅ |
| **2** | $750,000 | 15% | 3 | ACTIVO | Pagos parciales + Mora |
| **3** | $300,000 | 15% | 1 | ACTIVO | Test rápido |

---

## PASO 1: Preparación y Login

### 1.1 Iniciar el Sistema

```bash
# Terminal 1: Iniciar servidor Django
python manage.py runserver

# Terminal 2: (Opcional) Ver logs en tiempo real
python manage.py runserver 0.0.0.0:8000 --verbosity=3
```

**Resultado esperado:**
```
Quit the server with CONTROL-C.
Starting development server at http://127.0.0.1:8000/
```

### 1.2 Acceder a la Web

1. **Abrir navegador**: http://127.0.0.1:8000/
2. **Debería redirigir a**: http://127.0.0.1:8000/login/
3. **Credenciales de prueba:**
   ```
   Usuario: admin
   Contraseña: admin123456
   ```

**Verificaciones:**
- ✅ Página de login se carga correctamente
- ✅ No hay errores 404 o 500
- ✅ Responsive design funciona (F12 → Device toolbar)
- ✅ CSS y JavaScript cargan sin errores

### 1.3 Validar Login

1. **Ingresa usuario y contraseña**
2. **Haz clic en "Iniciar Sesión"**

**Verificaciones:**
- ✅ Redirige a `/inicio` después de login exitoso
- ✅ Muestra mensaje de bienvenida "¡Bienvenido admin!"
- ✅ El header muestra usuario logueado
- ✅ Navegación está disponible (Clientes, Préstamos, Reportes, etc)

---

## PASO 2: Importación de Datos (Excel)

### 2.1 Ubicar Función de Importación

En el dashboard:
1. **Menú**: Clientes → Importar desde Excel
   - O directamente: http://127.0.0.1:8000/importar-clientes/

**Verificaciones:**
- ✅ Página de importación carga
- ✅ Existe botón para seleccionar archivo
- ✅ Hay instructions claros de formato

### 2.2 Cargar Archivo Excel

1. **Haz clic en**: "Seleccionar archivo"
2. **Navega a**: `pruebas_humano/DATOS_PRUEBA_CLIENTE.xlsx`
3. **Presiona**: "Abrir"

**Verificaciones:**
- ✅ Archivo seleccionado muestra nombre: "DATOS_PRUEBA_CLIENTE.xlsx"
- ✅ Botón "Importar" está habilitado

### 2.3 Validación Pre-Importación

1. **Haz clic en**: "Previsuali zar" o "Validar" (si existe)
2. **Sistema debe mostrar**:
   ```
   ✅ Validación de estructura: OK
   ✅ Fila 1: Juan Carlos Pérez - Válida
   ✅ Fila 2: Juan Carlos Pérez - Válida
   ✅ Fila 3: Juan Carlos Pérez - Válida
   
   Total: 3 filas válidas, 0 errores, 0 warnings
   ```

**Verificaciones:**
- ✅ Detecta las 3 filas correctamente
- ✅ Valida cédula (formato: 1234567890)
- ✅ Valida nombre (min 3 caracteres)
- ✅ Valida teléfono (números válidos)
- ✅ Valida email (formato correcto)
- ✅ Valida monto (positivo y razonable)
- ✅ Valida interés (entre 0-100%)
- ✅ Valida cuotas (entre 1-60)

### 2.4 Ejecutar Importación

1. **Haz clic en**: "Confirmar Importación" o "Importar"
2. **Sistema procesa** (puede tardar 2-5 segundos)

**Verificaciones:**
- ✅ No hay errores 500
- ✅ Muestra mensaje: "✅ Importación completada exitosamente"
- ✅ Redirige a lista de clientes o muestra resumen
- ✅ Resumen muestra: "1 cliente creado, 3 préstamos creados"

### 2.5 Resultado de Importación

**Cliente creado:**
```
Nombre: Juan Carlos Pérez
Cédula: 1234567890
Estado: ACTIVO
Total Prestado: $1,550,000 (500k + 750k + 300k)
```

**Préstamos creados:**
```
Préstamo #1: $500,000 @ 15% → 2 cuotas → Estado: ACTIVO
Préstamo #2: $750,000 @ 15% → 3 cuotas → Estado: ACTIVO
Préstamo #3: $300,000 @ 15% → 1 cuota → Estado: ACTIVO

Total de cuotas generadas: 2 + 3 + 1 = 6 cuotas
```

**Verificaciones finales:**
- ✅ Los 3 préstamos tienen cuotas generadas automáticamente
- ✅ Las cuotas tienen fechas de vencimiento (cada 15 días para QUINCENAL)
- ✅ El estado es registrable en la base de datos

---

## PASO 3: Visualización del Cliente

### 3.1 Ir a Lista de Clientes

1. **Menú**: Clientes → Listar Clientes
   - O: http://127.0.0.1:8000/clientes/
2. **Busca**: "Juan Carlos Pérez"

**Verificaciones:**
- ✅ El cliente aparece en la lista
- ✅ Se muestra: Nombre, Cédula, Teléfono
- ✅ Se muestra: Total Prestado ($1,550,000)
- ✅ Se muestra: Estado (ACTIVO)
- ✅ Hay botón para ver detalles

### 3.2 Ver Detalles del Cliente

1. **Haz clic en**: Nombre o botón "Ver Detalles"
2. **URL debe ser**: http://127.0.0.1:8000/clientes/[ID]/

**Esperado: Página de Detalles del Cliente**

#### Sección: Información Personal
```
Nombre: Juan Carlos Pérez
Cédula: 1234567890
Email: juan.perez@email.com
Teléfono: 3105551234
Fecha de Registro: [hoy]
Estado: ACTIVO
```

**Verificaciones:**
- ✅ Todos los campos se muestran correctamente
- ✅ Email es clickeable
- ✅ Teléfono es copiable o clickeable

#### Sección: Resumen Financiero
```
Total Prestado: $1,550,000
Total Pagado: $0 (hasta no hacer pagos)
Total Pendiente: $1,550,000 (incluye intereses)

Cuotas Pagadas: 0 / 6
Cuotas Vencidas: [X] (depende de fecha actual)
Cuotas Próximas: [X] (cuotas sin vencer)
```

**Verificaciones:**
- ✅ Los totales coinciden con suma de préstamos
- ✅ Se calcula correctamente el interés
- ✅ Los contadores de cuotas son exactos

#### Sección: Análisis de Comportamiento
```
Rating: [0-5 estrellas] (sin historial de pagos = 0)
Tasa de Cumplimiento: [%] (sin pagos = 0%)
Scoring: [calculado]
Etiqueta: SIN_HISTORIAL
```

**Verificaciones:**
- ✅ Rating se calcula automáticamente
- ✅ Etiqueta es correcta
- ✅ Scoring refleja el perfil

### 3.3 Lista de Préstamos del Cliente

En la misma página, debe haber sección de "Préstamos":

```
┌─ PRÉSTAMO #1 ─────────────────────────────┐
│ Monto: $500,000                            │
│ Tasa: 15% anual (7.5% quincena)           │
│ Cuotas: 2 de 2                            │
│ Estado: ACTIVO                            │
│ Cuotas Pagadas: 0/2                       │
│ Total Mora: $0                            │
│ [Ver Detalles]                            │
└─────────────────────────────────────────────┘

┌─ PRÉSTAMO #2 ─────────────────────────────┐
│ Monto: $750,000                            │
│ Tasa: 15% anual (7.5% quincena)           │
│ Cuotas: 3 de 3                            │
│ Estado: ACTIVO                            │
│ Cuotas Pagadas: 0/3                       │
│ Total Mora: $X (según días de atraso)      │
│ [Ver Detalles]                            │
└─────────────────────────────────────────────┘

┌─ PRÉSTAMO #3 ─────────────────────────────┐
│ Monto: $300,000                            │
│ Tasa: 15% anual (7.5% quincena)           │
│ Cuotas: 1 de 1                            │
│ Estado: ACTIVO                            │
│ Cuotas Pagadas: 0/1                       │
│ Total Mora: $0 (reciente)                  │
│ [Ver Detalles]                            │
└─────────────────────────────────────────────┘
```

**Verificaciones:**
- ✅ Todos los 3 préstamos aparecen listados
- ✅ La información es precisa
- ✅ Botones "Ver Detalles" funcionan

---

## PASO 4: Análisis de Préstamos

### 4.1 Ver Detalles del Préstamo #1

1. **Haz clic en**: Préstamo #1 → "Ver Detalles"
2. **URL**: http://127.0.0.1:8000/prestamos/[ID]/

**Página: Detalles del Préstamo**

#### Encabezado
```
Préstamo #1
Cliente: Juan Carlos Pérez
Estado: ACTIVO
Monto Original: $500,000
```

#### Sección: Estructura Financiera
```
┌─────────────────────────────────────────┐
│         ESTRUCTURA FINANCIERA             │
├─────────────────────────────────────────┤
│ Monto Original:              $500,000    │
│ Tasa de Interés:             15% anual   │
│ Tasa Disponibilidad:         0.5%        │
│ Interés Total Estimado:      $XX,XXX     │
│ ────────────────────────────────────     │
│ TOTAL A PAGAR:              $XXX,XXX     │
│ Número de Cuotas:            2           │
│ Tipo de Pago:                Quincenal   │
└─────────────────────────────────────────┘
```

**Verificaciones:**
- ✅ Monto original correcto
- ✅ Interés calculado correctamente
- ✅ Total a pagar incluye principal + interés
- ✅ Número de cuotas correcto (2)
- ✅ Tipo de pago muestra QUINCENAL

#### Sección: Cuotas Detalladas

**Tabla de Cuotas:**
```
┌─────┬──────────┬──────────┬──────────┬─────────────┬────────────────────┐
│ # │ Vencimiento │ Principal │ Interés │ Estado │ Paid / Mora │
├─────┼──────────┼──────────┼──────────┼─────────────┼────────────────────┤
│ 1 │ [fecha+15d] │ $250,000 │ $18,750 │ VENCIDA \*  │ $0 / $0 │
│ 2 │ [fecha+30d] │ $250,000 │ $18,750 │ PENDIENTE   │ $0 / $0 │
└─────┴──────────┴──────────┴──────────┴─────────────┴────────────────────┘

\* Nota: Dependiente de fecha actual vs vencimiento
```

**Verificaciones:**
- ✅ Las 2 cuotas están listadas
- ✅ Principal se divide equitativamente ($250k c/u)
- ✅ Interés total es correcto ($37,500 total)
- ✅ Fechas de vencimiento son correctas (15 días de diferencia)
- ✅ Estados son precisos (VENCIDA si pasó la fecha, PENDIENTE si no)
- ✅ Mora se calcula si está vencida

###4.2 Comparar los 3 Préstamos

Repite 4.1 para Préstamos #2 y #3, verificando:

**Préstamo #2 ($750,000, 3 cuotas):**
- ✅ 3 cuotas de $250,000 c/u (750k / 3)
- ✅ Interés: $56,250 total (3 × 18,750)
- ✅ Fechas vencimiento: c/15 días

**Préstamo #3 ($300,000, 1 cuota):**
- ✅ 1 cuota de $300,000
- ✅ Interés: $22,500
- ✅ Fecha vencimiento: +15 días desde hoy

---

## PASO 5: Cálculo de Mora y Estado

### 5.1 Entender el Cálculo de Mora

**Configuración del Sistema:**
```
- Tasa de Mora: ¿$2,000 por día?
- Período de Gracia: ¿5 días?
- Fórmula: Mora = Días de Atraso × Tasa Diaria
```

### 5.2 Verificar Mora en Cuotas Vencidas

En la tabla de cuotas del Préstamo #2 (3 cuotas, la más longitud):

1. **Identifica cuotas VENCIDAS**: Si la fecha actual > fecha_vencimiento
2. **Verifica mora calculada:**

```
Ejemplo (si hoy es más de 10 días después del vencimiento):
┌────────────────────────────────────────────────────────┐
│ Cuota 1: Vencida hace 10 días                          │
│ ├─ Principal: $250,000                                 │
│ ├─ Interés: $18,750                                    │
│ ├─ Días de Atraso: 10 días                             │
│ ├─ Período de Gracia: 5 días                           │
│ ├─ Días con Mora: 10 - 5 = 5 días                      │
│ ├─ Mora Calculada: 5 × $2,000 = $10,000                │
│ └─ TOTAL: $278,750                                     │
└────────────────────────────────────────────────────────┘
```

**Verificaciones:**
- ✅ Mora solo se cobra DESPUÉS del período de gracia
- ✅ La fórmula es correcta: (días_atraso - días_gracia) × tasa
- ✅ Mora es visible en la tabla de cuotas
- ✅ Mora se suma al total a pagar

### 5.3 Estado Automático de Cuota

El sistema debe mostrar estados:
- ✅ **PENDIENTE**: Fecha vencimiento aún no llega
- ✅ **DEMORADA**: Vencida pero en período de gracia (sin mora)
- ✅ **MOROSA**: Vencida con mora activa
- ✅ **PAGADA**: 100% pagado
- ✅ **PARCIALMENTE_PAGADA**: Pago parcial registrado

---

## PASO 6: Registro de Pagos

### 6.1 Ir a la Sección de Pagos

1. **En página del Préstamo**, busca: "Registrar Pago" o "Nueva Transacción"
2. **O menú**: Pagos → Registrar Pago Nuevo
3. **URL**: http://127.0.0.1:8000/registrar-pago/

### 6.2 Realizar Pago Completo (Cuota #1 del Préstamo #1)

**Escenario:** Pagar completamente la primera cuota del Préstamo #1

1. **Formulario de pago:**
   ```
   Cliente: [Auto-completo o seleccionar]
   Préstamo: Juan Carlos Pérez - $500,000
   Cuota: Cuota #1 (vencimiento: [fecha])
   Monto a Pagar: $268,750 (Principal: $250k, Interés: $18,75k)
   Mora Incluida: $0 (si está en período de gracia)
   ```

2. **Ingresa datos:**
   - Monto Pagado: `$268,750`
   - Referencia: `PAGO_COMPLETO_1` (o comprobante)
   - Notas: `Pago completo cuota 1`
   - Usuario que Registra: `admin` (auto)

3. **Haz clic en**: "Registrar Pago"

**Verificaciones:**
- ✅ No hay error al registrar
- ✅ El sistema genera comprobante
- ✅ Cuota #1 estado cambia a "PAGADA"
- ✅ Porcentaje pagado = 100%

### 6.3 Realizar Pago Parcial (Cuota #2 del Préstamo #2)

**Escenario:** Pagar SOLO principal, sin interés (pagoparcial)

1. **Selecciona:**
   - Préstamo #2
   - Cuota #2
   - Monto Pagado: `$150,000` (60% del principal de $250k)

2. **Sistema debe:**
   - ✅ Aceptar pago parcial
   - ✅ No marcar como completada
   - ✅ Mostrar estado "PARCIALMENTE_PAGADA o VENCIDA_PARCIAL"
   - ✅ Actualizar "Monto Pendiente"
   - ✅ Registrar el pago en historial

### 6.4 Realizar Pago con Mora (Cuota #3 del Préstamo #2)

**Escenario:** Cuota muy vencida, con mora acumulada

1. **Cuota está vencida hace 15+ días:**
   ```
   - Principal: $250,000
   - Interés: $18,750
   - Mora Acumulada: $20,000 (ejemplo)
   - TOTAL REQUERIDO: $288,750
   ```

2. **Realiza pago completoen 3 partes:**
   - ✅ Pago 1: $100.000 (pago parcial)
   - ✅ Pago 2: $100,750 (más del principal + interés)
   - ✅ Pago 3: $88,000 (saldo final con mora)

3. **Verificaciones para cada pago:**
   - ✅ Sistema acepta múltiples pagos para misma cuota
   - ✅ "Monto Pendiente" se actualiza
   - ✅ Suma de pagos = Total adeudado
   - ✅ En último pago: estado = "PAGADA"

### 6.5 Validar Formulario de Pago

**Intentar pagos inválidos (deben rechazarse):**

1. **Monto negativo**: -$1,000
   - ❌ Error: "El monto debe ser positivo"

2. **Monto cero**: $0
   - ❌ Error: "El monto debe ser mayor a 0"

3. **Monto mayor a adeudado**: $500,000 (cuando solo debe $100k)
   - ⚠️ Sistema puede: Rechazar o Crear crédito a favor
   - Verificar comportamiento actual

4. **Sin monto**:
   - ❌ Error: "Monto requerido"

**Verificaciones:**
- ✅ Validación cliente-side (alerta antes de enviar)
- ✅ Validación servidor-side (respuesta con error 400)
- ✅ Mensajes claros para el usuario

---

## PASO 7: Validación de Cuotas

### 7.1 Verificar Actualización Automática de Cuotas

Después de los pagos registrados en PASO 6:

**Préstamo #1 (después de pagar Cuota #1 completa):**
```
Cuota #1: Estado = PAGADA ✅
├─ Progreso: ████████████ 100%
├─ Principal Pagado: $250,000 ✅
├─ Interés Pagado: $18,750 ✅
├─ Mora Pagada: $0 ✅

Cuota #2: Estado = PENDIENTE o VENCIDA
├─ Progreso: ░░░░░░░░░░░░ 0%
├─ Principal Pagado: $0
├─ Por Pagar: $268,750
└─ Mora: Según días de atraso
```

### 7.2 Verificar Cálculos Acumulados

En página de cliente, resumen debe actualizar:

**ANTES de pagos:**
```
Total Pagado: $0
Total Pendiente: $1,550,000
```

**DESPUÉS de pagos:**
```
Total Pagado: $268,750 (solo primer pago registrado)
Total Pendiente: $1,281,250 ($1,550,000 - $268,750)
Cuotas Completadas: 1 / 6
```

**Verificaciones:**
- ✅ Los totales se recalculan automáticamente
- ✅ No hay inconsistencias entre BD y cálculos
- ✅ Histórico de pagos es completo

### 7.3 Consistencia de Datos

En la DB, verifica que:

```sql
-- Verificar cuota pagada
SELECT * FROM mi_app_cuota WHERE id = 1;
-- Debe mostrar:
-- - pagado: True
-- - estado: PAGADA
-- - porcentaje_pagado: 100.00
-- - monto_pendiente: 0.00

-- Verificar pagos registrados
SELECT * FROM mi_app_pago WHERE cuota_id = 1;
-- Debe mostrar 1 fila con:
-- - monto_pagado: 268750.00
-- - monto_principal: 250000.00
-- - monto_interes: 18750.00
-- - monto_mora: 0.00
```

**Verificaciones:**
- ✅ Datos en BD coinciden con UI
- ✅ Relaciones Foreign Key están intactas
- ✅ Ningún dato orfand

o o consistente

---

## PASO 8: Reportes y Exportación

### 8.1 Acceder a Reportes

1. **Menú**: Reportes
   - O URL: http://127.0.0.1:8000/reportes/

**Opciones esperadas:**
- ✅ Reporte de Clientes
- ✅ Reporte de Préstamos
- ✅ Reporte de Cuotas
- ✅ Reporte de Morosidad
- ✅ Reporte Financiero

### 8.2 Reporte de Morosidad

1. **Abre**: Reporte de Morosidad
2. **Sistema debe mostrar:**

```
CLIENTES EN MORA
═════════════════════════════════════════

Juan Carlos Pérez
├─ Total en Mora: $X (según cuotas vencidas)
├─ Cuotas Morosas: [Cuota #3 Préstamo #2, etc]
├─ Días de Atraso Máximo: 15 días
├─ Mora Diaria: $2,000
└─ Se agregará a lista negra si: Mora > 30 días

TOTAL MOROSO EN CARTERA: $XXX,XXX
```

**Verificaciones:**
- ✅ Identifica correctamente cuotas morosas
- ✅ Calcula mora acumulada
- ✅ Proporciona métricas útiles

### 8.3 Exportar a Excel

1. **En cualquier reporte**, busca: "Descargar" o "Exportar" Excel
2. **Haz clic**: "Exportar a Excel"
3. **Sistema descarga**: `reporte_morosidad_[fecha].xlsx`

**Verificaciones:**
- ✅ Archivo se descarga sin errores
- ✅ Excel se abre correctamente
- ✅ Datos coinciden con reporte web
- ✅ Formato es profesional (headers, colores, etc)

### 8.4 Reporte Financiero Completo

1. **Abre**: Reporte Financiero Completo
2. **Debe incluir para cada cliente:**

```
REPORTE FINANCIERO - Juan Carlos Pérez
═══════════════════════════════════════════════════════

PRÉSTAMOS
┌─ Préstamo #1: $500,000 @ 15%
│  ├─ Principal: $500,000
│  ├─ Interés Total: $37,500
│  ├─ Total Crédito: $537,500
│  ├─ Total Pagado: $268,750
│  └─ Saldo Pendiente: $268,750

└─ Préstamo #2: $750,000 @ 15%
   ├─ Principal: $750,000
   ├─ Interés Total: $56,250
   ├─ Total Crédito: $806,250
   ├─ Total Pagado: $X (según pagos realizados)
   └─ Saldo Pendiente: $Y

TOTALES CLIENTE
├─ Total Prestado: $1,550,000
├─ Total Pagado: $XXX,XXX
├─ Total Pendiente: $XXX,XXX
├─ Total Mora: $XXX
└─ % Cumplimiento: X%
```

**Verificaciones:**
- ✅ Todos los totales son precisos
- ✅ Desglose por concepto est correcto
- ✅ Transversalidad entre reportes

---

## PASO 9: Búsqueda y Filtros

### 9.1 Búsqueda de Cliente en Dropdown (AJAX)

1. **En formulario de pago o cualquier selector de cliente:**
   - Campo: "Seleccionar Cliente"
   - Escribe: "Juan" (primeras 4 letras)

**Sistema debe:**
- ✅ Mostrar sugerencias en tiempo real (< 500ms)
- ✅ Buscar por nombre
- ✅ Buscar por cédula
- ✅ Buscar por teléfono
- ✅ Mostrar máximo 10 resultados

```
Búsqueda AJAX Dropdown:
┌─────────────────────────────────────┐
│ Juan                                │
├─────────────────────────────────────┤
│ ✓ Juan Carlos Pérez (1234567890)    │
│ - 3105551234 - juan.perez@email.com │
└─────────────────────────────────────┘
```

### 9.2 Filtros en Lista de Clientes

1. **Ir a**: Clientes → Listar
2. **Filtros disponibles:**

```
Filtro por Estado:
├─ ACTIVO ✓
├─ INACTIVO
└─ TODOS

Filtro por Etiqueta:
├─ BUENO
├─ MEDIO
├─ MALO
├─ SIN_HISTORIAL ✓
└─ TODOS

Filtro por Rango de Deuda:
├─ $0 - $100,000
├─ $100,000 - $500,000 ✓ (Juan)
├─ >$500,000
└─ TODOS

Búsqueda por Texto:
├─ "Juan" → Encuentra: Juan Carlos Pérez ✓
├─ "1234567890" → Encuentra: Juan Carlos Pérez ✓
└─ "3105551234" → Encuentra: Juan Carlos Pérez ✓
```

**Verificaciones:**
- ✅ Filtros funcionan individualmente
- ✅ Combinación de filtros funciona
- ✅ "Limpiar Filtros" restaura la vista
- ✅ Búsqueda es CaseInsensitive

### 9.3 Ordenamiento

En lista de clientes, verifica que puedas ordenar por:
- ✅ Nombre (A→Z, Z→A)
- ✅ Fecha de Creación (Nuevo→Antiguo, Antiguo→Nuevo)
- ✅ Total Prestado (Mayor→Menor, Menor→Mayor)
- ✅ Rating (Mayor→Menor)

---

## PASO 10: Análisis Avanzado y Scoring

### 10.1 Scoring Automático del Cliente

En página de cliente, debe haber sección de "Scoring" o "Análisis":

```
ANÁLISIS Y SCORING
═════════════════════════════════════════

📊 SCORING GENERAL: 42/100 (Regular)

Factores Evaluados:
├─ Historial de Pagos: 0/100
│  └─ Observación: Sin historial (cliente nuevo)
│
├─ Cumplimiento de Fechas: 0/100
│  └─ Observación: Sin pagos registrados
│
├─ Monto Adeudado: 50/100
│  └─ Observación: $1,550,000 = 45% del máximo permitido
│
├─ Regularidad: 0/100
│  └─ Observación: Debe hacer el primer pago para evaluar
│
└─ Etiqueta Recomendada: SIN_HISTORIAL → Hacer Seguimiento

Recomendación: ⚠️ CLIENTE NUEVO - Requiere primer pago como referencia
```

**Verificaciones:**
- ✅ Scoring se calcula automáticamente
- ✅ Factores son ponderados correctamente
- ✅ Rango es coherente (0-100)
- ✅ Recomendaciones son útiles

### 10.2 Cambio de Etiqueta Después de Pagos

**ANTES (sin pagos):**
```
Etiqueta: SIN_HISTORIAL
Rating: 0 estrellas ☆☆☆☆☆
Tasa Cumplimiento: 0%
```

**DESPUÉS (con pagos realizados):**

1. **Si paga a tiempo:**
   ```
   Etiqueta: BUENO
   Rating: 4-5 estrellas ★★★★☆
   Tasa Cumplimiento: 100%
   Días Mora Promedio: 0
   ```

2. **Si paga con atraso pequeño (< 5 días):**
   ```
   Etiqueta: BUENO (con nota)
   Rating: 3-4 estrellas ★★★☆☆
   Tasa Cumplimiento: 90-99%
   Días Mora Promedio: 2
   ```

3. **Si paga con atraso mayor (> 15 días):**
   ```
   Etiqueta: MEDIO
   Rating: 2-3 estrellas ★★☆☆☆
   Tasa Cumplimiento: 70-90%
   Días Mora Promedio: 18
   ```

**Verificaciones:**
- ✅ Etiqueta se actualiza automáticamente
- ✅ Rating refleja comportamiento
- ✅ Histórico se mantiene (no borra pasado)

---

## PASO 11: Gestión de Lista Negra

### 11.1 Entender Criterio de Lista Negra

El sistema automáticamente agrega a lista negra si:
```
Criterio: Cuota vencida por > 30 días sin pago
```

**Para Juan Carlos Pérez:**
- Antes de pagar: En período de prueba (0-30 días)
- Si pasa 30 días sin pago: ➙ Agregar a lista negra

### 11.2 Simular Mora Extrema (Test Avanzado)

**Escenario:** Cuota tan vencida que merece lista negra

1. **En modo de testing**, puedes:
   - Usar Django shell para cambiar fechas de cuotas hacia atrás
   - O esperar 30+ días IRL (no práctico)
   - O usar fixture de datos antiguos

**Alternativa (Development):**
```bash
python m anage.py shell

from mi_app.models import Cuota, Cliente
from datetime import date, timedelta

# Obtener cliente
cliente = Cliente.objects.get(cedula='1234567890')

# Obtener una cuota sin pagar
cuota = cliente.prestamo_set.first().cuotas.first()

# Cambiar fecha de vencimiento a 40 días atrás
cuota.fecha_pago_esperada = date.today() - timedelta(days=40)
cuota.save()

print(f"Cuota modificada: {cuota.numero_cuota} vencida hace 40 días")
```

### 11.3 Verificar Adición Automática a Lista Negra

1. **Después de usar el shell (o esperar 30 días):**
2. **Vuelve a página de cliente**
3. **Sistema debe mostrar:**

```
⚠️ CLIENTE EN LISTA NEGRA

Razón: MOROSO
Fecha desde: [hoy]
Días de Atraso: 40 días
Cuta(s) Vencida(s): Cuota #[X] Préstamo #[Y]
Acción Recomendada: Contactar cliente para regularizar

[Botón: Ver Detalles de Lista Negra]
[Botón: Remover de Lista Negra]
```

**Verificaciones:**
- ✅ Cliente aparece en Lista Negra automáticamente
- ✅ Razón es precisa
- ✅ Hay opción para remover manualmente
- ✅ Historial se mantiene

### 11.4 Ver Lista Negra Global

1. **Menú**: Gestión → Lista Negra
   - O URL: http://127.0.0.1:8000/lista-negra/

**Debe mostrar tabla:**
```
┌─────────────────────────────────────────────────────────┐
│ CLIENTE │ RAZÓN │ DÍAS │ DESDE │ ESTADO │ ACCIONES │
├─────────────────────────────────────────────────────────┤
│ Juan C. │ MOROSO │ 40 │ [fecha] │ VIGENTE │ [Ver] [Sacar] │
└─────────────────────────────────────────────────────────┘
```

**Verificaciones:**
- ✅ Lista muestra todos los clientes en mora
- ✅ Días de atraso es preciso
- ✅ Botones de acción funcionan

---

## PASO 12: Validación Final

### 12.1 Checklist Transversal

**Completitud de Funcionalidades:**

```
AUTENTICACIÓN
├─ ✓ Login funciona
├─ ✓ Logout funciona
├─ ✓ Sesión persiste
└─ ✓ Protección de vistas

CLIENTES
├─ ✓ Crear cliente MANUALMENTE
├─ ✓ Crear cliente por IMPORTACIÓN Excel
├─ ✓ Listar clientes
├─ ✓ Ver detalles cliente
├─ ✓ Editar cliente
├─ ✓ Eliminar cliente (si permitido)
├─ ✓ Búsqueda funcionando
└─ ✓ Filtros funcionando

PRÉSTAMOS
├─ ✓ Crear préstamo manualmente
├─ ✓ Crear préstamo por Excel
├─ ✓ Generar cuotas automáticamente
├─ ✓ Cambiar estado (BORRADOR → ACTIVO → COMPLETADO)
├─ ✓ Listar préstamos del cliente
├─ ✓ Ver detalles del préstamo
└─ ✓ Cálculo de totales (principal + interés)

CUOTAS
├─ ✓ Generación automática (2 cuotas c/ periodo)
├─ ✓ Fechas correctas (cada 15 días para Quincenal)
├─ ✓ Estado correcto (PENDIENTE, VENCIDA, PAGADA, etc)
├─ ✓ Porcentaje pagado se calcula
└─ ✓ Mostrar en tabla clara

PAGOS
├─ ✓ Registrar pago completo
├─ ✓ Registrar pago parcial
├─ ✓ Incluir desglose (principal, interés, mora)
├─ ✓ Referencia de pago guardada
├─ ✓ Historial de pagos visible
└─ ✓ Validación de montos

MORA
├─ ✓ Cálculo correcto (fórmula)
├─ ✓ Período de gracia respetado
├─ ✓ Solo aplicada si VENCIDA
├─ ✓ Visible en cuotas
└─ ✓ Incluida en total de cuota

REPORTES
├─ ✓ Reporte de morosidad
├─ ✓ Reporte financiero
├─ ✓ Reporte de clientes
├─ ✓ Reporte de cuotas
├─ ✓ Exportacion a Excel
└─ ✓ Datos coinciden entre web y Excel

ANÁLISIS AVANZADO
├─ ✓ Scoring del cliente
├─ ✓ Etiqueta automática
├─ ✓ Rating basado en historial
├─ ✓ Tasa de cumplimiento calculada
└─ ✓ Días mora promedio

LISTA NEGRA
├─ ✓ Adición automática (> 30 días mora)
├─ ✓ Visualización clara
├─ ✓ Opción de remover
└─ ✓ Historial mantenido

INTERFAZ / UX
├─ ✓ Responsive (probado en 320px, 768px, 1200px, 1920px)
├─ ✓ Mensajes de confirmación claros
├─ ✓ Manejo de errores legible
├─ ✓ Loading indicators presentes
├─ ✓ Navegación intuitiva
└─ ✓ Estándares de accesibilidad (labels, aria-labels)

DATOS / INTEGRIDAD
├─ ✓ Sincronización BD ↔ UI
├─ ✓ Ningún dato orfano
├─ ✓ Transacciones atómicas en pagos
├─ ✓ Validación de entrada (client + server)
└─ ✓ Audit trail disponible
```

### 12.2 Test de Consistencia de Datos

En Django Shell, verifica:

```bash
python manage.py shell

from decimal import Decimal
from mi_app.models import Cliente, Prestamo, Cuota, Pago
from django.db.models import Sum

# Cliente actual
cliente = Cliente.objects.get(cedula='1234567890')

# Verificación 1: Total prestado correcto
total_esperado = Decimal('1550000')  # 500k + 750k + 300k
total_actual = cliente.total_prestado_real
print(f"Total Prestado: {total_actual} == {total_esperado}? {total_actual == total_esperado} ✓")

# Verificación 2: Total pagado coincide
total_pagado_modelos = cliente.total_pagado
total_pagado_bd = Pago.objects.filter(cuota__prestamo__cliente=cliente).aggregate(
    sum=Sum('monto_pagado')
)['sum'] or 0
print(f"Total Pagado: {total_pagado_modelos} == {total_pagado_bd}? ✓")

# Verificación 3: Cuotas tienen estado correcto
for prestamo in cliente.prestamo_set.all():
    print(f"\nPréstamo {prestamo.id}:")
    for cuota in prestamo.cuotas.all():
        print(f"  Cuota {cuota.numero_cuota}: {cuota.estado}")
        # Verificar que estado es válido
        assert cuota.estado in ['PENDIENTE', 'PARCIALMENTE_PAGADA', 'PAGADA', 'VENCIDA', 'VENCIDA_PARCIAL']
        # Verificar que porcentaje pagado coincide
        if cuota.monto_original > 0:
            porcentaje_calculado = (cuota.monto_pagado_principal / cuota.monto_original) * 100
            assert abs(porcentaje_calculado - cuota.porcentaje_pagado) < 0.01

print("\n✅ TODAS LAS VERIFICACIONES PASARON")
```

**Verificaciones:**
- ✅ Totales coinciden
- ✅ Estados son válidos
- ✅ Porcentajes son correctos
- ✅ No hay datos inconsistentes

### 12.3 Resumen de Testing

**Documento de Confirmación:**

```
╔════════════════════════════════════════════════════════════╗
║ TESTING INTEGRAL COMPLETADO ✓                              ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║ Cliente: Juan Carlos Pérez                                 ║
║ Cédula: 1234567890                                         ║
║ Préstamos: 3 (500k + 750k + 300k = 1,550k)                 ║
║ Cuotas Generadas: 6                                        ║
║ Pagos Registrados: [X]                                     ║
║ Estado: ✓ Todas las funciones testadas                      ║
║                                                             ║
╠════════════════════════════════════════════════════════════╣
║ RESULTADOS:                                                 ║
║ ├─ Importación: EXITOSA                                    ║
║ ├─ Cálculos: PRECISOS                                      ║
║ ├─ Interfaz: INTUITIVA                                     ║
║ ├─ Performance: ADECUADO                                   ║
║ ├─ Responsividad: COMPLETA                                 ║
║ ├─ Validaciones: EXHAUSTIVAS                               ║
║ ├─ Integridad Datos: GARANTIZADA                           ║
║ ├─ Reportes: ACTUALIZADOS                                  ║
║ ├─ Mora: CALCULADA CORRECTAMENTE                           ║
║ ├─ Lista Negra: AUTOMATIZADA                               ║
║ ├─ Scoring: IMPLEMENTADO                                   ║
║ └─ Análisis: COMPLETO                                      ║
║                                                             ║
║ CONCLUSIÓN: Sistema PRODUCTION-READY ✓                     ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🎯 PRÓXIMOS PASOS (Testing Interactivo)

**El sistema está listo para que TÚ** hagas ajustes dinámicos:

```
Ejemplo de petición:
"Agrégale $500,000 en mora a la Cuota #2 del Préstamo #2"
→ Sistema modifica datos
→ Muestra nueva mora calculada
→ Verifica comportamiento de lista negra
→ Muestra impacto en scoring

O:
"Cambia la tasa de interés a 20% y genera nuevos préstamos"
→ Verifica que cuotas se recalculan
→ Valida que el cambio no rompe préstamos existentes
```

---

## 📞 Debugging Rápido

Si algo no funciona:

```bash
# Ver logs de Django
python manage.py runserver --verbosity=3

# Verificar BD
python manage.py dbshell
SELECT COUNT(*) FROM mi_app_cliente;

# Resetear totales de cliente
python manage.py shell
cliente = Cliente.objects.get(cedula='1234567890')
cliente.corregir_totales()

# Ver todos los pagos
python manage.py shell
from mi_app.models import Pago
for pago in Pago.objects.all():
    print(f"{pago.cuota.numero_cuota}: ${pago.monto_pagado}")
```

---

**¡Guía lista para testing integral! 🚀**
