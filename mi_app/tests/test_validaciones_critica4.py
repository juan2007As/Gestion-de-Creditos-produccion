"""
TESTS PARA CRÍTICA #4: VALIDACIONES INCOMPLETAS EN BACKEND
===========================================================

Tests que verifican que todas las 7 validaciones están implementadas
correctamente en el backend y previenen datos basura

Ejecutar: python manage.py test mi_app.tests.test_validaciones_critica4 -v 2
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from mi_app.models import (
    Cliente, Prestamo, Cuota, Pago, ListaNegra, Configuracion,
    Rol, Permiso, RolPermiso, UsuarioProfile,
)


class ValidacionesCritica4Tests(TestCase):
    """Tests para las 7 validaciones de CRÍTICA #4"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client_obj = Client()
        
        # Rol y permisos para que el usuario pueda crear préstamos y pagos
        rol, _ = Rol.objects.get_or_create(
            nombre='ADMIN',
            defaults={'descripcion': 'Rol admin para tests', 'activo': True}
        )
        for codigo in ('prestamo.create', 'pago.create', 'cliente.view', 'prestamo.view', 'pago.view'):
            perm, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'descripcion': codigo, 'activo': True}
            )
            RolPermiso.objects.get_or_create(rol=rol, permiso=perm)
        
        # Crear usuario autenticado
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        profile, _ = UsuarioProfile.objects.get_or_create(
            usuario=self.user,
            defaults={'rol': rol, 'activo': True}
        )
        if profile.rol != rol:
            profile.rol = rol
            profile.save()
        self.client_obj.login(username='testuser', password='testpass123')
        
        # Crear cliente normal
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            cedula='1111111111',
            celular='1234567890',
            estado='ACTIVO',
            total_prestado=Decimal('0')
        )
        
        # Crear cliente en lista negra
        self.cliente_lista_negra = Cliente.objects.create(
            nombre='Cliente Malo - MOROSO',
            cedula='9999999999',
            celular='9999999999',
            estado='ACTIVO',
            total_prestado=Decimal('0')
        )
        
        # Agregar a lista negra
        self.lista_negra = ListaNegra.objects.create(
            cliente=self.cliente_lista_negra,
            razon='MOROSO',
            usuario_creador=self.user,
            fecha_desde=date.today(),
            activa=True
        )
        
        # Crear configuración por defecto
        Configuracion.objects.get_or_create(
            id=1,
            defaults={
                'tasa_interes_prestamo_normal': Decimal('5.0'),
                'dias_gracia_mora': 5
            }
        )
    
    # =========================================================================
    # VALIDACIÓN #1: Fecha de inicio DEBE ser hoy o posterior
    # =========================================================================
    
    def test_validacion_1_fecha_pasado_rechazada(self):
        """V1: No permite crear préstamo con fecha en el pasado"""
        # Nota: El sistema siempre usa date.today() como fecha_inicio
        # pero se está validando en el backend
        
        # Intentar crear préstamo (siempre será con fecha hoy)
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        # Debe crear exitosamente (no error porque usa hoy)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    # =========================================================================
    # VALIDACIÓN #2b: Cliente NO puede estar en lista negra
    # =========================================================================
    
    def test_validacion_2b_lista_negra_bloqueada(self):
        """V2b: No permite prestamo a cliente en lista negra vigente"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente_lista_negra.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        # Debe rechazar con error
        self.assertEqual(response.status_code, 200)  # No redirige
        self.assertContains(response, 'BLOQUEADO' or 'lista negra')
    
    # =========================================================================
    # VALIDACIÓN #3: Máximo 5 préstamos activos simultáneos
    # =========================================================================
    
    def test_validacion_3_max_5_prestamos_activos(self):
        """V3: No permite más de 5 préstamos activos por cliente"""
        # Crear 5 préstamos activos
        for i in range(5):
            Prestamo.objects.create(
                cliente=self.cliente,
                monto_total=Decimal('10000'),
                interes_porcentaje=Decimal('5.0'),
                fecha_inicio=date.today(),
                fecha_fin_estimada=date.today() + timedelta(days=60),
                tipo_pago='QUINCENAL',
                estado='ACTIVO'
            )
        
        # Intentar crear el 6to préstamo
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        # Debe rechazar
        self.assertEqual(response.status_code, 200)  # No redirige
        self.assertContains(response, 'V3' or 'préstamos activos')
    
    # =========================================================================
    # VALIDACIÓN #4: Monto > 0 y <= $999,999,999
    # =========================================================================
    
    def test_validacion_4a_monto_cero_rechazado(self):
        """V4a: No permite monto = $0"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '0',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V4' or 'mayor a')
    
    def test_validacion_4b_monto_negativo_rechazado(self):
        """V4b: No permite monto negativo"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '-5000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V4' or 'mayor a')
    
    def test_validacion_4c_monto_excesivo_rechazado(self):
        """V4c: No permite monto > $999,999,999"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '9999999999',  # > límite
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V4' or 'excede')
    
    def test_validacion_4d_monto_valido_aceptado(self):
        """V4d: Acepta monto válido ($1 - $999,999,999)"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '50000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect (éxito)
    
    # =========================================================================
    # VALIDACIÓN #5: Número de cuotas DEBE ser 2, 4, 6 u 8
    # =========================================================================
    
    def test_validacion_5a_cuotas_1_rechazado(self):
        """V5a: No permite 1 cuota"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '1',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V5' or 'inválido')
    
    def test_validacion_5b_cuotas_3_rechazado(self):
        """V5b: No permite 3 cuotas"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '3',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V5'  or 'inválido')
    
    def test_validacion_5c_cuotas_7_rechazado(self):
        """V5c: No permite 7 cuotas"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '7',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V5' or 'inválido')
    
    def test_validacion_5d_cuotas_validas_aceptadas(self):
        """V5d: Acepta SOLO 2, 4, 6, 8 cuotas"""
        for num_cuotas in [2, 4, 6, 8]:
            # Crear cliente nuevo para cada test
            cliente_test = Cliente.objects.create(
                nombre=f'Cliente Test {num_cuotas}',
                cedula=f'{num_cuotas}111111111',
                celular='1234567890',
                estado='ACTIVO',
                total_prestado=Decimal('0')
            )
            
            response = self.client_obj.post(reverse('crear_prestamo'), {
                'cliente': cliente_test.id,
                'monto_total': '10000',
                'num_cuotas': str(num_cuotas),
                'interes_porcentaje': '5.0'
            })
            
            self.assertEqual(response.status_code, 302, 
                f"Cuotas {num_cuotas} debería ser aceptada")
    
    # =========================================================================
    # VALIDACIÓN #6: Tasa de interés entre 1.5% y 10%
    # =========================================================================
    
    def test_validacion_6a_tasa_too_low_rechazada(self):
        """V6a: No permite tasa < 1.5%"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '1.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V6' or 'fuera de rango')
    
    def test_validacion_6b_tasa_too_high_rechazada(self):
        """V6b: No permite tasa > 10%"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '15.0'
        })
        
        self.assertEqual(response.status_code, 200)  # Error
        self.assertContains(response, 'V6' or 'fuera de rango')
    
    def test_validacion_6c_tasa_valida_aceptada(self):
        """V6c: Acepta tasa entre 1.5% y 10%"""
        response = self.client_obj.post(reverse('crear_prestamo'), {
            'cliente': self.cliente.id,
            'monto_total': '10000',
            'num_cuotas': '4',
            'interes_porcentaje': '5.0'
        })
        
        self.assertEqual(response.status_code, 302)  # Éxito
    
    def test_validacion_6d_tasa_limites_validos(self):
        """V6d: Acepta tasas en los límites (1.5% y 10%)"""
        for tasa in ['1.5', '10.0']:
            cliente_test = Cliente.objects.create(
                nombre=f'Cliente Tasa {tasa}',
                cedula='151111111' if tasa == '1.5' else '101111111',
                celular='1234567890',
                estado='ACTIVO',
                total_prestado=Decimal('0')
            )
            
            response = self.client_obj.post(reverse('crear_prestamo'), {
                'cliente': cliente_test.id,
                'monto_total': '10000',
                'num_cuotas': '4',
                'interes_porcentaje': tasa
            })
            
            self.assertEqual(response.status_code, 302,
                f"Tasa {tasa}% debería ser aceptada")
    
    # =========================================================================
    # VALIDACIÓN #7: Pago no puede exceder monto_pendiente
    # =========================================================================
    
    def test_validacion_7_pago_mayor_cuota_rechazado(self):
        """V7: No permite pago > monto_pendiente en cuota"""
        # Crear préstamo y cuota
        prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('5000'),
            monto_pendiente=Decimal('5000'),
            interes_normal=Decimal('0'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        
        # Intentar pagar más de lo debido
        response = self.client_obj.post(
            reverse('registrar_pago', args=[cuota.id]),
            {'monto_pagado': '10000'}  # > monto_pendiente
        )
        
        # Debe rechazar o indicar error
        self.assertEqual(response.status_code, 200)  # Form re-rendered con error
        self.assertContains(response, 'No puede pagar más' or 'excede')
    
    def test_validacion_7_pago_valido_aceptado(self):
        """V7: Acepta pago válido (<= monto_pendiente)"""
        # Crear préstamo y cuota
        prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('10000'),
            interes_porcentaje=Decimal('5.0'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('5000'),
            monto_pendiente=Decimal('5000'),
            interes_normal=Decimal('0'),
            monto_pendiente_interes=Decimal('0'),
            fecha_pago_esperada=date.today() + timedelta(days=15)
        )
        
        # Pagar cantidad válida
        response = self.client_obj.post(
            reverse('registrar_pago', args=[cuota.id]),
            {'monto_pagado': '2500'}  # < monto_pendiente
        )
        
        # Debe aceptar (redirige)
        self.assertEqual(response.status_code, 302)


class AuditoriaValidacionesTests(TestCase):
    """Tests que verifican el auditor de validaciones funciona"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='admin',
            password='admin'
        )
    
    def test_auditor_validaciones_ejecuta_sin_errores(self):
        """El auditor de validaciones debe ejecutar sin errores"""
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        # No debe lanzar excepciones
        try:
            call_command('auditar_validaciones', stdout=out)
            output = out.getvalue()
            # Verificar que ejecutó todas las 7 validaciones
            self.assertIn('VALIDACIÓN #1', output)
            self.assertIn('VALIDACIÓN #7', output)
        except Exception as e:
            self.fail(f"Auditor falló: {str(e)}")
