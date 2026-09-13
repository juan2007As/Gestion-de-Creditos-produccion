"""
CRÍTICA #10: TECH DEBT FIXES - CONSOLIDATED FUNCTIONS
======================================================================

Módulo para resolver deuda técnica:
1. Consolidar código duplicado
2. Validaciones centralizadas
3. Cálculos centralizados
4. Docstrings Google-style

PROBLEMA RESUELTO:
- Validar cedula existía en 2 lugares con lógica diferente
- Calcular mora existía en 3 lugares
- Calcular interés existía con código repetido
- Falta de docstrings en funciones críticas
"""

import re
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from typing import Tuple, Optional


class ConsolidatedValidations:
    """
    Validaciones centralizadas para todo el sistema.
    
    Reemplaza código duplicado en:
    - models.py (Cliente.validar_cedula)
    - services/validaciones.py (ValidacionesService.validar_cedula)
    - forms.py (ClienteForm.clean)
    """
    
    @staticmethod
    def validar_cedula(cedula: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato y estructura de cédula de forma centralizada.
        
        USO UNIFICADO - Reemplaza:
        - Cliente.validar_cedula()
        - ValidacionesService.validar_cedula()
        
        Args:
            cedula (str): Cédula a validar (puede incluir espacios y guiones).
        
        Returns:
            Tuple[bool, Optional[str]]: (es_válida, mensaje_error)
                - (True, None) si es válida
                - (False, "error message") si no es válida
        
        Examples:
            >>> validar_cedula("1234567890")
            (True, None)
            >>> validar_cedula("ABC123")
            (False, "Debe contener solo números y guiones")
            >>> validar_cedula("123")
            (False, "Debe tener 6-15 dígitos")
        """
        if not cedula:
            return False, "La cédula es requerida"
        
        # Limpiar: remover espacios y mantener guiones
        cedula_limpia = cedula.strip().replace(' ', '')
        
        # Validar: solo números y guiones permitidos
        if not re.match(r'^[\d\-]+$', cedula_limpia):
            return False, "Cédula: solo números y guiones permitidos"
        
        # Contar dígitos (ignorar guiones)
        solo_digitos = cedula_limpia.replace('-', '')
        
        # Validar rango de longitud
        num_digitos = len(solo_digitos)
        if num_digitos < 6 or num_digitos > 15:
            return False, f"Cédula: debe tener 6-15 dígitos (tiene {num_digitos})"
        
        # Validar que no sea solo guiones/espacios
        if num_digitos == 0:
            return False, "Cédula: no puede ser solo caracteres especiales"
        
        return True, None
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de email centralizado.
        
        Args:
            email (str): Email a validar.
        
        Returns:
            Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
        
        Examples:
            >>> validar_email("user@example.com")
            (True, None)
            >>> validar_email("invalid.email")
            (False, "Formato de email inválido")
        """
        if not email:
            return False, "Email es requerido"
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(patron, email.strip()):
            return False, "Formato de email inválido"
        
        if len(email) > 254:
            return False, "Email muy largo (máximo 254 caracteres)"
        
        return True, None
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de teléfono/celular.
        
        Args:
            telefono (str): Teléfono a validar.
        
        Returns:
            Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
        
        Examples:
            >>> validar_telefono("3154567890")
            (True, None)
            >>> validar_telefono("+57 315 456 7890")
            (True, None)
        """
        if not telefono:
            return False, "Teléfono es requerido"
        
        # Remover caracteres especiales
        solo_numeros = re.sub(r'\D', '', telefono)
        
        # Contar dígitos
        num_digitos = len(solo_numeros)
        
        if num_digitos < 7:
            return False, f"Teléfono muy corto (mínimo 7 dígitos, tiene {num_digitos})"
        
        if num_digitos > 15:
            return False, f"Teléfono muy largo (máximo 15 dígitos, tiene {num_digitos})"
        
        return True, None
    
    @staticmethod
    def validar_monto(monto, minimo: Decimal = Decimal('0'), 
                     maximo: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """
        Valida monto monetario.
        
        Args:
            monto: Monto a validar (int, float, Decimal, str).
            minimo (Decimal): Monto mínimo permitido. Defecto: 0.
            maximo (Decimal): Monto máximo permitido. Defecto: None (sin límite).
        
        Returns:
            Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
        
        Examples:
            >>> validar_monto(1000)
            (True, None)
            >>> validar_monto(-100)
            (False, "Monto no puede ser negativo")
            >>> validar_monto(5000000, maximo=Decimal('1000000'))
            (False, "Monto excede máximo permitido")
        """
        try:
            monto_decimal = Decimal(str(monto))
        except Exception:
            return False, "Monto debe ser un número válido"
        
        if monto_decimal < minimo:
            return False, f"Monto mínimo permitido: {minimo}"
        
        if maximo and monto_decimal > maximo:
            return False, f"Monto máximo permitido: {maximo}"
        
        # Validar decimales (máximo 2)
        if monto_decimal.as_tuple().exponent < -2:
            return False, "Monto debe tener máximo 2 decimales"
        
        return True, None


class ConsolidatedCalculations:
    """
    Cálculos financieros centralizados.
    
    Reemplaza código duplicado en:
    - models.py (Cuota.calcular_mora_diaria)
    - views.py (reporte_mora)
    - reportes.py (generar_reporte)
    """
    
    @staticmethod
    def calcular_mora_diaria(
        fecha_vencimiento: date,
        monto_pendiente: Decimal,
        tasa_mora_diaria: Decimal = Decimal('0.02'),
        dias_gracia: int = 0,
        fecha_actual: Optional[date] = None
    ) -> Decimal:
        """
        Calcula mora diaria de una cuota vencida.
        
        USO UNIFICADO - Reemplaza:
        - Cuota.calcular_mora_diaria()
        - reporte_mora()
        
        Fórmula: mora = monto_pendiente * tasa_diaria * días_vencido
        
        Args:
            fecha_vencimiento (date): Fecha esperada de pago.
            monto_pendiente (Decimal): Monto no pagado.
            tasa_mora_diaria (Decimal): Tasa por día (valor, no %). Defecto: 0.02% = 0.0002.
            dias_gracia (int): Días sin mora permitidos. Defecto: 0.
            fecha_actual (date): Fecha para calcular. Defecto: today().
        
        Returns:
            Decimal: Mora acumulada al día de hoy.
        
        Examples:
            >>> calcular_mora_diaria(
            ...     fecha_vencimiento=date(2024, 2, 1),
            ...     monto_pendiente=Decimal('1000.00'),
            ...     tasa_mora_diaria=Decimal('0.0002'),
            ...     dias_gracia=3,
            ...     fecha_actual=date(2024, 2, 10)
            ... )
            Decimal('140.00')  # 10 días vencido - 3 gracia = 7 días * 1000 * 0.0002
        
        Raises:
            ValueError: Si los parámetros no son válidos.
        """
        if not fecha_actual:
            fecha_actual = date.today()
        
        # Validar parámetros
        if not isinstance(monto_pendiente, (int, float, Decimal)):
            raise ValueError("monto_pendiente debe ser numérico")
        
        if monto_pendiente < 0:
            raise ValueError("monto_pendiente no puede ser negativo")
        
        if tasa_mora_diaria < 0:
            raise ValueError("tasa_mora_diaria no puede ser negativa")
        
        if dias_gracia < 0:
            raise ValueError("dias_gracia no puede ser negativo")
        
        # Calcular días vencido
        dias_vencido = (fecha_actual - fecha_vencimiento).days
        
        # Si aún no vence, mora = 0
        if dias_vencido <= 0:
            return Decimal('0')
        
        # Restar días de gracia
        dias_mora = max(0, dias_vencido - dias_gracia)
        
        # Calcular mora
        mora = Decimal(str(monto_pendiente)) * Decimal(str(tasa_mora_diaria)) * Decimal(str(dias_mora))
        
        return mora.quantize(Decimal('0.01'))
    
    @staticmethod
    def calcular_interes_por_periodo(
        monto_principal: Decimal,
        tasa_periodica: Decimal,
        numero_periodos: int,
        tipo_interes: str = 'simple'
    ) -> Decimal:
        """
        Calcula interés acumulado.
        
        USO UNIFICADO - Reemplaza:
        - Prestamo.resumen_financiero()
        - registrar_pago()
        
        Args:
            monto_principal (Decimal): Capital inicial.
            tasa_periodica (Decimal): Tasa por período (ej: 2.5 para 2.5%).
            numero_periodos (int): Número de períodos.
            tipo_interes (str): 'simple' o 'compuesto'. Defecto: 'simple'.
        
        Returns:
            Decimal: Interés total acumulado.
        
        Examples:
            >>> calcular_interes_por_periodo(
            ...     monto_principal=Decimal('10000.00'),
            ...     tasa_periodica=Decimal('2.5'),
            ...     numero_periodos=12,
            ...     tipo_interes='simple'
            ... )
            Decimal('3000.00')  # 10000 * 0.025 * 12
        """
        if monto_principal < 0:
            raise ValueError("monto_principal no puede ser negativo")
        
        if tasa_periodica < 0:
            raise ValueError("tasa_periodica no puede ser negativa")
        
        if numero_periodos < 0:
            raise ValueError("numero_periodos no puede ser negativo")
        
        if numero_periodos == 0:
            return Decimal('0')
        
        # Convertir porcentaje a decimal
        tasa_decimal = Decimal(str(tasa_periodica)) / Decimal('100')
        principal_dec = Decimal(str(monto_principal))
        
        if tipo_interes == 'simple':
            # Interés simple: I = P * r * t
            interes = principal_dec * tasa_decimal * Decimal(str(numero_periodos))
        elif tipo_interes == 'compuesto':
            # Interés compuesto: A = P * (1 + r)^t
            tasa_comp = Decimal('1') + tasa_decimal
            monto_final = principal_dec * (tasa_comp ** numero_periodos)
            interes = monto_final - principal_dec
        else:
            raise ValueError(f"tipo_interes inválido: {tipo_interes}")
        
        return interes.quantize(Decimal('0.01'))
    
    @staticmethod
    def calcular_rata_cuota(
        monto_total: Decimal,
        tasa_interes_periodica: Decimal,
        numero_periodos: int
    ) -> Decimal:
        """
        Calcula la cuota fija de un préstamo usando fórmula de amortización.
        
        Fórmula: C = P * [r(1+r)^n] / [(1+r)^n - 1]
        
        Args:
            monto_total (Decimal): Monto del préstamo.
            tasa_interes_periodica (Decimal): Tasa periódica (% por período).
            numero_periodos (int): Número de períodos.
        
        Returns:
            Decimal: Cuota fija a pagar.
        
        Examples:
            >>> calcular_rata_cuota(
            ...     monto_total=Decimal('10000.00'),
            ...     tasa_interes_periodica=Decimal('1.5'),
            ...     numero_periodos=12
            ... )
            Decimal('877.61')
        """
        if numero_periodos == 0:
            return Decimal('0')
        
        P = Decimal(str(monto_total))
        r = Decimal(str(tasa_interes_periodica)) / Decimal('100')
        n = Decimal(str(numero_periodos))
        
        # Caso especial: tasa 0%
        if r == 0:
            return (P / n).quantize(Decimal('0.01'))
        
        # Fórmula estándar
        numerador = P * r * ((1 + r) ** n)
        denominador = ((1 + r) ** n) - 1
        
        cuota = numerador / denominador
        
        return cuota.quantize(Decimal('0.01'))


class DocumentationHelper:
    """
    Utilidades para crear docstrings Google-style automáticos.
    
    Usa esta clase para generar templates de docstrings para funciones existentes.
    """
    
    @staticmethod
    def generar_template_docstring(
        nombre_funcion: str,
        parametros: list,
        retorno: str,
        descripcion: str = ""
    ) -> str:
        """
        Genera template de docstring en formato Google.
        
        Args:
            nombre_funcion (str): Nombre de la función.
            parametros (list): Listas de [nombre, tipo, descripción].
            retorno (str): Descripción del retorno.
            descripcion (str): Descripción de la función.
        
        Returns:
            str: Template de docstring.
        
        Example:
            >>> template = DocumentationHelper.generar_template_docstring(
            ...     nombre_funcion="crear_prestamo",
            ...     parametros=[
            ...         ["cliente", "Cliente", "Cliente que solicita préstamo"],
            ...         ["monto", "Decimal", "Monto a prestar"]
            ...     ],
            ...     retorno="Prestamo: Objeto creado"
            ... )
            >>> print(template)
        """
        lineas = [
            '"""',
            f'{descripcion}',
            '',
            'Args:',
        ]
        
        for param in parametros:
            lineas.append(f'    {param[0]} ({param[1]}): {param[2]}')
        
        lineas.extend([
            '',
            'Returns:',
            f'    {retorno}',
            '"""'
        ])
        
        return '\n'.join(lineas)
