#!/usr/bin/env python
"""
Tests para Validación de Total Prestado
========================================

Valida que el cálculo de total_prestado sea correcto en todas las operaciones.

Casos de prueba:
1. Cálculo de total_prestado_real: suma correcta de todos los préstamos
2. Cálculo de total_prestado_activo: suma solo de préstamos activos
3. Cálculo de total_prestado_completado: suma solo de préstamos completados
4. Detección de inconsistencias: identifica correctamente cuando hay mismatch
5. Corrección de inconsistencias: actualiza el total a su valor real
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from mi_app.models import Cliente, Prestamo
from datetime import datetime, timedelta

class TotalPrestadoTestCase(TestCase):
    """Pruebas para validar cálculos de total_prestado"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombre='Juan López Pérez',
            ci='12345678',
            telefono='+34612345678',
            email='juan@example.com',
            total_prestado=Decimal('0')
        )
        
        # Fecha base para préstamos
        self.fecha_base = datetime.now().date()
    
    def test_total_prestado_real_suma_correcta(self):
        """
        CASO 1: total_prestado_real debe sumar correctamente todos los préstamos
        """
        print("\n🧪 TEST 1: Suma correcta de total_prestado_real")
        print("-" * 60)
        
        # Crear 3 préstamos
        prestamo1 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            tasa_interes=Decimal('20'),
            num_cuotas=4,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo2 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('50000'),
            tasa_interes=Decimal('15'),
            num_cuotas=6,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo3 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('75000'),
            tasa_interes=Decimal('25'),
            num_cuotas=3,
            estado='COMPLETADO',
            fecha_creacion=self.fecha_base
        )
        
        # Calcular suma esperada
        suma_esperada = Decimal('225000')
        
        # Verificar que total_prestado_real es correcto
        total_real = self.cliente.total_prestado_real
        
        print(f"   Préstamo 1: ${prestamo1.monto_total:,.2f}")
        print(f"   Préstamo 2: ${prestamo2.monto_total:,.2f}")
        print(f"   Préstamo 3: ${prestamo3.monto_total:,.2f}")
        print(f"   Total esperado: ${suma_esperada:,.2f}")
        print(f"   Total real: ${total_real:,.2f}")
        
        self.assertEqual(
            total_real, 
            suma_esperada,
            f"Total debe ser {suma_esperada}, pero es {total_real}"
        )
        
        print("   ✅ PASO: Suma correcta")
    
    def test_total_prestado_activo_filtra_correctamente(self):
        """
        CASO 2: total_prestado_activo debe sumar SOLO préstamos activos
        """
        print("\n🧪 TEST 2: Filtrado correcto de préstamos activos")
        print("-" * 60)
        
        # Crear préstamos con diferentes estados
        prestamo_activo1 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            tasa_interes=Decimal('20'),
            num_cuotas=4,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo_en_proceso = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('50000'),
            tasa_interes=Decimal('15'),
            num_cuotas=6,
            estado='EN_PROCESO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo_completado = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('75000'),
            tasa_interes=Decimal('25'),
            num_cuotas=3,
            estado='COMPLETADO',
            fecha_creacion=self.fecha_base
        )
        
        # Suma esperada: solo ACTIVO + EN_PROCESO
        suma_esperada = Decimal('150000')  # 100000 + 50000
        
        total_activo = self.cliente.total_prestado_activo
        
        print(f"   Préstamo ACTIVO: ${prestamo_activo1.monto_total:,.2f}")
        print(f"   Préstamo EN_PROCESO: ${prestamo_en_proceso.monto_total:,.2f}")
        print(f"   Préstamo COMPLETADO: ${prestamo_completado.monto_total:,.2f}")
        print(f"   Total activo esperado: ${suma_esperada:,.2f}")
        print(f"   Total activo real: ${total_activo:,.2f}")
        
        self.assertEqual(
            total_activo,
            suma_esperada,
            f"Total activo debe ser {suma_esperada}, pero es {total_activo}"
        )
        
        print("   ✅ PASO: Filtrado correcto")
    
    def test_total_prestado_completado_filtra_correctamente(self):
        """
        CASO 3: total_prestado_completado debe sumar SOLO préstamos completados
        """
        print("\n🧪 TEST 3: Filtrado correcto de préstamos completados")
        print("-" * 60)
        
        # Crear préstamos con diferentes estados
        prestamo_activo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            tasa_interes=Decimal('20'),
            num_cuotas=4,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo_completado1 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('50000'),
            tasa_interes=Decimal('15'),
            num_cuotas=6,
            estado='COMPLETADO',
            fecha_creacion=self.fecha_base
        )
        
        prestamo_completado2 = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('75000'),
            tasa_interes=Decimal('25'),
            num_cuotas=3,
            estado='COMPLETADO',
            fecha_creacion=self.fecha_base
        )
        
        # Suma esperada: solo COMPLETADO
        suma_esperada = Decimal('125000')  # 50000 + 75000
        
        total_completado = self.cliente.total_prestado_completado
        
        print(f"   Préstamo ACTIVO: ${prestamo_activo.monto_total:,.2f}")
        print(f"   Préstamo COMPLETADO 1: ${prestamo_completado1.monto_total:,.2f}")
        print(f"   Préstamo COMPLETADO 2: ${prestamo_completado2.monto_total:,.2f}")
        print(f"   Total completado esperado: ${suma_esperada:,.2f}")
        print(f"   Total completado real: ${total_completado:,.2f}")
        
        self.assertEqual(
            total_completado,
            suma_esperada,
            f"Total completado debe ser {suma_esperada}, pero es {total_completado}"
        )
        
        print("   ✅ PASO: Filtrado correcto")
    
    def test_deteccion_inconsistencias(self):
        """
        CASO 4: tiene_inconsistencia_totales debe detectar correctamente mismatches
        """
        print("\n🧪 TEST 4: Detección de inconsistencias")
        print("-" * 60)
        
        # Crear un préstamo
        prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            tasa_interes=Decimal('20'),
            num_cuotas=4,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        # SIN inconsistencia: total_prestado == total_prestado_real
        print(f"   Total prestado en BD: ${self.cliente.total_prestado:,.2f}")
        print(f"   Total prestado real: ${self.cliente.total_prestado_real:,.2f}")
        
        tiene_inconsistencia, diferencia = self.cliente.tiene_inconsistencia_totales()
        
        if not tiene_inconsistencia:
            print(f"   ✅ Sin inconsistencia: diferencia = ${diferencia:,.2f}")
        else:
            print(f"   ❌ Inconsistencia detectada: ${diferencia:,.2f}")
        
        # CREAR inconsistencia: actualizar manualmente total_prestado
        self.cliente.total_prestado = Decimal('50000')
        self.cliente.save()
        
        print(f"\n   (Simulando inconsistencia...)")
        print(f"   Total prestado en BD: ${self.cliente.total_prestado:,.2f}")
        print(f"   Total prestado real: ${self.cliente.total_prestado_real:,.2f}")
        
        tiene_inconsistencia, diferencia = self.cliente.tiene_inconsistencia_totales()
        
        self.assertTrue(
            tiene_inconsistencia,
            "Debe detectar inconsistencia cuando total_prestado != total_prestado_real"
        )
        
        self.assertEqual(
            diferencia,
            Decimal('50000'),
            f"Diferencia debe ser 50000, pero es {diferencia}"
        )
        
        print(f"   ✅ Inconsistencia correctamente detectada: ${diferencia:,.2f}")
    
    def test_correccion_inconsistencias(self):
        """
        CASO 5: corregir_totales debe actualizar el total al valor real
        """
        print("\n🧪 TEST 5: Corrección de inconsistencias")
        print("-" * 60)
        
        # Crear un préstamo
        prestamo = Prestamo.objects.create(
            cliente=self.cliente,
            monto_total=Decimal('100000'),
            tasa_interes=Decimal('20'),
            num_cuotas=4,
            estado='ACTIVO',
            fecha_creacion=self.fecha_base
        )
        
        # CREAR inconsistencia
        self.cliente.total_prestado = Decimal('0')
        self.cliente.save()
        
        print(f"   ANTES de corrección:")
        print(f"   Total prestado en BD: ${self.cliente.total_prestado:,.2f}")
        print(f"   Total prestado real: ${self.cliente.total_prestado_real:,.2f}")
        
        # Corregir
        total_anterior, total_nuevo, diferencia = self.cliente.corregir_totales()
        
        print(f"\n   DESPUÉS de corrección:")
        print(f"   Total anterior: ${total_anterior:,.2f}")
        print(f"   Total nuevo: ${total_nuevo:,.2f}")
        print(f"   Diferencia manejada: ${diferencia:,.2f}")
        
        # Verificar que se corrigió
        self.cliente.refresh_from_db()
        tiene_inconsistencia, _ = self.cliente.tiene_inconsistencia_totales()
        
        self.assertFalse(
            tiene_inconsistencia,
            "Inconsistencia debe ser corregida después de llamar a corregir_totales()"
        )
        
        self.assertEqual(
            self.cliente.total_prestado,
            Decimal('100000'),
            "Total debe ser actualizado al valor real"
        )
        
        print(f"   ✅ Corrección exitosa")


# ============================================================================
# EJECUTAR TESTS
# ============================================================================

if __name__ == '__main__':
    import unittest
    
    print("\n" + "=" * 80)
    print("🧪 TESTS DE VALIDACIÓN - TOTAL PRESTADO")
    print("=" * 80)
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TotalPrestadoTestCase)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "=" * 80)
    print("📋 RESUMEN DE TESTS")
    print("=" * 80)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ Todos los tests pasaron correctamente")
    else:
        print("\n❌ Algunos tests fallaron")
    
    print("=" * 80)
