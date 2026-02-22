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
import pandas as pd
import io
import os
from mi_app.models import Cliente, Prestamo, Cuota, Configuracion
from mi_app.services.excel_validator import ExcelValidator, ExcelValidationError, ExcelValidationResult


# ===============================================================================
# ALTO #3: EXCEL IMPORT ERROR HANDLING TESTS
# ===============================================================================

class ExcelValidatorTests(TestCase):
    """Tests para el validador de Excel (ALTO #3)"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.validator = ExcelValidator()
        # Crear un cliente existente para pruebas de duplicados
        self.duplicate_client = Cliente.objects.create(
            nombre='Cliente Existente',
            cedula='1234567890',
            celular='3001234567',
            email='existente@example.com'
        )
    
    def test_validar_estructura_excel_valida(self):
        """Prueba que estructura válida de Excel es detectada"""
        # Crear DataFrame con columnas válidas
        data = {
            'Cédula': ['1111111111'],
            'Nombre': ['Test Cliente'],
            'Teléfono': ['3001234567'],
            'Email': ['test@example.com'],
            'Monto': [50000],
            'Interés': [10],
            'Cuotas': [12]
        }
        df = pd.DataFrame(data)
        
        is_valid, message, found_cols = self.validator.validate_excel_structure(df)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, 'Estructura válida')
        self.assertIn('cedula', found_cols)
        self.assertIn('nombre', found_cols)
    
    def test_validar_estructura_excel_faltante_columnas(self):
        """Prueba que faltan columnas requeridas"""
        # DataFrame sin columna de email
        data = {
            'Cédula': ['1111111111'],
            'Nombre': ['Test Cliente'],
            'Teléfono': ['3001234567'],
            'Monto': [50000],
        }
        df = pd.DataFrame(data)
        
        is_valid, message, missing = self.validator.validate_excel_structure(df)
        
        self.assertFalse(is_valid)
        self.assertIn('email', missing)
    
    def test_validar_estructura_excel_vacio(self):
        """Prueba que Excel vacío es rechazado"""
        df = pd.DataFrame()
        
        is_valid, message, _ = self.validator.validate_excel_structure(df)
        
        self.assertFalse(is_valid)
        self.assertIn('vacío', message.lower())
    
    def test_validar_fila_cedula_invalida(self):
        """Prueba validación de cédula inválida"""
        found_cols = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'email': 'Email',
            'monto': 'Monto',
            'interes': 'Interés',
            'cuotas': 'Cuotas'
        }
        
        row_data = {
            'Cédula': 'ABC',  # Inválido
            'Nombre': 'Test',
            'Teléfono': '3001234567',
            'Email': 'test@example.com',
            'Monto': 50000,
            'Interés': 10,
            'Cuotas': 12
        }
        
        is_valid, cleaned, errors = self.validator.validate_row(1, row_data, found_cols)
        
        self.assertFalse(is_valid)
        self.assertTrue(any(e.error_type == 'CEDULA_INVALIDA' for e in errors))
    
    def test_validar_fila_cedula_duplicada(self):
        """Prueba validación de cédula duplicada"""
        found_cols = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'email': 'Email',
            'monto': 'Monto',
            'interes': 'Interés',
            'cuotas': 'Cuotas'
        }
        
        row_data = {
            'Cédula': self.duplicate_client.cedula,  # Duplicada
            'Nombre': 'Otro Nombre',
            'Teléfono': '3001234567',
            'Email': 'otro@example.com',
            'Monto': 50000,
            'Interés': 10,
            'Cuotas': 12
        }
        
        is_valid, cleaned, errors = self.validator.validate_row(1, row_data, found_cols)
        
        # Debe seguir siendo válida pero con warning
        critical_errors = [e for e in errors if e.severity == 'error']
        self.assertTrue(len(critical_errors) == 0)
        self.assertTrue(any(e.error_type == 'CEDULA_DUPLICADA' for e in errors))
    
    def test_validar_fila_monto_invalido(self):
        """Prueba validación de monto negativo"""
        found_cols = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'email': 'Email',
            'monto': 'Monto',
            'interes': 'Interés',
            'cuotas': 'Cuotas'
        }
        
        row_data = {
            'Cédula': '9999999999',
            'Nombre': 'Test',
            'Teléfono': '3001234567',
            'Email': 'test99@example.com',
            'Monto': -50000,  # Negativo
            'Interés': 10,
            'Cuotas': 12
        }
        
        is_valid, cleaned, errors = self.validator.validate_row(1, row_data, found_cols)
        
        self.assertFalse(is_valid)
        self.assertTrue(any(e.error_type == 'MONTO_INVALIDO' for e in errors))
    
    def test_validar_fila_interes_fuera_rango(self):
        """Prueba validación de interés fuera de rango"""
        found_cols = {
            'cedula': 'Cédula',
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'email': 'Email',
            'monto': 'Monto',
            'interes': 'Interés',
            'cuotas': 'Cuotas'
        }
        
        row_data = {
            'Cédula': '9999999999',
            'Nombre': 'Test',
            'Teléfono': '3001234567',
            'Email': 'test99@example.com',
            'Monto': 50000,
            'Interés': 150,  # >100%
            'Cuotas': 12
        }
        
        is_valid, cleaned, errors = self.validator.validate_row(1, row_data, found_cols)
        
        self.assertFalse(is_valid)
        self.assertTrue(any(e.error_type == 'INTERES_INVALIDO' for e in errors))


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
        
        # Crear cliente
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
        
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_api_mora_actual_con_autenticacion(self):
        """Prueba que endpoint retorna mora actual"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cuota_id'], self.cuota.id)
        self.assertIn('mora_diaria', data)
        self.assertIn('timestamp', data)
    
    def test_api_mora_actual_datos_correctos(self):
        """Prueba que los datos retornados son correctos"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        # Verificar estructura
        self.assertIn('mora_acumulada', data)
        self.assertIn('interes_pendiente', data)
        self.assertIn('monto_pendiente', data)
        self.assertIn('total_pendiente', data)
        self.assertIn('estado', data)
        self.assertIn('dias_atraso', data)
    
    def test_api_mora_actual_otro_usuario_autenticado(self):
        """Prueba que otro usuario autenticado puede acceder (API no restringe por cliente)"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client_app.login(username='otheruser', password='testpass123')

        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)

        # La API actual permite cualquier usuario autenticado
        self.assertEqual(response.status_code, 200)
    
    def test_api_mora_actual_cuota_no_existe(self):
        """Prueba que cuota inexistente retorna 404"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': 99999})
        response = self.client_app.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_api_mora_calcula_dias_atraso(self):
        """Prueba que los días de atraso se calculan correctamente"""
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        # Cuota fue vencida hace 10 días
        self.assertEqual(data['dias_atraso'], 10)
    
    def test_api_mora_con_cuota_pagada(self):
        """Prueba que cuota pagada retorna 0 mora"""
        # Marcar cuota como pagada
        self.cuota.pagado = True
        self.cuota.save()
        
        self.client_app.login(username='testuser', password='testpass123')
        url = reverse('api_cuota_mora_actual', kwargs={'cuota_id': self.cuota.id})
        response = self.client_app.get(url)
        
        data = response.json()
        
        self.assertEqual(data['mora_diaria'], '0')


# ===============================================================================
# INTEGRATION TESTS
# ===============================================================================

class ALTO_IntegrationTests(TestCase):
    """Tests de integración para ALTO #3 y #4"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nombre='Test',
            cedula='1234567890',
            celular='3001234567',
            email='test@example.com'
        )
    
    def test_excel_validator_con_archivo_real(self):
        """Prueba validador con archivo Excel real"""
        # Crear un DataFrame de prueba
        data = {
            'Cédula': ['1111111111', '2222222222'],
            'Nombre': ['Cliente 1', 'Cliente 2'],
            'Teléfono': ['3001234567', '3007654321'],
            'Email': ['client1@test.com', 'client2@test.com'],
            'Monto': [50000, 75000],
            'Interés': [10, 12],
            'Cuotas': [12, 18]
        }
        df = pd.DataFrame(data)
        
        # Convertir a archivo bytes
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        result = ExcelValidator.validate_excel_file(excel_file)
        
        self.assertEqual(result.total_valid, 2)
        self.assertEqual(result.total_errors, 0)
    
    def test_excel_validator_con_errores_mixtos(self):
        """Prueba validador con mezcla de filas válidas e inválidas"""
        data = {
            'Cédula': ['1111111111', 'ABC', self.cliente.cedula],
            'Nombre': ['Cliente 1', 'Cliente 2', 'Cliente 3'],
            'Teléfono': ['3001234567', '3007654321', '3009876543'],
            'Email': ['client1@test.com', 'invalid-email', 'client3@test.com'],
            'Monto': [50000, 'no-es-numero', 75000],
            'Interés': [10, 12, 15],
            'Cuotas': [12, 18, 24]
        }
        df = pd.DataFrame(data)
        
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        result = ExcelValidator.validate_excel_file(excel_file)
        
        # Fila 0: válida. Fila 1: errores (cédula ABC, monto no numérico). Fila 2: válida (cédula duplicada es warning)
        self.assertEqual(result.total_valid, 2)
        self.assertGreater(result.total_errors, 0)
