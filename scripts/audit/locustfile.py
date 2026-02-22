"""
Locust Load Testing Configuration for Gestion Prestamos

This can be run locally to simulate concurrent users and measure performance.

Installation:
    pip install locust

Usage:
    locust -f tests/locustfile.py --host=http://localhost:8000

Then open http://localhost:8089 in browser and start test
"""

from locust import HttpUser, task, between, TaskSet
from datetime import date, timedelta
import random


class PrestamosTasks(TaskSet):
    """Conjunto de tareas para simular usuario en sistema de prestamos"""
    
    def setup(self):
        """Login before tasks"""
        self.login()
    
    def login(self):
        """Login con usuario de prueba"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, catch_response=True)
        
        if response.status_code == 200 or 'login' not in response.url.lower():
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(10)
    def list_clientes(self):
        """Ver lista de clientes (tarea más frecuente)"""
        self.client.get('/clientes/', name='/clientes/')
    
    @task(5)
    def search_cliente(self):
        """Buscar cliente por cedula"""
        cedula = random.randint(10000000, 99999999)
        self.client.get(f'/clientes/?buscar={cedula}', name='/clientes/?buscar=*')
    
    @task(3)
    def view_cliente_detail(self):
        """Ver detalle de cliente específico"""
        cliente_id = random.randint(1, 50)
        self.client.get(f'/clientes/{cliente_id}/', name='/clientes/[id]/')
    
    @task(6)
    def list_prestamos(self):
        """Ver lista de todos los préstamos"""
        self.client.get('/prestamos/', name='/prestamos/')
    
    @task(3)
    def view_prestamo_detail(self):
        """Ver detalle de préstamo específico"""
        prestamo_id = random.randint(1, 100)
        self.client.get(f'/prestamos/{prestamo_id}/', name='/prestamos/[id]/')
    
    @task(2)
    def list_cuotas(self):
        """Ver lista de cuotas"""
        self.client.get('/cuotas/', name='/cuotas/')
    
    @task(4)
    def view_estadisticas(self):
        """Ver página de estadísticas"""
        self.client.get('/estadisticas/', name='/estadisticas/')
    
    @task(2)
    def filter_prestamos_by_estado(self):
        """Filtrar préstamos por estado"""
        estado = random.choice(['vigente', 'pagado', 'todos'])
        self.client.get(f'/prestamos/?estado={estado}', name='/prestamos/?estado=*')
    
    @task(1)
    def export_clientes(self):
        """Exportar lista de clientes (tarea pesada)"""
        self.client.get('/clientes/export/', name='/clientes/export/')


class RegularUser(HttpUser):
    """Simula usuario regular del sistema"""
    
    tasks = [PrestamosTasks]
    wait_time = between(1, 3)  # Esperar 1-3 segundos entre tareas


class PowerUser(HttpUser):
    """Simula usuario que hace muchas acciones (gestor)"""
    
    tasks = [PrestamosTasks]
    wait_time = between(0.5, 1)  # Esperar 0.5-1 segundo entre tareas
    weight = 3  # 25% de los usuarios serán power users


class AdminUser(HttpUser):
    """Simula usuario administrador"""
    
    tasks = [PrestamosTasks]
    wait_time = between(0.1, 0.5)  # Esperar 0.1-0.5 segundo entre tareas
    weight = 1  # 10% de los usuarios serán admin


"""
CONFIGURACIÓN RECOMENDADA PARA LOCUST:

1. PEQUEÑA CARGA (Local Development):
   - Number of users: 10
   - Spawn rate: 2 users/sec
   - Duration: 5-10 minutes
   
2. CARGA MEDIA (Testing):
   - Number of users: 50
   - Spawn rate: 5 users/sec
   - Duration: 15 minutes
   
3. CARGA ALTA (Stress Test):
   - Number of users: 100-200
   - Spawn rate: 10 users/sec
   - Duration: 30 minutes

4. SOSTENIBILIDAD (Spike Test):
   - Start with 50 users
   - Spike to 500 users instantaneously
   - Duration: 5 minutes
   
MONITOREO DURANTE LAS PRUEBAS:
- Response Time Median (Target: < 200ms)
- Response Time 95th Percentile (Target: < 500ms)
- Failures (Target: < 1%)
- Requests per Second (RPS)
- Connection utilization

DATOS ESPERADOS EN RESULTADOS:
- Type: GET/POST/etc
- Name: Ruta accedida
- # requests: Número de peticiones
- # fails: Número de fallos
- Median: Tiempo medio de respuesta
- 95%ile: 95% de las peticiones responden en este tiempo
- Max: Respuesta más lenta
- Avg (Average): Tiempo promedio
- Min: Respuesta más rápida
"""

# Performance Assertions
# Configurar para que falle automáticamente si no se cumple:
# response.ok or response.failure(f"Got response code {response.status_code}")
