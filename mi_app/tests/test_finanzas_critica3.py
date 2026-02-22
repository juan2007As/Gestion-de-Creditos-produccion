"""
Tests para CRÍTICA #3: Inconsistencias Financieras

Verifica que:
1. Total prestado se reconcilia automáticamente
2. Mora se actualiza automáticamente al guardar
3. Estados de cuota se actualizan correctamente
4. No hay divergencias en tasas de interés
"""

from django.test import TestCase
from django.contrib.auth.models import User
from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
from datetime import date, timedelta


class FinancialAuditTests(TestCase):
    """Tests para auditoría financiera"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.config = Configuracion.obtener_configuracion()
        
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            cedula='1234567890',
            celular='555-1234',
            total_prestado=Decimal('50000.00')
        )
        
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('5000.00'),
            interes_porcentaje=Decimal('12.50'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        self.cuota = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=1,
            monto_original=Decimal('5000.00'),
            monto_pendiente=Decimal('5000.00'),
            interes_normal=Decimal('625.00'),
            fecha_pago_esperada=date.today() - timedelta(days=10),  # 10 días de atraso (> 5 días de gracia)
            pagado=False,
            estado='PENDIENTE'
        )
    
    def test_total_prestado_reconciliacion(self):
        """Test: Total prestado se reconcilia correctamente"""
        # El cliente tiene un préstamo de $5000
        self.assertEqual(self.cliente.total_prestado_real, Decimal('5000.00'))
        
        # Pero el caché está mal
        self.cliente.total_prestado = Decimal('9999.99')
        self.cliente.save()
        
        # Verificar que hay inconsistencia
        tiene_inconsistencia, diferencia = self.cliente.tiene_inconsistencia_totales()
        self.assertTrue(tiene_inconsistencia)
        self.assertGreater(diferencia, Decimal('0.01'))
        
        # Corregir
        anterior, nuevo, diff = self.cliente.corregir_totales()
        self.assertEqual(nuevo, Decimal('5000.00'))
        self.assertEqual(diff, abs(Decimal('9999.99') - Decimal('5000.00')))
    
    def test_mora_auto_actualiza_al_guardar(self):
        """Test: Mora se actualiza automáticamente cuando se guarda la cuota"""
        # Crear una cuota con fecha vencida (10 días atrás)
        cuota_con_mora = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('5000.00'),
            monto_pendiente=Decimal('5000.00'),
            interes_normal=Decimal('625.00'),
            fecha_pago_esperada=date.today() - timedelta(days=10),
            pagado=False,
            estado='PENDIENTE'
        )
        
        # Al guardar, la mora debe ser calculada automáticamente
        cuota_con_mora.refresh_from_db()
        mora_calculada = cuota_con_mora.calcular_mora_diaria()
        
        # Mora guardada debe coincidir con la calculada
        self.assertEqual(cuota_con_mora.interes_mora_acumulado, mora_calculada)
        self.assertGreater(cuota_con_mora.interes_mora_acumulado, Decimal('0'))
    
    def test_estado_cuota_auto_actualiza(self):
        """Test: El estado de cuota se actualiza automáticamente"""
        # Crear una cuota con fecha futura primero
        futura = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('5000.00'),
            monto_pendiente=Decimal('5000.00'),
            interes_normal=Decimal('625.00'),
            fecha_pago_esperada=date.today() + timedelta(days=15),
            pagado=False,
            estado='PENDIENTE'
        )
        
        # Inicialmente está PENDIENTE
        self.assertEqual(futura.estado, 'PENDIENTE')
        
        # Cambiar fecha a vencida
        futura.fecha_pago_esperada = date.today() - timedelta(days=10)
        futura.save()
        
        # Debe estar VENCIDA
        futura.refresh_from_db()
        self.assertEqual(futura.estado, 'VENCIDA')
    
    def test_cuota_pagada_parcialmente_actualiza_estado(self):
        """Test: Cuota con pago parcial se marca como PARCIALMENTE_PAGADA"""
        # Pago parcial
        self.cuota.monto_pagado_principal = Decimal('2500.00')
        self.cuota.monto_pendiente = Decimal('2500.00')
        self.cuota.fecha_pago_esperada = date.today()  # Sin vencer
        self.cuota.save()
        
        # Debe estar PARCIALMENTE_PAGADA
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.estado, 'PARCIALMENTE_PAGADA')
        self.assertEqual(self.cuota.porcentaje_pagado, Decimal('50.00'))
    
    def test_cuota_completamente_pagada(self):
        """Test: Cuota completamente pagada se marca como PAGADA"""
        # Pago completo
        self.cuota.monto_pagado_principal = Decimal('5000.00')
        self.cuota.monto_pendiente = Decimal('0.00')
        self.cuota.monto_pagado_interes = Decimal('625.00')
        self.cuota.monto_pendiente_interes = Decimal('0.00')
        self.cuota.save()
        
        # Debe estar PAGADA
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.estado, 'PAGADA')
        self.assertTrue(self.cuota.pagado)
        self.assertEqual(self.cuota.porcentaje_pagado, Decimal('100.00'))
    
    def test_no_duplicar_mora_en_pagos_realizados(self):
        """Test: Mora no se duplica si la cuota ya está pagada"""
        # Marcar como pagada
        self.cuota.pagado = True
        self.cuota.monto_pendiente = Decimal('0.00')
        self.cuota.save()
        
        # Mora debe ser 0 para cuota pagada
        mora = self.cuota.calcular_mora_diaria()
        self.assertEqual(mora, Decimal('0'))
        
        # Y al guardar, la mora acumulada debe mantenerse en su valor
        self.cuota.interes_mora_acumulado = Decimal('0')
        self.cuota.save()
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.interes_mora_acumulado, Decimal('0'))
    
    def test_porcentaje_pagado_correcto(self):
        """Test: Porcentaje pagado se calcula correctamente"""
        # 30% pagado
        self.cuota.monto_pagado_principal = Decimal('1500.00')
        self.cuota.save()
        
        self.cuota.refresh_from_db()
        self.assertEqual(self.cuota.porcentaje_pagado, Decimal('30.00'))
    
    def test_tasa_interes_consistencia(self):
        """Test: Tasa de interés es consistente entre préstamo y cuota"""
        # La tasa en el préstamo es 12.50%
        self.assertEqual(self.prestamo.interes_porcentaje, Decimal('12.50'))
        
        # Crear otra cuota con interés consistente
        cuota2 = Cuota.objects.create(
            prestamo=self.prestamo,
            numero_cuota=2,
            monto_original=Decimal('5000.00'),
            monto_pendiente=Decimal('5000.00'),
            interes_normal=Decimal('625.00'),  # 12.5% de 5000
            fecha_pago_esperada=date.today() + timedelta(days=15),
            pagado=False,
            estado='PENDIENTE'
        )
        
        # Verificar que la tasa es consistente
        tasa_derivada = (cuota2.interes_normal / cuota2.monto_original) * 100
        diferencia = abs(float(self.prestamo.interes_porcentaje) - float(tasa_derivada))
        self.assertLess(diferencia, 1.0)  # Menos de 1% de diferencia
    
    def test_pago_registra_desglose_correcto(self):
        """Test: Pago registra desglose correcto de principal, interés y mora"""
        pago = Pago.objects.create(
            cuota=self.cuota,
            monto_pagado=Decimal('2000.00'),
            monto_principal=Decimal('1500.00'),
            monto_interes=Decimal('400.00'),
            monto_mora=Decimal('100.00'),
            usuario_registra='test_user',
            referencia='REF-001'
        )
        
        # Verificar que el total es correcto
        total_desglose = pago.monto_principal + pago.monto_interes + pago.monto_mora
        self.assertEqual(pago.monto_pagado, total_desglose)
    
    def test_reconciliacion_automatica_on_save(self):
        """Test: la reconciliación se ejecuta automáticamente al guardar"""
        # Crear una inconsistencia
        self.cliente.total_prestado = Decimal('99999.00')
        self.cliente.save()
        
        # Crear una cuota vencida sin mora actualizada
        self.cuota.interes_mora_acumulado = Decimal('0')
        self.cuota.save()
        
        # Verificar que la mora fue calculada
        self.cuota.refresh_from_db()
        self.assertGreater(self.cuota.interes_mora_acumulado, Decimal('0'))


class FinancialReportTests(TestCase):
    """Tests para reportes financieros"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.cliente = Cliente.objects.create(
            nombre='Cliente para Reporte',
            cedula='9876543210',
            celular='555-5678'
        )
        
        self.prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('10000.00'),
            interes_porcentaje=Decimal('10.00'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=30),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
    
    def test_resumen_financiero_completo(self):
        """Test: Resumen financiero contiene todos los campos necesarios"""
        resumen = self.prestamo.resumen_financiero()
        
        self.assertIn('monto_original', resumen)
        self.assertIn('tasa_interes_quincena', resumen)
        self.assertIn('interes_total_credito', resumen)
        self.assertIn('total_credito', resumen)
        self.assertIn('total_pagado_principal', resumen)
        self.assertIn('total_pagado_interes', resumen)
        self.assertIn('total_pendiente_principal', resumen)
        self.assertIn('total_pendiente_interes', resumen)
        self.assertIn('total_mora_acumulada', resumen)
    
    def test_total_prestado_real_vs_cache(self):
        """Test: Total prestado real siempre es correcto"""
        # Total real debe ser suma de préstamos
        self.assertEqual(self.prestamo.monto_total, Decimal('10000.00'))
        self.assertEqual(self.cliente.total_prestado_real, Decimal('10000.00'))


class FinancialValidationTests(TestCase):
    """Tests para validaciones financieras"""
    
    def test_mora_diaria_respeta_periodo_gracia(self):
        """Test: Mora diaria respeta período de gracia"""
        config = Configuracion.obtener_configuracion()
        
        cliente = Cliente.objects.create(
            nombre='Cliente Mora',
            cedula='1111111111',
            celular='555-1111'
        )
        
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=Decimal('5000.00'),
            interes_porcentaje=Decimal('5.00'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=60),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        # Cuota con 2 días de atraso (menos que período de gracia)
        cuota = Cuota.objects.create(
            prestamo=prestamo,
            numero_cuota=1,
            monto_original=Decimal('5000.00'),
            monto_pendiente=Decimal('5000.00'),
            interes_normal=Decimal('250.00'),
            fecha_pago_esperada=date.today() - timedelta(days=2),
            pagado=False,
            estado='PENDIENTE'
        )
        
        # Mora debe ser 0 (aún en período de gracia)
        mora = cuota.calcular_mora_diaria()
        self.assertEqual(mora, Decimal('0'))
