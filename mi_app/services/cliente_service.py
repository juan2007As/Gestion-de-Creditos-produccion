"""
CLIENTE SERVICE
===============================================================================
Propósito: Lógica de negocio para operaciones de clientes
Métodos: Crear, actualizar, obtener, listar, validar clientes
===============================================================================
"""

from django.db.models import Q
from mi_app.models import Cliente


class ClienteService:
    """Servicio para operaciones de clientes"""

    @staticmethod
    def crear_cliente(datos):
        """
        Crear un nuevo cliente
        
        Args:
            datos (dict): Diccionario con los datos del cliente
            
        Returns:
            Cliente: Instancia del cliente creado o None si hay error
        """
        try:
            cliente = Cliente.objects.create(**datos)
            return cliente
        except Exception as e:
            print(f"Error creando cliente: {str(e)}")
            return None

    @staticmethod
    def actualizar_cliente(id_cliente, datos):
        """
        Actualizar un cliente existente
        
        Args:
            id_cliente (int): ID del cliente
            datos (dict): Diccionario con los datos a actualizar
            
        Returns:
            bool: True si se actualiza, False si hay error
        """
        try:
            cliente = Cliente.objects.get(id=id_cliente)
            for clave, valor in datos.items():
                setattr(cliente, clave, valor)
            cliente.save()
            return True
        except Cliente.DoesNotExist:
            print(f"Cliente con ID {id_cliente} no existe")
            return False
        except Exception as e:
            print(f"Error actualizando cliente: {str(e)}")
            return False

    @staticmethod
    def obtener_cliente(id_cliente):
        """
        Obtener un cliente por ID
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            Cliente: Instancia del cliente o None
        """
        try:
            return Cliente.objects.get(id=id_cliente)
        except Cliente.DoesNotExist:
            return None

    @staticmethod
    def listar_clientes(filtro=None, orden='-id', pagina=1, items_por_pagina=10):
        """
        Listar clientes con opciones de filtro y paginación
        
        Args:
            filtro (dict): Diccionario con criterios de filtro
            orden (str): Campo para ordenar
            pagina (int): Número de página
            items_por_pagina (int): Items por página
            
        Returns:
            QuerySet: Conjunto de clientes
        """
        queryset = Cliente.objects.all()

        if filtro:
            # Filtros por búsqueda
            if 'busqueda' in filtro:
                termino = filtro['busqueda']
                queryset = queryset.filter(
                    Q(nombre__icontains=termino) |
                    Q(cedula__icontains=termino) |
                    Q(email__icontains=termino) |
                    Q(telefono__icontains=termino)
                )

            # Otros filtros
            if 'estado' in filtro:
                queryset = queryset.filter(activo=filtro['estado'])

        # Ordenar
        queryset = queryset.order_by(orden)

        # Paginar
        inicio = (pagina - 1) * items_por_pagina
        fin = inicio + items_por_pagina
        return queryset[inicio:fin]

    @staticmethod
    def buscar_cliente(termino):
        """
        Buscar cliente por término
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            QuerySet: Clientes que coinciden
        """
        return Cliente.objects.filter(
            Q(nombre__icontains=termino) |
            Q(cedula__icontains=termino) |
            Q(email__icontains=termino)
        )

    @staticmethod
    def eliminar_cliente(id_cliente):
        """
        Eliminar un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            bool: True si se elimina, False si hay error
        """
        try:
            cliente = Cliente.objects.get(id=id_cliente)
            cliente.delete()
            return True
        except Cliente.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error eliminando cliente: {str(e)}")
            return False

    @staticmethod
    def contar_clientes():
        """
        Contar total de clientes
        
        Returns:
            int: Total de clientes
        """
        return Cliente.objects.count()

    @staticmethod
    def obtener_cliente_por_cedula(cedula):
        """
        Obtener cliente por cédula
        
        Args:
            cedula (str): Cédula del cliente
            
        Returns:
            Cliente: Cliente encontrado o None
        """
        try:
            return Cliente.objects.get(cedula=cedula)
        except Cliente.DoesNotExist:
            return None
