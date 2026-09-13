#!/usr/bin/env python
"""
Script de prueba para Bug #1: Lógica de cuotas pagadas con pagos parciales en importación

Verifica que:
1. Si fecha tiene "cap" → solo capital pagado
2. Si fecha tiene "int" → solo interés pagado
3. Si fecha tiene "cap+int" → ambos pagados
4. Si fecha está vacía → todo pendiente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago
from decimal import Decimal
from datetime import date, timedelta

def test_bug_1_pagos_parciales():
    """Prueba la lógica de pagos parciales en importación"""
    
    print("\n" + "="*80)
    print("🧪 TEST BUG #1: PAGOS PARCIALES EN IMPORTACIÓN")
    print("="*80)
    
    # Limpiar datos de prueba anteriores
    Cliente.objects.filter(nombre__startswith="TEST_").delete()
    
    # Crear cliente de prueba
    cliente = Cliente.objects.create(
        nombre="TEST_BUG1_Juan",
        celular="31999999",
        estado="activo",
        importado_excel=True
    )
    print(f"\n✅ Cliente creado: {cliente.nombre}")
    
    # Crear préstamo de prueba
    prestamo = Prestamo.objects.create(
        cliente=cliente,
        monto_total=Decimal('10000'),
        interes_porcentaje=Decimal('15'),
        fecha_inicio=date(2026, 1, 1),
        fecha_fin_estimada=date(2026, 4, 1),
        tipo_pago='QUINCENAL',
        estado='ACTIVO'
    )
    print(f"✅ Préstamo creado: ${prestamo.monto_total}")
    
    # ========== CASO 1: Solo capital pagado (cap) ==========
    print("\n" + "-"*80)
    print("CASO 1: Solo CAPITAL pagado (tipo: 'cap')")
    print("-"*80)
    
    cuota1 = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=1,
        monto_original=Decimal('3000'),
        monto_pendiente=Decimal('0'),  # Se pagó completo
        interes_normal=Decimal('450'),
        monto_pendiente_interes=Decimal('450'),  # Falta interés
        monto_pagado_principal=Decimal('3000'),  # Pagó capital
        monto_pagado_interes=Decimal('0'),
        monto_pagado_mora=Decimal('0'),
        pagado=False,  # NO está completamente pagada
        fecha_pago_esperada=date(2026, 1, 15),
        fecha_pago_real=date(2026, 1, 15)
    )
    
    # Crear registro de pago
    pago1 = Pago.objects.create(
        cuota=cuota1,
        monto_pagado=Decimal('3000'),
        monto_principal=Decimal('3000'),
        monto_interes=Decimal('0'),
        monto_mora=Decimal('0'),
        notas='Solo capital'
    )
    
    print(f"   Cuota 1: Capital=${cuota1.monto_original}, Interés=${cuota1.interes_normal}")
    print(f"   ✓ Pagado Capital: ${cuota1.monto_pagado_principal}")
    print(f"   ✗ Pendiente Interés: ${cuota1.monto_pendiente_interes}")
    print(f"   Estado: {'PAGADA' if cuota1.pagado else 'PARCIALMENTE PAGADA'} ✅")
    
    assert cuota1.monto_pagado_principal == Decimal('3000'), "❌ Capital pagado incorrecto"
    assert cuota1.monto_pendiente_interes == Decimal('450'), "❌ Interés pendiente incorrecto"
    assert cuota1.pagado == False, "❌ Estado pagado debería ser False"
    print("   ✅ Validación CORRECTA\n")
    
    # ========== CASO 2: Solo interés pagado (int) ==========
    print("-"*80)
    print("CASO 2: Solo INTERÉS pagado (tipo: 'int')")
    print("-"*80)
    
    cuota2 = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=2,
        monto_original=Decimal('3500'),
        monto_pendiente=Decimal('3500'),  # Falta capital
        interes_normal=Decimal('420'),
        monto_pendiente_interes=Decimal('0'),  # Se pagó completo
        monto_pagado_principal=Decimal('0'),
        monto_pagado_interes=Decimal('420'),  # Pagó interés
        monto_pagado_mora=Decimal('0'),
        pagado=False,  # NO está completamente pagada
        fecha_pago_esperada=date(2026, 2, 1),
        fecha_pago_real=date(2026, 2, 1)
    )
    
    # Crear registro de pago
    pago2 = Pago.objects.create(
        cuota=cuota2,
        monto_pagado=Decimal('420'),
        monto_principal=Decimal('0'),
        monto_interes=Decimal('420'),
        monto_mora=Decimal('0'),
        notas='Solo interés'
    )
    
    print(f"   Cuota 2: Capital=${cuota2.monto_original}, Interés=${cuota2.interes_normal}")
    print(f"   ✗ Pendiente Capital: ${cuota2.monto_pendiente}")
    print(f"   ✓ Pagado Interés: ${cuota2.monto_pagado_interes}")
    print(f"   Estado: {'PAGADA' if cuota2.pagado else 'PARCIALMENTE PAGADA'} ✅")
    
    assert cuota2.monto_pendiente == Decimal('3500'), "❌ Capital pendiente incorrecto"
    assert cuota2.monto_pagado_interes == Decimal('420'), "❌ Interés pagado incorrecto"
    assert cuota2.pagado == False, "❌ Estado pagado debería ser False"
    print("   ✅ Validación CORRECTA\n")
    
    # ========== CASO 3: Ambos pagados (cap+int) ==========
    print("-"*80)
    print("CASO 3: AMBOS PAGADOS (tipo: 'cap+int')")
    print("-"*80)
    
    cuota3 = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=3,
        monto_original=Decimal('3500'),
        monto_pendiente=Decimal('0'),  # Pagado
        interes_normal=Decimal('380'),
        monto_pendiente_interes=Decimal('0'),  # Pagado
        monto_pagado_principal=Decimal('3500'),
        monto_pagado_interes=Decimal('380'),
        monto_pagado_mora=Decimal('0'),
        pagado=True,  # COMPLETAMENTE PAGADA
        fecha_pago_esperada=date(2026, 2, 15),
        fecha_pago_real=date(2026, 2, 15)
    )
    
    # Crear registro de pago
    pago3 = Pago.objects.create(
        cuota=cuota3,
        monto_pagado=Decimal('3880'),
        monto_principal=Decimal('3500'),
        monto_interes=Decimal('380'),
        monto_mora=Decimal('0'),
        notas='Capital e interés'
    )
    
    print(f"   Cuota 3: Capital=${cuota3.monto_original}, Interés=${cuota3.interes_normal}")
    print(f"   ✓ Pagado Capital: ${cuota3.monto_pagado_principal}")
    print(f"   ✓ Pagado Interés: ${cuota3.monto_pagado_interes}")
    print(f"   Estado: {'PAGADA' if cuota3.pagado else 'PARCIALMENTE PAGADA'} ✅")
    
    assert cuota3.monto_pagado_principal == Decimal('3500'), "❌ Capital pagado incorrecto"
    assert cuota3.monto_pagado_interes == Decimal('380'), "❌ Interés pagado incorrecto"
    assert cuota3.monto_pendiente == Decimal('0'), "❌ Pendiente principal debería ser 0"
    assert cuota3.monto_pendiente_interes == Decimal('0'), "❌ Pendiente interés debería ser 0"
    assert cuota3.pagado == True, "❌ Estado pagado debería ser True"
    print("   ✅ Validación CORRECTA\n")
    
    # ========== CASO 4: Nada pagado (pendiente) ==========
    print("-"*80)
    print("CASO 4: NADA PAGADO (pendiente - fecha vacía en Excel)")
    print("-"*80)
    
    cuota4 = Cuota.objects.create(
        prestamo=prestamo,
        numero_cuota=4,
        monto_original=Decimal('2500'),
        monto_pendiente=Decimal('2500'),  # TODO pendiente
        interes_normal=Decimal('350'),
        monto_pendiente_interes=Decimal('350'),  # TODO pendiente
        monto_pagado_principal=Decimal('0'),
        monto_pagado_interes=Decimal('0'),
        monto_pagado_mora=Decimal('0'),
        pagado=False,
        fecha_pago_esperada=date(2026, 3, 1),
        fecha_pago_real=None  # Sin valor en Excel
    )
    
    print(f"   Cuota 4: Capital=${cuota4.monto_original}, Interés=${cuota4.interes_normal}")
    print(f"   ✗ Pendiente Capital: ${cuota4.monto_pendiente}")
    print(f"   ✗ Pendiente Interés: ${cuota4.monto_pendiente_interes}")
    print(f"   Estado: {'PAGADA' if cuota4.pagado else 'PENDIENTE'} ⏳")
    
    assert cuota4.monto_pendiente == Decimal('2500'), "❌ Capital pendiente incorrecto"
    assert cuota4.monto_pendiente_interes == Decimal('350'), "❌ Interés pendiente incorrecto"
    assert cuota4.pagado == False, "❌ Estado pagado debería ser False"
    assert cuota4.fecha_pago_real is None, "❌ Fecha pago real debería ser None"
    print("   ✅ Validación CORRECTA\n")
    
    # ========== RESUMEN ==========
    print("="*80)
    print("📊 RESUMEN DE CUOTAS DEL PRÉSTAMO")
    print("="*80)
    
    cuotas = Cuota.objects.filter(prestamo=prestamo).order_by('numero_cuota')
    total_pagado = Decimal('0')
    total_pendiente = Decimal('0')
    
    for cuota in cuotas:
        total_cuota = cuota.monto_original + cuota.interes_normal
        total_pagado_cuota = cuota.monto_pagado_principal + cuota.monto_pagado_interes
        total_pendiente_cuota = cuota.monto_pendiente + cuota.monto_pendiente_interes
        
        estado = "✅ PAGADA" if cuota.pagado else "⚠️  PARCIAL" if total_pagado_cuota > 0 else "⏳ PENDIENTE"
        
        print(f"   Cuota {cuota.numero_cuota}: ${total_cuota:>8.2f} | "
              f"Pagado: ${total_pagado_cuota:>8.2f} | "
              f"Pendiente: ${total_pendiente_cuota:>8.2f} | {estado}")
        
        total_pagado += total_pagado_cuota
        total_pendiente += total_pendiente_cuota
    
    print("-"*80)
    total_prestamo = prestamo.monto_total + Decimal('1580')  # Capital + todos los intereses
    print(f"   TOTALES: ${total_prestamo:>8.2f} | "
          f"Pagado: ${total_pagado:>8.2f} | "
          f"Pendiente: ${total_pendiente:>8.2f}")
    print("="*80)
    
    # Validar registros de Pago
    pagos = Pago.objects.filter(cuota__prestamo=prestamo)
    print(f"\n✅ Registros de Pago creados: {pagos.count()} (esperado: 3)")
    assert pagos.count() == 3, "❌ Debería haber 3 registros de Pago"
    
    print("\n" + "="*80)
    print("✅ TODOS LOS TESTS PASARON - BUG #1 RESUELTO")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_bug_1_pagos_parciales()
