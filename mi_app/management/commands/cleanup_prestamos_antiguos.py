"""
Management Command: cleanup_prestamos_antiguos
===============================================
Limpia automáticamente préstamos completados hace más de X días
Conserva los agregados de scoring en ClienteScoring y Cliente
Permite auditoría completa de comportamiento histórico
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date
from mi_app.models import Cliente, Prestamo, Pago, ClienteScoring


class Command(BaseCommand):
    help = 'Limpia préstamos completados antiguos preservando scoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=90,
            help='Número de días para considerar un préstamo como "antiguo" (default: 90)'
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Flag para ejecutar la limpieza (sin esto, solo hace preview)'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        execute = options['execute']
        
        fecha_limite = timezone.now() - timedelta(days=dias)
        
        self.stdout.write(self.style.WARNING(f"\n{'='*70}"))
        self.stdout.write(self.style.WARNING("LIMPIEZA DE PRÉSTAMOS ANTIGUOS"))
        self.stdout.write(self.style.WARNING(f"{'='*70}"))
        self.stdout.write(f"Fecha límite: {fecha_limite.strftime('%d/%m/%Y')}")
        self.stdout.write(f"(Eliminar préstamos completados antes de esta fecha)")
        self.stdout.write(f"Modo: {'EJECUCIÓN' if execute else 'PREVIEW (DRY RUN)'}\n")
        
        # Buscar préstamos completados antiguos
        prestamos_antiguos = Prestamo.objects.filter(
            estado='COMPLETADO',
            fecha_ultima_modificacion__lt=fecha_limite
        ).select_related('cliente')
        
        total_prestamos = prestamos_antiguos.count()
        
        if total_prestamos == 0:
            self.stdout.write(self.style.SUCCESS("✓ No hay préstamos antiguos para limpiar"))
            return
        
        self.stdout.write(f"📊 Préstamos a procesar: {total_prestamos}\n")
        
        # Agrupar por cliente
        clientes_dict = {}
        for prestamo in prestamos_antiguos:
            cliente_id = prestamo.cliente.id
            if cliente_id not in clientes_dict:
                clientes_dict[cliente_id] = []
            clientes_dict[cliente_id].append(prestamo)
        
        # Procesar cada cliente
        total_eliminado = 0
        total_monto = Decimal('0')
        
        for cliente_id, prestamos in clientes_dict.items():
            cliente = Cliente.objects.get(id=cliente_id)
            
            # Calcular agregados antes de eliminar
            cuotas_pagadas_a_tiempo = 0
            cuotas_vencidas = 0
            total_monto_local = Decimal('0')
            total_pagado_local = Decimal('0')
            dias_mora_list = []
            
            for prestamo in prestamos:
                total_monto_local += (prestamo.monto_total or Decimal('0'))
                
                # Contar cuotas
                for cuota in prestamo.cuotas.all():
                    total_pagado_local += (
                        (cuota.monto_pagado_principal or Decimal('0')) +
                        (cuota.monto_pagado_interes or Decimal('0')) +
                        (cuota.monto_pagado_mora or Decimal('0'))
                    )
                    
                    if cuota.estado == 'PAGADA':
                        # Calcular si fue a tiempo
                        pago = Pago.objects.filter(cuota=cuota).order_by('-fecha_pago').first()
                        if pago and cuota.fecha_pago_esperada:
                            dias_diferencia = (pago.fecha_pago.date() - cuota.fecha_pago_esperada).days
                            if dias_diferencia <= 0:
                                cuotas_pagadas_a_tiempo += 1
                            else:
                                cuotas_vencidas += 1
                                dias_mora_list.append(dias_diferencia)
                        elif cuota.fecha_pago_real and cuota.fecha_pago_esperada:
                            dias_diferencia = (cuota.fecha_pago_real - cuota.fecha_pago_esperada).days
                            if dias_diferencia <= 0:
                                cuotas_pagadas_a_tiempo += 1
                            else:
                                cuotas_vencidas += 1
                                dias_mora_list.append(dias_diferencia)
                        else:
                            cuotas_pagadas_a_tiempo += 1
                    elif cuota.estado == 'PENDIENTE':
                        # Cuota vencida
                        if cuota.fecha_pago_esperada:
                            dias_vencida = (date.today() - cuota.fecha_pago_esperada).days
                        else:
                            dias_vencida = 0
                        if dias_vencida > 0:
                            cuotas_vencidas += 1
                            dias_mora_list.append(dias_vencida)
            
            # Calcular métricas
            total_cuotas = cuotas_pagadas_a_tiempo + cuotas_vencidas
            tasa_cumplimiento = (cuotas_pagadas_a_tiempo / total_cuotas * 100) if total_cuotas > 0 else 100.0
            dias_mora_promedio = sum(dias_mora_list) / len(dias_mora_list) if dias_mora_list else 0.0
            
            # Crear registro de scoring
            if execute:
                scoring = ClienteScoring.objects.create(
                    cliente=cliente,
                    total_prestado_acumulado=cliente.total_prestado_historico + total_monto_local,
                    total_pagado_acumulado=cliente.total_pagado_historico + total_pagado_local,
                    saldo_pendiente=(cliente.total_prestado_historico + total_monto_local) - (cliente.total_pagado_historico + total_pagado_local),
                    cuotas_pagadas_a_tiempo=cuotas_pagadas_a_tiempo,
                    cuotas_vencidas=cuotas_vencidas,
                    tasa_cumplimiento=tasa_cumplimiento,
                    dias_mora_promedio=dias_mora_promedio,
                    prestamos_limpiados=len(prestamos),
                    periodo_inicio=min((p.fecha_inicio for p in prestamos), default=None),
                    periodo_fin=max((p.fecha_fin_estimada for p in prestamos), default=None),
                )
                
                # Actualizar agregados en Cliente
                cliente.total_prestado_historico += total_monto_local
                cliente.total_pagado_historico += total_pagado_local
                cliente.tasa_cumplimiento = tasa_cumplimiento
                cliente.dias_mora_promedio = dias_mora_promedio
                cliente.ultima_evaluacion = timezone.now()
                cliente.save()
                
                # Eliminar préstamos y sus relaciones
                for prestamo in prestamos:
                    prestamo.cuotas.all().delete()
                    prestamo.delete()
                
                total_eliminado += len(prestamos)
                total_monto += total_monto_local
                
                self.stdout.write(self.style.SUCCESS(f"  ✓ {cliente.nombre}: {len(prestamos)} préstamo(s)"))
            else:
                self.stdout.write(f"  → {cliente.nombre}: {len(prestamos)} préstamo(s)")
        
        # Resumen final
        self.stdout.write(self.style.WARNING(f"\n{'='*70}"))
        self.stdout.write(f"📈 Resumen:")
        self.stdout.write(f"   Préstamos procesados: {total_eliminado}")
        self.stdout.write(f"   Monto total: ${total_monto:,.2f}")
        self.stdout.write(f"   Clientes afectados: {len(clientes_dict)}")
        
        if execute:
            self.stdout.write(self.style.SUCCESS(f"\n✅ ¡LIMPIEZA COMPLETADA! Los datos históricos fueron preservados en ClienteScoring"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚙️  Modo PREVIEW (DRY RUN)"))
            self.stdout.write(self.style.WARNING(f"Ejecuta con --execute para aplicar los cambios"))
        
        self.stdout.write(self.style.WARNING(f"{'='*70}\n"))
