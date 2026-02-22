# 📋 REGLAS DE DESARROLLO - PROYECTO GESTOR DE PRÉSTAMOS

**Versión:** 3.0  
**Última Actualización:** 02 de Febrero de 2026  
**Estado:** Activo - Todos deben cumplir

---

## 🔴 REGLA #0: CONTEXTO COMPLETO ANTES DE CUALQUIER ACCIÓN

**PRIORIDAD:** 🔴 CRÍTICA MÁXIMA - APLICA ANTES DE TODAS LAS OTRAS REGLAS

### Principio Fundamental

**JAMÁS** sugerir, crear, modificar, agregar, eliminar o cambiar NADA sin:

1. ✅ **Leer TODO el contexto del workspace**
   - Leer TODOS los archivos relevantes
   - Entender estructura actual
   - Identificar patrones existentes
   - Revisar documentación histórica

2. ✅ **Analizar el estado ACTUAL del proyecto**
   - ¿Qué está hecho?
   - ¿Qué está en proceso?
   - ¿Qué está documentado?
   - ¿Qué está pendiente?

3. ✅ **Identificar TODOS los archivos impactados**
   - Backend (models, views, urls, forms, admin, utils, tests)
   - Frontend (templates, CSS, JS, images)
   - Configuración (settings, requirements, .env)
   - Documentación y guías

4. ✅ **Proponer explícitamente ANTES de actuar**
   - Explicar QUÉ se va a cambiar
   - Explicar POR QUÉ en cada archivo
   - Mostrar el impacto transversal
   - ESPERAR CONFIRMACIÓN explícita

5. ✅ **Ejecutar SOLO lo confirmado**
   - No hacer cambios "por si acaso"
   - No agregar funcionalidades no solicitadas
   - No "mejorar" cosas sin pedir
   - Ser conservador y preciso

### ANTI-PATRÓN: Lo que NUNCA hacer

```markdown
❌ MALO (Violación Regla #0):
"Voy a crear un nuevo archivo para..."
"Voy a agregar esta funcionalidad..."
"Te propongo cambiar esto..."
"Aquí está el código..."
[Sin haber analizado el contexto completo]
```

### PATRÓN CORRECTO: Lo que SIEMPRE hacer

```markdown
✅ BUENO (Cumple Regla #0):

Después de revisar el proyecto completo, encontré:

📁 ARCHIVOS EXISTENTES:
- archivo1.py (propósito)
- archivo2.css (propósito)
- template_base.html (propósito)

📋 ARCHIVOS A IMPACTAR:
1. archivo1.py (línea X-Y) - Razón del cambio
2. archivo2.css (sección ABC) - Razón del cambio
3. template_base.html - Razón del cambio

📊 IMPACTO EN EL SISTEMA:
[Explicación clara de cómo afecta]

❓ ¿CONFIRMÁS antes de que proceda?
```

### Ejemplo Real: Violación vs Cumplimiento de Regla #0

**Escenario:** Usuario pide "Agregar búsqueda avanzada"

❌ **MALO** (Violación Regla #0 - Lo que pasó con CSS):
```
"Ok, voy a crear búsqueda-avanzada.js
Aquí está el código..."
[1000 líneas de código creadas]
[Migraciones CSS sin analizar body styling, disabled states, etc]
→ RESULTADO: Faltaron 3 migraciones críticas
```

✅ **BUENO** (Cumple Regla #0):
```
Después de revisar el proyecto completo, encontré:

📁 ARCHIVOS EXISTENTES:
- dropdown-search.js (búsqueda básica de clientes)
- static/mi_app/css/componentes.css
- templates/formulario_prestamo.html
- views.py con api_buscar_cliente()

📋 ARCHIVOS A IMPACTAR:
1. views.py (línea 150-180)
   ↳ Nueva vista: api_buscar_avanzado()
   ↳ Agregar filtros: fecha, monto, estado

2. static/mi_app/js/busqueda-avanzada.js (NUEVO)
   ↳ Módulo con 5+ filtros
   ↳ Debounce 300ms

3. templates/base.html
   ↳ Importar: busqueda-avanzada.js
   ↳ HTML modal de filtros

4. static/mi_app/css/componentes.css
   ↳ Estilos .filtro-busqueda
   ↳ Estados: activo, hover, disabled

📊 IMPACTO:
- +1 vista backend
- +1 módulo JS
- +30 líneas CSS
- Búsqueda: 3s → 0.5s

❓ ¿CONFIRMÁS?
```

### Checklist Obligatorio ANTES de CUALQUIER CAMBIO

```
□ ¿Leí TODO el contexto del workspace?
□ ¿Identifiqué TODOS los archivos impactados?
□ ¿Propuse explícitamente QUÉ cambios?
□ ¿Expliqué POR QUÉ en cada archivo?
□ ¿Mostré el impacto transversal?
□ ¿Esperé confirmación del usuario?
□ ¿Verifiqué que entiende las consecuencias?

SI NO PUEDO MARCAR TODOS = NO PROCEDO
```

### Consecuencias de Violar Regla #0

| Violación | Resultado |
|-----------|-----------|
| No leer contexto completo | Duplicación de código, cambios incompletos |
| No identificar archivos impactados | Sistema quebrado, inconsistencias |
| No proponer explícitamente | Cambios no deseados, tiempo perdido |
| No esperar confirmación | Trabajo rehecho, frustración |

### Aplicación a TODAS las situaciones

**Regla #0 se aplica SIEMPRE para:**
- ✅ Crear funcionalidades nuevas
- ✅ Corregir bugs
- ✅ Refactorizar código
- ✅ Agregar validaciones
- ✅ Cambiar UI/UX
- ✅ Optimizar performance
- ✅ Actualizar documentación
- ✅ Migrar código (como FASE 2)
- ✅ Cualquier modificación
- ✅ **TODO, sin excepción**

**No hay excepciones. REGLA #0 SIEMPRE PRIMERO.**

---

## 📊 MATRIZ DE PRIORIDADES ACTUALIZADA

| Prioridad | Regla | Aplicación |
|-----------|-------|-----------|
| 🔴🔴🔴 **CRÍTICA** | **REGLA #0: Contexto Completo** | **SIEMPRE PRIMERO** |
| 🔴 CRÍTICA | Cambios Transversales | Después de Regla #0 |
| 🔴 CRÍTICA | Validación Servidor | Después de Regla #0 |
| 🔴 CRÍTICA | Sin Código Inline | Después de Regla #0 |
| 🟠 ALTA | Tests Completos | Después de Regla #0 |
| 🟠 ALTA | Mobile Responsive | Después de Regla #0 |
| 🟡 MEDIA | Documentación | Después de Regla #0 |

---

## 🔍 PARTE 1: CONTEXTO Y ANÁLISIS DEL PROYECTO

### REGLA GENERAL DE CONTEXTO Y CAMBIOS

Antes de realizar cualquier cambio, creación, eliminación o recomendación, **DEBES analizar y comprender el contexto completo del proyecto existente**.

### 1️⃣ Análisis Completo del Repositorio (OBLIGATORIO)

Antes de cualquier desarrollo, examina y comprende toda la estructura:

#### Backend (Django)
- ✅ `models.py` - Modelos de datos y relaciones
- ✅ `views.py` - Lógica de negocio y controladores
- ✅ `urls.py` - Rutas y endpoints
- ✅ `forms.py` - Validaciones y formularios
- ✅ `admin.py` - Configuración del panel admin
- ✅ `middleware/` - Procesadores personalizados
- ✅ `utils.py` - Funciones auxiliares reutilizables
- ✅ `settings.py` - Configuración global

#### Frontend
- ✅ `templates/` - Plantillas HTML
- ✅ `static/js/` - Archivos JavaScript
- ✅ `static/css/` - Estilos CSS
- ✅ `static/images/` - Imágenes y assets

#### Infraestructura
- ✅ `requirements.txt` - Dependencias Python
- ✅ `.env` y `.env.example` - Configuraciones sensibles
- ✅ `scripts/` - Scripts auxiliares
- ✅ `tests/` - Tests unitarios

#### Documentación
- ✅ `docs/` - Documentación técnica
- ✅ `documentation/` - Guías y análisis

**Debes identificar:**
- Dependencias principales y sus relaciones
- Puntos de entrada del sistema (manage.py, settings.py, urls.py)
- Integraciones con BD, APIs externas, servicios

---

### 2️⃣ Contexto Persistente y Uso Responsable

#### Antes de crear algo NUEVO:

```
✓ Verificar si ya existe:
  - Archivo similar
  - Componente/Vista existente
  - Ruta ya implementada
  - Servicio/Utilidad duplicada
  - Función similar

✓ Si ya existe:
  - Reutilizar o mejorar lo existente
  - Evitar duplicar lógica
  - Refactorizar si es necesario

✓ Si NO existe:
  - Proponer EXPLÍCITAMENTE ubicación
  - Definir responsabilidad del archivo
  - Explicar relación con el resto del sistema
  - ESPERAR CONFIRMACIÓN antes de crear
```

---

### 3️⃣ Regla CRÍTICA: Consistencia Global de Cambios

**Cualquier cambio debe analizarse de forma TRANSVERSAL.**

Si modificas una estructura, modelo, endpoint, servicio o vista:

```
DEBES identificar TODOS los lugares impactados:

Backend:
  ├─ models.py (si cambia BD)
  ├─ views.py (si cambia lógica)
  ├─ forms.py (si cambia validación)
  ├─ urls.py (si cambia rutas)
  └─ admin.py (si cambia visualización)

Frontend:
  ├─ templates/ (si cambia presentación)
  ├─ static/js/ (si cambia comportamiento)
  ├─ static/css/ (si cambia estilos)

Transversal:
  ├─ tests/ (actualizar tests)
  ├─ documentation/ (documentar cambios)
  └─ scripts/ (si afecta scripts)

❌ NO se permiten cambios parciales que dejen el sistema inconsistente
✅ TODO ajuste debe ser COHERENTE en todos los puntos implicados
```

---

### 4️⃣ Protocolo de Cambios y Mejoras

Cuando se soliciten cambios o mejoras:

**DEBES explicar:**
1. ✅ **Qué archivos** serán modificados
2. ✅ **Por qué** cada archivo necesita el cambio
3. ✅ **Qué secciones/líneas** serán afectadas
4. ✅ **Impacto** en el flujo general del sistema
5. ✅ **Esperar confirmación explícita** antes de aplicar

**Formato requerido:**
```markdown
## Cambio: [Nombre del cambio]

### Archivos impactados:
- archivo1.py → Líneas X-Y → Razón del cambio
- archivo2.html → Sección ABC → Razón del cambio

### Justificación:
[Explicar por qué se necesita el cambio]

### Impacto en el sistema:
[Cómo afecta el resto del proyecto]

### Solicito confirmación para proceder
```

---

## 📁 PARTE 2: ESTRUCTURA Y ORGANIZACIÓN DE ARCHIVOS

### Estructura Base del Proyecto

```
proyecto_john/
│
├── 📂 mi_app/                          ← Aplicación Django principal
│   ├── migrations/                     ← Migraciones de BD
│   │   └── 0001_initial.py
│   ├── static/mi_app/                  ← Assets estáticos
│   │   ├── css/                        ← ✅ TODOS los CSS aquí
│   │   │   ├── style.css               ← Estilos principales
│   │   │   ├── responsive.css          ← Media queries
│   │   │   └── components.css          ← Componentes reutilizables
│   │   ├── js/                         ← ✅ TODOS los JavaScript aquí
│   │   │   ├── main.js                 ← Script principal
│   │   │   ├── dropdown-search.js      ← Funcionalidades específicas
│   │   │   ├── utils.js                ← Utilidades compartidas
│   │   │   └── validators.js           ← Validaciones cliente
│   │   └── images/                     ← ✅ TODAS las imágenes aquí
│   │       ├── logo.png
│   │       ├── icons/
│   │       └── backgrounds/
│   │
│   ├── templates/mi_app/               ← ✅ TODOS los HTML aquí
│   │   ├── base.html                   ← Template base
│   │   ├── inicio.html
│   │   ├── formularios/                ← Organizar por funcionalidad
│   │   │   ├── formulario_cliente.html
│   │   │   └── formulario_prestamo.html
│   │   ├── reportes/
│   │   │   ├── reporte_clientes.html
│   │   │   └── reporte_prestamos.html
│   │   └── modales/
│   │       ├── modal_confirmacion.html
│   │       └── modal_eliminar.html
│   │
│   ├── models.py                       ← Modelos de BD
│   ├── views.py                        ← Vistas/Controladores
│   ├── urls.py                         ← Rutas
│   ├── forms.py                        ← Formularios Django
│   ├── admin.py                        ← Admin panel
│   ├── utils.py                        ← Funciones auxiliares
│   └── tests.py                        ← Tests unitarios
│
├── 📂 proyecto_john/                   ← Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── 📂 scripts/                         ← Scripts auxiliares
│   ├── tools/                          ← Scripts de testing
│   ├── backup_manager.py
│   ├── crear_usuario_gerente.py
│   └── limpiar_bd.py
│
├── 📂 documentation/                   ← Documentación del proyecto
│   ├── bugs/
│   ├── development/
│   └── guides/
│
├── manage.py
├── requirements.txt
└── REGLAS_DESARROLLO.md                ← ✅ ESTE ARCHIVO
```

---

## 🎯 PARTE 3: BUENAS PRÁCTICAS DE CÓDIGO

### Convenciones de Nombres

#### Python (Backend)
```python
# Variables y funciones: snake_case
cliente_nombre = "Juan"
def obtener_clientes_activos():
    pass

# Clases: PascalCase
class ClientePrestamo:
    pass

# Constantes: UPPER_SNAKE_CASE
TASA_INTERES_MAXIMA = 0.30
DIAS_GRACIA_PRESTAMO = 5

# Métodos privados: _nombre_privado
def _validar_monto_interno(monto):
    pass
```

#### JavaScript (Frontend)
```javascript
// Variables y funciones: camelCase
let clienteNombre = "Juan";
function obtenerClientesActivos() {}

// Clases: PascalCase
class ClientePrestamo {}

// Constantes: UPPER_SNAKE_CASE
const TASA_INTERES_MAXIMA = 0.30;

// Métodos privados: _nombrePrivado
function _validarMontoInterno(monto) {}
```

#### HTML/CSS
```html
<!-- IDs: kebab-case (usado en JavaScript) -->
<div id="formulario-cliente">

<!-- Classes: kebab-case (para CSS) -->
<div class="tarjeta-prestamo card-premium">

<!-- Data attributes: kebab-case -->
<button data-prestamo-id="123">
```

#### CSS
```css
/* Classes: kebab-case */
.container-fluid { }
.tarjeta-principal { }
.boton-primario { }

/* Variables CSS: kebab-case */
:root {
    --color-primario: #007bff;
    --espaciado-base: 1rem;
}
```

---

### Organización de Código

#### Python/Django - Estructura de models.py

```python
"""
Modelos de datos del sistema de préstamos.
"""
from django.db import models
from django.contrib.auth.models import User

# Ordenar imports: Django → Aplicación

class Cliente(models.Model):
    """Modelo para representar un cliente."""
    
    # 1. Campos de BD
    usuario = models.OneToOneField(User, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    
    # 2. Meta información
    class Meta:
        ordering = ['nombre']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    # 3. String representation
    def __str__(self):
        return f"{self.nombre} ({self.cedula})"
    
    # 4. Propiedades y métodos
    @property
    def prestamos_activos(self):
        return self.prestamo_set.filter(estado='ACTIVO')
    
    def calcular_mora_total(self):
        """Calcula la mora total del cliente."""
        pass
```

#### Python/Django - Estructura de views.py

```python
"""
Vistas (controladores) de la aplicación.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cliente, Prestamo
from .forms import ClienteForm

# 1. Vistas de lectura (GET)
@login_required
def listar_clientes(request):
    """Muestra listado de clientes."""
    clientes = Cliente.objects.all()
    return render(request, 'mi_app/lista_clientes.html', {'clientes': clientes})

# 2. Vistas de creación (POST)
@login_required
def crear_cliente(request):
    """Crea un nuevo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'mi_app/formulario_cliente.html', {'form': form})

# 3. Vistas de detalle
@login_required
def detalle_cliente(request, pk):
    """Muestra detalles de un cliente."""
    cliente = Cliente.objects.get(pk=pk)
    return render(request, 'mi_app/detalle_cliente.html', {'cliente': cliente})

# 4. Vistas de actualización (PUT)
@login_required
def actualizar_cliente(request, pk):
    """Actualiza datos de un cliente."""
    pass

# 5. Vistas de eliminación (DELETE)
@login_required
def eliminar_cliente(request, pk):
    """Elimina un cliente."""
    pass

# 6. Vistas API (JSON)
@login_required
def api_mora_diaria(request):
    """API que retorna mora diaria en JSON."""
    mora = Cliente.objects.aggregate(mora_total=Sum('prestamo__mora'))
    return JsonResponse({'mora': mora['mora_total']})
```

#### JavaScript - Estructura de módulos

```javascript
/**
 * Module: clienteDropdown
 * Funcionalidad de búsqueda de clientes en dropdown
 * @version 1.0
 */

const clienteDropdown = (() => {
    // 1. Variables privadas
    const debounceDelay = 300;
    let debounceTimer = null;
    
    // 2. Configuración
    const config = {
        inputSelector: '#cliente-search',
        resultsSelector: '#cliente-results',
        apiEndpoint: '/api/buscar-cliente/'
    };
    
    // 3. Funciones privadas
    function _sanitizeInput(input) {
        return input.trim().toLowerCase();
    }
    
    function _requestClientes(query) {
        return fetch(`${config.apiEndpoint}?q=${query}`)
            .then(response => response.json());
    }
    
    // 4. Funciones públicas
    function init() {
        const input = document.querySelector(config.inputSelector);
        input.addEventListener('input', _handleInput);
    }
    
    function _handleInput(event) {
        clearTimeout(debounceTimer);
        const query = _sanitizeInput(event.target.value);
        
        debounceTimer = setTimeout(() => {
            _requestClientes(query);
        }, debounceDelay);
    }
    
    // 5. API pública
    return {
        init: init,
        config: config
    };
})();

// Inicializar al cargar
document.addEventListener('DOMContentLoaded', clienteDropdown.init);
```

---

### Separación de Responsabilidades

#### ❌ MALO - Todo en un archivo
```python
# views.py: 2000+ líneas de código
def crear_prestamo(request):
    # Validación
    # Cálculos
    # BD
    # Emails
    # PDFs
    # Logging
```

#### ✅ BUENO - Separado por responsabilidad
```python
# views.py: Solo lógica de presentación
def crear_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = PrestamoService.crear(form.cleaned_data)
            return redirect('detalle_prestamo', pk=prestamo.id)

# services.py: Lógica de negocio
class PrestamoService:
    @staticmethod
    def crear(datos):
        # Validaciones complejas
        # Cálculos de interés
        prestamo = Prestamo.objects.create(**datos)
        # Notificaciones
        PrestamoNotificador.enviar_confirmacion(prestamo)
        return prestamo

# validators.py: Validaciones
def validar_monto_prestamo(monto):
    pass

# utils.py: Funciones auxiliares
def calcular_interes_compuesto(monto, tasa, periodos):
    pass
```

---

## 📋 PARTE 4: ESTÁNDARES FRONTEND

### CSS - Organización y Estructura

```css
/* 1. Variables CSS (Tema) */
:root {
    /* Colores */
    --color-primario: #007bff;
    --color-secundario: #6c757d;
    --color-exito: #28a745;
    --color-peligro: #dc3545;
    
    /* Espaciado */
    --espaciado-xs: 0.25rem;
    --espaciado-sm: 0.5rem;
    --espaciado-base: 1rem;
    --espaciado-lg: 1.5rem;
    --espaciado-xl: 2rem;
    
    /* Tipografía */
    --font-principal: 'Segoe UI', sans-serif;
    --font-tamaño-base: 1rem;
    --font-peso-normal: 400;
    --font-peso-bold: 700;
}

/* 2. Reset y estilos base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-principal);
    font-size: var(--font-tamaño-base);
    line-height: 1.6;
    color: #333;
}

/* 3. Componentes reutilizables */
.boton {
    padding: var(--espaciado-base) var(--espaciado-lg);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.boton-primario {
    background-color: var(--color-primario);
    color: white;
}

.boton-primario:hover {
    background-color: darken(var(--color-primario), 10%);
}

/* 4. Utilidades */
.texto-centrado { text-align: center; }
.d-flex { display: flex; }
.gap-1 { gap: var(--espaciado-base); }

/* 5. Media queries al final */
@media (max-width: 768px) {
    .contenedor { padding: var(--espaciado-base); }
}
```

### JavaScript - Mejores Prácticas

```javascript
// ✅ BUENO: Usar const por defecto, let si es necesario
const CONFIG = { /* ... */ };
let estado = 'inicial';

// ✅ BUENO: Funciones con documentación JSDoc
/**
 * Obtiene un cliente por ID
 * @param {number} clienteId - ID del cliente
 * @returns {Promise<Object>} Datos del cliente
 * @throws {Error} Si el cliente no existe
 */
async function obtenerCliente(clienteId) {
    const response = await fetch(`/api/clientes/${clienteId}`);
    if (!response.ok) throw new Error('Cliente no encontrado');
    return response.json();
}

// ✅ BUENO: Manejo de errores
try {
    const cliente = await obtenerCliente(123);
} catch (error) {
    console.error('Error:', error.message);
}

// ❌ MALO: Var (deprecated)
var cliente = {}; // ← NO USAR

// ❌ MALO: Sin documentación
function foo(x) { /* ... */ }

// ❌ MALO: Sin manejo de errores
const cliente = fetch('/api/cliente').then(r => r.json());
```

---

## 🔒 PARTE 5: SEGURIDAD Y VALIDACIÓN

### Backend

```python
# ✅ BUENO: Validar SIEMPRE en el servidor
def crear_prestamo(request):
    if request.method == 'POST':
        # 1. Validar con Forms/Serializers
        form = PrestamoForm(request.POST)
        if form.is_valid():  # ← Valida límites, tipos, etc
            # 2. Validar lógica de negocio
            if not PrestamService.puede_crear(request.user):
                return error_response('No tienes permisos')
            # 3. Sanitizar datos
            datos = form.cleaned_data
            # 4. Procesar
            prestamo = Prestamo.objects.create(**datos)
        else:
            return error_response(form.errors)

# ❌ MALO: Confiar en cliente
def crear_prestamo(request):
    monto = request.POST.get('monto')  # ← Sin validación
    Prestamo.objects.create(monto=monto)  # ← Riesgo
```

### Frontend

```javascript
// ✅ BUENO: Validar también en cliente (UX) + Servidor (Seguridad)
function validarFormulario(datos) {
    if (!datos.nombre) throw new Error('Nombre requerido');
    if (datos.monto < 1000) throw new Error('Monto mínimo: $1000');
    // Más validaciones...
}

// ❌ MALO: Solo validar en cliente
if (usuario.ingresaFecha()) {  // ← Fácil de bypass
    guardar();
}
```

---

## ✅ PARTE 6: CHECKLIST ANTES DE COMMIT

Antes de hacer `git commit`, verifica:

```
□ Código formateado correctamente
□ No hay console.log() o print() en producción
□ Todos los archivos nuevos están en la carpeta correcta
□ HTML en templates/
□ CSS en static/css/
□ JavaScript en static/js/
□ Imágenes en static/images/

□ No hay código duplicado
□ Funciones tienen documentación
□ Variables tienen nombres descriptivos

□ Validación de entrada (Server-side primero)
□ Manejo de errores implementado
□ No hay datos sensibles en el código

□ Tests ejecutados y pasan
□ Sin errores de linting
□ Cambios documentados en este archivo

□ Todos los archivos impactados fueron modificados
□ El sistema está coherente (no hay cambios parciales)
```

---

## 🚀 PARTE 7: FLUJO DE TRABAJO ESTÁNDAR

### Para nueva funcionalidad

```
1. PLANIFICACIÓN
   ├─ Analizar el proyecto existente
   ├─ Identificar archivos a modificar
   ├─ Proponer cambios explícitamente
   └─ Esperar confirmación

2. DESARROLLO
   ├─ Crear/Modificar archivos según estructura
   ├─ Seguir convenciones de nombres
   ├─ Separar responsabilidades
   └─ Documentar código

3. VALIDACIÓN
   ├─ Ejecutar tests
   ├─ Verificar no hay duplicados
   ├─ Validar consistencia global
   └─ Checklist antes de commit

4. DOCUMENTACIÓN
   ├─ Actualizar documentación técnica
   ├─ Agregar comentarios complejos
   ├─ Actualizar este archivo si hay nuevas reglas
   └─ Actualizar HISTORICO_DE_CAMBIOS.md
```

### Para bugs/fixes

```
1. REPRODUCIR
   ├─ Identificar exactamente qué falla
   ├─ Documentar pasos de reproducción
   └─ Ubicar dónde ocurre (frontend/backend)

2. DIAGNOSTICAR
   ├─ Analizar logs
   ├─ Revisar código relacionado
   ├─ Identificar TODOS los archivos impactados
   └─ Proponer solución coherente

3. CORREGIR
   ├─ Hacer cambios consistentes en TODOS los archivos
   ├─ No dejar cambios parciales
   ├─ Verificar que no rompe algo más
   └─ Testing exhaustivo

4. DOCUMENTAR
   ├─ Agregar al HISTORICO_DE_CAMBIOS.md
   ├─ Actualizar documentación si es necesario
   └─ Crear test que evite regresión
```

---

## 🎨 PARTE 8: BUENAS PRÁCTICAS DE ORGANIZACIÓN

### Regla 1: NUNCA Código Inline - Archivos Separados Siempre

#### ❌ MALO - CSS/JS Inline en HTML
```html
<!-- ❌ NO HACER -->
<div style="color: red; font-size: 16px; margin: 10px;">
    Contenido
</div>

<button onclick="alert('Hecho')">Hacer algo</button>

<script>
    function hacerAlgo() {
        console.log('Algo');
    }
</script>
```

#### ✅ BUENO - Archivos Separados
```html
<!-- ✅ HACER -->
<div class="contenedor-principal">
    Contenido
</div>

<button id="boton-accion" class="boton-primario">Hacer algo</button>
```

```css
/* static/css/componentes.css */
.contenedor-principal {
    color: red;
    font-size: 16px;
    margin: 10px;
}

.boton-primario {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
}
```

```javascript
// static/js/acciones.js
document.getElementById('boton-accion').addEventListener('click', () => {
    hacerAlgo();
});

function hacerAlgo() {
    console.log('Algo');
}
```

**Ventajas:**
- ✅ Reutilizable en múltiples páginas
- ✅ Fácil de mantener y actualizar
- ✅ Mejor rendimiento (cache de navegador)
- ✅ Separación clara de responsabilidades
- ✅ Código más limpio y legible

---

### Regla 2: Respetar Estructura de Carpetas SIEMPRE

#### Estructura Obligatoria
```
mi_app/
├── static/mi_app/
│   ├── css/                    ← TODOS los estilos aquí
│   │   ├── style.css           ✅ Estilos globales
│   │   ├── responsive.css      ✅ Media queries
│   │   ├── componentes.css     ✅ Componentes
│   │   ├── formas.css          ✅ Formularios
│   │   └── modales.css         ✅ Modales
│   │
│   ├── js/                     ← TODOS los scripts aquí
│   │   ├── main.js             ✅ Script principal
│   │   ├── dropdown-search.js  ✅ Funcionalidades específicas
│   │   ├── validadores.js      ✅ Validaciones
│   │   ├── utils.js            ✅ Utilidades compartidas
│   │   └── handlers.js         ✅ Manejadores de eventos
│   │
│   └── images/                 ← TODAS las imágenes aquí
│       ├── logo.png
│       ├── icons/
│       └── backgrounds/
│
└── templates/mi_app/           ← TODOS los HTML aquí
    ├── base.html
    ├── inicio.html
    ├── formularios/
    ├── reportes/
    └── modales/
```

#### ❌ MALO - Mezclar en ubicaciones incorrectas
```
❌ NO HACER:
├── style.css en raíz
├── main.js en raíz
├── HTML dentro de mi_app/ (no en templates/)
├── CSS en templates/
└── JS en templates/
```

#### ✅ BUENO - Estructura coherente
```
✅ HACER:
├── static/mi_app/css/style.css
├── static/mi_app/js/main.js
├── static/mi_app/images/logo.png
└── templates/mi_app/base.html
```

**Por qué importa:**
- ✅ Fácil encontrar archivos
- ✅ Django collectstatic funciona correctamente
- ✅ Otros desarrolladores entienden la estructura
- ✅ Evita conflictos de rutas
- ✅ Mantiene proyecto organizado

---

### Regla 3: ANALIZAR Archivos Existentes ANTES de Crear Nuevos

#### Protocolo Obligatorio

```
┌─────────────────────────────────────────────────────┐
│ ANTES DE CREAR UN ARCHIVO NUEVO:                    │
└─────────────────────────────────────────────────────┘

PASO 1: BUSCAR
  ├─ ¿Existe un archivo similar?
  ├─ ¿Hay una carpeta existente para esto?
  └─ ¿Qué patrón siguen los archivos existentes?

PASO 2: ANALIZAR
  ├─ Revisar archivos similares
  ├─ Entender la estructura actual
  ├─ Identificar convenciones usadas
  └─ Ver cómo se organizan los módulos

PASO 3: DECIDIR
  ├─ ¿Puedo reutilizar archivo existente?
  ├─ ¿Debo crear uno nuevo?
  ├─ ¿Debo refactorizar lo existente?
  └─ PROPONER explícitamente la solución

PASO 4: ACTUAR
  └─ Crear/modificar siguiendo el patrón existente
```

#### Ejemplo: Crear nuevo JavaScript

```
❌ MALO - Crear sin análisis:
// Crear: mi_app/static/busqueda.js (en lugar equivocado)
// Sin revisar si ya existe algo similar

✅ BUENO - Analizar primero:

1. BUSCAR archivos JS existentes:
   ✓ Encontré: static/mi_app/js/
   ✓ Encontré: dropdown-search.js (búsqueda de clientes)

2. ANALIZAR estructura existente:
   ✓ Los archivos están en static/mi_app/js/
   ✓ Tienen nombres descriptivos con guiones
   ✓ Son módulos auto-contenidos

3. DECIDIR:
   ¿Es búsqueda avanzada diferente a dropdown-search.js?
   → SÍ: Crear: static/mi_app/js/busqueda-avanzada.js
   → NO: Extender: dropdown-search.js

4. ACTUAR:
   Seguir el patrón de dropdown-search.js
```

#### Ejemplo: Crear nuevo CSS

```
❌ MALO - Crear sin análisis:
// Crear: mi_app/static/mi_app/estilos.css (nombre genérico)
// Sin revisar la estructura

✅ BUENO - Analizar primero:

1. BUSCAR archivos CSS existentes:
   ✓ Encontré: style.css (global)
   ✓ Encontré: responsive.css (media queries)
   ✓ Encontré: componentes.css (componentes)

2. ANALIZAR estructura:
   ✓ Los estilos globales van en style.css
   ✓ Media queries en responsive.css
   ✓ Componentes en componentes.css

3. DECIDIR:
   ¿Son estilos globales?
   → SÍ: Agregar a style.css
   → NO: Agregar a componentes.css o crear archivo específico

4. ACTUAR:
   Modificar archivo existente, NO crear uno nuevo
```

---

### Regla 4: TRABAJAR Sobre Código Existente - NO Duplicar

#### Principio: DRY (Don't Repeat Yourself)

```
❌ MALO - Duplicación de código:

// archivo1.js
function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// archivo2.js (DUPLICADO)
function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// archivo3.js (DUPLICADO NUEVAMENTE)
function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

```
✅ BUENO - Código centralizado:

// static/mi_app/js/validadores.js
function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// En cualquier otro archivo que lo necesite:
// <script src="{% static 'mi_app/js/validadores.js' %}"></script>
// Luego usar: validarEmail(usuario.email)
```

#### Cuándo extender vs crear

```
┌──────────────────────────────────────────────────┐
│ DECIDIR: ¿Crear o Extender?                      │
└──────────────────────────────────────────────────┘

Escenario 1: Función similar existe
  Pregunta: ¿Hace lo mismo?
  → SÍ: Reutilizar
  → PARCIALMENTE: Refactorizar para reutilizar
  → NO: Crear nueva

Escenario 2: Componente similar existe
  Pregunta: ¿Puedo adaptarlo?
  → SÍ: Modificar existente
  → NO: Crear especializado

Escenario 3: Estilo similar existe
  Pregunta: ¿Es casi igual?
  → SÍ: Crear clase derivada
  → NO: Agregar nuevo en mismo archivo

Ejemplo:

EXISTE: .boton-primario
NECESITO: .boton-secundario

❌ MALO: Crear boton-secundario desde cero
✅ BUENO: 
.boton { /* estilos comunes */ }
.boton-primario { /* extensión */ }
.boton-secundario { /* extensión */ }
```

---

### Regla 5: Convención de Archivos por Tipo

#### JavaScript
```
✅ BUENO - Nombres descriptivos:
├── main.js                    ← Punto entrada principal
├── validadores.js             ← Validaciones
├── utilidades.js              ← Funciones auxiliares
├── dropdown-search.js         ← Funcionalidad específica
├── modal-confirmacion.js      ← Modal específico
└── handlers-pagos.js          ← Manejadores de pagos
```

#### CSS
```
✅ BUENO - Nombres descriptivos:
├── style.css                  ← Estilos globales
├── responsive.css             ← Media queries
├── componentes.css            ← Componentes reutilizables
├── formas.css                 ← Formularios
├── tablas.css                 ← Tablas
├── modales.css                ← Modales
└── temas.css                  ← Temas/Dark mode
```

#### HTML
```
✅ BUENO - Organización por funcionalidad:
templates/mi_app/
├── base.html                  ← Template base
├── inicio.html
├── formularios/
│   ├── formulario_cliente.html
│   ├── formulario_prestamo.html
│   └── formulario_pago.html
├── reportes/
│   ├── reporte_clientes.html
│   └── reporte_prestamos.html
├── modales/
│   ├── modal_confirmacion.html
│   ├── modal_eliminar.html
│   └── modal_editar.html
└── componentes/
    ├── navbar.html
    ├── sidebar.html
    └── pie.html
```

---

### Regla 6: Refactorización Antes de Crear

#### Escenario: Código Duplicado Encontrado

```python
# ❌ MALO - Dejar duplicado

# En views.py:
def crear_prestamo(request):
    monto = request.POST.get('monto')
    if monto < 1000 or monto > 999999999:
        return error('Monto inválido')
    # ... más código

def actualizar_prestamo(request, pk):
    monto = request.POST.get('monto')
    if monto < 1000 or monto > 999999999:
        return error('Monto inválido')
    # ... más código

# ✅ BUENO - Refactorizar en utils.py

# utils.py
def validar_rango_monto(monto, minimo=1000, maximo=999999999):
    """Valida que el monto esté en el rango permitido."""
    if monto < minimo or monto > maximo:
        raise ValueError(f'Monto debe estar entre {minimo} y {maximo}')
    return True

# views.py
def crear_prestamo(request):
    monto = request.POST.get('monto')
    try:
        validar_rango_monto(monto)
    except ValueError as e:
        return error(str(e))

def actualizar_prestamo(request, pk):
    monto = request.POST.get('monto')
    try:
        validar_rango_monto(monto)
    except ValueError as e:
        return error(str(e))
```

---

### Checklist: Buenas Prácticas ANTES de Crear/Modificar

```
□ ANÁLISIS
  ├─ ¿Revisar archivos existentes?
  ├─ ¿Existe estructura similar?
  ├─ ¿Qué convenciones se usan?
  └─ ¿Puedo reutilizar?

□ ORGANIZACIÓN
  ├─ ¿HTML en templates/?
  ├─ ¿CSS en static/css/?
  ├─ ¿JS en static/js/?
  ├─ ¿Imágenes en static/images/?
  └─ ¿Nada inline o en <style> tags?

□ DUPLICACIÓN
  ├─ ¿Existe código similar?
  ├─ ¿Puedo refactorizar?
  ├─ ¿Centralizar funciones?
  └─ ¿Evitar copiar-pegar?

□ CONVENCIONES
  ├─ ¿Nombres descriptivos?
  ├─ ¿snake_case en Python?
  ├─ ¿camelCase en JavaScript?
  ├─ ¿kebab-case en CSS?
  └─ ¿Patrón consistente?

□ DOCUMENTACIÓN
  ├─ ¿Archivo tiene comentario de propósito?
  ├─ ¿Funciones tienen docstrings?
  └─ ¿Propósito es obvio?
```

---

## 📌 RESUMEN DE REGLAS CRÍTICAS

| Regla | Cumplimiento | Consecuencia |
|-------|-------------|-------------|
| Analizar contexto completo ANTES de cambiar | **OBLIGATORIO** | Cambios inconsistentes |
| Cambios transversales (todos los archivos impactados) | **OBLIGATORIO** | Sistema quebrado |
| NUNCA código inline (CSS/JS) - Archivos separados | **OBLIGATORIO** | Código sucio y no mantenible |
| Respetar estructura de carpetas SIEMPRE | **OBLIGATORIO** | Caos y desorden |
| ANALIZAR archivos existentes ANTES de crear nuevos | **OBLIGATORIO** | Duplicación de código |
| TRABAJAR sobre código existente - NO duplicar | **OBLIGATORIO** | Deuda técnica |
| HTML en templates/, CSS en css/, JS en js/ | **OBLIGATORIO** | Caos y desorden |
| Convenciones de nombres (snake_case, camelCase, etc) | **OBLIGATORIO** | Código ilegible |
| Documentar cambios en REGLAS_DESARROLLO.md y HISTORICO_DE_CAMBIOS.md | **OBLIGATORIO** | Pérdida de contexto |
| Validación en servidor (no confiar en cliente) | **OBLIGATORIO** | Vulnerabilidades |
| Tests y verificación antes de commit | **RECOMENDADO** | Bugs en producción |

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Puedo guardar un archivo JavaScript en templates/?**  
R: NO. Siempre en `static/js/`. Los templates son para HTML únicamente.

**P: ¿Puedo usar estilos inline en HTML?**  
R: Evitarlo. Usar clases CSS en `static/css/`. Inline solo para casos excepcionales.

**P: ¿Puedo crear una nueva carpeta/archivo sin avisar?**  
R: NO. Proponer explícitamente antes de crearla.

**P: ¿Puedo cambiar solo la vista sin actualizar el modelo?**  
R: NO si el modelo está impactado. Cambios transversales.

**P: ¿Puedo hacer un commit con cambios en 5 archivos solo para 1 funcionalidad?**  
R: SÍ si todos están relacionados. NO si algunos son "por si acaso".

---

---

## 🧪 PARTE 9: TESTING Y QUALITY ASSURANCE

### Regla 1: Tests Antes de Producción
- Código → Tests → Review → Merge → Producción
- NO omitir tests

### Regla 2: Validación Dual
- Cliente: Feedback inmediato (UX)
- Servidor: Validación real (Seguridad)

### Regla 3: Linting
black . / flake8 .

---

## 🔀 PARTE 10: CONTROL DE VERSIONES

### Regla 1: Commits Descriptivos
- feat: Agregar búsqueda
- fix: Corregir mora
- refactor: Centralizar

### Regla 2: Branches
main → develop → feature/* → fix/*

### Regla 3: PRs con descripción

---

## 📱 PARTE 11: RESPONSIVE DESIGN

### Regla 1: Mobile-First SIEMPRE
320px → 768px → 1200px → 2440px

### Regla 2: Breakpoints
- 320px: Móvil pequeño
- 768px: Tablet
- 1200px: Desktop
- 1920px: Full HD
- 2440px: 4K

### Regla 3: Testing (5 mínimo)
✅ 320px ✅ 768px ✅ 1200px ✅ 1920px ✅ 2440px

### Regla 4: NUNCA max-width
@media (min-width: 768px) ✅
@media (max-width: 768px) ❌

---

## 🎨 PARTE 12: ESTÁNDARES UI/UX

### Regla 1: Variables CSS
:root { --color-primario, --espaciado-md, --transition }

### Regla 2: Accesibilidad A11y
- Labels + aria-label
- Contraste 4.5:1
- Fuente ≥ 14px

### Regla 3: Animaciones
Respetar prefers-reduced-motion

### Regla 4: Feedback Visual
Estados: hover, activo, disabled, loading, success, error

---

## ⚡ PARTE 13: PERFORMANCE

### Regla 1: Queries Optimizadas
select_related() / prefetch_related()

### Regla 2: Lazy Loading
<img loading="lazy">

### Regla 3: Caching
cache.set('key', value, 3600)

### Regla 4: Target < 3 segundos
Google PageSpeed

---

## 🔐 PARTE 14: SEGURIDAD

### Regla 1: CSRF - OBLIGATORIO
{% csrf_token %} en todo POST

### Regla 2: NO SQL Injection
ORM Django / Queries paramétrizadas

### Regla 3: NO XSS
{{ variable }} escapa automáticamente

### Regla 4: Rate Limiting
Máximo 5 intentos en 1 hora

---

## 📝 PARTE 15: DOCUMENTACIÓN

### Regla 1: Docstrings
Función + Args + Returns + Raises

### Regla 2: Comentarios Útiles
Comentar el POR QUÉ

### Regla 3: README
Instalación + Características + Contribuir

---

## 🎯 PARTE 16: MANTENIBILIDAD

### Regla 1: Versionado Semántico
MAYOR.MENOR.PATCH (v2.1.3)

### Regla 2: Changelog
Por versión: Agregado, Corregido, Seguridad

### Regla 3: Deuda Técnica
Lista visible con prioridades: 🔴 Alto, 🟡 Medio, 🟢 Bajo

### Regla 4: Deprecaciones
Avisar 2 versiones antes

---

## 📚 PARTE 17: DOCUMENTOS VIVOS - ACTUALIZACIÓN CONSISTENTE

### REGLA CRÍTICA: Documentación NO es Opcional

Desde 2026-02-20, las siguientes 10 "living documents" DEBEN ser leídas y actualizadas SIEMPRE:

**Ubicación:** `docs/sistemas/`

### Los 10 Documentos Vivos (OBLIGATORIOS)

1. **DASHBOARD_PROYECTO.md** - Estado actual diario
   - Leído: ✅ AL INICIAR sesión (5 min)
   - Actualizado: ✅ AL TERMINAR sesión (2 min)
   - ¿Por qué?: Saber en qué estado está el proyecto

2. **CHANGELOG_DETALLADO.md** - Historial de cambios
   - Leído: ✅ ANTES de trabajar (5 min)
   - Actualizado: ✅ ANTES de cada commit
   - ¿Por qué?: Entender qué pasó antes, evitar regresiones

3. **MANIFEST_ACTUALIZACION.md** - Qué actualizar cuándo
   - Leído: ✅ ANTES de cada sesión (5 min)
   - Actualizado: ✅ Si cambian procesos
   - ¿Por qué?: Ser disciplinado en actualizar docs

4. **MATRIZ_TRANSVERSAL_CAMBIOS.md** - Impacto cruzado
   - Leído: ✅ ANTES de cambios en múltiples modulos
   - Actualizado: ✅ Cuando se agregan nuevos módulos
   - ¿Por qué?: Evitar impactos inesperados

5. **ESTADO_COMPONENTES.md** - Versiones y status
   - Leído: ✅ CUANDO cambias componente
   - Actualizado: ✅ DESPUÉS de cambios técnicos
   - ¿Por qué?: Saber qué versión está en qué estado

6. **REGISTRO_DECISIONES_TECNICAS.md** - ADR (Architectural Decision Records)
   - Leído: ✅ CUANDO tomas decisión nueva
   - Actualizado: ✅ Cuando decisiones importantes se toman
   - ¿Por qué?: Explicar POR QUÉ se hizo así vs otra forma

7. **DEUDA_TECNICA.md** - Bugs conocidos y TODOs
   - Leído: ✅ ANTES de trabajar EN ESE ÁREA
   - Actualizado: ✅ Cuando descubres bug o adds workaround
   - ¿Por qué?: Evitar pisar rakes conocidos

8. **CHECKLIST_DEPLOYMENT.md** - Pre-producción
   - Leído: ✅ ANTES de cualquier deploy
   - Actualizado: ✅ Cuando cambian procesos de deploy
   - ¿Por qué?: Garantizar deploys seguros y repetibles

9. **INDICE_BUGS_POR_COMPONENTE.md** - Bug tracking by module
   - Leído: ✅ CUANDO trabajas EN componente
   - Actualizado: ✅ Cuando cierras bug o abre nuevo
   - ¿Por qué?: Saber qué bugs afectan qué áreas

10. **CRONOGRAMA_ACTUALIZACIONES.md** - Schedule
    - Leído: ✅ Al inicio de cada sprint/fase
    - Actualizado: ✅ Semanalmente con progreso
    - ¿Por qué?: No perder track de sprints y fechas

---

### REGLA CRÍTICA #1: LECTURA OBLIGATORIA AL INICIAR

**ANTES de cualquier trabao, debes leer:**

```
1. DASHBOARD_PROYECTO.md (5 min)
   ├─ ¿Cuál es el estado del proyecto?
   ├─ ¿Cuáles errores están pendientes?
   └─ ¿Qué versión estoy trabajando?

2. CHANGELOG_DETALLADO.md (5 min)
   ├─ ¿Qué cambios se hicieron recientemente?
   ├─ ¿Hay breaking changes?
   └─ ¿Qué bugs fueron arreglados?

3. DEUDA_TECNICA.md (3 min)
   ├─ ¿Hay trampas en esta área?
   ├─ ¿Hay workarounds conocidos?
   └─ ¿Hay bugs que debo evitar?
```

**SIN ESTA LECTURA, NO COMENZAR A TRABAJAR.**

---

### REGLA CRÍTICA #2: ACTUALIZACIÓN OBLIGATORIA ANTES DE COMMIT

**NO PUEDES HACER `git commit` SIN actualizar mínimo:**

```
✅ CHANGELOG_DETALLADO.md
   └─ Agregar entrada del cambio que hiciste

✅ DASHBOARD_PROYECTO.md
   └─ Actualizar métricas si cambiaron

✅ El documento específico del cambio
   ├─ ESTADO_COMPONENTES.md (si tocaste componente)
   ├─ REGISTRO_DECISIONES_TECNICAS.md (si decision nueva)
   ├─ DEUDA_TECNICA.md (si descubriste/resolviste deuda)
   └─ INDICE_BUGS_POR_COMPONENTE.md (si cerraste bug)
```

**SI NO ACTUALIZASTE ESTOS, TU COMMIT ESTÁ INCOMPLETO.**

---

### REGLA CRÍTICA #3: DISCIPLINA DE ACTUALIZACIÓN

**Tabla de responsabilidades:**

| Evento | Documento | Acción |
|--------|-----------|--------|
| Iniciar sesión | DASHBOARD, CHANGELOG, DEUDA_TECNICA | Leer |
| Cambio en módulo | ESTADO_COMPONENTES | Actualizar |
| Tomas decisión | REGISTRO_DECISIONES_TECNICAS | Agregar ADR |
| Descubres bug | DEUDA_TECNICA | Agregar DEBT-xxx |
| Cierras bug | INDICE_BUGS_POR_COMPONENTE | Marcar resuelto |
| Cambio multi-módulo | MATRIZ_TRANSVERSAL_CAMBIOS | Verificar impacto |
| Antes de deploy | CHECKLIST_DEPLOYMENT | Seguir pasos |
| Antes de commit | CHANGELOG, DASHBOARD, Doc específica | Actualizar |
| Fin de sesión | DASHBOARD, s y CRONOGRAMA | Registrar progreso |

---

### CHECKLIST: Ritual de Sesión Completa

**INICIO (10 minutos):**
```
- [ ] Leí DASHBOARD_PROYECTO.md
- [ ] Leí CHANGELOG_DETALLADO.md
- [ ] Leí DEUDA_TECNICA.md
- [ ] Leí CRONOGRAMA_ACTUALIZACIONES.md (si es lunes/start sprint)
```

**DURANTE (N horas):**
```
- [ ] Cada cambio importante → actualizar CHANGELOG_DETALLADO.md
- [ ] Si cambio en componente → actualizar ESTADO_COMPONENTES.md
- [ ] Si descubro algo → actualizar DEUDA_TECNICA.md
```

**ANTES DE CADA COMMIT (5 minutos):**
```
- [ ] Leí MATRIZ_TRANSVERSAL_CAMBIOS.md
- [ ] Actualicé CHANGELOG_DETALLADO.md
- [ ] Actualicé DASHBOARD_PROYECTO.md
- [ ] Actualicé documento específico del cambio
- [ ] Commit: "TIPO: Descripción"
```

**FIN DE SESIÓN (5 minutos):**
```
- [ ] Actualicé DASHBOARD_PROYECTO.md (última línea con fecha/hora)
- [ ] Actualicé CRONOGRAMA_ACTUALIZACIONES.md con progreso
- [ ] Git push
- [ ] ✅ SESIÓN COMPLETA
```

---

### Por QUE esto es importante (HISTORIA)

Antes (2026-02-20):
```
❌ Sin documentación centralizada
❌ "¿Qué pasó la sesión pasada?" - sin forma de saberlo
❌ Cambios parciales (se olvidaban de actualizar cosas)
❌ Contexto perdido entre sesiones
❌ Imposible auditar decisiones
❌ Bugs que se volvían a abrir
```

Ahora (2026-02-20+):
```
✅ 10 documentos vivos mantienen contexto
✅ Cada sesión sabe qué pasó antes
✅ Cambios documentados mientras suceden
✅ Contexto SIEMPRE disponible
✅ Decisiones auditables
✅ Bugs imposibles de "volver a romper"
```

---

### REGLA CRÍTICA #4: Sin Excepciones

NO HAY EXCEPCIÓN PARA ESTO.

- "Es un cambio pequeño" → ACTUALIZAR CHANGELOG IGUAL
- "Es un hotfix rápido" → ACTUALIZAR DASHBOARD IGUAL
- "No tengo tiempo" → Entonces no commits
- "Ya lo haré después" → No, ANTES de commit o no hay commit

**Esta regla es como REGLA #0: SIEMPRE PRIMERO.**

---

## ✅ CHECKLIST PRE-COMMIT (35+ Items)

ANÁLISIS: [ ] Contexto [ ] Archivos [ ] Transversales
CÓDIGO: [ ] Sin inline [ ] Descriptivos [ ] Sin duplicación
TESTING: [ ] Tests ✅ [ ] Validación [ ] Sin errores
RESPONSIVE: [ ] 320px ✅ [ ] 768px ✅ [ ] 1200px ✅ [ ] 1920px ✅ [ ] 2440px ✅
ACCESIBILIDAD: [ ] Labels [ ] aria-label [ ] Contraste [ ] Fuente
SEGURIDAD: [ ] CSRF [ ] Servidor [ ] Parámetrizadas
PERFORMANCE: [ ] Queries [ ] Lazy [ ] Cache [ ] <3s
GIT: [ ] Commits [ ] HISTORICO

---

## 📊 MATRIZ CRÍTICA

| Prioridad | Regla | Impacto |
|-----------|-------|--------|
| 🔴 CRÍTICA | Analizar contexto | Quebrado |
| 🔴 CRÍTICA | Transversales | Inconsistencia |
| 🔴 CRÍTICA | Sin inline | Inmantenible |
| 🔴 CRÍTICA | Mobile 320-2440px | No responsivo |
| 🔴 CRÍTICA | CSRF+SQL+XSS | Vulnerable |
| 🟠 ALTA | Queries optimizadas | Lento |
| 🟠 ALTA | Accesibilidad | Excluyente |
| 🟡 MEDIA | Documentación | Conocimiento perdido |

---

**Documento oficial del proyecto. Última revisión: 02/02/2026**
Versión: 3.0 - Completo, Exhaustivo y Profesional

