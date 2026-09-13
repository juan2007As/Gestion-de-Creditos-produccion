"""
VALIDACIONES SERVICE
===============================================================================
Propósito: Validaciones de negocio centralizadas
Métodos: Validar cedula, email, teléfono, etc.
===============================================================================
"""

import re
from django.core.exceptions import ValidationError


class ValidacionesService:
    """Servicio de validaciones"""

    @staticmethod
    def validar_cedula(cedula):
        """
        Validar formato y estructura de cédula
        
        Args:
            cedula (str): Cédula a validar
            
        Returns:
            bool: True si es válida
        """
        if not cedula or not cedula.isdigit():
            return False
        
        if len(cedula) < 8 or len(cedula) > 12:
            return False
        
        return True

    @staticmethod
    def validar_email(email):
        """
        Validar formato de email
        
        Args:
            email (str): Email a validar
            
        Returns:
            bool: True si es válido
        """
        patron = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return bool(re.match(patron, email))

    @staticmethod
    def validar_telefono(telefono):
        """
        Validar formato de teléfono
        
        Args:
            telefono (str): Teléfono a validar
            
        Returns:
            bool: True si es válido
        """
        # Solo números, entre 7 y 15 dígitos
        numeros = re.sub(r'\D', '', telefono)
        return 7 <= len(numeros) <= 15

    @staticmethod
    def validar_monto(monto, minimo=0, maximo=None):
        """
        Validar monto monetario
        
        Args:
            monto (float): Monto a validar
            minimo (float): Monto mínimo
            maximo (float): Monto máximo (opcional)
            
        Returns:
            bool: True si es válido
        """
        try:
            monto_num = float(monto)
            if monto_num < minimo:
                return False
            if maximo and monto_num > maximo:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validar_fecha(fecha):
        """
        Validar formato de fecha
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
            
        Returns:
            bool: True si es válida
        """
        try:
            from datetime import datetime
            datetime.strptime(fecha, '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validar_cliente_datos(datos):
        """
        Validar datos de un cliente
        
        Args:
            datos (dict): Diccionario con datos del cliente
            
        Returns:
            tuple: (válido: bool, errores: list)
        """
        errores = []
        
        # Validar cédula
        if 'cedula' in datos:
            if not ValidacionesService.validar_cedula(datos['cedula']):
                errores.append('Cédula inválida')
        
        # Validar email
        if 'email' in datos:
            if not ValidacionesService.validar_email(datos['email']):
                errores.append('Email inválido')
        
        # Validar teléfono
        if 'telefono' in datos:
            if not ValidacionesService.validar_telefono(datos['telefono']):
                errores.append('Teléfono inválido')
        
        # Validar nombre
        if 'nombre' in datos:
            if not datos['nombre'] or len(datos['nombre']) < 3:
                errores.append('Nombre debe tener mínimo 3 caracteres')
        
        return len(errores) == 0, errores

    @staticmethod
    def validar_prestamo_datos(datos):
        """
        Validar datos de un préstamo
        
        Args:
            datos (dict): Diccionario con datos del préstamo
            
        Returns:
            tuple: (válido: bool, errores: list)
        """
        errores = []
        
        # Validar monto
        if 'monto' in datos:
            if not ValidacionesService.validar_monto(datos['monto'], minimo=1000):
                errores.append('Monto debe ser mayor a 1000')
        
        # Validar cliente
        if 'cliente_id' not in datos:
            errores.append('Cliente es requerido')
        
        # Validar tasa
        if 'tasa_interes' in datos:
            if not isinstance(datos['tasa_interes'], (int, float)) or datos['tasa_interes'] < 0:
                errores.append('Tasa de interés inválida')
        
        return len(errores) == 0, errores

    @staticmethod
    def validar_contraseña(contraseña):
        """
        Validar fortaleza de contraseña
        
        Args:
            contraseña (str): Contraseña a validar
            
        Returns:
            tuple: (válida: bool, requisitos_no_cumplidos: list)
        """
        requisitos_no_cumplidos = []
        
        if len(contraseña) < 8:
            requisitos_no_cumplidos.append('Mínimo 8 caracteres')
        
        if not re.search(r'[A-Z]', contraseña):
            requisitos_no_cumplidos.append('Debe tener mayúsculas')
        
        if not re.search(r'[a-z]', contraseña):
            requisitos_no_cumplidos.append('Debe tener minúsculas')
        
        if not re.search(r'\d', contraseña):
            requisitos_no_cumplidos.append('Debe tener números')
        
        return len(requisitos_no_cumplidos) == 0, requisitos_no_cumplidos

    @staticmethod
    def sanitizar_entrada(texto):
        """
        Sanitizar entrada de usuario (básico)
        
        Args:
            texto (str): Texto a sanitizar
            
        Returns:
            str: Texto sanitizado
        """
        # Remover caracteres especiales peligrosos
        texto = re.sub(r'[<>\"\'%;()&+]', '', texto)
        return texto.strip()

    @staticmethod
    def validar_rango_fecha(fecha_inicio, fecha_fin):
        """
        Validar que fecha_inicio < fecha_fin
        
        Args:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD
            fecha_fin (str): Fecha fin YYYY-MM-DD
            
        Returns:
            bool: True si es válido
        """
        try:
            from datetime import datetime
            f_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            f_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            return f_inicio < f_fin
        except (ValueError, TypeError):
            return False
