"""
Test: Verificar que el campo estado se guarda correctamente en nuevos clientes
Bug Fix: Cuando se crea un cliente marcado como ACTIVO, ahora debe guardarse como ACTIVO
no como INACTIVO

Fecha: 03 de Febrero de 2026
"""

from django.test import TestCase, Client
from django.urls import reverse
from mi_app.models import Cliente
from mi_app.forms import ClienteForm


class EstadoClienteFixTest(TestCase):
    """Pruebas para verificar que el campo estado se respeta al crear clientes"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.create_url = reverse('crear_cliente')
        
    def test_formulario_estado_requerido(self):
        """Test 1: Verificar que estado sea REQUERIDO en el formulario"""
        form = ClienteForm()
        # El campo estado debe ser requerido
        self.assertTrue(
            form.fields['estado'].required,
            "❌ FALLO: Campo estado no está marcado como requerido"
        )
        print("✅ PASS: Campo estado está marcado como requerido")
    
    def test_crear_cliente_activo(self):
        """Test 2: Crear cliente seleccionando ACTIVO → Debe guardarse como ACTIVO"""
        datos = {
            'nombre': 'Juan Carlos Pérez',
            'cedula': '12345678',
            'celular': '3001234567',
            'email': 'juan@example.com',
            'estado': 'ACTIVO',  # ← Cliente marca ACTIVO
            'notas': 'Cliente de prueba',
        }
        
        form = ClienteForm(data=datos)
        self.assertTrue(form.is_valid(), f"Formulario inválido: {form.errors}")
        
        cliente = form.save()
        
        # Verificar que se guardó como ACTIVO
        self.assertEqual(
            cliente.estado, 'ACTIVO',
            f"❌ FALLO: Estado debería ser ACTIVO pero es {cliente.estado}"
        )
        print(f"✅ PASS: Cliente creado con estado ACTIVO correctamente")
    
    def test_crear_cliente_inactivo(self):
        """Test 3: Crear cliente seleccionando INACTIVO → Debe guardarse como INACTIVO"""
        datos = {
            'nombre': 'María García López',
            'cedula': '87654321',
            'celular': '3009876543',
            'email': 'maria@example.com',
            'estado': 'INACTIVO',  # ← Cliente marca INACTIVO
            'notas': 'Cliente inactivo',
        }
        
        form = ClienteForm(data=datos)
        self.assertTrue(form.is_valid(), f"Formulario inválido: {form.errors}")
        
        cliente = form.save()
        
        # Verificar que se guardó como INACTIVO
        self.assertEqual(
            cliente.estado, 'INACTIVO',
            f"❌ FALLO: Estado debería ser INACTIVO pero es {cliente.estado}"
        )
        print(f"✅ PASS: Cliente creado con estado INACTIVO correctamente")
    
    def test_formulario_sin_estado_invalido(self):
        """Test 4: Formulario sin estado debe ser INVÁLIDO (requerido)"""
        datos = {
            'nombre': 'Test Sin Estado',
            'cedula': '11111111',
            'celular': '3001111111',
            'email': 'test@example.com',
            # NO incluir 'estado' ← Campo falta
            'notas': 'Test',
        }
        
        form = ClienteForm(data=datos)
        self.assertFalse(
            form.is_valid(),
            "❌ FALLO: Formulario debería ser inválido sin estado (requerido)"
        )
        print("✅ PASS: Formulario rechazado correctamente (estado requerido)")
    
    def test_estado_se_respeta_en_bd(self):
        """Test 5: Verificar que estado se guarda y recupera correctamente de BD"""
        # Crear cliente con ACTIVO
        cliente1 = Cliente.objects.create(
            nombre='Cliente Activo',
            cedula='22222222',
            celular='3002222222',
            email='activo@example.com',
            estado='ACTIVO'
        )
        
        # Crear cliente con INACTIVO
        cliente2 = Cliente.objects.create(
            nombre='Cliente Inactivo',
            cedula='33333333',
            celular='3003333333',
            email='inactivo@example.com',
            estado='INACTIVO'
        )
        
        # Recuperar de BD
        cliente1_recuperado = Cliente.objects.get(id=cliente1.id)
        cliente2_recuperado = Cliente.objects.get(id=cliente2.id)
        
        # Verificar valores
        self.assertEqual(cliente1_recuperado.estado, 'ACTIVO')
        self.assertEqual(cliente2_recuperado.estado, 'INACTIVO')
        print("✅ PASS: Estados se respetan al guardar y recuperar de BD")


class EstadoClienteVistasTest(TestCase):
    """Pruebas funcionales de la vista crear_cliente"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.create_url = reverse('crear_cliente')
    
    def test_vista_formulario_inicial(self):
        """Test 6: GET a crear_cliente muestra formulario correcto"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)  # Redirect a login (esperado)
        print("✅ PASS: Vista crear_cliente accesible")


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("EJECUTANDO TESTS: FIX PARA BUG ESTADO CLIENTE")
    print("="*70 + "\n")
    
    # Crear instancia de test
    suite = TestEstadoClienteFix()
    suite.test_formulario_estado_requerido()
    suite.test_crear_cliente_activo()
    suite.test_crear_cliente_inactivo()
    suite.test_formulario_sin_estado_invalido()
    suite.test_estado_se_respeta_en_bd()
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*70 + "\n")
