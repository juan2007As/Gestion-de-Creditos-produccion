"""
TESTS FOR ALTO #3 & #4 - FINAL VERSION
===============================================================================
ALTO #3: Excel Import Error Handling
ALTO #4: Real-time Mora Updates  
===============================================================================
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.test.client import RequestFactory
from decimal import Decimal
from datetime import date, timedelta
from mi_app.models import Cliente, Prestamo, Cuota


# ===============================================================================
# ALTO #4: REAL-TIME MORA UPDATES - API TESTS
# ===============================================================================

class MoraRealTimeAPITests(TestCase):
    """Tests para API de mora en tiempo real (ALTO #4)"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client_app = Client()
        self.factory = RequestFactory()
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            cedula='1234567890',
            celular='3001234567',
            email='test@example.com'
        )
        
        # Crear préstamo basado en estructura real del model
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000.00'),
            interes_porcentaje=Decimal('10.00'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=180),
            estado='ACTIVO'
        )
        
        # Crear cuota vencida
        self.cuota = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('8334.00'),
            monto_pendiente=Decimal('8334.00'),
            interes_normal=Decimal('834.00'),
            fecha_pago_esperada=date.today() - timedelta(days=10),
            pagado=False
        )
    
    def test_endpoint_url_existe(self):
        """Prueba que la URL del endpoint existe"""
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        self.assertIsNotNone(url)
        self.assertIn('api/cuota', url)
        self.assertIn('mora-actual', url)
    
    def test_endpoint_requiere_login(self):
        """Prueba que endpoint requiere usuarios autenticados"""
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        # Sin autenticación, debe redirigir a login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_endpoint_retorna_json(self):
        """Prueba que endpoint retorna JSON válido"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIsInstance(data, dict)
    
    def test_endpoint_estructura_respuesta(self):
        """Prueba que respuesta contiene campos requeridos"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        # Campo de éxito
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        
        # Campos de mora
        self.assertIn('mora_diaria', data)
        self.assertIn('mora_acumulada', data)
        self.assertIn('interes_pendiente', data)
        self.assertIn('monto_pendiente', data)
        self.assertIn('total_pendiente', data)
        
        # Campos de estado
        self.assertIn('estado', data)
        self.assertIn('fecha_vencimiento', data)
        self.assertIn('dias_atraso', data)
        self.assertIn('timestamp', data)
    
    def test_endpoint_cuota_no_existe(self):
        """Prueba que cuota inexistente retorna 404"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': 99999})
        response = self.client_app.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_endpoint_solo_get_permitido(self):
        """Prueba que solo GET es permitido"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        
        # POST no debe estar permitido
        response = self.client_app.post(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [405, 404])


# ===============================================================================
# ALTO #3: EXCEL VALIDATOR TESTS  
# ===============================================================================

class ExcelValidatorServiceTests(TestCase):
    """Tests para servicio validador de Excel (ALTO #3)"""
    
    def test_validator_module_importable(self):
        """Prueba que el módulo validador existe y es importable"""
        try:
            from mi_app.services.excel_validator import (
                ExcelValidator,
                ExcelValidationError,
                ExcelValidationResult
            )
            self.assertTrue(callable(ExcelValidator))
        except ImportError as e:
            self.fail(f"No se puede importar Excel validator: {e}")
    
    def test_validator_tiene_metodos_principales(self):
        """Prueba que validador tiene todos los métodos necesarios"""
        from mi_app.services.excel_validator import ExcelValidator
        
        methods = [
            'validate_excel_structure',
            'validate_row',
            'validate_excel_file'
        ]
        
        for method in methods:
            self.assertTrue(
                hasattr(ExcelValidator, method),
                f"Método {method} no existe en ExcelValidator"
            )
    
    def test_error_class_tiene_estructura(self):
        """Prueba que ExcelValidationError tiene estructura correcta"""
        from mi_app.services.excel_validator import ExcelValidationError
        
        error = ExcelValidationError(1, 'TEST_ERROR', 'Test detail')
        
        self.assertEqual(error.row_number, 1)
        self.assertEqual(error.error_type, 'TEST_ERROR')
        self.assertEqual(error.detail, 'Test detail')
        self.assertTrue(hasattr(error, 'to_dict'))
    
    def test_result_class_acumula_errores(self):
        """Prueba que ExcelValidationResult acumula errores"""
        from mi_app.services.excel_validator import (
            ExcelValidationError,
            ExcelValidationResult
        )
        
        result = ExcelValidationResult()
        
        error1 = ExcelValidationError(1, 'ERROR1', 'Detail 1')
        error2 = ExcelValidationError(2, 'ERROR2', 'Detail 2')
        
        result.add_error(error1)
        result.add_error(error2)
        
        self.assertEqual(result.total_errors, 2)
        self.assertEqual(len(result.errors), 2)


# ===============================================================================
# INTEGRATION TESTS
# ===============================================================================

class ALTO_3_4_IntegrationTests(TestCase):
    """Tests de integración para ALTO #3 y #4"""
    
    def test_servicios_disponibles(self):
        """Prueba que todos los servicios están disponibles"""
        # ALTO #3 services
        from mi_app.services.excel_validator import ExcelValidator
        
        # ALTO #4 endpoints
        from mi_app.views import api_cuota_mora_actual
        
        self.assertTrue(callable(ExcelValidator.validate_excel_structure))
        self.assertTrue(callable(api_cuota_mora_actual))
    
    def test_javascript_mora_archivo_existe(self):
        """Prueba que archivo JavaScript para mora existe"""
        import os
        from pathlib import Path
        
        base_path = Path('mi_app/static/mi_app/js')
        mora_js = base_path / 'mora-realtime.js'
        
        self.assertTrue(mora_js.exists(), f"Archivo {mora_js} no existe")
    
    def test_css_mora_actualizado(self):
        """Prueba que estilos CSS para mora están incluidos"""
        from pathlib import Path
        
        css_file = Path('mi_app/static/mi_app/css/componentes.css')
        self.assertTrue(css_file.exists(), "Archivo componentes.css no existe")
        
        with open(css_file, 'r') as f:
            content = f.read()
            self.assertIn('mora-realtime', content)
            self.assertIn('mora-updated', content)
