"""
EXCEL VALIDATOR SERVICE - ALTO #3
===============================================================================
Propósito: Validación y procesamiento de importación de Excel
Mejoras: Error handling granular, sin cancelar importación completamente
===============================================================================
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime, date, timedelta
import re
from django.core.exceptions import ValidationError
from mi_app.models import Cliente, Prestamo, Cuota
from mi_app.services.validaciones import ValidacionesService


class ExcelValidationError:
    """Representa un error en una fila del Excel"""
    
    def __init__(self, row_number, error_type, detail, severity='error'):
        self.row_number = row_number
        self.error_type = error_type  # 'CEDULA_INVALIDA', 'EMAIL_DUPLICADO', etc
        self.detail = detail
        self.severity = severity  # 'error' o 'warning'
    
    def to_dict(self):
        return {
            'fila': self.row_number,
            'tipo': self.error_type,
            'detalle': self.detail
        }


class ExcelValidationResult:
    """Resultado de la validación de un Excel"""
    
    def __init__(self):
        self.valid_rows = []
        self.errors = []
        self.warnings = []
    
    def add_valid_row(self, row_idx, row_data):
        """Agrega una fila válida"""
        self.valid_rows.append({
            'row_idx': row_idx,
            'data': row_data
        })
    
    def add_error(self, error):
        """Agrega un error"""
        self.errors.append(error)
    
    def add_warning(self, error):
        """Agrega una advertencia"""
        self.warnings.append(error)
    
    @property
    def total_errors(self):
        return len(self.errors)
    
    @property
    def total_warnings(self):
        return len(self.warnings)
    
    @property
    def total_valid(self):
        return len(self.valid_rows)
    
    def to_dict(self):
        return {
            'valid_rows': self.valid_rows,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'summary': {
                'total_valid': self.total_valid,
                'total_errors': self.total_errors,
                'total_warnings': self.total_warnings
            }
        }


class ExcelValidator:
    """Validador centralizado de importación de Excel"""
    
    # Columnas requeridas por su nombre
    REQUIRED_COLUMNS_MAP = {
        'cedula': ['Cédula', 'cedula', 'CEDULA', 'CC'],
        'nombre': ['Nombre', 'nombre', 'NOMBRE'],
        'telefono': ['Teléfono', 'telefono', 'Celular', 'celular', 'TELEFONO', 'CELULAR'],
        'email': ['Email', 'email', 'EMAIL', 'Correo', 'correo'],
        'monto': ['Monto', 'monto', 'MONTO', 'Valor', 'valor', 'Cantidad'],
        'interes': ['Interés', 'interes', 'INTERES', 'Tasa', 'tasa'],
        'cuotas': ['Cuotas', 'cuotas', 'CUOTAS', 'Número Cuotas']
    }
    
    @classmethod
    def validate_excel_structure(cls, df):
        """
        Valida que el Excel tenga la estructura correcta
        
        Args:
            df (DataFrame): Excel cargado como DataFrame
        
        Returns:
            tuple: (is_valid, message, missing_columns)
        """
        if df is None or len(df) == 0:
            return False, "El archivo Excel está vacío", []
        
        # Detectar columnas en el Excel
        actual_columns = df.columns.tolist()
        
        # Verificar columnas requeridas
        missing_columns = []
        found_columns = {}
        
        for required, variants in cls.REQUIRED_COLUMNS_MAP.items():
            found = False
            for variant in variants:
                if variant in actual_columns:
                    found_columns[required] = variant
                    found = True
                    break
            
            if not found:
                missing_columns.append(required)
        
        if missing_columns:
            return False, f"Faltan columnas requeridas: {', '.join(missing_columns)}", missing_columns
        
        return True, "Estructura válida", found_columns
    
    @classmethod
    def validate_row(cls, row_idx, row_data, found_columns):
        """
        Valida una fila del Excel
        
        Args:
            row_idx (int): Número de fila (1-indexed)
            row_data (Series): Fila de datos
            found_columns (dict): Mapeo de columnas encontradas
        
        Returns:
            tuple: (is_valid, cleaned_data, errors_list)
        """
        errors = []
        cleaned_data = {}
        
        try:
            # 1. CÉDULA
            cedula_col = found_columns.get('cedula')
            cedula = str(row_data.get(cedula_col, '')).strip() if cedula_col else ''
            
            if not cedula:
                errors.append(ExcelValidationError(
                    row_idx, 'CEDULA_REQUERIDA',
                    'Cédula vacía o no válida'
                ))
            elif not ValidacionesService.validar_cedula(cedula):
                errors.append(ExcelValidationError(
                    row_idx, 'CEDULA_INVALIDA',
                    f'Cédula inválida: {cedula}'
                ))
            else:
                # Verificar duplicados
                if Cliente.objects.filter(cedula=cedula).exists():
                    errors.append(ExcelValidationError(
                        row_idx, 'CEDULA_DUPLICADA',
                        f'Cédula ya existe en BD: {cedula}',
                        severity='warning'
                    ))
                cleaned_data['cedula'] = cedula
            
            # 2. NOMBRE
            nombre_col = found_columns.get('nombre')
            nombre = str(row_data.get(nombre_col, '')).strip() if nombre_col else ''
            
            if not nombre or len(nombre) < 3:
                errors.append(ExcelValidationError(
                    row_idx, 'NOMBRE_INVALIDO',
                    'Nombre vacío o muy corto'
                ))
            else:
                cleaned_data['nombre'] = nombre
            
            # 3. TELÉFONO
            telefono_col = found_columns.get('telefono')
            telefono = str(row_data.get(telefono_col, '')).strip() if telefono_col else ''
            
            if telefono:
                # Limpiar formato
                telefono = re.sub(r'[^\d+]', '', telefono)
                if len(telefono) < 7:
                    errors.append(ExcelValidationError(
                        row_idx, 'TELEFONO_INVALIDO',
                        f'Teléfono inválido: {telefono}'
                    ))
                else:
                    cleaned_data['telefono'] = telefono
            else:
                cleaned_data['telefono'] = ''
            
            # 4. EMAIL
            email_col = found_columns.get('email')
            email = str(row_data.get(email_col, '')).strip() if email_col else ''
            
            if email:
                if not ValidacionesService.validar_email(email):
                    errors.append(ExcelValidationError(
                        row_idx, 'EMAIL_INVALIDO',
                        f'Email no válido: {email}'
                    ))
                else:
                    # Verificar duplicados
                    if Cliente.objects.filter(email=email).exists():
                        errors.append(ExcelValidationError(
                            row_idx, 'EMAIL_DUPLICADO',
                            f'Email ya existe en BD: {email}',
                            severity='warning'
                        ))
                    cleaned_data['email'] = email.lower()
            else:
                cleaned_data['email'] = ''
            
            # 5. MONTO
            monto_col = found_columns.get('monto')
            try:
                monto = Decimal(str(row_data.get(monto_col, 0)))
                if monto <= 0:
                    errors.append(ExcelValidationError(
                        row_idx, 'MONTO_INVALIDO',
                        f'Monto debe ser positivo: {monto}'
                    ))
                else:
                    cleaned_data['monto'] = monto
            except:
                errors.append(ExcelValidationError(
                    row_idx, 'MONTO_INVALIDO',
                    f'Monto no es un número válido'
                ))
            
            # 6. INTERÉS
            interes_col = found_columns.get('interes')
            try:
                interes = Decimal(str(row_data.get(interes_col, 0)))
                if interes < 0 or interes > 100:
                    errors.append(ExcelValidationError(
                        row_idx, 'INTERES_INVALIDO',
                        f'Interés debe estar entre 0-100: {interes}'
                    ))
                else:
                    cleaned_data['interes'] = interes
            except:
                errors.append(ExcelValidationError(
                    row_idx, 'INTERES_INVALIDO',
                    f'Interés no es un número válido'
                ))
            
            # 7. CUOTAS
            cuotas_col = found_columns.get('cuotas')
            try:
                cuotas = int(float(row_data.get(cuotas_col, 1)))
                if cuotas < 1 or cuotas > 60:
                    errors.append(ExcelValidationError(
                        row_idx, 'CUOTAS_INVALIDAS',
                        f'Cuotas debe estar entre 1-60: {cuotas}'
                    ))
                else:
                    cleaned_data['cuotas'] = cuotas
            except:
                errors.append(ExcelValidationError(
                    row_idx, 'CUOTAS_INVALIDAS',
                    f'Cuotas no es un número válido'
                ))
        
        except Exception as e:
            errors.append(ExcelValidationError(
                row_idx, 'ERROR_GENERAL',
                f'Error procesando fila: {str(e)}'
            ))
        
        # Determinar si la fila es válida (sin errores críticos)
        critical_errors = [e for e in errors if e.severity == 'error']
        is_valid = len(critical_errors) == 0
        
        return is_valid, cleaned_data, errors
    
    @classmethod
    def validate_excel_file(cls, file_obj):
        """
        Valida un archivo Excel completo
        
        Args:
            file_obj: Archivo Excel cargado
        
        Returns:
            ExcelValidationResult: Resultado de la validación
        """
        result = ExcelValidationResult()
        
        try:
            # Cargar el archivo
            df = pd.read_excel(file_obj, sheet_name=0)
        except Exception as e:
            error = ExcelValidationError(0, 'ERROR_LECTURA', f'Error leyendo Excel: {str(e)}')
            result.add_error(error)
            return result
        
        # Validar estructura
        is_valid, message, found_columns = cls.validate_excel_structure(df)
        if not is_valid:
            error = ExcelValidationError(0, 'ESTRUCTURA_INVALIDA', message)
            result.add_error(error)
            return result
        
        # Validar cada fila
        for idx, (row_idx, row_data) in enumerate(df.iterrows(), 1):
            is_valid, cleaned_data, errors = cls.validate_row(
                row_idx + 1, row_data, found_columns  # +1 porque Excel es 1-indexed
            )
            
            # Procesar errores y warnings
            for error in errors:
                if error.severity == 'error':
                    result.add_error(error)
                else:
                    result.add_warning(error)
            
            if is_valid:
                result.add_valid_row(idx, cleaned_data)
        
        return result
