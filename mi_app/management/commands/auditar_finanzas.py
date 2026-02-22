"""
Management command para ejecutar auditoría financiera completa

python manage.py auditar_finanzas
"""

from django.core.management.base import BaseCommand
from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Auditoría financiera completa para identificar inconsistencias - CRÍTICA #3'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("AUDITORIA FINANCIERA COMPLETA - CRÍTICA #3")
        self.stdout.write("="*80 + "\n")

        # ============================================================================
        # RESUMEN GENERAL
        # ============================================================================

        CLIENTE_TOTAL = Cliente.objects.count()
        PRESTAMO_TOTAL = Prestamo.objects.count()
        CUOTA_TOTAL = Cuota.objects.count()
        PAGO_TOTAL = Pago.objects.count()

        self.stdout.write(f"📊 ESTADÍSTICAS GENERALES:")
        self.stdout.write(f"   Clientes: {CLIENTE_TOTAL}")
        self.stdout.write(f"   Préstamos: {PRESTAMO_TOTAL}")
        self.stdout.write(f"   Cuotas: {CUOTA_TOTAL}")
        self.stdout.write(f"   Pagos: {PAGO_TOTAL}\n")

        # ============================================================================
        # REPORTE 1: INCONSISTENCIAS EN TOTAL PRESTADO (Problema A)
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("REPORTE 1: INCONSISTENCIAS EN TOTAL PRESTADO")
        self.stdout.write("-"*80)

        inconsistencias_total_prestado = []

        for cliente in Cliente.objects.all():
            total_real = cliente.total_prestado_real
            total_cache = cliente.total_prestado
            
            diferencia = abs(total_real - total_cache)
            
            if diferencia > Decimal('0.01'):  # Tolerancia de 1 centavo
                inconsistencias_total_prestado.append({
                    'cliente_id': cliente.id,
                    'cliente_nombre': cliente.nombre,
                    'total_cache': str(total_cache),
                    'total_real': str(total_real),
                    'diferencia': str(diferencia),
                    'severidad': 'CRÍTICA' if diferencia > Decimal('100') else 'MEDIA'
                })

        if inconsistencias_total_prestado:
            self.stdout.write(self.style.ERROR(f"🔴 ENCONTRADAS {len(inconsistencias_total_prestado)} INCONSISTENCIAS:\n"))
            for inc in inconsistencias_total_prestado:
                self.stdout.write(f"   Cliente: {inc['cliente_nombre']} (ID: {inc['cliente_id']})")
                self.stdout.write(f"   Cache guardado: ${inc['total_cache']}")
                self.stdout.write(f"   Debe ser: ${inc['total_real']}")
                self.stdout.write(f"   Diferencia: ${inc['diferencia']}")
                self.stdout.write(f"   Severidad: {inc['severidad']}")
                self.stdout.write("")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No hay inconsistencias en total_prestado\n"))

        # ============================================================================
        # REPORTE 2: DIVERGENCIA TASA INTERÉS (Problema B)
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("REPORTE 2: DIVERGENCIA TASA DE INTERÉS")
        self.stdout.write("-"*80)

        divergencias_interes = []

        for prestamo in Prestamo.objects.all():
            tasa_prestamo = prestamo.interes_porcentaje
            
            for cuota in prestamo.cuotas.all():
                tasa_cuota = cuota.interes_normal
                
                if tasa_cuota > 0 and tasa_prestamo > 0:
                    if cuota.monto_original > 0:
                        tasa_derivada = (cuota.interes_normal / cuota.monto_original) * 100
                        diferencia_tasa = abs(float(tasa_prestamo) - float(tasa_derivada))
                        
                        if diferencia_tasa > 0.5:  # Tolerancia de 0.5%
                            divergencias_interes.append({
                                'prestamo_id': prestamo.id,
                                'cliente_nombre': prestamo.cliente.nombre,
                                'cuota_numero': cuota.numero_cuota,
                                'tasa_prestamo': str(tasa_prestamo),
                                'interes_cuota_monto': str(cuota.interes_normal),
                                'monto_original': str(cuota.monto_original),
                                'diferencia': str(diferencia_tasa)
                            })

        if divergencias_interes:
            self.stdout.write(self.style.ERROR(f"🔴 ENCONTRADAS {len(divergencias_interes)} DIVERGENCIAS:\n"))
            for div in divergencias_interes[:10]:
                self.stdout.write(f"   Préstamo: {div['prestamo_id']} - {div['cliente_nombre']}")
                self.stdout.write(f"   Cuota: {div['cuota_numero']}")
                self.stdout.write(f"   Tasa Préstamo: {div['tasa_prestamo']}%")
                self.stdout.write(f"   Interés en Cuota: ${div['interes_cuota_monto']}")
                self.stdout.write(f"   Monto Original: ${div['monto_original']}")
                self.stdout.write(f"   Diferencia: {div['diferencia']}%")
                self.stdout.write("")
            if len(divergencias_interes) > 10:
                self.stdout.write(f"   ... y {len(divergencias_interes) - 10} más\n")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No hay divergencias de tasa de interés\n"))

        # ============================================================================
        # REPORTE 3: MORA CALCULADA INCORRECTAMENTE (Problema C)
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("REPORTE 3: MORA CALCULADA INCORRECTAMENTE")
        self.stdout.write("-"*80)

        mora_problemas = []

        for cuota in Cuota.objects.filter(pagado=False):
            if not cuota.fecha_pago_esperada:
                continue
            
            mora_calculada = cuota.calcular_mora_diaria()
            mora_guardada = cuota.interes_mora_acumulado
            
            diferencia_mora = abs(mora_calculada - mora_guardada)
            
            if diferencia_mora > Decimal('0.01'):
                pagado_parcial = (cuota.monto_pagado_principal > 0) and (cuota.monto_pendiente > 0)
                
                mora_problemas.append({
                    'cuota_id': cuota.id,
                    'prestamo_id': cuota.prestamo.id,
                    'cliente_nombre': cuota.prestamo.cliente.nombre,
                    'numero_cuota': cuota.numero_cuota,
                    'fecha_vencimiento': str(cuota.fecha_pago_esperada),
                    'mora_calculada': str(mora_calculada),
                    'mora_guardada': str(mora_guardada),
                    'diferencia': str(diferencia_mora),
                    'pagado_parcial': pagado_parcial,
                    'monto_pagado': str(cuota.monto_pagado_principal),
                    'monto_pendiente': str(cuota.monto_pendiente)
                })

        if mora_problemas:
            self.stdout.write(self.style.ERROR(f"🔴 ENCONTRADOS {len(mora_problemas)} PROBLEMAS CON MORA:\n"))
            for prob in mora_problemas[:10]:
                self.stdout.write(f"   Préstamo: {prob['prestamo_id']} - {prob['cliente_nombre']}")
                self.stdout.write(f"   Cuota: {prob['numero_cuota']}")
                self.stdout.write(f"   Fecha Vencimiento: {prob['fecha_vencimiento']}")
                self.stdout.write(f"   Mora Calculada: ${prob['mora_calculada']}")
                self.stdout.write(f"   Mora Guardada: ${prob['mora_guardada']}")
                self.stdout.write(f"   Diferencia: ${prob['diferencia']}")
                if prob['pagado_parcial']:
                    self.stdout.write(f"   ⚠️  PAGO PARCIAL: Pagado ${prob['monto_pagado']}, Pendiente ${prob['monto_pendiente']}")
                self.stdout.write("")
            if len(mora_problemas) > 10:
                self.stdout.write(f"   ... y {len(mora_problemas) - 10} más\n")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No hay problemas con mora aplicada\n"))

        # ============================================================================
        # REPORTE 4: TOTALES INCONSISTENTES EN PAGOS
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("REPORTE 4: TOTALES INCONSISTENTES EN PAGOS")
        self.stdout.write("-"*80)

        pago_inconsistencias = []

        for pago in Pago.objects.all():
            total_desglose = (pago.monto_principal + pago.monto_interes + pago.monto_mora)
            
            diferencia = abs(pago.monto_pagado - total_desglose)
            
            if diferencia > Decimal('0.01'):
                pago_inconsistencias.append({
                    'pago_id': pago.id,
                    'monto_total': str(pago.monto_pagado),
                    'principal': str(pago.monto_principal),
                    'interes': str(pago.monto_interes),
                    'mora': str(pago.monto_mora),
                    'suma_desglose': str(total_desglose),
                    'diferencia': str(diferencia)
                })

        if pago_inconsistencias:
            self.stdout.write(self.style.ERROR(f"🔴 ENCONTRADAS {len(pago_inconsistencias)} INCONSISTENCIAS:\n"))
            for inc in pago_inconsistencias[:10]:
                self.stdout.write(f"   Pago ID: {inc['pago_id']}")
                self.stdout.write(f"   Total Pagado: ${inc['monto_total']}")
                self.stdout.write(f"   Desglose: ${inc['principal']} + ${inc['interes']} + ${inc['mora']} = ${inc['suma_desglose']}")
                self.stdout.write(f"   Diferencia: ${inc['diferencia']}")
                self.stdout.write("")
            if len(pago_inconsistencias) > 10:
                self.stdout.write(f"   ... y {len(pago_inconsistencias) - 10} más\n")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No hay inconsistencias en totales de pagos\n"))

        # ============================================================================
        # REPORTE 5: CUOTAS CON CÁLCULO DE MORA DIVERGENTE (Por pago parcial)
        # ============================================================================

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("REPORTE 5: CUOTAS CON PAGO PARCIAL SIN ACTUALIZAR MORA")
        self.stdout.write("-"*80)

        cuotas_mora_sin_actualizar = []

        for cuota in Cuota.objects.filter(pagado=False):
            if cuota.monto_pagado_principal > 0 and cuota.monto_pendiente > 0:
                mora = cuota.calcular_mora_diaria()
                
                if mora > 0 and cuota.monto_pagado_mora == 0:
                    cuotas_mora_sin_actualizar.append({
                        'cuota_id': cuota.id,
                        'prestamo_id': cuota.prestamo.id,
                        'cliente_nombre': cuota.prestamo.cliente.nombre,
                        'numero_cuota': cuota.numero_cuota,
                        'monto_original': str(cuota.monto_original),
                        'monto_pagado': str(cuota.monto_pagado_principal),
                        'monto_pendiente': str(cuota.monto_pendiente),
                        'mora_acumulada': str(mora),
                        'mora_pagada': str(cuota.monto_pagado_mora)
                    })

        if cuotas_mora_sin_actualizar:
            self.stdout.write(self.style.WARNING(f"⚠️  ENCONTRADAS {len(cuotas_mora_sin_actualizar)} CUOTAS CON MORA SIN PAGAR:\n"))
            for cuota_prob in cuotas_mora_sin_actualizar[:10]:
                self.stdout.write(f"   Cuota: {cuota_prob['numero_cuota']} - Préstamo {cuota_prob['prestamo_id']}")
                self.stdout.write(f"   Cliente: {cuota_prob['cliente_nombre']}")
                self.stdout.write(f"   Monto Original: ${cuota_prob['monto_original']}")
                self.stdout.write(f"   Pagado: ${cuota_prob['monto_pagado']} / Pendiente: ${cuota_prob['monto_pendiente']}")
                self.stdout.write(f"   Mora Acumulada: ${cuota_prob['mora_acumulada']} (No pagada)")
                self.stdout.write("")
            if len(cuotas_mora_sin_actualizar) > 10:
                self.stdout.write(f"   ... y {len(cuotas_mora_sin_actualizar) - 10} más\n")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No hay cuotas con mora sin cobrar\n"))

        # ============================================================================
        # RESUMEN FINAL
        # ============================================================================

        self.stdout.write("\n" + "="*80)
        self.stdout.write("RESUMEN FINAL")
        self.stdout.write("="*80 + "\n")

        total_problemas = (
            len(inconsistencias_total_prestado) +
            len(divergencias_interes) +
            len(mora_problemas) +
            len(pago_inconsistencias) +
            len(cuotas_mora_sin_actualizar)
        )

        self.stdout.write(f"🔴 PROBLEMAS ENCONTRADOS: {total_problemas}\n")
        self.stdout.write(f"   Inconsistencias en total_prestado: {len(inconsistencias_total_prestado)}")
        self.stdout.write(f"   Divergencias de tasa de interés: {len(divergencias_interes)}")
        self.stdout.write(f"   Problemas con mora: {len(mora_problemas)}")
        self.stdout.write(f"   Inconsistencias en pagos: {len(pago_inconsistencias)}")
        self.stdout.write(f"   Cuotas con mora sin cobrar: {len(cuotas_mora_sin_actualizar)}\n")

        if total_problemas == 0:
            self.stdout.write(self.style.SUCCESS("✅ EXCELENTE: No se encontraron inconsistencias financieras\n"))
        else:
            self.stdout.write(self.style.ERROR(f"⚠️  ACCIÓN REQUERIDA: Ejecutar script de reconciliación\n"))

        self.stdout.write("="*80 + "\n")
