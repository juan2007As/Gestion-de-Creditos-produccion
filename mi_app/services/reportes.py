"""
REPORTES SERVICE
===============================================================================
Propósito: Generar reportes y estadísticas
Métodos: Reportes de clientes, préstamos, pagos, etc.
===============================================================================
"""

from django.db.models import Sum, Count, Avg
from mi_app.models import Cliente, Prestamo, Cuota, Pago
from datetime import datetime, timedelta


class ReportesService:
    """Servicio para generar reportes"""

    @staticmethod
    def reporte_general():
        """
        Generar reporte general del sistema
        
        Returns:
            dict: Estadísticas generales
        """
        total_clientes = Cliente.objects.count()
        total_prestamos = Prestamo.objects.count()
        total_monto_prestado = Prestamo.objects.aggregate(total=Sum('monto'))['total'] or 0
        total_cuotas = Cuota.objects.count()
        cuotas_pagadas = Cuota.objects.filter(estado='pagada').count()
        total_pagado = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0
        
        return {
            'fecha_reporte': datetime.now(),
            'total_clientes': total_clientes,
            'total_prestamos': total_prestamos,
            'total_monto_prestado': total_monto_prestado,
            'total_cuotas': total_cuotas,
            'cuotas_pagadas': cuotas_pagadas,
            'cuotas_pendientes': total_cuotas - cuotas_pagadas,
            'total_pagado': total_pagado,
            'total_pendiente': total_monto_prestado - total_pagado,
            'porcentaje_pago': round((total_pagado / total_monto_prestado * 100), 2) if total_monto_prestado > 0 else 0,
        }

    @staticmethod
    def reporte_clientes_por_mes(mes, año):
        """
        Reporte de clientes registrados en un mes
        
        Args:
            mes (int): Mes (1-12)
            año (int): Año
            
        Returns:
            dict: Reporte de clientes del mes
        """
        clientes = Cliente.objects.filter(
            fecha_creacion__month=mes,
            fecha_creacion__year=año
        )
        
        return {
            'mes': mes,
            'año': año,
            'total_clientes': clientes.count(),
            'clientes': list(clientes.values('id', 'nombre', 'cedula', 'email', 'fecha_creacion')),
        }

    @staticmethod
    def reporte_prestamos_por_estado():
        """
        Reporte de préstamos por estado
        
        Returns:
            dict: Préstamos agrupados por estado
        """
        activos = Prestamo.objects.filter(activo=True).count()
        inactivos = Prestamo.objects.filter(activo=False).count()
        
        return {
            'total': activos + inactivos,
            'activos': activos,
            'inactivos': inactivos,
            'monto_activos': Prestamo.objects.filter(activo=True).aggregate(Sum('monto'))['monto__sum'] or 0,
            'monto_inactivos': Prestamo.objects.filter(activo=False).aggregate(Sum('monto'))['monto__sum'] or 0,
        }

    @staticmethod
    def reporte_pagos_por_mes(mes, año):
        """
        Reporte de pagos en un mes específico
        
        Args:
            mes (int): Mes (1-12)
            año (int): Año
            
        Returns:
            dict: Reporte de pagos del mes
        """
        pagos = Pago.objects.filter(
            fecha_pago__month=mes,
            fecha_pago__year=año
        )
        
        total = pagos.aggregate(Sum('monto'))['monto__sum'] or 0
        cantidad = pagos.count()
        
        return {
            'mes': mes,
            'año': año,
            'total_pagos': total,
            'cantidad_transacciones': cantidad,
            'promedio_pago': round(total / cantidad, 2) if cantidad > 0 else 0,
            'pagos': list(pagos.values()),
        }

    @staticmethod
    def reporte_cartera_vencida():
        """
        Reporte de cartera vencida
        
        Returns:
            dict: Cuotas vencidas y su información
        """
        cuotas_vencidas = Cuota.objects.filter(
            fecha_vencimiento__lt=datetime.now().date(),
            estado='pendiente'
        )
        
        total_vencido = cuotas_vencidas.aggregate(Sum('monto'))['monto__sum'] or 0
        
        return {
            'fecha_reporte': datetime.now(),
            'total_cuotas_vencidas': cuotas_vencidas.count(),
            'total_monto_vencido': total_vencido,
            'cuotas': list(cuotas_vencidas.values()),
        }

    @staticmethod
    def reporte_cliente_detallado(id_cliente):
        """
        Reporte detallado de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            dict: Información completa del cliente
        """
        try:
            cliente = Cliente.objects.get(id=id_cliente)
            prestamos = Prestamo.objects.filter(cliente=cliente)
            total_prestado = prestamos.aggregate(Sum('monto'))['monto__sum'] or 0
            total_pagado = Pago.objects.filter(cuota__prestamo__cliente=cliente).aggregate(Sum('monto'))['monto__sum'] or 0
            
            return {
                'cliente': {
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'cedula': cliente.cedula,
                    'email': cliente.email,
                    'telefono': cliente.telefono,
                },
                'total_prestamos': prestamos.count(),
                'total_prestado': total_prestado,
                'total_pagado': total_pagado,
                'saldo_pendiente': total_prestado - total_pagado,
                'porcentaje_pago': round((total_pagado / total_prestado * 100), 2) if total_prestado > 0 else 0,
            }
        except Cliente.DoesNotExist:
            return None

    @staticmethod
    def reporte_tops():
        """
        Reporte de tops (mejores clientes, mayores préstamos, etc.)
        
        Returns:
            dict: Información de tops
        """
        # Top clientes por monto prestado
        top_clientes = Cliente.objects.annotate(
            total_prestado=Sum('prestamo__monto')
        ).order_by('-total_prestado')[:5]
        
        # Mayores préstamos
        mayores_prestamos = Prestamo.objects.order_by('-monto')[:5]
        
        return {
            'top_clientes': list(top_clientes.values('id', 'nombre', 'total_prestado')),
            'mayores_prestamos': list(mayores_prestamos.values('id', 'cliente__nombre', 'monto', 'fecha_creacion')),
        }

    @staticmethod
    def reporte_comparativo_periodos(fecha_inicio, fecha_fin):
        """
        Reporte comparativo entre dos períodos
        
        Args:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD
            fecha_fin (str): Fecha fin YYYY-MM-DD
            
        Returns:
            dict: Comparación de períodos
        """
        from datetime import datetime
        f_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        f_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        clientes_nuevo = Cliente.objects.filter(
            fecha_creacion__range=[f_inicio, f_fin]
        ).count()
        
        prestamos_nuevo = Prestamo.objects.filter(
            fecha_creacion__range=[f_inicio, f_fin]
        ).aggregate(cantidad=Count('id'), monto=Sum('monto'))
        
        pagos_nuevo = Pago.objects.filter(
            fecha_pago__range=[f_inicio, f_fin]
        ).aggregate(cantidad=Count('id'), monto=Sum('monto'))
        
        return {
            'periodo': f'Desde {fecha_inicio} hasta {fecha_fin}',
            'clientes_nuevos': clientes_nuevo,
            'prestamos_nuevos': prestamos_nuevo['cantidad'],
            'monto_prestado': prestamos_nuevo['monto'] or 0,
            'pagos_realizados': pagos_nuevo['cantidad'],
            'monto_pagado': pagos_nuevo['monto'] or 0,
        }
