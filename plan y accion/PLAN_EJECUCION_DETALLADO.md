# 📋 PLAN DE EJECUCIÓN DETALLADO - PROBLEMAS DEL PROYECTO

**Fecha:** 21 de Febrero, 2026  
**Objetivo:** Resolver 32 problemas de forma sistemática y ordenada  
**Score Actual:** 4.9/10 → **Score Target:** 9.5/10  
**Tiempo Total:** ~135 horas (~2 semanas intensivas)  

---

# 🗂️ CÓMO USAR ESTE DOCUMENTO

1. **Necesario leer ANTES:**
   - ✅ `!IMPORTANTE LEER SIEMPRE!REGLAS_DESARROLLO.md` (CRÍTICO)
   - ✅ `PROBLEMAS_PRIORIZADO_COMPLETO.md` (en Desktop)

2. **Cómo resolver cada problema:**
   - Leer la descripción completa
   - Seguir los PASOS (1, 2, 3, etc)
   - Ejecutar los COMANDOS especificados
   - Crear/modificar los ARCHIVOS listados
   - Crear los TESTS especificados
   - Verificar con CHECKLIST
   - Escribir NOTAS de cambios en documentación

3. **Después de cada problema:**
   - Hacer commit con mensaje claro
   - Actualizar documentación
   - Pasar al siguiente problema

---

# 🔴 FASE 1: BLOQUEADORES CRÍTICOS (80 HORAS)

## ⏱️ Estimado: Semana 1 (40h intensivas)

El equipo debe trabajar en paralelo en esta fase:
- Developer 1: Problemas #1, #4, #6
- Developer 2: Problemas #2, #5
- Developer 3: Problemas #3, #7, #8, #9, #10

---

## CRÍTICA #1: SIN AUTENTICACIÓN DE USUARIOS (8-10 HORAS)

**AsignTo:** Developer que entienda Django Auth  
**Blocker:** Sí - **NO PUEDE IR A PRODUCCIÓN SIN ESTO**  

### 📋 CHECKLIST PRE-INICIO
```
□ Leí REGLAS_DESARROLLO.md completamente
□ Entiendo REGLA #0 (contexto completo antes de actuar)
□ Entiendo REGLA #3 (cambios transversales obligatorios)
□ Leí descripción de CRÍTICA #1
□ Tengo las herramientas instaladas (Django, Python 3.11)
```

### 🎯 OBJETIVOS DEL PROBLEMA
```
❌ ACTUAL:
- Cualquiera accede a /clientes/ sin login
- No hay sesiones
- No se sabe quién hizo qué

✅ DESPUÉS:
- Solo usuarios autenticados pueden acceder
- Cada operación está asociada a un usuario
- Sistema auditado y seguro
```

### 📍 ARCHIVOS A MODIFICAR

1. **proyecto_john/settings.py**
   - Verificar/añadir Django auth middleware
   - Configurar LOGIN_URL
   - Verificar INSTALLED_APPS tiene 'django.contrib.auth'

2. **mi_app/views.py**
   - Agregar @login_required a TODAS las vistas
   - Modificar operaciones para registrar request.user

3. **mi_app/models.py**
   - Agregar campo 'usuario' a Prestamo, Cuota, Pago, Cliente (si no existen)
   - Agregar timestamps (created_at, updated_at)

4. **Crear: mi_app/auth_views.py**
   - Vista de login
   - Vista de logout
   - Vista de registro

5. **Crear: mi_app/templates/login.html**
   - Formulario de login
   - Links a registro/password reset

6. **proyecto_john/urls.py**
   - Añadir rutas de login/logout
   - Proteger todas las vistas

### 🔧 PASOS A EJECUTAR

#### PASO 1: Verificar Django Auth (30 min)
```bash
# En terminal Python shell
python manage.py shell

# Ejecutar:
from django.contrib.auth.models import User
print(f"Django auth instalado: {User}")
# Debería imprimir algo como: <class 'django.contrib.auth.models.User'>

# Salir
exit()
```

#### PASO 2: Crear usuario admin (15 min)
```bash
python manage.py createsuperuser
# Responder:
# Username: admin
# Email: admin@localhost
# Password: (crear fuerte)
```

#### PASO 3: Crear auth_views.py (45 min)

**Crear archivo:** `mi_app/auth_views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login"""
    if request.method == 'GET':
        return render(request, 'login.html')
    
    # POST
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, f"Bienvenido {user.first_name or user.username}")
        return redirect('index')  # O view principal
    else:
        messages.error(request, "Usuario o contraseña incorrectos")
        return render(request, 'login.html', {
            'username': username,
            'error': 'Credenciales inválidas'
        })

@login_required(login_url='login')
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, "Sesión cerrada correctamente")
    return redirect('login')

def register_view(request):
    """Vista de registro (opcional)"""
    if request.method == 'GET':
        return render(request, 'register.html')
    
    # POST
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')
    
    if password != password_confirm:
        messages.error(request, "Contraseñas no coinciden")
        return render(request, 'register.html')
    
    if User.objects.filter(username=username).exists():
        messages.error(request, "Usuario ya existe")
        return render(request, 'register.html')
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    messages.success(request, "Usuario creado. Inicia sesión")
    return redirect('login')
```

#### PASO 4: Crear login.html (30 min)

**Crear archivo:** `mi_app/templates/login.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h3>Iniciar Sesión</h3>
                </div>
                <div class="card-body">
                    {% if messages %}
                        {% for message in messages %}
                            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}

                    <form method="POST" action="{% url 'login' %}">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="username" class="form-label">Usuario</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>

                        <div class="mb-3">
                            <label for="password" class="form-label">Contraseña</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>

                        <button type="submit" class="btn btn-primary w-100">Iniciar Sesión</button>
                    </form>

                    <hr>
                    <p class="text-center">
                        ¿No tienes cuenta? <a href="{% url 'register' %}">Regístrate</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### PASO 5: Actualizar proyecto_john/urls.py (30 min)

**Modificar:** `proyecto_john/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from mi_app import views, auth_views  # Añadir auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mi_app.urls')),
    
    # Auth URLs
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
]
```

#### PASO 6: Proteger todas las vistas (90 min)

**Modificar:** `mi_app/views.py`

En TODAS las vistas que acceden/modifican datos, agregar:
```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def lista_clientes(request):
    # ... código existente
```

⚠️ **CRÍTICO:** Esto debe aplicarse a:
- lista_clientes
- crear_cliente
- editar_cliente
- eliminar_cliente
- lista_prestamos
- crear_prestamo
- editar_prestamo
- lista_pagos
- crear_pago
- (Y cualquier otra vista que maneje datos)

#### PASO 7: Registrar usuario en operaciones (60 min)

**Modificar:** `mi_app/views.py` - en cada CREATE/UPDATE

```python
# ANTES:
prestamo = Prestamo.objects.create(
    cliente=cliente,
    monto=monto,
    # ...
)

# DESPUÉS:
prestamo = Prestamo.objects.create(
    cliente=cliente,
    monto=monto,
    usuario_creador=request.user,  # ← AGREGAR
    # ...
)
```

⚠️ **NECESARIO:** Crear migrations para agregar campo usuario_creador

```bash
python manage.py makemigrations
python manage.py migrate
```

### ✅ CHECKLIST DE FINALIZACIÓN

```
□ Django auth middleware verificado en settings.py
□ Superuser creado y funciona en /admin/
□ auth_views.py creado con login/logout/register
□ login.html creado con formulario
□ URLs configuradas correctamente
□ @login_required en TODAS las vistas de mi_app/views.py
□ usuario_creador campo agregado a modelos
□ Migrations ejecutadas
□ Puedo ir a /login/ y funciona
□ Login funciona con credenciales correctas
□ Login rechaza credenciales incorrectas
□ Después de logout, /clientes/ redirige a /login/
□ Tests escritos (ver TESTS requeridos abajo)
```

### 🧪 TESTS REQUERIDOS

**Crear archivo:** `mi_app/tests/test_auth.py`

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthenticationTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_accessible(self):
        """GET /login/ debe estar accesible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_valid_credentials(self):
        """Login con credenciales correctas funciona"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_invalid_credentials(self):
        """Login con credenciales incorrectas falla"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # No redirect
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_works(self):
        """Logout funciona"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_cliente_lista_requires_login(self):
        """/clientes/ requiere estar logueado"""
        response = self.client.get(reverse('lista_clientes'))
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_cliente_lista_with_login(self):
        """/clientes/ accesible después de login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('lista_clientes'))
        self.assertEqual(response.status_code, 200)
```

**Ejecutar tests:**
```bash
python manage.py test mi_app.tests.test_auth -v 2
```

### 📝 DOCUMENTACIÓN A ACTUALIZAR

Después de finalizar este problema, actualizar:

1. **Crear:** `IMPLEMENTACION_AUTENTICACION.md` con:
   - Cómo loguearse
   - Cómo crear usuarios
   - Cómo cambiar contraseña
   - Cómo habilitar nuevos usuarios

2. **Actualizar:** README.md
   - Sección "Seguridad" indicar que sistema requiere autenticación

3. **Actualizar:** Archivo de desarrollo
   - Registrar que autenticación fue implementada

### 🎯 RESULTADO ESPERADO

✅ Después de este problema:
- Solo usuarios autenticados pueden access a /clientes/
- Cada operación es trazada al usuario que la hizo
- Sistema es seguro para producción
- Score sube de 4.9 → 5.5 aproximadamente

---

## CRÍTICA #2: BÚSQUEDA AJAX ROTA (4-6 HORAS)

**AsignTo:** Developer con experiencia en frontend/JavaScript  
**Blocker:** Sí - Funcionalidad core rota  

### 📋 CHECKLIST PRE-INICIO
```
□ Leí REGLAS_DESARROLLO.md completamente
□ Entiendo problema en CRÍTICA #2
□ Tengo Firefox y Chrome para testing
□ Tengo DevTools abierto
```

### 🎯 PROBLEMA ACTUAL

```
La búsqueda de clientes en dropdown:
1. A veces funciona, a veces no
2. Desaparece al scrollear
3. No funciona en móvil (<768px)
4. Hay 3 scripts JavaScript conflictivos
5. Z-index completamente roto
```

### 📍 ARCHIVOS A MODIFICAR

1. **mi_app/templates/base.html** - Línea 600-800 (dropdown HTML)
2. **mi_app/static/js/dynamic_search.js** (eliminar o refactorizar)
3. **mi_app/static/js/universal_search.js** (eliminar o refactorizar)
4. **Crear:** `mi_app/static/js/client_search.js` (nuevo, limpio)

### 🔧 PASOS A EJECUTAR

#### PASO 1: Limpiar templates/base.html (45 min)

Buscar TODAS las referencias a búsqueda y comentar (para referencia):

```html
<!-- BÚSQUEDA DE CLIENTES - LIMPIA -->
<div class="search-container">
    <input 
        type="text" 
        id="clientSearchInput" 
        placeholder="Buscar cliente..."
        class="form-control"
        autocomplete="off"
    >
    <ul id="clientSearchResults" class="search-results-dropdown"></ul>
</div>

<style>
    .search-container {
        position: relative;
        width: 100%;
        z-index: 1000;
    }
    
    #clientSearchInput {
        width: 100%;
        padding: 8px;
        font-size: 14px;
    }
    
    .search-results-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        list-style: none;
        margin: 0;
        padding: 0;
        max-height: 300px;
        overflow-y: auto;
        z-index: 1001;
        display: none;
    }
    
    .search-results-dropdown.active {
        display: block;
    }
    
    .search-results-dropdown li {
        padding: 10px;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    
    .search-results-dropdown li:hover {
        background: #f5f5f5;
    }
</style>
```

#### PASO 2: Crear client_search.js (90 min)

**Crear archivo:** `mi_app/static/js/client_search.js`

```javascript
/**
 * BÚSQUEDA DE CLIENTES - CLEAN & SIMPLE
 * 
 * Una sola fuente de verdad para búsqueda de clientes
 * Sin conflictos, sin duplicados
 */

class ClientSearch {
    constructor(inputSelector, resultsSelector) {
        this.input = document.querySelector(inputSelector);
        this.resultsContainer = document.querySelector(resultsSelector);
        this.debounceTimer = null;
        this.debounceDelay = 300; // ms
        this.currentResults = [];
        
        if (this.input && this.resultsContainer) {
            this.attachEventListeners();
        }
    }
    
    attachEventListeners() {
        // Input event con debounce
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            
            if (e.target.value.length < 2) {
                this.hideResults();
                return;
            }
            
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, this.debounceDelay);
        });
        
        // Click fuera para cerrar
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });
        
        // Enter para seleccionar primer resultado
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const firstResult = this.resultsContainer.querySelector('li');
                if (firstResult) {
                    firstResult.click();
                }
            }
        });
    }
    
    search(query) {
        console.log(`Buscando: ${query}`);
        
        fetch(`/api/clientes/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.currentResults = data.results;
                this.renderResults(data.results);
            })
            .catch(error => {
                console.error('Error en búsqueda:', error);
                this.showError('Error en búsqueda');
            });
    }
    
    renderResults(results) {
        if (results.length === 0) {
            this.showError('No se encontraron resultados');
            return;
        }
        
        // Limpiar resultados previos
        this.resultsContainer.innerHTML = '';
        
        // Agregar nuevos resultados
        results.forEach(client => {
            const li = document.createElement('li');
            li.textContent = `${client.nombre} - CI: ${client.cedula}`;
            li.dataset.clientId = client.id;
            li.addEventListener('click', () => this.selectClient(client));
            this.resultsContainer.appendChild(li);
        });
        
        this.showResults();
    }
    
    selectClient(client) {
        console.log(`Cliente seleccionado: ${client.nombre} (${client.id})`);
        
        // Actualizar input
        this.input.value = client.nombre;
        
        // Trigger custom event para que otros scripts escuchen
        const event = new CustomEvent('clientSelected', {
            detail: client
        });
        this.input.dispatchEvent(event);
        
        // Limpiar resultados
        this.hideResults();
    }
    
    showResults() {
        this.resultsContainer.classList.add('active');
    }
    
    hideResults() {
        this.resultsContainer.classList.remove('active');
    }
    
    showError(message) {
        this.resultsContainer.innerHTML = `<li class="error">${message}</li>`;
        this.showResults();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.clientSearch = new ClientSearch(
        '#clientSearchInput',
        '#clientSearchResults'
    );
});
```

#### PASO 3: Crear endpoint API para búsqueda (60 min)

**Crear archivo:** `mi_app/api_views.py`

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Cliente

@login_required
@require_http_methods(["GET"])
def api_clientes_search(request):
    """
    API endpoint para búsqueda de clientes
    
    GET /api/clientes/search/?q=juan
    
    Returns: {
        "success": true,
        "results": [
            {"id": 1, "nombre": "Juan Pérez", "cedula": "1234567890"},
            ...
        ]
    }
    """
    q = request.GET.get('q', '').strip()
    
    if len(q) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Mínimo 2 caracteres',
            'results': []
        })
    
    # Buscar en nombre o cédula
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=q) | Q(cedula__icontains=q)
    ).values('id', 'nombre', 'cedula')[:20]  # Máximo 20 resultados
    
    return JsonResponse({
        'success': True,
        'query': q,
        'results': list(clientes)
    })
```

**Agregar a:** `proyecto_john/urls.py`

```python
path('api/clientes/search/', api_clientes_search, name='api_clientes_search'),
```

#### PASO 4: Incluir script en base.html (15 min)

En el footer de `mi_app/templates/base.html`:

```html
<!-- Búsqueda de clientes -->
<script src="{% static 'js/client_search.js' %}"></script>
```

#### PASO 5: ELIMINAR scripts viejos (15 min)

Buscar y ELIMINAR (o comentar) en templates:
- Llamadas a `dynamic_search.js`
- Llamadas a `universal_search.js`
- Scripts inline de búsqueda

### ✅ CHECKLIST DE FINALIZACIÓN

```
□ base.html limpio (solo un input de búsqueda)
□ client_search.js creado y funciona
□ api_clientes_search endpoint funciona
□ Débounce funciona (espera 300ms antes de buscar)
□ Resultados aparecen en dropdown
□ Dropdown tiene z-index correcto (siempre visible)
□ Funciona en todos los navegadores (Firefox, Chrome, Safari)
□ Funciona en móvil (<768px)
□ Scrolling no afecta dropdown
□ Seleccionar cliente limpia búsqueda
□ Cero conflictos de JavaScript
□ Tests escritos (ver TESTS abajo)
```

### 🧪 TESTS REQUERIDOS

**Crear archivo:** `mi_app/tests/test_search.py`

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from mi_app.models import Cliente

class ClientSearchTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
        # Crear clientes de prueba
        Cliente.objects.create(nombre='Juan Pérez', cedula='1234567890')
        Cliente.objects.create(nombre='María García', cedula='0987654321')
        Cliente.objects.create(nombre='Carlos López', cedula='5555555555')
        
        self.client.login(username='testuser', password='testpass')
    
    def test_search_api_requires_login(self):
        """API de búsqueda requiere estar logueado"""
        self.client.logout()
        response = self.client.get('/api/clientes/search/?q=juan')
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_search_with_short_query(self):
        """Búsqueda con query < 2 caracteres retorna error"""
        response = self.client.get('/api/clientes/search/?q=j')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertEqual(len(data['results']), 0)
    
    def test_search_by_nombre(self):
        """Búsqueda por nombre funciona"""
        response = self.client.get('/api/clientes/search/?q=juan')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['nombre'], 'Juan Pérez')
    
    def test_search_by_cedula(self):
        """Búsqueda por cédula funciona"""
        response = self.client.get('/api/clientes/search/?q=1234567890')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['cedula'], '1234567890')
    
    def test_search_case_insensitive(self):
        """Búsqueda es case-insensitive"""
        response = self.client.get('/api/clientes/search/?q=JUAN')
        data = response.json()
        self.assertEqual(len(data['results']), 1)
    
    def test_search_multiple_results(self):
        """Búsqueda retorna múltiples resultados"""
        response = self.client.get('/api/clientes/search/?q=a')
        data = response.json()
        self.assertGreater(len(data['results']), 1)
    
    def test_search_no_results(self):
        """Búsqueda sin resultados"""
        response = self.client.get('/api/clientes/search/?q=xyz123notfound')
        data = response.json()
        self.assertEqual(len(data['results']), 0)
```

**Ejecutar tests:**
```bash
python manage.py test mi_app.tests.test_search -v 2
```

### 📝 DOCUMENTACIÓN A ACTUALIZAR

Crear: `IMPLEMENTACION_BUSQUEDA.md`

```markdown
# Búsqueda de Clientes

## Cómo funciona

1. Usuario escribe en el input "Buscar cliente..."
2. Se espera 300ms (debounce)
3. Se hace fetch a `/api/clientes/search/?q=texto`
4. Resultados aparecen en dropdown
5. Click en resultado selecciona cliente

## Arquitectura

- `client_search.js` - Controlador de búsqueda (frontend)
- `/api/clientes/search/` - Endpoint backend
- `base.html` - HTML del input

## Performance

- Búsqueda es rápida (<200ms)
- No hay lag al escribir
- Máximo 20 resultados mostrados
```

### 🎯 RESULTADO ESPERADO

✅ Después de este problema:
- Búsqueda funciona siempre (sin fallos intermitentes)
- Performance es excelente
- Funciona en todos los dispositivos
- Código limpio y sin conflictos
- Score sube de 5.5 → 6.2 aproximadamente

---

## CRÍTICA #3: INCONSISTENCIAS FINANCIERAS LATENTES (8-12 HORAS)

**[Continúa en próximo documento debido a límite de caracteres]**

*(Ver PLAN_EJECUCION_DETALLADO_PARTE2.md para CRÍTICA #3-#10)*

---

# 🟡 FASE 2: DEUDA TÉCNICA (40 HORAS)

## ⏱️ Estimado: Semana 2

*[Ver PLAN_EJECUCION_DETALLADO_PARTE2.md]*

---

# 🟢 FASE 3: TESTS & COBERTURA (15-20 HORAS)

## ⏱️ Estimado: Semana 3

*[Ver PLAN_EJECUCION_DETALLADO_PARTE3.md]*

---

## 📊 RESUMEN EJECUTIVO

| Fase | Problemas | Horas | Score Before | Score After |
|------|-----------|-------|--------------|-------------|
| **FASE 1** | #1-#10 | 80h | 4.9/10 | 7.2/10 |
| **FASE 2** | #11-#20 | 40h | 7.2/10 | 8.8/10 |
| **FASE 3** | #21-#32 | 15h | 8.8/10 | 9.5/10 |
| **TOTAL** | 32 | **135h** | 4.9/10 | **9.5/10** |

---

## 🔄 WORKFLOW PARA CADA PROBLEMA

Para cada problema, el developer debe:

1. ✅ **LEER:** Descripción completa del problema
2. ✅ **REVISAR:** REGLAS_DESARROLLO.md (especialmente REGLA #0 y #3)
3. ✅ **EJECUTAR:** Pasos 1, 2, 3, etc (en orden)
4. ✅ **CREAR:** Tests especificados
5. ✅ **VERIFICAR:** Checklist de finalización
6. ✅ **DOCUMENTAR:** Notas en IMPLEMENTACION_*.md
7. ✅ **COMMIT:** Con mensaje claro
8. ✅ **PASAR:** Al siguiente problema

---

## 🎯 KPIs DE PROGRESO

Rastrear durante el proyecto:

```
Sesión 1:
- Problemas resueltos: #1-#3 (24h)
- Score estimado: 5.5/10
- Tests añadidos: 15+
- Commits: 3+

Sesión 2:
- Problemas resueltos: #4-#6 (18h)
- Score estimado: 6.2/10
- Tests añadidos: 10+
- Commits: 3+

... (continúa)
```

---

**Próximo:** PLAN_EJECUCION_DETALLADO_PARTE2.md (CRÍTICA #3-#10)
