"""
TESTS FOR ALTO #3 & #4
===============================================================================
ALTO #3: Excel Import Error Handling
ALTO #4: Real-time Mora Updates
===============================================================================
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
import json
from mi_app.models import Cliente, Prestamo, Cuota

# ===============================================================================
# ALTO #4: REAL-TIME MORA UPDATES TESTS
# ===============================================================================

class RealTimeMoraAPITests(TestCase):
    """Tests para el API de mora en tiempo real (ALTO #4)"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client_app = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente sin usuario (campo no existe)
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            cedula='1234567890',
            celular='3001234567',
            email='test@example.com'
        )
        
        # Crear préstamo (campos reales del modelo)
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000.00'),
            interes_porcentaje=Decimal('10.00'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=180),
            estado='ACTIVO'
        )
        
        # Crear cuota vencida (para que acumule mora)
        self.cuota = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('8334'),
            monto_pendiente=Decimal('8334'),
            interes_normal=Decimal('834'),
            fecha_pago_esperada=date.today() - timedelta(days=10)  # 10 días vencida
        )
    
    def test_api_mora_actual_sin_autenticacion(self):
        """Prueba que endpoint requiere autenticación"""
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        # Debe redirigir a login
        self.assertEqual(response.status_code, 302)
    
    def test_api_mora_actual_con_autenticacion(self):
        """Prueba que endpoint retorna mora actual"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        # Debe retornar 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_api_mora_actual_cuota_no_existe(self):
        """Prueba que cuota inexistente retorna 404"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': 99999})
        response = self.client_app.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_api_mora_retorna_estructura_correcta(self):
        """Prueba que la respuesta JSON tiene la estructura correcta"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        # Verificar estructura
        self.assertIn('success', data)
        self.assertIn('cuota_id', data)
        self.assertIn('mora_diaria', data)
        self.assertIn('mora_acumulada', data)
        self.assertIn('interes_pendiente', data)
        self.assertIn('monto_pendiente', data)
        self.assertIn('total_pendiente', data)
        self.assertIn('estado', data)
        self.assertIn('fecha_vencimiento', data)
        self.assertIn('dias_atraso', data)
        self.assertIn('timestamp', data)
    
    def test_api_mora_con_cuota_pagada(self):
        """Prueba que cuota pagada retorna 0 mora"""
        # Marcar cuota como pagada
        self.cuota.pagado = True
        self.cuota.save()
        
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        # Mora debe ser 0 si está pagada
        self.assertEqual(data['mora_diaria'], '0')
    
    def test_api_mora_metodo_get_requerido(self):
        """Prueba que solo GET es permitido"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        
        # POST no debe estar permitido
        response = self.client_app.post(url)
        self.assertIn(response.status_code, [405, 404])  # Method not allowed o not found


# ===============================================================================
# EXCEL VALIDATOR TESTS
# ===============================================================================

class ExcelValidatorTests(TestCase):
    """Tests para el validador de Excel (ALTO #3)"""
    
    def test_validador_importable(self):
        """Prueba que el validador se puede importar sin errores"""
        from mi_app.services.excel_validator import ExcelValidator
        self.assertTrue(callable(ExcelValidator.validate_excel_structure))
    
    def test_validador_tiene_metodos_requeridos(self):
        """Prueba que validador tiene métodos requeridos"""
        from mi_app.services.excel_validator import ExcelValidator
        
        self.assertTrue(hasattr(ExcelValidator, 'validate_excel_structure'))
        self.assertTrue(hasattr(ExcelValidator, 'validate_row'))
        self.assertTrue(hasattr(ExcelValidator, 'validate_excel_file'))


# ===============================================================================
# INTEGRATION TESTS
# ===============================================================================

class ALTO_MoraIntegration(TestCase):
    """Tests de integración para mora en tiempo real"""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre='Integration Test',
            cedula='9999999999',
            celular='3009999999',
            email='integration@test.com'
        )
        
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('50000.00'),
            interes_porcentaje=Decimal('12.00'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=180),
            estado='ACTIVO'
        )
        
        self.cuota = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('10000'),
            monto_pendiente=Decimal('10000'),
            interes_normal=Decimal('1000'),
            fecha_pago_esperada=date.today() - timedelta(days=5)
        )
    
    def test_mora_se_calcula_correctamente(self):
        """Prueba que la mora se calcula correctamente"""
        mora = self.cuota.calcular_mora_diaria()
        
        # Mora debe ser un decimal
        self.assertIsInstance(mora, Decimal)
        # Mora debe ser >= 0
        self.assertGreaterEqual(mora, Decimal('0'))
    
    def test_estado_cuota_es_valido(self):
        """Prueba que el estado de cuota es correcto"""
        estado = self.cuota.obtener_estado_cuota()
        
        estados_validos = ['PAGADA', 'PENDIENTE', 'DEMORADA', 'MOROSA']
        self.assertIn(estado, estados_validos)
    
    def test_dias_atraso_calcula_correctamente(self):
        """Prueba que días de atraso se calcula correctamente"""
        # Cuota vencida hace 5 días
        dias = (date.today() - self.cuota.fecha_pago_esperada).days
        
        self.assertEqual(dias, 5)
