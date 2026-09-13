"""
PAGO SERVICE
===============================================================================
Propósito: Lógica de negocio para operaciones de pagos
Métodos: Registrar, listar, procesar pagos
===============================================================================
"""

from django.db.models import Q, Sum
from mi_app.models import Pago, Cuota
from datetime import datetime


class PagoService:
    """Servicio para operaciones de pagos"""

    @staticmethod
    def registrar_pago(datos):
        """
        Registrar un nuevo pago
        
        Args:
            datos (dict): Diccionario con los datos del pago
            
        Returns:
            Pago: Instancia del pago creado o None
        """
        try:
            pago = Pago.objects.create(**datos)
            
            # Actualizar cuota asociada
            if 'cuota_id' in datos:
                cuota = Cuota.objects.get(id=datos['cuota_id'])
                cuota.estado = 'pagada'
                cuota.fecha_pago = datetime.now().date()
                cuota.save()
            
            return pago
        except Exception as e:
            print(f"Error registrando pago: {str(e)}")
            return None

    @staticmethod
    def listar_pagos_cliente(id_cliente):
        """
        Listar todos los pagos de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            QuerySet: Pagos del cliente ordenados por fecha
        """
        return Pago.objects.filter(
            cuota__prestamo__cliente_id=id_cliente
        ).order_by('-fecha_pago')

    @staticmethod
    def listar_pagos_prestamo(id_prestamo):
        """
        Listar todos los pagos de un préstamo
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            QuerySet: Pagos del préstamo
        """
        return Pago.objects.filter(
            cuota__prestamo_id=id_prestamo
        ).order_by('-fecha_pago')

    @staticmethod
    def obtener_pago(id_pago):
        """
        Obtener un pago por ID
        
        Args:
            id_pago (int): ID del pago
            
        Returns:
            Pago: Instancia del pago o None
        """
        try:
            return Pago.objects.get(id=id_pago)
        except Pago.DoesNotExist:
            return None

    @staticmethod
    def obtener_total_pagado_cliente(id_cliente):
        """
        Obtener total pagado por un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            float: Total pagado
        """
        total = Pago.objects.filter(
            cuota__prestamo__cliente_id=id_cliente
        ).aggregate(total=Sum('monto'))['total']
        return total or 0

    @staticmethod
    def obtener_total_pagado_prestamo(id_prestamo):
        """
        Obtener total pagado de un préstamo
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            float: Total pagado
        """
        total = Pago.objects.filter(
            cuota__prestamo_id=id_prestamo
        ).aggregate(total=Sum('monto'))['total']
        return total or 0

    @staticmethod
    def procesar_pago(id_cuota, monto, referencia, metodo='transferencia'):
        """
        Procesar un pago con validaciones
        
        Args:
            id_cuota (int): ID de la cuota
            monto (float): Monto a pagar
            referencia (str): Referencia del pago
            metodo (str): Método de pago
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            cuota = Cuota.objects.get(id=id_cuota)
            
            # Validar monto
            if monto <= 0:
                return {'exitoso': False, 'error': 'Monto debe ser mayor a 0'}
            
            if monto > cuota.monto:
                return {'exitoso': False, 'error': 'Monto excede el saldo de la cuota'}
            
            # Crear registro de pago
            pago = Pago.objects.create(
                cuota=cuota,
                monto=monto,
                referencia_pago=referencia,
                metodo_pago=metodo,
                fecha_pago=datetime.now().date()
            )
            
            # Actualizar cuota
            cuota.monto_pagado = monto
            cuota.estado = 'pagada' if monto >= cuota.monto else 'parcial'
            cuota.fecha_pago = datetime.now().date()
            cuota.save()
            
            return {
                'exitoso': True,
                'pago_id': pago.id,
                'mensaje': 'Pago procesado exitosamente'
            }
        
        except Cuota.DoesNotExist:
            return {'exitoso': False, 'error': 'Cuota no encontrada'}
        except Exception as e:
            return {'exitoso': False, 'error': str(e)}

    @staticmethod
    def obtener_resumen_pagos(id_cliente):
        """
        Obtener resumen de pagos de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            dict: Resumen de pagos
        """
        pagos = Pago.objects.filter(
            cuota__prestamo__cliente_id=id_cliente
        )
        
        total_pagado = pagos.aggregate(total=Sum('monto'))['total'] or 0
        cantidad_pagos = pagos.count()
        
        return {
            'cliente_id': id_cliente,
            'total_pagado': total_pagado,
            'cantidad_pagos': cantidad_pagos,
            'promedio_pago': round(total_pagado / cantidad_pagos, 2) if cantidad_pagos > 0 else 0,
            'ultimo_pago': pagos.order_by('-fecha_pago').first(),
        }

    @staticmethod
    def buscar_pago(termino):
        """
        Buscar pago por término
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            QuerySet: Pagos que coinciden
        """
        return Pago.objects.filter(
            Q(referencia_pago__icontains=termino) |
            Q(cuota__prestamo__cliente__nombre__icontains=termino)
        )

    @staticmethod
    def anular_pago(id_pago):
        """
        Anular un pago (reversar)
        
        Args:
            id_pago (int): ID del pago
            
        Returns:
            bool: True si se anula
        """
        try:
            pago = Pago.objects.get(id=id_pago)
            cuota = pago.cuota
            
            # Revertir estado de cuota
            cuota.estado = 'pendiente'
            cuota.monto_pagado = 0
            cuota.fecha_pago = None
            cuota.save()
            
            # Eliminar pago
            pago.delete()
            return True
        except Pago.DoesNotExist:
            return False
