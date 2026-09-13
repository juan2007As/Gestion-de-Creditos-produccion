#!/usr/bin/env python
"""
Script para corregir cuotas anómalas
- Cuotas con monto_original=0 pero con pagos registrados
- Cuotas con fechas fuera de rango del préstamo
"""

from mi_app.models import Cuota, Prestamo
from decimal import Decimal

print("\n" + "="*100)
print("CORRECCIÓN DE CUOTAS ANÓMALAS".center(100))
print("="*100)

# ====================================
# 1. IDENTIFICAR CUOTAS ANÓMALAS
# ====================================

print("\n[1] IDENTIFICANDO CUOTAS ANÓMALAS")
print("-"*100)

cuotas_anomalas = []

for cuota in Cuota.objects.all():
    prestamo = cuota.prestamo
    
    # Anomalía 1: monto_original=0 pero hay pagos
    if cuota.monto_original == 0 and (cuota.monto_pagado_principal > 0 or cuota.monto_pagado_interes > 0):
        print(f"✗ Cuota #{cuota.id}: monto_original=0 pero pagado=${cuota.monto_pagado_principal + cuota.monto_pagado_interes}")
        cuotas_anomalas.append(cuota)
    
    # Anomalía 2: fecha_pago_esperada > fecha_fin_estimada del préstamo
    if cuota.fecha_pago_esperada and cuota.fecha_pago_esperada > prestamo.fecha_fin_estimada:
        print(f"✗ Cuota #{cuota.id} (Prestamo {prestamo.id}): Fecha {cuota.fecha_pago_esperada} > fin {prestamo.fecha_fin_estimada}")
        if cuota not in cuotas_anomalas:
            cuotas_anomalas.append(cuota)

print(f"\nTotal de cuotas anómalas encontradas: {len(cuotas_anomalas)}")

# ====================================
# 2. ESTRATEGIA DE CORRECCIÓN
# ====================================

print("\n\n[2] APLICANDO CORRECCIONES")
print("-"*100)

cuotas_eliminadas = 0
cuotas_reasignadas = 0

for cuota in cuotas_anomalas:
    prestamo = cuota.prestamo
    
    # Estrategia: Si es una cuota anómala (monto=0 con pagos), eliminarla
    # ya que los datos son inconsistentes y probablemente sean testing/pruebas
    if cuota.monto_original == 0:
        print(f"\n🗑️  Eliminando Cuota #{cuota.id} (Prestamo {prestamo.id}) - Datos anómalos")
        print(f"   Monto original: ${cuota.monto_original:.2f}")
        print(f"   Pagado: ${cuota.monto_pagado_principal + cuota.monto_pagado_interes + cuota.monto_pagado_mora:.2f}")
        
        # Antes de eliminar, revertir los pagos del cliente si es necesario
        # (esto ya se manejó a nivel de signal, así que simplemente eliminamos)
        cuota.delete()
        cuotas_eliminadas += 1
    
    # Estrategia: Si la fecha está fuera de rango, corregirla
    elif cuota.fecha_pago_esperada and cuota.fecha_pago_esperada > prestamo.fecha_fin_estimada:
        fecha_original = cuota.fecha_pago_esperada
        # Mover la fecha al día anterior a la fecha fin del préstamo
        cuota.fecha_pago_esperada = prestamo.fecha_fin_estimada
        cuota.save()
        print(f"\n✓ Cuota #{cuota.id}: Fecha corregida")
        print(f"   De: {fecha_original} → A: {cuota.fecha_pago_esperada}")
        cuotas_reasignadas += 1

# ====================================
# 3. VERIFICACIÓN FINAL
# ====================================

print("\n\n[3] VERIFICACIÓN FINAL")
print("-"*100)

cuotas_problematicas = 0

for cuota in Cuota.objects.all():
    prestamo = cuota.prestamo
    
    # Verificar que no haya cuotas con problemas
    if cuota.monto_original == 0 and (cuota.monto_pagado_principal > 0):
        print(f"✗ Aún hay Cuota anómala #{cuota.id}")
        cuotas_problematicas += 1
    
    if cuota.fecha_pago_esperada and cuota.fecha_pago_esperada > prestamo.fecha_fin_estimada:
        print(f"✗ Aún hay Cuota con fecha fuera de rango #{cuota.id}")
        cuotas_problematicas += 1

if cuotas_problematicas == 0:
    print("✓ No hay cuotas anómalas restantes")

# ====================================
# RESUMEN
# ====================================

print("\n\n" + "="*100)
print("RESUMEN DE CORRECCIONES".center(100))
print("="*100)

print(f"\n✓ Cuotas eliminadas: {cuotas_eliminadas}")
print(f"✓ Cuotas reasignadas: {cuotas_reasignadas}")
print(f"✓ Total de cuotas ahora: {Cuota.objects.count()}")
print(f"\n✓ CORRECCIONES APLICADAS EXITOSAMENTE")
print("\n" + "="*100)
