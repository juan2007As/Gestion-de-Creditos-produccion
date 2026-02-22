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
    
    def test_login_view_exists(self):
        """La vista de login existe"""
        # Verifica que la URL está configurada
        url = reverse('login')
        self.assertIsNotNone(url)
    
    def test_logout_view_exists(self):
        """La vista de logout existe"""
        url = reverse('logout')
        self.assertIsNotNone(url)
    
    def test_register_view_exists(self):
        """La vista de registro existe"""
        url = reverse('register')
        self.assertIsNotNone(url)
    
    def test_user_authentication(self):
        """Un usuario puede autenticarse"""
        # Verifica que el usuario se puede autenticar
        authenticated = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(authenticated)
    
    def test_user_creation(self):
        """Se puede crear un nuevo usuario"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@test.com',
            password='newpass123'
        )
        self.assertEqual(new_user.username, 'newuser')
        self.assertTrue(new_user.check_password('newpass123'))
    
    def test_user_model_integration(self):
        """Django User model está correctamente integrado"""
        users_count = User.objects.count()
        self.assertGreater(users_count, 0)

