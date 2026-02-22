# 🔍 Monitoring & Debugging Guide - Gestion Prestamos

## 1. Django Shell - Inspeccionar datos en tiempo real

```bash
python manage.py shell
```

### Queries útiles

```python
from mi_app.models import Cliente, Prestamo, Cuota, Pago, ListaNegra

# Ver clientes
Cliente.objects.count()  # Total
cliente = Cliente.objects.first()

# Ver préstamos activos
prestamos_activos = Prestamo.objects.filter(estado='vigente')
prestamos_activos.count()

# Encontrar clientes en lista negra
lista_negra = ListaNegra.objects.filter(activa=True)
for item in lista_negra:
    print(f"{item.cliente.nombre}: {item.razon}")

# Calcular totales
from django.db.models import Sum, Count, Avg
Prestamo.objects.aggregate(
    total=Sum('monto'),
    promedio=Avg('monto'),
    count=Count('id')
)

# Encontrar préstamos vencidos
from datetime import date
prestamos_vencidos = Prestamo.objects.filter(fecha_fin_teorica__lt=date.today())
prestamos_vencidos.count()

# Ver performance del cliente (N+1 query fix validation)
from django.db.models import Count, Q
clientes = Cliente.objects.annotate(
    prestamos_count=Count('prestamo', filter=Q(prestamo__estado='vigente'))
).order_by('-prestamos_count')
```

---

## 2. Django Debug Toolbar - Análisis interactivo

### Instalación

```bash
pip install django-debug-toolbar
```

### Configuración (settings.py)

```python
# Si DEBUG=True en desarrollo
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Uso

- Abrir app en http://localhost:8000 con DEBUG=True
- Ver panel en esquina inferior derecha
- Analizar:
  - SQL queries ejecutadas
  - Tiempo de respuesta
  - Headers HTTP
  - Cache hits/misses

---

## 3. Query Optimization Scripts

### Detectar N+1 queries

```bash
cat > check_n_plus_one.py << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test.utils import CaptureQueriesContext
from django.db import connection
from mi_app.models import Cliente, Prestamo

print("\n🔍 N+1 Query Detection\n")
print("=" * 70)

# Test 1: List all clients
print("\n[TEST 1] Cliente.objects.all()[:20]")
with CaptureQueriesContext(connection) as ctx:
    clientes = list(Cliente.objects.all()[:20])
print(f"  Queries: {len(ctx)}")
print(f"  Status: {'✅ GOOD' if len(ctx) <= 1 else '❌ POTENTIAL N+1'}")

# Test 2: List loans with client info (WITHOUT optimization)
print("\n[TEST 2] Prestamo.objects.all()[:20] (No optimization)")
with CaptureQueriesContext(connection) as ctx:
    prestamos = list(Prestamo.objects.all()[:20])
    # Access cliente (this would cause N+1)
    # [p.cliente.nombre for p in prestamos]
print(f"  Queries: {len(ctx)}")
print(f"  Status: {'✅ GOOD' if len(ctx) <= 1 else '❌ POTENTIAL N+1'}")

# Test 3: Same with select_related (OPTIMIZED)
print("\n[TEST 3] Prestamo.objects.select_related('cliente')[:20] (Optimized)")
with CaptureQueriesContext(connection) as ctx:
    prestamos = list(Prestamo.objects.select_related('cliente')[:20])
    nombres = [p.cliente.nombre for p in prestamos]
print(f"  Queries: {len(ctx)}")
print(f"  Status: {'✅ GOOD' if len(ctx) <= 3 else '❌ POTENTIAL N+1'}")

print("\n" + "=" * 70 + "\n")
EOF
python check_n_plus_one.py
```

---

## 4. Database Inspection

### Ver índices de BD

```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()

# SQLite - Ver índices
cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
indices = cursor.fetchall()

print("\n📊 Database Indexes:")
for idx in indices:
    print(f"  - {idx[0]}")

# Ver tabla schema
cursor.execute("PRAGMA table_info(mi_app_prestamo)")
columns = cursor.fetchall()
print("\nmi_app_prestamo columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")
```

### Vaciar BD (PELIGROSO - solo desarrollo)

```bash
# Full reset
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Or just clear app data
python manage.py migrate mi_app zero
python manage.py migrate mi_app
```

---

## 5. Logging Configuration

### Activar logging detallado

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'mi_app': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    },
}
```

### Ver logs

```bash
tail -f debug.log
```

---

## 6. Performance Monitoring

### Medir tiempo de respuesta

```bash
cat > measure_response_time.py << 'EOF'
import os
import django
import time
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.test import Client

client = Client()

print("\n⏱️  Response Time Measurements\n")
print("=" * 70)

endpoints = [
    ('GET', '/clientes/', 'List Clientes'),
    ('GET', '/prestamos/', 'List Prestamos'),
    ('GET', '/estadisticas/', 'Estadisticas'),
]

for method, url, description in endpoints:
    times = []
    for i in range(5):
        start = time.time()
        if method == 'GET':
            response = client.get(url)
        elapsed = time.time() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    avg = sum(times) / len(times)
    print(f"\n{description} ({url})")
    print(f"  Min: {min(times):.2f}ms")
    print(f"  Max: {max(times):.2f}ms")
    print(f"  Avg: {avg:.2f}ms")
    print(f"  Status: {'✅ GOOD' if avg < 200 else '⚠️  SLOW'}")

print("\n" + "=" * 70 + "\n")
EOF
python measure_response_time.py
```

---

## 7. Live Environment Monitoring

### Verificar salud del sistema

```bash
cat > health_check.py << 'EOF'
#!/usr/bin/env python
import os
import django
import subprocess
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from io import StringIO

print("\n🏥 System Health Check")
print("=" * 70)
print(f"Timestamp: {datetime.now().isoformat()}")

# Django check
print("\n[1] Django System Check:")
out = StringIO()
try:
    call_command('check', stdout=out)
    print("  ✅ No system issues found")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Database connection
print("\n[2] Database Connection:")
try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("  ✅ Database connected")
except Exception as e:
    print(f"  ❌ Database error: {e}")

# Migrations status
print("\n[3] Migrations Status:")
from django.db.migrations.executor import MigrationExecutor
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
if plan:
    print(f"  ⚠️  {len(plan)} pending migrations")
else:
    print("  ✅ All migrations applied")

# Data statistics
print("\n[4] Data Statistics:")
from mi_app.models import Cliente, Prestamo, Cuota, Pago
print(f"  Clientes: {Cliente.objects.count()}")
print(f"  Prestamos: {Prestamo.objects.count()}")
print(f"  Cuotas: {Cuota.objects.count()}")
print(f"  Pagos: {Pago.objects.count()}")

print("\n" + "=" * 70 + "\n")
EOF
python health_check.py
```

---

## 8. Error Tracking

### Ver errores recientes

```bash
# Si estás usando Sentry (recomendado)
pip install sentry-sdk

# Configurar en settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-key@sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)
```

### Ver logs de Django

```bash
# Con DEBUG=True, los errores aparecen en terminal
# Con DEBUG=False, revisar:
cat logs/django.log

# O configurar logging (ver sección 5)
```

---

## 9. Memory Profiling

### Detectar memory leaks

```bash
pip install memory-profiler

cat > profile_memory.py << 'EOF'
from memory_profiler import profile

@profile
def loadcache():
    from mi_app.models import Cliente, Prestamo
    clientes = list(Cliente.objects.all())
    prestamos = list(Prestamo.objects.select_related('cliente'))
    return clientes, prestamos

if __name__ == '__main__':
    loadcache()
EOF

python -m memory_profiler profile_memory.py
```

---

## 10. Database Query Analysis

### Ver todas las queries en una view

```python
# En views.py, usar decorator
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.conf import settings

def mi_view(request):
    if settings.DEBUG:
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as ctx:
            # Your view logic
            result = my_expensive_operation()
            
        print(f"Queries executed: {len(ctx)}")
        for i, query in enumerate(ctx, 1):
            print(f"{i}. {query['sql'][:100]}...")
```

---

## 11. Continuous Integration Checks

### Antes de commit

```bash
#!/bin/bash
# pre-commit hook

echo "🔍 Running pre-commit checks..."

# Check syntax
python -m py_compile mi_app/*.py && echo "✅ Syntax check passed"

# Run tests
python manage.py test mi_app --no-input --fail-fast && echo "✅ Tests passed"

# Check coverage
coverage run --source='.' manage.py test mi_app
coverage report --fail-under=80 && echo "✅ Coverage check passed"

echo "✅ All pre-commit checks passed!"
```

---

## 12. Production Monitoring Checklist

- [ ] Configure error tracking (Sentry)
- [ ] Set up logging aggregation (ELK, Splunk)
- [ ] Configure performance monitoring (New Relic, Datadog)
- [ ] Set up alerts for:
  - [ ] High error rates (> 1%)
  - [ ] Slow responses (> 1000ms)
  - [ ] Database issues
  - [ ] Memory usage (> 90%)
  - [ ] CPU usage (> 80%)
- [ ] Configure automated backups
- [ ] Set up uptime monitoring

---

## 13. Quick Debugging Commands

```bash
# Ver version de Django
python manage.py --version

# Ver installed apps
python manage.py shell
>>> from django.conf import settings
>>> settings.INSTALLED_APPS

# Validate models
python manage.py makemigrations --dry-run --check

# See all migrations
python manage.py showmigrations

# Specific database query logging
# settings.py: LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

# See actual SQL
python manage.py shell
>>> from mi_app.models import Cliente
>>> from django.db.models import Q
>>> str(Cliente.objects.filter(Q(nombre='John')).query)

# Benchmark a queryset
>>> import time
>>> start = time.time(); list(Cliente.objects.all()); print(time.time() - start)
```

---

## 14. Common Issues & Solutions

### Issue: Slow database queries
**Solution:**
1. Check indexes: `check_n_plus_one.py` script
2. Add select_related/prefetch_related
3. Use database profiling
4. Analyze query plans: `EXPLAIN` in SQL

### Issue: Memory leaks in long-running processes
**Solution:**
1. Use memory_profiler
2. Check for circular references
3. Use Django's connection.close_old_connections()
4. Monitor process memory usage

### Issue: High error rate
**Solution:**
1. Check error logs
2. Monitor Database errors
3. Check external service connectivity
4. Review recent changes

### Issue: Slow migrations
**Solution:**
1. Split large migrations
2. Use `--fake-initial` if needed
3. Backup before applying
4. Test in staging first

---

## 15. Useful Django Commands

```bash
# Environment info
python manage.py shell

# Optimize DB
python manage.py optimize_admin_autodiscover

# Populate cache
python manage.py sync_perms_and_cache

# Create test database snapshot
python manage.py dumpdata --indent 2 > test_data.json

# Print SQL for a migration
python manage.py sqlmigrate mi_app 0001

# Run management command
python manage.py custom_command

# Generate test coverage HTML
coverage html
# Open htmlcov/index.html

# Format code
black mi_app/
isort mi_app/

# Lint code
flake8 mi_app/
```

---

**Last Updated:** 2026-02-21
**Status:** ✅ Complete Monitoring Suite Ready

