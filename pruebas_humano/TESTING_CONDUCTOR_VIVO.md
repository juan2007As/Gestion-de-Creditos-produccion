# 🎮 TESTING CONDUCTOR EN TIEMPO REAL
**Versión:** 2.0 - Interactive  
**Fecha:** 21 de Febrero de 2026  
**Modalidad:** Tú ejecutas → Yo veo → Te guío + Ajusto dinámicamente

---

## 📌 CÓMO FUNCIONA

1. **Yo te dico exactamente QUÉ hacer**
2. **Tú lo haces y me reportas QUÉ ves**
3. **Yo interpreto el resultado**
4. **Si hay error**: Yo arreglo en la BD/código en tiempo real
5. **Pasamos al siguiente PASO**

---

## 🔴 PASO 1: SERVIDOR CORRIENDO

### QUÉ HACER:

```bash
cd c:\Users\Juancho\Desktop\proyecto_john
python manage.py runserver
```

### QUÉ DEBERÍAS VER:

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 21, 2026 - XX:XX:XX
Django version 4.x, using settings 'proyecto_john.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### STATUS ESPERADO:
- ✅ Servidor corriendo en http://127.0.0.1:8000/
- ✅ NO hay errores de BD
- ✅ NO hay errores de imports

---

## 🟡 INGRESA AL NAVEGADOR

### QUÉ HACER:

1. Abre navegador
2. Ve a: `http://127.0.0.1:8000/`
3. **Espera 2-3 segundos**

### QUÉ DEBERÍAS VER:

**ESCENARIO A - Redirige a Login:**
```
Página: Login
- Campo "Usuario"
- Campo "Contraseña"
- Botón "Iniciar Sesión"
- ¿Está el logo? ¿Se ve bien?
```

**ESCENARIO B - Redirige a Inicio Directo:**
```
Página: Dashboard/Inicio
- Muestra nombre del usuario (arriba derecha)
- Menú: Clientes, Préstamos, Reportes, etc
- Esto significa ya tienes sesión activa
```

---

## 🟢 ¿QUÉ VISTE?

**Confirma aquí:**
```
[ ] ESCENARIO A → Página de Login (ir a PASO 2A)
[ ] ESCENARIO B → Página de Inicio directo (ir a PASO 2B)
[ ] ERROR → Muestra error 404 / 500 (reportar)
```

---

---

## 🔴 PASO 2A: LOGIN (si viste página de login)

### QUÉ HACER:

1. **Campo Usuario:** escribe `admin`
2. **Campo Contraseña:** escribe `admin123456`
3. **Haz clic en:** "Iniciar Sesión" o botón similar

**⏱️ ESPERA 2-3 segundos**

### QUÉ DEBERÍAS VER:

```
✅ Se carga página nuevo (http://127.0.0.1:8000/inicio/ o similar)
✅ Muestra: "Bienvenido Admin" (o similar)
✅ Menú disponible: Clientes, Préstamos, Reportes
✅ Header muestra usuario logueado
```

### ⚠️ SI VES ERROR:

Reporte exacto:
```
❌ Mensaje: _______________
❌ URL: _______________
❌ Campo rojo: _______________
```

---

## 🔴 PASO 2B: ya estás en Inicio

Si saltaste directo a Inicio:

### CONFIRMA QUE VES:

```
✅ Menú superior con: Clientes, Préstamos, Reportes
✅ Usuario mostrado en esquina superior derecha
✅ No hay menú de login
✅ Navegación funciona al hacer clic
```

---

---

## 🔴 PASO 3: IMPORTACIÓN EXCEL

### QUÉ HACER:

1. **Menú:** Clientes → Importar desde Excel
2. O directamente: `http://127.0.0.1:8000/importar-clientes/`

**⏱️ ESPERA 1-2 segundos**

### QUÉ VES:

```
Página: Importar Clientes
├─ Título: "Importar Clientes desde Excel"
├─ Botón: "Seleccionar Archivo" o área de drag-drop
├─ Instructions: ¿Qué formato espera?
└─ (Posible botón Preview/Validar)
```

---

### NO VISTE PÁGINA DE IMPORTACIÓN:

**Reporta:**
```
❌ No encontré menú de importación
❌ URL está rota (error 404)
❌ Otra cosa: _______________

Yo voy a:
1. Verificar que existe la vista
2. Crear si no existe
3. Ajustar si falta
```

---

## 🟡 PASO 3.1: CARGAR ARCHIVO

### QUÉ HACER:

1. **Haz clic:** "Seleccionar Archivo"
2. **Navega a:** `C:\Users\Juancho\Desktop\proyecto_john\pruebas_humano\DATOS_PRUEBA_CLIENTE.xlsx`
3. **Selecciona y abre**

### QUÉ DEBERÍAS VER:

```
✅ Nombre del archivo: "DATOS_PRUEBA_CLIENTE.xlsx" (mostrado en página)
✅ Botón "Importar" o "Validar" está habilitado
✅ Posible preview con 3 filas visibles
```

---

### PROBLEMA: No veo botón "Seleccionar Archivo"

**Te voy a crear la vista si no existe:**

```python
# Yo agregaré en views.py:
@login_required
def importar_clientes(request):
    if request.method == 'POST':
        # Procesar Excel
    return render(request, 'mi_app/importar_clientes.html')
```

---

## 🟢 PASO 3.2: VALIDACIÓN PRE-IMPORTACIÓN

### QUÉ HACER:

1. **Si ves botón "Validar":** Haz clic
2. **Si no hay, haz clic directo en "Importar"**

**⏱️ ESPERA 3-5 segundos**

### QUÉ DEBERÍAS VER:

```
RESULTADO DE VALIDACIÓN:
✅ Estructura: OK
✅ Fila 1: Juan Carlos Pérez - VÁLIDA
✅ Fila 2: Juan Carlos Pérez - VÁLIDA
✅ Fila 3: Juan Carlos Pérez - VÁLIDA

RESUMEN:
├─ Clientes a crear: 1
├─ Préstamos a crear: 3
├─ Filas válidas: 3
└─ Errores: 0
```

---

### VISTE ERRORES:

**Reporta exacto:**
```
❌ Fila 1: _______________
❌ Fila 2: _______________
❌ Error general: _______________

Yo voy a debuggear el validador
```

---

## 🟡 PASO 3.3: EJECUTAR IMPORTACIÓN

### QUÉ HACER:

Haz clic en: **"Confirmar Importación"** o **"Importar"**

**⏱️ ESPERA 5-10 segundos** (puede procesarse)

### QUÉ DEBERÍAS VER:

**ESCENARIO A - ÉXITO:**
```
🟢 MENSAJE: "✅ Importación completada exitosamente"

RESUMEN:
├─ Cliente creado: Juan Carlos Pérez
├─ Cédula: 1234567890
├─ Préstamos creados: 3
│  ├─ Préstamo 1: $500,000 (2 cuotas)
│  ├─ Préstamo 2: $750,000 (3 cuotas)
│  └─ Préstamo 3: $300,000 (1 cuota)
├─ Cuotas generadas: 6
└─ Total: $1,550,000

[Botón: Ver Cliente] [Botón: Ir a Lista]
```

**ESCENARIO B - ERROR:**
```
❌ MENSAJE: "Error durante importación"
Detalle: _______________
```

---

## 🔴 ¿RESULTADO DE IMPORTACIÓN?

**Reporta:**
```
[ ] ✅ EXITOSA - Vi el mensaje de éxito
[ ] ⚠️ PARCIAL - Importó pero con warnings
[ ] ❌ ERROR - Qué error?
```

---

---

## 🔴 PASO 4: VER CLIENTE IMPORTADO

### QUÉ HACER:

1. **Menú:** Clientes → Listar Clientes
2. O URL: `http://127.0.0.1:8000/clientes/`

**⏱️ ESPERA 1-2 segundos**

### QUÉ DEBERÍAS VER:

```
LISTA DE CLIENTES:
┌─────────────────────────────────────────┐
│ Nombre           │ Cédula      │ ... │
├─────────────────────────────────────────┤
│ Juan Carlos P... │ 1234567890  │ ... │
│ [Ver] [Editar]                         │
└─────────────────────────────────────────┘
```

---

### PASO 4.1: VER DETALLES

### QUÉ HACER:

1. Haz clic en: "Juan Carlos Pérez" o botón [Ver]

**⏱️ ESPERA 1-2 segundos**

### QUÉ DEBERÍAS VER:

```
PÁGINA: Detalles del Cliente

📋 INFORMACIÓN PERSONAL
├─ Nombre: Juan Carlos Pérez
├─ Cédula: 1234567890
├─ Email: juan.perez@email.com
├─ Teléfono: 3105551234
└─ Estado: ACTIVO

💰 RESUMEN FINANCIERO
├─ Total Prestado: $1,550,000
├─ Total Pagado: $0
├─ Total Pendiente: $1,550,000
├─ Cuotas: 0/6 pagadas
└─ Mora: $0 (calculada automáticamente)

📊 ANÁLISIS
├─ Rating: ☆☆☆☆☆ (sin historial)
├─ Etiqueta: SIN_HISTORIAL
├─ Tasa Cumplimiento: 0%
└─ Scoring: [calculado]

📌 PRÉSTAMOS (sección)
├─ Préstamo #1: $500,000 @ 15% → 2 cuotas
├─ Préstamo #2: $750,000 @ 15% → 3 cuotas
└─ Préstamo #3: $300,000 @ 15% → 1 cuota
```

---

## 🟢 PUNTO DE REVISIÓN: ¿TODO CORRECTO HASTA AQUÍ?

**Confirma CADA línea:**

```
INFORMACIÓN PERSONAL:
[ ] ✅ Nombre: Juan Carlos Pérez
[ ] ✅ Cédula: 1234567890
[ ] ✅ Email: juan.perez@email.com
[ ] ✅ Teléfono: 3105551234
[ ] ✅ Estado: ACTIVO

RESUMEN FINANCIERO:
[ ] ✅ Total Prestado: $1,550,000
[ ] ✅ Total Pagado: $0
[ ] ✅ Total Pendiente: $1,550,000
[ ] ✅ Cuotas: 0/6

PRÉSTAMOS LISTADOS:
[ ] ✅ Préstamo 1: $500,000 (2 cuotas)
[ ] ✅ Préstamo 2: $750,000 (3 cuotas)
[ ] ✅ Préstamo 3: $300,000 (1 cuota)
```

---

## ⚠️ SI ALGO NO COINCIDE:

**Reporte:**
```
❌ Campo: _______________
❌ Esperado: _______________
❌ Vi: _______________

Yo voy a:
1. Revisar la BD
2. Corregir datos si es necesario
3. Recargar página para confirmar
```

---

---

## 🔴 PASO 5: VER DETALLES DE PRÉSTAMO

### QUÉ HACER:

En la página del cliente, haz clic en:
**"Préstamo #1" → [Ver Detalles]** (o similar)

**⏱️ ESPERA 1-2 segundos**

### QUÉ DEBERÍAS VER:

```
PÁGINA: Detalles del Préstamo

HEADER:
├─ Préstamo #1
├─ Cliente: Juan Carlos Pérez
├─ Estado: ACTIVO
└─ Monto Original: $500,000

ESTRUCTURA FINANCIERA:
├─ Monto Principal: $500,000
├─ Tasa de Interés: 15% anual (7.5% por quincena)
├─ Interés Total Estimado: $37,500
├─ TOTAL A PAGAR: $537,500
├─ Número de Cuotas: 2
└─ Tipo de Pago: QUINCENAL

📊 TABLA DE CUOTAS:
┌─────┬─────────────┬──────────┬──────────┬───────────────┬─────────────┐
│ # │ Vencimiento │ Principal │ Interés │ Estado │ Pagado/Mora │
├─────┼─────────────┼──────────┼──────────┼───────────────┼─────────────┤
│ 1 │ [fecha+15d] │ $250,000 │ $18,750 │ VENCIDA* │ $0/$0 │
│ 2 │ [fecha+30d] │ $250,000 │ $18,750 │ PENDIENTE │ $0/$0 │
└─────┴─────────────┴──────────┴──────────┴───────────────┴─────────────┘

*Dependiendo de hoy vs fecha vencimiento
```

---

## 🟢 CONFIRMACIÓN PRÉSTAMO #1:

```
ESTRUCTURA FINANCIERA:
[ ] ✅ Principal: $500,000
[ ] ✅ Interés Total: $37,500
[ ] ✅ Total a Pagar: $537,500
[ ] ✅ Cuotas: 2

CUOTA #1:
[ ] ✅ Principal: $250,000
[ ] ✅ Interés: $18,750
[ ] ✅ Vencimiento: +15 días desde hoy
[ ] ✅ Estado: VENCIDA o PENDIENTE (según hoy)

CUOTA #2:
[ ] ✅ Principal: $250,000
[ ] ✅ Interés: $18,750
[ ] ✅ Vencimiento: +30 días desde hoy
[ ] ✅ Estado: PENDIENTE
```

---

---

## 🔴 PASO 6: VERIFICAR LOS 3 PRÉSTAMOS

### QUÉ HACER:

**Vuelve a página de cliente**
Haz clic en cada Préstamo y verifica:

```
PRÉSTAMO #2:
[ ] ✅ Monto: $750,000
[ ] ✅ Cuotas: 3
[ ] ✅ Principal c/u: $250,000
[ ] ✅ Interés c/u: $18,750
[ ] ✅ Vencimientos: cada 15 días

PRÉSTAMO #3:
[ ] ✅ Monto: $300,000
[ ] ✅ Cuotas: 1
[ ] ✅ Principal: $300,000
[ ] ✅ Interés: $22,500
[ ] ✅ Vencimiento: +15 días
```

---

---

## 🔴 PASO 7: REGISTRO DE PAGO

### QUÉ HACER:

1. Menú: Pagos → Registrar Pago
2. O URL: `http://127.0.0.1:8000/registrar-pago/`

**⏱️ ESPERA 1-2 segundos**

### QUÉ DEBERÍAS VER:

```
PÁGINA: Registrar Pago

FORMULARIO:
┌─────────────────────────────────────┐
│ Cliente: [Seleccionar / Buscar] │
│         → Busca: "juan"            │
│         → Elige: Juan Carlos Pérez │
│                                     │
│ Préstamo: [Auto-completa]          │
│ → Elige: Préstamo #1 ($500,000)   │
│                                     │
│ Cuota: [Selecciona]                │
│ → Cuota #1 (vencimiento: [fecha])  │
│                                     │
│ Monto a Pagar: [Ingresa]           │
│ → Sugerencia: $268,750 (Principal  │
│   $250,000 + Interés $18,750)     │
│                                     │
│ Referencia: [Ingresa]              │
│ Notas: [Opcional]                  │
│                                     │
│ [Botón: Registrar Pago]            │
└─────────────────────────────────────┘
```

---

## 🟡 HACER UN PAGO COMPLETO

### QUÉ HACER:

1. **Cliente:** Busca y selecciona "Juan Carlos Pérez"
2. **Préstamo:** Selecciona "Préstamo #1 - $500,000"
3. **Cuota:** Selecciona "Cuota #1"
4. **Monto:** Ingresa `268750`
5. **Referencia:** Ingresa `PAGO_TEST_1`
6. **Más:** Deja las notas vacías
7. **Haz clic:** "Registrar Pago"

**⏱️ ESPERA 3-5 segundos**

### QUÉ DEBERÍAS VER:

**ESCENARIO A - ÉXITO:**
```
🟢 MENSAJE: "✅ Pago registrado exitosamente"

COMPROBANTE:
├─ Referencia: PAGO_TEST_1
├─ Monto: $268,750
├─ Desglose:
│  ├─ Principal: $250,000
│  ├─ Interés: $18,750
│  └─ Mora: $0
├─ Fecha: [Hoy]
└─ Estado de Cuota: Ahora PAGADA ✅

[Botón: Ver Cuota] [Botón: Nuevo Pago]
```

**ESCENARIO B - ERROR:**
```
❌ MENSAJE: "Error al registrar pago"
Detalle: _______________
```

---

## 🟢 ¿PAGO REGISTRADO?

```
[ ] ✅ ÉXITO - Vi comprobante
[ ] ⚠️ PARCIAL - Registró pero con warning
[ ] ❌ ERROR - Reporta qué error
```

---

---

## 🔴 PASO 8: VERIFICAR ACTUALIZACIÓN AUTOMÁTICA

### QUÉ HACER:

1. **Vuelve a** página del cliente: Menú Clientes → Listar → Juan Carlos Pérez

**⏱️ ESPERA 1-2 segundos**

### QUÉ DEBERÍAS VER CAMBIADO:

```
RESUMEN FINANCIERO (ACTUALIZADO):

ANTES:
├─ Total Pagado: $0
├─ Total Pendiente: $1,550,000
└─ Cuotas Pagadas: 0/6

AHORA:
├─ Total Pagado: $268,750 ✅ (cambió!)
├─ Total Pendiente: $1,281,250 ✅ (cambió!)
└─ Cuotas Pagadas: 1/6 ✅ (cambió!)
```

---

## 🟢 ¿TOTALES SE ACTUALIZARON?

```
[ ] ✅ SÍ - Total Pagado ahora es $268,750
[ ] ✅ SÍ - Total Pendiente ahora es $1,281,250
[ ] ✅ SÍ - Cuotas Pagadas: 1/6
[ ] ❌ NO - Siguen igual (voy a forza refresh)
```

---

---

## 🔴 PASO 9: TESTEAR VALIDACIONES DE PAGO

### QUÉ HACER:

Vuelve a Registrar Pago e intenta casos inválidos:

### CASO 1: Monto Negativo

```
1. Cliente: Juan Carlos Pérez
2. Préstamo: Préstamo #2 ($750,000)
3. Cuota: Cuota #1
4. Monto: -100000 (NEGATIVO)
5. Haz clic: "Registrar Pago"
```

**DEBERÍAS VER:**
```
❌ ERROR: "El monto debe ser positivo"
```

---

### CASO 2: Monto Cero

```
1. Igual setup
2. Monto: 0
3. Haz clic: "Registrar Pago"
```

**DEBERÍAS VER:**
```
❌ ERROR: "El monto debe ser mayor a 0"
```

---

### CASO 3: Monto Muy Grande

```
1. Igual setup
2. Cuota #1 debe: $268,750
3. Monto: 1000000 (MUCHO MÁS)
4. Haz clic: "Registrar Pago"
```

**DEBERÍAS VER:**
```
⚠️ Sistema puede:
├─ Rechazar: "Monto excede lo adeudado"
└─ O Aceptar: "Crédito a favor: $731,250"

Reporta qué hizo:
[ ] Rechazó
[ ] Aceptó con crédito
```

---

## 🟢 VALIDACIONES FUNCIONAN:

```
[ ] ✅ Negativo: Rechazado
[ ] ✅ Cero: Rechazado
[ ] ✅ Muy grande: Rechazado o Crédito
[ ] ❌ Ninguno funciona (voy a revisar formulario)
```

---

---

## 🔴 PASO 10: MORA Y CUOTAS VENCIDAS

### QUÉ HACER:

En Django Shell, voy a simular que una cuota está vencida hace 15 días:

```bash
python manage.py shell
```

```python
from mi_app.models import Cuota, Cliente
from datetime import date, timedelta

# Obtener cliente
cliente = Cliente.objects.get(cedula='1234567890')

# Obtener Préstamo #2, Cuota #1
prestamo2 = cliente.prestamo_set.all()[1]  # Préstamo #2
cuota_morosa = prestamo2.cuotas.first()

# Cambiar fecha a 15 días atrás
cuota_morosa.fecha_pago_esperada = date.today() - timedelta(days=15)
cuota_morosa.save()

print(f"✅ Cuota modificada: Vencida hace 15 días")
print(f"   Fecha: {cuota_morosa.fecha_pago_esperada}")
print(f"   Mora calculada: {cuota_morosa.calcular_mora_diaria()}")
```

### QUÉ HACER DESPUÉS:

1. Vuelve a página del cliente
2. Abre Préstamo #2
3. **VE CUOTA #1**

### QUÉ DEBERÍAS VER:

```
CUOTA #1 (Préstamo #2):

ANTES:
├─ Estado: PENDIENTE
├─ Mora: $0
└─ Total adeudado: $268,750

AHORA:
├─ Estado: VENCIDA ✅ (cambió!)
├─ Mora: $10,000 ✅ (calculada! -5 días gracia = 10 días × $2k)
├─ Total adeudado: $278,750 ✅ ($268,750 + $10,000 mora)
└─ Días de atraso: 15 días
```

---

## 🟢 ¿MORA SE CALCULA?

```
[ ] ✅ SÍ - Vi mora de $10,000
[ ] ✅ SÍ - Estado cambió a VENCIDA
[ ] ✅ SÍ - Total adeudado subió a $278,750
[ ] ❌ NO - Sigue igual (voy a chequear fórmula)
```

---

---

## 🔴 PASO 11: PAGO CON MORA

### QUÉ HACER:

Registra un pago para la cuota morosa:

```
1. Cliente: Juan Carlos Pérez
2. Préstamo: Préstamo #2
3. Cuota: Cuota #1 (la que está VENCIDA)
4. Monto: 278750 (principal + interés + mora)
5. Referencia: PAGO_CON_MORA
6. Haz clic: "Registrar Pago"
```

### QUÉ DEBERÍAS VER:

```
🟢 ÉXITO:
├─ Comprobante generado
├─ Desglose:
│  ├─ Principal: $250,000
│  ├─ Interés: $18,750
│  └─ Mora: $10,000 ✅
├─ Estado de Cuota: PAGADA ✅
└─ Total Pagado Acumulado: Debe aumentar
```

---

## 🟢 ¿PAGO CON MORA FUNCIONA?

```
[ ] ✅ SÍ - Aceptó los $278,750
[ ] ✅ SÍ - Desglose incluye mora
[ ] ✅ SÍ - Cuota ahora PAGADA
[ ] ❌ NO - Error en registro (reporta)
```

---

---

## 🔴 PASO 12: ESTADO DE SCORING

### QUÉ HACER:

En página del cliente, busca sección "Scoring" o "Análisis":

### QUÉ DEBERÍAS VER:

```
ANÁLISIS Y SCORING

ANTES (sin pagos):
├─ Etiqueta: SIN_HISTORIAL
├─ Rating: ☆☆☆☆☆
├─ Tasa Cumplimiento: 0%
└─ Scoring: 0/100

AHORA (con pagos):
├─ Etiqueta: SIN_HISTORIAL → BUENO (si fue a tiempo)
├─ Rating: ★★★☆☆ o mejor
├─ Tasa Cumplimiento: 50% o mejor
└─ Scoring: 40-60/100 (mejoró)

O si pago CON MORA:
├─ Etiqueta: MEDIO (por el atraso)
├─ Rating: ★★☆☆☆
├─ Tasa Cumplimiento: 30-50%
└─ Scoring: 20-30/100 (bajó un poco)
```

---

## 🟢 ¿SCORING SE ACTUALIZÓ?

```
[ ] ✅ SÍ - Vi cambios en Rating/Etiqueta
[ ] ✅ SÍ - Tasa de Cumplimiento cambió
[ ] ✅ SÍ - Scoring subió/bajó
[ ] ⚠️ PARCIAL - Algunos campos cambiaron
[ ] ❌ NO - Nada cambió (voy a revisar)
```

---

---

## 📊 RESUMEN DE TESTING HASTA AQUÍ

```
FUNCIONALIDAD                 ESTADO
═════════════════════════════════════════
Login                        [ ] ✅ [ ] ❌
Importación Excel            [ ] ✅ [ ] ❌
Visualización Cliente        [ ] ✅ [ ] ❌
Detalles Préstamos           [ ] ✅ [ ] ❌
Cálculo de Interés           [ ] ✅ [ ] ❌
Registro de Pago             [ ] ✅ [ ] ❌
Actualización Automática     [ ] ✅ [ ] ❌
Validaciones Formulario      [ ] ✅ [ ] ❌
Cálculo de Mora              [ ] ✅ [ ] ❌
Pago con Mora                [ ] ✅ [ ] ❌
Scoring/Rating               [ ] ✅ [ ] ❌
```

---

## 🔴 PRÓXIMOS PASOS

Si TODO está ✅:
- PASO 13: Reportes
- PASO 14: Búsqueda y Filtros
- PASO 15: Lista Negra Automática

Si hay ❌:
- Reporta exactamente qué falló
- Yo diagnostico en la BD
- Hacemos correcciones dinámicamente

---

## ✍️ PARA REPORTAR PROBLEMAS:

**FORMATO:**
```
❌ PASO X: [Nombre del Paso]

QUÉ HICE:
[Tu acción exacta]

QUÉ VI:
[Screenshot o descripción exacta]

QUÉ ESPERABA:
[Lo que debía ver]

DIFERENCIA:
[Qué no coincide]
```

---

**¿Listo? Comienza con PASO 1 ahora 👇**

