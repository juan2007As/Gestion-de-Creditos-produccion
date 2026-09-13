from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from mi_app.models import Cliente
import json

class ClientSearchAPITests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear clientes de prueba
        self.cliente1 = Cliente.objects.create(
            nombre='Juan Pérez',
            cedula='1234567890',
            celular='555-1111'
        )
        self.cliente2 = Cliente.objects.create(
            nombre='María García',
            cedula='0987654321',
            celular='555-2222'
        )
        self.cliente3 = Cliente.objects.create(
            nombre='Carlos López',
            cedula='5555555555',
            celular='555-3333'
        )
        
        # Hacer login
        self.client.login(username='testuser', password='testpass123')
    
    def test_search_api_requires_login(self):
        """API requiere estar logueado"""
        self.client.logout()
        response = self.client.get('/api/clientes/search/?q=juan')
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_search_with_short_query(self):
        """Búsqueda con query < 2 caracteres retorna error"""
        response = self.client.get('/api/clientes/search/?q=j')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(len(data['results']), 0)
    
    def test_search_by_nombre(self):
        """Búsqueda por nombre funciona"""
        response = self.client.get('/api/clientes/search/?q=juan')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)
        self.assertGreater(len(data['results']), 0)
        self.assertEqual(data['results'][0]['nombre'], 'Juan Pérez')
    
    def test_search_by_cedula(self):
        """Búsqueda por cédula funciona"""
        response = self.client.get('/api/clientes/search/?q=1234567890')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)
        self.assertGreater(len(data['results']), 0)
        self.assertEqual(data['results'][0]['cedula'], '1234567890')
    
    def test_search_case_insensitive(self):
        """Búsqueda es case-insensitive"""
        response = self.client.get('/api/clientes/search/?q=JUAN')
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
    
    def test_search_multiple_results(self):
        """Búsqueda retorna múltiples resultados"""
        response = self.client.get('/api/clientes/search/?q=ar')
        data = json.loads(response.content)
        self.assertGreaterEqual(len(data['results']), 2)
    
    def test_search_no_results(self):
        """Búsqueda sin resultados"""
        response = self.client.get('/api/clientes/search/?q=xyz999notfound')
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 0)
    
    def test_search_limit_parameter(self):
        """Parámetro limit funciona"""
        response = self.client.get('/api/clientes/search/?q=a&limit=1')
        data = json.loads(response.content)
        self.assertLessEqual(len(data['results']), 1)
    
    def test_search_response_format(self):
        """Respuesta tiene formato correcto"""
        response = self.client.get('/api/clientes/search/?q=juan')
        data = json.loads(response.content)
        
        # Verificar campos obligatorios
        self.assertIn('success', data)
        self.assertIn('query', data)
        self.assertIn('results', data)
        self.assertIn('count', data)
    
    def test_search_result_fields(self):
        """Cada resultado tiene campos necesarios"""
        response = self.client.get('/api/clientes/search/?q=juan')
        data = json.loads(response.content)
        
        if data['results']:
            result = data['results'][0]
            self.assertIn('id', result)
            self.assertIn('nombre', result)
            self.assertIn('cedula', result)


class ClientSearchComponentTests(TestCase):
    """Tests para el componente físico de búsqueda"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_search_component_exists(self):
        """El componente de búsqueda existe"""
        # Este es más un test de verificación que el archivo existe
        from django.template.loader import get_template
        template = get_template('search_component.html')
        self.assertIsNotNone(template)
    
    def test_api_endpoint_exists(self):
        """El endpoint /api/clientes/search/ existe"""
        url = reverse('api_clientes_search')
        self.assertIsNotNone(url)
