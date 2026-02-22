"""
PASO 1: AUDITORIA FINANCIERA COMPLETA - CRÍTICA #3

Script para verificar inconsistencias financieras en:
1. Total prestado vs suma de préstamos
2. Tasa de interés del préstamo vs cuotas
3. Mora calculada correctamente
4. Totales de pagos consistentes

Ejecutar: python manage.py shell < auditoria_financiera_critica3.py
"""

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
from datetime import date, timedelta
import json

print("\n" + "="*80)
print("AUDITORIA FINANCIERA COMPLETA - CRÍTICA #3")
print("="*80 + "\n")

# ============================================================================
# RESUMEN GENERAL
# ============================================================================

CLIENTE_TOTAL = Cliente.objects.count()
PRESTAMO_TOTAL = Prestamo.objects.count()
CUOTA_TOTAL = Cuota.objects.count()
PAGO_TOTAL = Pago.objects.count()

print(f"📊 ESTADÍSTICAS GENERALES:")
print(f"   Clientes: {CLIENTE_TOTAL}")
print(f"   Préstamos: {PRESTAMO_TOTAL}")
print(f"   Cuotas: {CUOTA_TOTAL}")
print(f"   Pagos: {PAGO_TOTAL}\n")

# ============================================================================
# REPORTE 1: INCONSISTENCIAS EN TOTAL PRESTADO (Problema A)
# ============================================================================

print("\n" + "-"*80)
print("REPORTE 1: INCONSISTENCIAS EN TOTAL PRESTADO")
print("-"*80)

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
    print(f"🔴 ENCONTRADAS {len(inconsistencias_total_prestado)} INCONSISTENCIAS:\n")
    for inc in inconsistencias_total_prestado:
        print(f"   Cliente: {inc['cliente_nombre']} (ID: {inc['cliente_id']})")
        print(f"   Cache guardado: ${inc['total_cache']}")
        print(f"   Debe ser: ${inc['total_real']}")
        print(f"   Diferencia: ${inc['diferencia']}")
        print(f"   Severidad: {inc['severidad']}")
        print()
else:
    print("✅ No hay inconsistencias en total_prestado\n")

# ============================================================================
# REPORTE 2: DIVERGENCIA TASA INTERÉS (Problema B)
# ============================================================================

print("\n" + "-"*80)
print("REPORTE 2: DIVERGENCIA TASA DE INTERÉS")
print("-"*80)

divergencias_interes = []

for prestamo in Prestamo.objects.all():
    tasa_prestamo = prestamo.interes_porcentaje
    
    for cuota in prestamo.cuotas.all():
        tasa_cuota = cuota.interes_normal
        
        # Comparar la tasa (simplificado: asumimos que interes_normal es la tasa aplicada)
        # En realidad, interes_normal es el MONTO, no la tasa
        # Pero debemos verificar que sean consistentes
        
        if tasa_cuota > 0 and tasa_prestamo > 0:
            # Calcular qué tasa de la cuota representa
            # monto_original * tasa = interes_normal (si fuera cálculo simple)
            # tasa_derivada = interes_normal / monto_original
            if cuota.monto_original > 0:
                tasa_derivada = (cuota.interes_normal / cuota.monto_original) * 100
                
                # Si la tasa derivada diverge del préstamo, hay inconsistencia
                # (permitir pequeña tolerancia por redondeos)
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
    print(f"🔴 ENCONTRADAS {len(divergencias_interes)} DIVERGENCIAS:\n")
    for div in divergencias_interes[:10]:  # Mostrar primeras 10
        print(f"   Préstamo: {div['prestamo_id']} - {div['cliente_nombre']}")
        print(f"   Cuota: {div['cuota_numero']}")
        print(f"   Tasa Préstamo: {div['tasa_prestamo']}%")
        print(f"   Interés en Cuota: ${div['interes_cuota_monto']}")
        print(f"   Monto Original: ${div['monto_original']}")
        print(f"   Diferencia: {div['diferencia']}%")
        print()
    if len(divergencias_interes) > 10:
        print(f"   ... y {len(divergencias_interes) - 10} más\n")
else:
    print("✅ No hay divergencias de tasa de interés\n")

# ============================================================================
# REPORTE 3: MORA CALCULADA INCORRECTAMENTE (Problema C)
# ============================================================================

print("\n" + "-"*80)
print("REPORTE 3: MORA CALCULADA INCORRECTAMENTE")
print("-"*80)

mora_problemas = []

for cuota in Cuota.objects.filter(pagado=False):
    if not cuota.fecha_pago_esperada:
        continue
    
    mora_calculada = cuota.calcular_mora_diaria()
    mora_guardada = cuota.interes_mora_acumulado
    
    # Si hay diferencia significativa entre calculada y guardada
    diferencia_mora = abs(mora_calculada - mora_guardada)
    
    if diferencia_mora > Decimal('0.01'):
        # Verificar si es un problema de pago parcial
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
    print(f"🔴 ENCONTRADOS {len(mora_problemas)} PROBLEMAS CON MORA:\n")
    for prob in mora_problemas[:10]:
        print(f"   Préstamo: {prob['prestamo_id']} - {prob['cliente_nombre']}")
        print(f"   Cuota: {prob['numero_cuota']}")
        print(f"   Fecha Vencimiento: {prob['fecha_vencimiento']}")
        print(f"   Mora Calculada: ${prob['mora_calculada']}")
        print(f"   Mora Guardada: ${prob['mora_guardada']}")
        print(f"   Diferencia: ${prob['diferencia']}")
        if prob['pagado_parcial']:
            print(f"   ⚠️  PAGO PARCIAL: Pagado ${prob['monto_pagado']}, Pendiente ${prob['monto_pendiente']}")
        print()
    if len(mora_problemas) > 10:
        print(f"   ... y {len(mora_problemas) - 10} más\n")
else:
    print("✅ No hay problemas con mora aplicada\n")

# ============================================================================
# REPORTE 4: TOTALES INCONSISTENTES EN PAGOS
# ============================================================================

print("\n" + "-"*80)
print("REPORTE 4: TOTALES INCONSISTENTES EN PAGOS")
print("-"*80)

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
    print(f"🔴 ENCONTRADAS {len(pago_inconsistencias)} INCONSISTENCIAS:\n")
    for inc in pago_inconsistencias[:10]:
        print(f"   Pago ID: {inc['pago_id']}")
        print(f"   Total Pagado: ${inc['monto_total']}")
        print(f"   Desglose: ${inc['principal']} + ${inc['interes']} + ${inc['mora']} = ${inc['suma_desglose']}")
        print(f"   Diferencia: ${inc['diferencia']}")
        print()
    if len(pago_inconsistencias) > 10:
        print(f"   ... y {len(pago_inconsistencias) - 10} más\n")
else:
    print("✅ No hay inconsistencias en totales de pagos\n")

# ============================================================================
# REPORTE 5: CUOTAS CON CÁLCULO DE MORA DIVERGENTE (Por pago parcial)
# ============================================================================

print("\n" + "-"*80)
print("REPORTE 5: CUOTAS CON PAGO PARCIAL SIN ACTUALIZAR MORA")
print("-"*80)

cuotas_mora_sin_actualizar = []

for cuota in Cuota.objects.filter(pagado=False):
    # Si tiene pago parcial (monto_pagado_principal > 0 pero monto_pendiente > 0)
    if cuota.monto_pagado_principal > 0 and cuota.monto_pendiente > 0:
        mora = cuota.calcular_mora_diaria()
        
        # La mora debería ser prorrateada pero check si está siendo calculada correctamente
        # Si no tiene registro de pago de mora, es un problema
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
    print(f"⚠️  ENCONTRADAS {len(cuotas_mora_sin_actualizar)} CUOTAS CON MORA SIN PAGAR:\n")
    for cuota_prob in cuotas_mora_sin_actualizar[:10]:
        print(f"   Cuota: {cuota_prob['numero_cuota']} - Préstamo {cuota_prob['prestamo_id']}")
        print(f"   Cliente: {cuota_prob['cliente_nombre']}")
        print(f"   Monto Original: ${cuota_prob['monto_original']}")
        print(f"   Pagado: ${cuota_prob['monto_pagado']} / Pendiente: ${cuota_prob['monto_pendiente']}")
        print(f"   Mora Acumulada: ${cuota_prob['mora_acumulada']} (No pagada)")
        print()
    if len(cuotas_mora_sin_actualizar) > 10:
        print(f"   ... y {len(cuotas_mora_sin_actualizar) - 10} más\n")
else:
    print("✅ No hay cuotas con mora sin cobrar\n")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80 + "\n")

total_problemas = (
    len(inconsistencias_total_prestado) +
    len(divergencias_interes) +
    len(mora_problemas) +
    len(pago_inconsistencias) +
    len(cuotas_mora_sin_actualizar)
)

print(f"🔴 PROBLEMAS ENCONTRADOS: {total_problemas}\n")
print(f"   Inconsistencias en total_prestado: {len(inconsistencias_total_prestado)}")
print(f"   Divergencias de tasa de interés: {len(divergencias_interes)}")
print(f"   Problemas con mora: {len(mora_problemas)}")
print(f"   Inconsistencias en pagos: {len(pago_inconsistencias)}")
print(f"   Cuotas con mora sin cobrar: {len(cuotas_mora_sin_actualizar)}\n")

if total_problemas == 0:
    print("✅ EXCELENTE: No se encontraron inconsistencias financieras\n")
else:
    print(f"⚠️  ACCIÓN REQUERIDA: Ejecutar script de reconciliación\n")

print("="*80 + "\n")
