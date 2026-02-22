"""
PRESTAMO SERVICE
===============================================================================
Propósito: Lógica de negocio para operaciones de préstamos
Métodos: Crear, actualizar, listar, calcular cuotas
===============================================================================
"""

from django.db.models import Q, Sum
from mi_app.models import Prestamo, Cliente
from datetime import datetime, timedelta


class PrestamoService:
    """Servicio para operaciones de préstamos"""

    @staticmethod
    def crear_prestamo(datos):
        """
        Crear un nuevo préstamo
        
        Args:
            datos (dict): Diccionario con los datos del préstamo
            
        Returns:
            Prestamo: Instancia del préstamo creado o None
        """
        try:
            prestamo = Prestamo.objects.create(**datos)
            return prestamo
        except Exception as e:
            print(f"Error creando préstamo: {str(e)}")
            return None

    @staticmethod
    def listar_prestamos_cliente(id_cliente):
        """
        Listar todos los préstamos de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            QuerySet: Préstamos del cliente
        """
        return Prestamo.objects.filter(cliente_id=id_cliente).order_by('-fecha_creacion')

    @staticmethod
    def obtener_prestamo(id_prestamo):
        """
        Obtener un préstamo por ID
        
        Args:
            id_prestamo (int): ID del préstamo
            
        Returns:
            Prestamo: Instancia del préstamo o None
        """
        try:
            return Prestamo.objects.get(id=id_prestamo)
        except Prestamo.DoesNotExist:
            return None

    @staticmethod
    def calcular_interes(monto, tasa_anual, meses):
        """
        Calcular interés simple
        
        Args:
            monto (float): Monto del préstamo
            tasa_anual (float): Tasa anual en porcentaje
            meses (int): Número de meses
            
        Returns:
            float: Monto de interés
        """
        tasa_mensual = tasa_anual / 12 / 100
        interes = monto * tasa_mensual * meses
        return round(interes, 2)

    @staticmethod
    def calcular_cuota_mensual(monto_principal, interes_total, meses):
        """
        Calcular cuota mensual
        
        Args:
            monto_principal (float): Monto del préstamo
            interes_total (float): Interés total
            meses (int): Número de meses
            
        Returns:
            float: Cuota mensual
        """
        total = monto_principal + interes_total
        cuota = total / meses
        return round(cuota, 2)

    @staticmethod
    def listar_prestamos_activos():
        """
        Listar todos los préstamos activos
        
        Returns:
            QuerySet: Préstamos activos
        """
        return Prestamo.objects.filter(activo=True).order_by('-fecha_creacion')

    @staticmethod
    def obtener_total_prestado():
        """
        Obtener total prestado
        
        Returns:
            float: Total de dinero prestado
        """
        total = Prestamo.objects.aggregate(total=Sum('monto'))['total']
        return total or 0

    @staticmethod
    def buscar_prestamo(termino):
        """
        Buscar préstamo por término
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            QuerySet: Préstamos que coinciden
        """
        return Prestamo.objects.filter(
            Q(cliente__nombre__icontains=termino) |
            Q(cliente__cedula__icontains=termino) |
            Q(descripcion__icontains=termino)
        )

    @staticmethod
    def actualizar_prestamo(id_prestamo, datos):
        """
        Actualizar un préstamo
        
        Args:
            id_prestamo (int): ID del préstamo
            datos (dict): Datos a actualizar
            
        Returns:
            bool: True si se actualiza
        """
        try:
            prestamo = Prestamo.objects.get(id=id_prestamo)
            for clave, valor in datos.items():
                setattr(prestamo, clave, valor)
            prestamo.save()
            return True
        except Prestamo.DoesNotExist:
            return False

    @staticmethod
    def obtener_proximos_vencimientos(dias=7):
        """
        Obtener préstamos con próximos vencimientos
        
        Args:
            dias (int): Número de días para buscar
            
        Returns:
            QuerySet: Préstamos próximos a vencer
        """
        fecha_limite = datetime.now().date() + timedelta(days=dias)
        return Prestamo.objects.filter(
            fecha_vencimiento__lte=fecha_limite,
            activo=True
        ).order_by('fecha_vencimiento')
