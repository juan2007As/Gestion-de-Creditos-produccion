"""
Management command para reconciliación financiera automática

python manage.py reconciliar_finanzas --fix
"""

from django.core.management.base import BaseCommand
from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Reconciliación automática de inconsistencias financieras - CRÍTICA #3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Aplicar correaciones automáticas (sin --fix solo simula)',
        )

    def handle(self, *args, **options):
        fix_mode = options.get('fix', False)
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("RECONCILIACIÓN FINANCIERA")
        self.stdout.write("="*80)
        
        if not fix_mode:
            self.stdout.write(self.style.WARNING("\n⚠️  MODO SIMULACIÓN (sin correcciones reales)"))
            self.stdout.write("   Para aplicar correcciones: python manage.py reconciliar_finanzas --fix\n")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ MODO CORRECCIÓN (aplicando cambios)\n"))

        correcciones_totales = {
            'total_prestado': 0,
            'mora_actualizada': 0,
            'cuotas_corregidas': 0
        }

        # ============================================================================
        # CORRECCIÓN 1: TOTAL PRESTADO INCONSISTENTE
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("CORRECCIÓN 1: TOTAL PRESTADO INCONSISTENTE")
        self.stdout.write("-"*80 + "\n")

        for cliente in Cliente.objects.all():
            total_real = cliente.total_prestado_real
            total_cache = cliente.total_prestado
            
            diferencia = abs(total_real - total_cache)
            
            if diferencia > Decimal('0.01'):
                self.stdout.write(f"   Cliente: {cliente.nombre} (ID: {cliente.id})")
                self.stdout.write(f"   Cache: ${total_cache} → Real: ${total_real}")
                self.stdout.write(f"   Diferencia: ${diferencia}")
                
                if fix_mode:
                    cliente.total_prestado = total_real
                    cliente.save()
                    self.stdout.write(self.style.SUCCESS(f"   ✅ CORREGIDO"))
                    correcciones_totales['total_prestado'] += 1
                else:
                    self.stdout.write(f"   [Simulación] Se correguería a ${total_real}")
                self.stdout.write("")

        # ============================================================================
        # CORRECCIÓN 2: MORA NO ACTUALIZADA
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("CORRECCIÓN 2: MORA NO ACTUALIZADA EN CUOTAS")
        self.stdout.write("-"*80 + "\n")

        for cuota in Cuota.objects.filter(pagado=False):
            if not cuota.fecha_pago_esperada:
                continue
            
            mora_calculada = cuota.calcular_mora_diaria()
            mora_guardada = cuota.interes_mora_acumulado
            
            diferencia_mora = abs(mora_calculada - mora_guardada)
            
            if diferencia_mora > Decimal('0.01'):
                self.stdout.write(f"   Cuota: {cuota.numero_cuota} - Préstamo {cuota.prestamo.id}")
                self.stdout.write(f"   Cliente: {cuota.prestamo.cliente.nombre}")
                self.stdout.write(f"   Mora Guardada: ${mora_guardada} → Debe ser: ${mora_calculada}")
                self.stdout.write(f"   Diferencia: ${diferencia_mora}")
                
                if fix_mode:
                    cuota.interes_mora_acumulado = mora_calculada
                    cuota.save()
                    self.stdout.write(self.style.SUCCESS(f"   ✅ ACTUALIZADA"))
                    correcciones_totales['mora_actualizada'] += 1
                else:
                    self.stdout.write(f"   [Simulación] Se actualizaría a ${mora_calculada}")
                self.stdout.write("")

        # ============================================================================
        # CORRECCIÓN 3: ACTUALIZAR ESTADO DE CUOTAS
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("CORRECCIÓN 3: ACTUALIZAR ESTADO DE CUOTAS")
        self.stdout.write("-"*80 + "\n")

        for cuota in Cuota.objects.all():
            estado_anterior = cuota.estado
            
            if fix_mode:
                cuota.actualizar_estado()
                correcciones_totales['cuotas_corregidas'] += 1
                
                if estado_anterior != cuota.estado:
                    self.stdout.write(f"   Cuota: {cuota.numero_cuota}")
                    self.stdout.write(f"   Estado: {estado_anterior} → {cuota.estado}")
                    self.stdout.write(self.style.SUCCESS(f"   ✅ ACTUALIZADO"))
                    self.stdout.write("")

        # ============================================================================
        # RESUMEN
        # ============================================================================

        self.stdout.write("\n" + "="*80)
        self.stdout.write("RESUMEN DE RECONCILIACIÓN")
        self.stdout.write("="*80 + "\n")

        self.stdout.write(f"Total Prestado Corregido: {correcciones_totales['total_prestado']}")
        self.stdout.write(f"Mora Actualizada: {correcciones_totales['mora_actualizada']}")
        self.stdout.write(f"Cuotas Corregidas: {correcciones_totales['cuotas_corregidas']}\n")

        if fix_mode:
            self.stdout.write(self.style.SUCCESS("✅ RECONCILIACIÓN COMPLETADA"))
            self.stdout.write("   Todos los cambios han sido guardados\n")
        else:
            self.stdout.write(self.style.WARNING("⚠️  RECONCILIACIÓN SIMULADA"))
            self.stdout.write("   Para aplicar los cambios: python manage.py reconciliar_finanzas --fix\n")

        self.stdout.write("="*80 + "\n")
