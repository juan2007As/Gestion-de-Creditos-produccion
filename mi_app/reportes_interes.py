"""
Módulo auxiliar para el cálculo de reportes de interés mensual.
Separa la lógica de negocio de la view para mayor claridad.
"""

from decimal import Decimal
from datetime import date, timedelta, datetime
from django.db.models import Sum, Q
from .models import Prestamo, PrestamoRapido, Pago, Cuota, CuotaRapida, PagoPrestamoRapido


class ReporteInteresMensual:
    """Clase para calcular reportes de interés mensual"""
    
    def __init__(self):
        self.hoy = date.today()
    
    def get_fecha_inicio_periodo(self, meses=1):
        """Calcula la fecha de inicio hace X meses"""
        # Ir al primer día del mes hace X meses
        if meses == 1:
            # Mes actual desde el día 1
            return date(self.hoy.year, self.hoy.month, 1)
        else:
            # Hace X meses
            mes = self.hoy.month - meses
            año = self.hoy.year
            
            while mes < 1:
                mes += 12
                año -= 1
            
            return date(año, mes, 1)
    
    def calcular_interes_prestamo_normal(self, prestamo):
        """Calcula el interés total de un préstamo normal"""
        interes_total = Decimal('0')
        
        # Sumar interés de todas las cuotas pagadas
        cuotas_pagadas = prestamo.cuotas.filter(pagado=True)
        for cuota in cuotas_pagadas:
            if cuota.interes_normal:
                interes_total += cuota.interes_normal
        
        return interes_total
    
    def calcular_interes_prestamo_rapido(self, prestamo):
        """Calcula el interés total de un préstamo rápido"""
        interes_total = Decimal('0')
        
        # Lógica 1: Si tiene CuotaRapida (con cuotas)
        cuotas_pagadas = CuotaRapida.objects.filter(
            prestamo_rapido=prestamo,
            pagado=True
        )
        for cuota in cuotas_pagadas:
            if cuota.interes_normal:
                interes_total += cuota.interes_normal
        
        # Lógica 2: Si fue pagado directamente (sin cuotas)
        if interes_total == 0:
            # Calcular interés como: monto * porcentaje / 100
            if prestamo.interes_porcentaje:
                interes_calculado = prestamo.monto * (prestamo.interes_porcentaje / 100)
                
                # Contar solo si ya fue pagado
                pagos = PagoPrestamoRapido.objects.filter(prestamo_rapido=prestamo)
                if pagos.exists():
                    interes_total = Decimal(str(interes_calculado))
        
        return interes_total
    
    def get_interes_por_periodo(self, dias=30):
        """Calcula interés recaudado en los últimos X días"""
        fecha_inicio = self.hoy - timedelta(days=dias)
        
        interes_normal = Decimal('0')
        interes_rapido = Decimal('0')
        
        # Préstamos normales: sumar cuotas pagadas en el período
        cuotas_pagadas = Cuota.objects.filter(
            fecha_pago_real__gte=fecha_inicio,
            fecha_pago_real__lte=self.hoy,
            pagado=True
        )
        interes_normal = cuotas_pagadas.aggregate(
            total=Sum('interes_normal')
        )['total'] or Decimal('0')
        
        # Préstamos rápidos: sumar cuotas pagadas en el período
        cuotas_rapidas_pagadas = CuotaRapida.objects.filter(
            fecha_pago_real__gte=fecha_inicio,
            fecha_pago_real__lte=self.hoy,
            pagado=True
        )
        interes_rapido = cuotas_rapidas_pagadas.aggregate(
            total=Sum('interes_normal')
        )['total'] or Decimal('0')
        
        return {
            'normal': interes_normal,
            'rapido': interes_rapido,
            'total': interes_normal + interes_rapido,
        }
    
    def get_datos_por_mes(self, meses_atras):
        """Obtiene datos mes a mes para los últimos X meses"""
        data = []
        
        for i in range(meses_atras, 0, -1):
            # Calcular rango de fechas para este mes
            fecha_fin = self.hoy - timedelta(days=(i-1)*30)
            fecha_inicio = self.hoy - timedelta(days=i*30)
            
            # Asegurar que sea el primer día del mes
            fecha_inicio = date(fecha_inicio.year, fecha_inicio.month, 1)
            
            # Si es el mes actual, fecha_fin es hoy
            if i == 1:
                fecha_fin = self.hoy
            else:
                # Último día del mes
                if fecha_fin.month == 12:
                    fecha_fin = date(fecha_fin.year + 1, 1, 1) - timedelta(days=1)
                else:
                    fecha_fin = date(fecha_fin.year, fecha_fin.month + 1, 1) - timedelta(days=1)
            
            # Calcular interés en este período
            interes_normal = Decimal('0')
            interes_rapido = Decimal('0')
            
            # Cuotas normales pagadas en este mes
            cuotas_normal = Cuota.objects.filter(
                fecha_pago_real__gte=fecha_inicio,
                fecha_pago_real__lte=fecha_fin,
                pagado=True
            )
            interes_normal = cuotas_normal.aggregate(
                total=Sum('interes_normal')
            )['total'] or Decimal('0')
            
            # Cuotas rápidas pagadas en este mes
            cuotas_rapido = CuotaRapida.objects.filter(
                fecha_pago_real__gte=fecha_inicio,
                fecha_pago_real__lte=fecha_fin,
                pagado=True
            )
            interes_rapido = cuotas_rapido.aggregate(
                total=Sum('interes_normal')
            )['total'] or Decimal('0')
            
            nombre_mes = fecha_inicio.strftime('%B %Y')
            
            data.append({
                'mes': nombre_mes,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'interes_normal': float(interes_normal),
                'interes_rapido': float(interes_rapido),
                'interes_total': float(interes_normal + interes_rapido),
                'cantidad_cuotas_normal': cuotas_normal.count(),
                'cantidad_cuotas_rapido': cuotas_rapido.count(),
            })
        
        return data
    
    def calcular_proyeccion_mes_actual(self):
        """Calcula proyección de interés para fin de mes"""
        dias_transcurridos = self.hoy.day
        dias_mes = (date(self.hoy.year, self.hoy.month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        dias_totales = dias_mes.day
        
        # Interés recaudado hasta hoy
        interes_hoy = self.get_interes_por_periodo(dias_transcurridos)
        
        # Proyectar para fin de mes (regla de 3)
        if dias_transcurridos > 0:
            factor = Decimal(str(dias_totales)) / Decimal(str(dias_transcurridos))
            interes_proyectado_normal = Decimal(str(interes_hoy['normal'])) * factor
            interes_proyectado_rapido = Decimal(str(interes_hoy['rapido'])) * factor
            interes_proyectado_total = interes_proyectado_normal + interes_proyectado_rapido
        else:
            interes_proyectado_normal = Decimal('0')
            interes_proyectado_rapido = Decimal('0')
            interes_proyectado_total = Decimal('0')
        
        return {
            'interes_actual_normal': float(interes_hoy['normal']),
            'interes_actual_rapido': float(interes_hoy['rapido']),
            'interes_actual_total': float(interes_hoy['total']),
            'interes_proyectado_normal': float(interes_proyectado_normal),
            'interes_proyectado_rapido': float(interes_proyectado_rapido),
            'interes_proyectado_total': float(interes_proyectado_total),
            'dias_transcurridos': dias_transcurridos,
            'dias_totales': dias_totales,
        }
    
    def get_comparativa_mes_anterior(self):
        """Compara el mes actual con el mes anterior"""
        # Mes actual
        datos_mes_actual = self.get_datos_por_mes(1)
        mes_actual = datos_mes_actual[0] if datos_mes_actual else None
        
        # Mes anterior
        datos_mes_anterior = self.get_datos_por_mes(2)
        mes_anterior = datos_mes_anterior[0] if datos_mes_anterior and len(datos_mes_anterior) > 0 else None
        
        if mes_anterior:
            variacion = mes_actual['interes_total'] - mes_anterior['interes_total']
            variacion_pct = (variacion / mes_anterior['interes_total'] * 100) if mes_anterior['interes_total'] > 0 else 0
        else:
            variacion = 0
            variacion_pct = 0
        
        return {
            'mes_actual': mes_actual,
            'mes_anterior': mes_anterior,
            'variacion': float(variacion),
            'variacion_pct': float(variacion_pct),
            'es_positivo': variacion >= 0,
        }
    
    def get_resumen_general(self):
        """Obtiene un resumen general de los períodos solicitados"""
        datos_1mes = self.get_datos_por_mes(1)
        datos_3meses = self.get_datos_por_mes(3)
        datos_12meses = self.get_datos_por_mes(12)
        
        # Totales por período
        interes_1mes = sum([d['interes_total'] for d in datos_1mes])
        interes_3meses = sum([d['interes_total'] for d in datos_3meses])
        interes_12meses = sum([d['interes_total'] for d in datos_12meses])
        
        # Desglose por tipo
        normal_1mes = sum([d['interes_normal'] for d in datos_1mes])
        rapido_1mes = sum([d['interes_rapido'] for d in datos_1mes])
        
        normal_3meses = sum([d['interes_normal'] for d in datos_3meses])
        rapido_3meses = sum([d['interes_rapido'] for d in datos_3meses])
        
        normal_12meses = sum([d['interes_normal'] for d in datos_12meses])
        rapido_12meses = sum([d['interes_rapido'] for d in datos_12meses])
        
        return {
            'periodo_1_mes': {
                'total': interes_1mes,
                'normal': normal_1mes,
                'rapido': rapido_1mes,
                'datos': datos_1mes,
            },
            'periodo_3_meses': {
                'total': interes_3meses,
                'normal': normal_3meses,
                'rapido': rapido_3meses,
                'datos': datos_3meses,
            },
            'periodo_12_meses': {
                'total': interes_12meses,
                'normal': normal_12meses,
                'rapido': rapido_12meses,
                'datos': datos_12meses,
            },
            'promedio_mensual': interes_12meses / 12 if interes_12meses > 0 else 0,
        }
