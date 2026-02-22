"""
CUOTA SERVICE
===============================================================================
Propósito: Lógica de negocio para operaciones de cuotas
Métodos: Crear, actualizar, listar, calcular estado de cuotas
===============================================================================
"""

from django.db.models import Q, Sum
from mi_app.models import Cuota, Prestamo
from datetime import datetime


class CuotaService:
    """Servicio para operaciones de cuotas"""

    @staticmethod
    def crear_cuota(datos):
        """
        Crear una nueva cuota
        
        Args:
            datos (dict): Diccionario con los datos de la cuota
            
        Returns:
            Cuota: Instancia de la cuota creada o None
        """
        try:
            cuota = Cuota.objects.create(**datos)
            return cuota
        except Exception as e:
            print(f"Error creando cuota: {str(e)}")
            return None

    @staticmethod
    def listar_cuotas_prestamo(id_prestamo):
        """
        Listar todas las cuotas de un préstamo
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            QuerySet: Cuotas del préstamo ordenadas
        """
        return Cuota.objects.filter(prestamo_id=id_prestamo).order_by('numero_cuota')

    @staticmethod
    def obtener_cuota(id_cuota):
        """
        Obtener una cuota por ID
        
        Args:
            id_cuota (int): ID de la cuota
            
        Returns:
            Cuota: Instancia de la cuota o None
        """
        try:
            return Cuota.objects.get(id=id_cuota)
        except Cuota.DoesNotExist:
            return None

    @staticmethod
    def obtener_cuotas_vencidas():
        """
        Obtener todas las cuotas vencidas no pagadas
        
        Returns:
            QuerySet: Cuotas vencidas
        """
        return Cuota.objects.filter(
            fecha_vencimiento__lt=datetime.now().date(),
            estado='pendiente'
        ).order_by('fecha_vencimiento')

    @staticmethod
    def obtener_cuotas_proximas(dias=7):
        """
        Obtener cuotas próximas a vencer
        
        Args:
            dias (int): Número de días
            
        Returns:
            QuerySet: Cuotas próximas a vencer
        """
        from datetime import timedelta
        fecha_limite = datetime.now().date() + timedelta(days=dias)
        
        return Cuota.objects.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=datetime.now().date(),
            estado='pendiente'
        ).order_by('fecha_vencimiento')

    @staticmethod
    def marcar_como_pagada(id_cuota, monto_pagado=None):
        """
        Marcar una cuota como pagada
        
        Args:
            id_cuota (int): ID de la cuota
            monto_pagado (float): Monto pagado (opcional)
            
        Returns:
            bool: True si se actualiza
        """
        try:
            cuota = Cuota.objects.get(id=id_cuota)
            cuota.estado = 'pagada'
            cuota.fecha_pago = datetime.now().date()
            if monto_pagado:
                cuota.monto_pagado = monto_pagado
            cuota.save()
            return True
        except Cuota.DoesNotExist:
            return False

    @staticmethod
    def obtener_total_cuotas_pendientes(id_prestamo):
        """
        Obtener total de cuotas pendientes de un préstamo
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            float: Total pendiente
        """
        total = Cuota.objects.filter(
            prestamo_id=id_prestamo,
            estado='pendiente'
        ).aggregate(total=Sum('monto'))['total']
        return total or 0

    @staticmethod
    def obtener_progreso_cuotas(id_prestamo):
        """
        Obtener progreso de pagos de cuotas
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            dict: Información de progreso
        """
        cuotas = Cuota.objects.filter(prestamo_id=id_prestamo)
        total = cuotas.count()
        pagadas = cuotas.filter(estado='pagada').count()
        pendientes = total - pagadas
        
        porcentaje = (pagadas / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'pagadas': pagadas,
            'pendientes': pendientes,
            'porcentaje': round(porcentaje, 2)
        }

    @staticmethod
    def actualizar_cuota(id_cuota, datos):
        """
        Actualizar una cuota
        
        Args:
            id_cuota (int): ID de la cuota
            datos (dict): Datos a actualizar
            
        Returns:
            bool: True si se actualiza
        """
        try:
            cuota = Cuota.objects.get(id=id_cuota)
            for clave, valor in datos.items():
                setattr(cuota, clave, valor)
            cuota.save()
            return True
        except Cuota.DoesNotExist:
            return False

    @staticmethod
    def generar_reporte_cuotas(id_prestamo):
        """
        Generar reporte de cuotas
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            dict: Reporte completo
        """
        cuotas = Cuota.objects.filter(prestamo_id=id_prestamo).order_by('numero_cuota')
        
        return {
            'prestamo_id': id_prestamo,
            'total_cuotas': cuotas.count(),
            'total_monto': cuotas.aggregate(Sum('monto'))['monto__sum'] or 0,
            'total_pagado': cuotas.filter(estado='pagada').aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0,
            'total_pendiente': CuotaService.obtener_total_cuotas_pendientes(id_prestamo),
            'cuotas': list(cuotas.values()),
        }
