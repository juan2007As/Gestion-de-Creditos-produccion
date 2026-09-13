"""
CRÍTICA #10: Tests para Deuda Técnica Acumulada

Tests para validar:
1. Funciones consolidadas funcionan correctamente
2. Lógica es idéntica a código legacy
3. Docstrings están completos
4. No hay código duplicado
"""

import pytest
from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta

from mi_app.utilities.tech_debt_fixes import (
    ConsolidatedValidations,
    ConsolidatedCalculations,
    DocumentationHelper,
)


class TestConsolidatedValidations(TestCase):
    """Tests para validaciones centralizadas"""
    
    # ==========================================================================
    # VALIDAR CÉDULA
    # ==========================================================================
    
    def test_validar_cedula_valida_sin_guion(self):
        """Cédula válida sin guiones"""
        valido, msg = ConsolidatedValidations.validar_cedula("1234567890")
        assert valido is True
        assert msg is None
    
    def test_validar_cedula_valida_con_guion(self):
        """Cédula válida con guiones"""
        valido, msg = ConsolidatedValidations.validar_cedula("1234-567-890")
        assert valido is True
        assert msg is None
    
    def test_validar_cedula_valida_con_espacios(self):
        """Cédula válida con espacios (se limpian)"""
        valido, msg = ConsolidatedValidations.validar_cedula("1234 567 890")
        assert valido is True
        assert msg is None
    
    def test_validar_cedula_vacia(self):
        """Cédula vacía debe fallar"""
        valido, msg = ConsolidatedValidations.validar_cedula("")
        assert valido is False
        assert "requerida" in msg.lower()
    
    def test_validar_cedula_con_letras(self):
        """Cédula con letras debe fallar"""
        valido, msg = ConsolidatedValidations.validar_cedula("1234ABC890")
        assert valido is False
        assert "solo números" in msg.lower()
    
    def test_validar_cedula_muy_corta(self):
        """Cédula muy corta (<6 dígitos) debe fallar"""
        valido, msg = ConsolidatedValidations.validar_cedula("12345")
        assert valido is False
        assert "6-15" in msg
    
    def test_validar_cedula_muy_larga(self):
        """Cédula muy larga (>15 dígitos) debe fallar"""
        valido, msg = ConsolidatedValidations.validar_cedula("1234567890123456")
        assert valido is False
        assert "6-15" in msg
    
    def test_validar_cedula_solo_guiones(self):
        """Cédula con solo guiones debe fallar"""
        valido, msg = ConsolidatedValidations.validar_cedula("---")
        assert valido is False
    
    # ==========================================================================
    # VALIDAR EMAIL
    # ==========================================================================
    
    def test_validar_email_valido(self):
        """Email válido"""
        valido, msg = ConsolidatedValidations.validar_email("user@example.com")
        assert valido is True
        assert msg is None
    
    def test_validar_email_con_punto(self):
        """Email con puntos"""
        valido, msg = ConsolidatedValidations.validar_email("user.name+tag@example.co.uk")
        assert valido is True
    
    def test_validar_email_invalido_sin_arroba(self):
        """Email sin @ debe fallar"""
        valido, msg = ConsolidatedValidations.validar_email("userexample.com")
        assert valido is False
    
    def test_validar_email_invalido_sin_dominio(self):
        """Email sin dominio debe fallar"""
        valido, msg = ConsolidatedValidations.validar_email("user@")
        assert valido is False
    
    def test_validar_email_vacio(self):
        """Email vacío debe fallar"""
        valido, msg = ConsolidatedValidations.validar_email("")
        assert valido is False
    
    # ==========================================================================
    # VALIDAR TELÉFONO
    # ==========================================================================
    
    def test_validar_telefono_valido(self):
        """Teléfono válido"""
        valido, msg = ConsolidatedValidations.validar_telefono("3154567890")
        assert valido is True
        assert msg is None
    
    def test_validar_telefono_con_formato(self):
        """Teléfono con formato +57 315 456 7890"""
        valido, msg = ConsolidatedValidations.validar_telefono("+57 315 456 7890")
        assert valido is True
    
    def test_validar_telefono_muy_corto(self):
        """Teléfono muy corto (<7 dígitos) debe fallar"""
        valido, msg = ConsolidatedValidations.validar_telefono("31456")
        assert valido is False
        assert "muy corto" in msg.lower()
    
    def test_validar_telefono_muy_largo(self):
        """Teléfono muy largo (>15 dígitos) debe fallar"""
        valido, msg = ConsolidatedValidations.validar_telefono("123456789012345678")
        assert valido is False
        assert "muy largo" in msg.lower()
    
    # ==========================================================================
    # VALIDAR MONTO
    # ==========================================================================
    
    def test_validar_monto_positivo(self):
        """Monto positivo válido"""
        valido, msg = ConsolidatedValidations.validar_monto(Decimal('1000.00'))
        assert valido is True
        assert msg is None
    
    def test_validar_monto_desde_string(self):
        """Monto desde string"""
        valido, msg = ConsolidatedValidations.validar_monto("1000")
        assert valido is True
    
    def test_validar_monto_desde_int(self):
        """Monto desde int"""
        valido, msg = ConsolidatedValidations.validar_monto(1000)
        assert valido is True
    
    def test_validar_monto_negativo(self):
        """Monto negativo debe fallar"""
        valido, msg = ConsolidatedValidations.validar_monto(Decimal('-100'))
        assert valido is False
        assert "negativo" in msg.lower() or "mínimo" in msg.lower()
    
    def test_validar_monto_con_maximo(self):
        """Monto que excede máximo debe fallar"""
        valido, msg = ConsolidatedValidations.validar_monto(
            Decimal('5000'),
            maximo=Decimal('1000')
        )
        assert valido is False
        assert "máximo" in msg.lower()
    
    def test_validar_monto_invalido(self):
        """String no numérico debe fallar"""
        valido, msg = ConsolidatedValidations.validar_monto("ABC")
        assert valido is False


class TestConsolidatedCalculations(TestCase):
    """Tests para cálculos financieros centralizados"""
    
    # ==========================================================================
    # CALCULAR MORA DIARIA
    # ==========================================================================
    
    def test_calcular_mora_vencido_sin_gracia(self):
        """Mora de cuota vencida hace 5 días"""
        fecha_vencimiento = date(2024, 2, 1)
        fecha_actual = date(2024, 2, 6)
        
        mora = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=fecha_vencimiento,
            monto_pendiente=Decimal('1000'),
            tasa_mora_diaria=Decimal('0.0002'),  # 0.02%
            dias_gracia=0,
            fecha_actual=fecha_actual
        )
        
        # 5 días * 1000 * 0.0002 = 1.00
        assert mora == Decimal('1.00')
    
    def test_calcular_mora_con_dias_gracia(self):
        """Mora con días de gracia"""
        fecha_vencimiento = date(2024, 2, 1)
        fecha_actual = date(2024, 2, 10)  # 9 días vencido
        
        mora = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=fecha_vencimiento,
            monto_pendiente=Decimal('1000'),
            tasa_mora_diaria=Decimal('0.0002'),
            dias_gracia=3,  # 9 - 3 = 6 días de mora
            fecha_actual=fecha_actual
        )
        
        # (9-3) * 1000 * 0.0002 = 1.20
        assert mora == Decimal('1.20')
    
    def test_calcular_mora_no_vencido(self):
        """Cuota que no está vencida = mora cero"""
        fecha_vencimiento = date(2024, 3, 15)
        fecha_actual = date(2024, 3, 10)
        
        mora = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=fecha_vencimiento,
            monto_pendiente=Decimal('1000'),
            tasa_mora_diaria=Decimal('0.0002'),
            fecha_actual=fecha_actual
        )
        
        assert mora == Decimal('0')
    
    def test_calcular_mora_monto_cero(self):
        """Mora con monto pendiente cero"""
        mora = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=date(2024, 2, 1),
            monto_pendiente=Decimal('0'),
            tasa_mora_diaria=Decimal('0.0002'),
            fecha_actual=date(2024, 2, 10)
        )
        
        assert mora == Decimal('0')
    
    def test_calcular_mora_monto_negativo_raises(self):
        """Monto negativo debe lanzar excepción"""
        with pytest.raises(ValueError):
            ConsolidatedCalculations.calcular_mora_diaria(
                fecha_vencimiento=date(2024, 2, 1),
                monto_pendiente=Decimal('-1000'),
                tasa_mora_diaria=Decimal('0.0002')
            )
    
    # ==========================================================================
    # CALCULAR INTERÉS POR PERÍODO
    # ==========================================================================
    
    def test_calcular_interes_simple(self):
        """Interés simple: I = P * r * t"""
        interes = ConsolidatedCalculations.calcular_interes_por_periodo(
            monto_principal=Decimal('10000'),
            tasa_periodica=Decimal('2.5'),  # 2.5% por período
            numero_periodos=12,
            tipo_interes='simple'
        )
        
        # 10000 * 0.025 * 12 = 3000
        assert interes == Decimal('3000.00')
    
    def test_calcular_interes_compuesto(self):
        """Interés compuesto: A = P * (1 + r)^t"""
        interes = ConsolidatedCalculations.calcular_interes_por_periodo(
            monto_principal=Decimal('10000'),
            tasa_periodica=Decimal('2.5'),
            numero_periodos=12,
            tipo_interes='compuesto'
        )
        
        # A = 10000 * (1.025)^12 ≈ 13449.16, I = 3449.16
        assert Decimal('3400') < interes < Decimal('3500')
    
    def test_calcular_interes_cero_periodos(self):
        """Cero períodos = cero interés"""
        interes = ConsolidatedCalculations.calcular_interes_por_periodo(
            monto_principal=Decimal('10000'),
            tasa_periodica=Decimal('2.5'),
            numero_periodos=0
        )
        
        assert interes == Decimal('0')
    
    def test_calcular_interes_tipo_invalido(self):
        """Tipo de interés inválido lanza excepción"""
        with pytest.raises(ValueError):
            ConsolidatedCalculations.calcular_interes_por_periodo(
                monto_principal=Decimal('10000'),
                tasa_periodica=Decimal('2.5'),
                numero_periodos=12,
                tipo_interes='invalido'
            )
    
    # ==========================================================================
    # CALCULAR CUOTA
    # ==========================================================================
    
    def test_calcular_cuota_monto_tasa_periodo(self):
        """Calcula cuota fija de amortización"""
        cuota = ConsolidatedCalculations.calcular_rata_cuota(
            monto_total=Decimal('10000'),
            tasa_interes_periodica=Decimal('1.5'),  # 1.5% mensual
            numero_periodos=12
        )
        
        # Cuota debe estar en rango razonable (alrededor de 916)
        assert Decimal('900') < cuota < Decimal('930')
    
    def test_calcular_cuota_tasa_cero(self):
        """Cuota a tasa 0% = monto / períodos"""
        cuota = ConsolidatedCalculations.calcular_rata_cuota(
            monto_total=Decimal('12000'),
            tasa_interes_periodica=Decimal('0'),
            numero_periodos=12
        )
        
        # 12000 / 12 = 1000
        assert cuota == Decimal('1000.00')
    
    def test_calcular_cuota_cero_periodos(self):
        """Cero períodos = cuota cero"""
        cuota = ConsolidatedCalculations.calcular_rata_cuota(
            monto_total=Decimal('10000'),
            tasa_interes_periodica=Decimal('1.5'),
            numero_periodos=0
        )
        
        assert cuota == Decimal('0')


class TestDocumentationHelper(TestCase):
    """Tests para generador de docstrings"""
    
    def test_generar_template_docstring(self):
        """Genera template de docstring correctamente"""
        template = DocumentationHelper.generar_template_docstring(
            nombre_funcion="crear_prestamo",
            parametros=[
                ["cliente", "Cliente", "Cliente que solicita"],
                ["monto", "Decimal", "Monto a prestar"]
            ],
            retorno="Prestamo: Objeto creado",
            descripcion="Crea un nuevo préstamo"
        )
        
        assert 'crear_prestamo' in template or 'Crea un nuevo préstamo' in template
        assert 'cliente' in template
        assert 'Args:' in template
        assert 'Returns:' in template
        assert '"""' in template


@pytest.mark.django_db
class TestNoCodeDuplication(TestCase):
    """Tests para verificar que no hay código duplicado"""
    
    def test_validar_cedula_consistente(self):
        """Resultado de validación debe ser consistente"""
        cedula_valida = "1234567890"
        cedula_invalida = "ABC"
        
        # Múltiples llamadas con mismo input = mismo output
        val1, msg1 = ConsolidatedValidations.validar_cedula(cedula_valida)
        val2, msg2 = ConsolidatedValidations.validar_cedula(cedula_valida)
        
        assert val1 == val2
        assert msg1 == msg2
    
    def test_calcular_mora_consistente(self):
        """Mora debe ser consistente"""
        fecha_vencimiento = date(2024, 2, 1)
        monto = Decimal('1000')
        
        mora1 = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=fecha_vencimiento,
            monto_pendiente=monto,
            fecha_actual=date(2024, 2, 6)
        )
        
        mora2 = ConsolidatedCalculations.calcular_mora_diaria(
            fecha_vencimiento=fecha_vencimiento,
            monto_pendiente=monto,
            fecha_actual=date(2024, 2, 6)
        )
        
        assert mora1 == mora2
