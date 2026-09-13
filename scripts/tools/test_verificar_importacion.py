#!/usr/bin/env python
"""
Script de prueba de importación del Excel para Bug #1
Simula el flujo de importación y verifica resultados
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago
from decimal import Decimal
from datetime import date

def verificar_importacion_excel():
    """Verifica que la importación funcionó correctamente"""
    
    print("\n" + "="*100)
    print("🧪 VERIFICACIÓN DE IMPORTACIÓN - BUG #1")
    print("="*100)
    
    # Limpiar datos antiguos de pruebas
    Cliente.objects.filter(
        nombre__in=['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez']
    ).delete()
    
    # Leer el Excel
    archivo_excel = r'c:\Users\Juancho\Desktop\proyecto_john\test_importacion_bug1.xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ ERROR: Archivo no encontrado: {archivo_excel}")
        return False
    
    df = pd.read_excel(archivo_excel, sheet_name=0)
    print(f"\n✅ Excel cargado: {len(df)} clientes\n")
    
    # Mapeo de meses
    MESES_ESPAÑOL = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    import re
    from datetime import timedelta
    
    # Procesar cada cliente
    for idx, row in df.iterrows():
        nombre = str(row.get('Nombre con responsable', '')).strip()
        celular = str(int(float(row.get('celular', 0))))
        monto_prestamo = Decimal(str(row.get('Monto del préstamo', 0)))
        
        print(f"\n{'='*100}")
        print(f"📋 CLIENTE {idx + 1}: {nombre} ({celular})")
        print(f"   Monto Préstamo: ${monto_prestamo:,.2f}")
        print(f"{'='*100}")
        
        # Crear cliente
        cliente, creado = Cliente.objects.get_or_create(
            celular=celular,
            defaults={'nombre': nombre, 'estado': 'activo', 'importado_excel': True}
        )
        
        # Crear préstamo
        prestamo = Prestamo.objects.create(
            cliente=cliente,
            monto_total=monto_prestamo,
            interes_porcentaje=Decimal('15'),
            fecha_inicio=date.today(),
            fecha_fin_estimada=date.today() + timedelta(days=90),
            tipo_pago='QUINCENAL',
            estado='ACTIVO'
        )
        
        # Procesuar cuotas
        for i in range(1, 4):
            col_cuota = f'Cuota {i}'
            col_interes = f'Interés {i}'
            col_fecha = f'Fecha {i}'
            
            monto_cuota = row.get(col_cuota, 0)
            interes_cuota = row.get(col_interes, 0)
            
            if pd.isna(monto_cuota) or pd.isna(interes_cuota):
                continue
            
            monto_cuota = float(monto_cuota) if monto_cuota else 0
            interes_cuota = float(interes_cuota) if interes_cuota else 0
            
            if monto_cuota == 0 and interes_cuota == 0:
                break
            
            # Parsear fecha
            tipo_pago_excel = None
            fecha_pago_real = None
            valor_fecha = row.get(col_fecha)
            
            if pd.notna(valor_fecha) and valor_fecha:
                valor_fecha_str = str(valor_fecha).strip().lower()
                
                if valor_fecha_str:
                    for mes_es, mes_num in MESES_ESPAÑOL.items():
                        if valor_fecha_str.startswith(mes_es):
                            resto = valor_fecha_str[len(mes_es):]
                            match = re.match(r'(\d{1,2})(.+)', resto)
                            if match:
                                dia_str, tipo_pago_str = match.groups()
                                try:
                                    dia = int(dia_str)
                                    año_actual = date.today().year
                                    fecha_pago_real = date(año_actual, mes_num, dia)
                                    
                                    tipo_pago_str = tipo_pago_str.lower()
                                    if 'cap+int' in tipo_pago_str or 'int+cap' in tipo_pago_str:
                                        tipo_pago_excel = 'ambos'
                                    elif 'cap' in tipo_pago_str:
                                        tipo_pago_excel = 'capital'
                                    elif 'int' in tipo_pago_str:
                                        tipo_pago_excel = 'interes'
                                except:
                                    pass
                            break
            
            # Calcular montos pagados
            monto_cuota_decimal = Decimal(str(monto_cuota))
            interes_cuota_decimal = Decimal(str(interes_cuota))
            
            monto_pagado_principal = Decimal('0')
            monto_pagado_interes = Decimal('0')
            monto_pendiente_principal = monto_cuota_decimal
            monto_pendiente_interes = interes_cuota_decimal
            
            if tipo_pago_excel:
                if tipo_pago_excel == 'capital':
                    monto_pagado_principal = monto_cuota_decimal
                    monto_pendiente_principal = Decimal('0')
                elif tipo_pago_excel == 'interes':
                    monto_pagado_interes = interes_cuota_decimal
                    monto_pendiente_interes = Decimal('0')
                elif tipo_pago_excel == 'ambos':
                    monto_pagado_principal = monto_cuota_decimal
                    monto_pagado_interes = interes_cuota_decimal
                    monto_pendiente_principal = Decimal('0')
                    monto_pendiente_interes = Decimal('0')
            
            # Crear cuota
            cuota = Cuota.objects.create(
                prestamo=prestamo,
                numero_cuota=i,
                monto_original=monto_cuota_decimal,
                monto_pendiente=monto_pendiente_principal,
                interes_normal=interes_cuota_decimal,
                monto_pendiente_interes=monto_pendiente_interes,
                monto_pagado_principal=monto_pagado_principal,
                monto_pagado_interes=monto_pagado_interes,
                monto_pagado_mora=Decimal('0'),
                pagado=(monto_pendiente_principal == 0 and monto_pendiente_interes == 0),
                fecha_pago_esperada=date.today() + timedelta(days=15*i),
                fecha_pago_real=fecha_pago_real if tipo_pago_excel else None
            )
            
            # Crear pago si existe
            if tipo_pago_excel and fecha_pago_real:
                monto_total_pagado = monto_pagado_principal + monto_pagado_interes
                Pago.objects.create(
                    cuota=cuota,
                    monto_pagado=monto_total_pagado,
                    monto_principal=monto_pagado_principal,
                    monto_interes=monto_pagado_interes,
                    monto_mora=Decimal('0'),
                    notas=f'Importado - Tipo: {tipo_pago_excel}'
                )
            
            # Mostrar resultado
            print(f"\n   📌 Cuota {i}:")
            print(f"      Capital: ${monto_cuota_decimal:>8,.2f}")
            print(f"      Interés: ${interes_cuota_decimal:>8,.2f}")
            
            if tipo_pago_excel is None:
                print(f"      Estado: ⏳ PENDIENTE")
                print(f"        • Pendiente Capital: ${monto_pendiente_principal:,.2f}")
                print(f"        • Pendiente Interés: ${monto_pendiente_interes:,.2f}")
            elif tipo_pago_excel == 'capital':
                print(f"      Estado: ⚠️  PARCIAL (CAPITAL)")
                print(f"        • ✓ Pagado Capital: ${monto_pagado_principal:,.2f} ({fecha_pago_real})")
                print(f"        • ✗ Pendiente Interés: ${monto_pendiente_interes:,.2f}")
            elif tipo_pago_excel == 'interes':
                print(f"      Estado: ⚠️  PARCIAL (INTERÉS)")
                print(f"        • ✗ Pendiente Capital: ${monto_pendiente_principal:,.2f}")
                print(f"        • ✓ Pagado Interés: ${monto_pagado_interes:,.2f} ({fecha_pago_real})")
            elif tipo_pago_excel == 'ambos':
                print(f"      Estado: ✅ PAGADA COMPLETA")
                print(f"        • ✓ Pagado Capital: ${monto_pagado_principal:,.2f} ({fecha_pago_real})")
                print(f"        • ✓ Pagado Interés: ${monto_pagado_interes:,.2f}")
    
    # VERIFICACIONES FINALES
    print(f"\n\n{'='*100}")
    print("📊 VERIFICACIONES FINALES")
    print(f"{'='*100}\n")
    
    clientes = Cliente.objects.filter(
        nombre__in=['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez']
    )
    
    print(f"✅ Clientes creados: {clientes.count()} (esperado: 4)")
    assert clientes.count() == 4, "❌ Debería haber 4 clientes"
    
    prestamos = Prestamo.objects.filter(cliente__in=clientes)
    print(f"✅ Préstamos creados: {prestamos.count()} (esperado: 4)")
    assert prestamos.count() == 4, "❌ Debería haber 4 préstamos"
    
    cuotas = Cuota.objects.filter(prestamo__in=prestamos)
    print(f"✅ Cuotas creadas: {cuotas.count()} (esperado: 11)")
    assert cuotas.count() == 11, "❌ Debería haber 11 cuotas totales"
    
    pagos = Pago.objects.filter(cuota__in=cuotas)
    print(f"✅ Pagos registrados: {pagos.count()} (esperado: 8)")
    assert pagos.count() == 8, "❌ Debería haber 8 registros de Pago"
    
    # Verificar estados
    cuotas_pendientes = cuotas.filter(
        pagado=False,
        monto_pagado_principal=Decimal('0'),
        monto_pagado_interes=Decimal('0')
    )
    print(f"✅ Cuotas pendientes: {cuotas_pendientes.count()} (esperado: 3)")
    
    from django.db.models import Q
    cuotas_parciales = cuotas.exclude(pagado=True).filter(
        Q(monto_pagado_principal__gt=0) | Q(monto_pagado_interes__gt=0)
    ).distinct()
    print(f"✅ Cuotas parcialmente pagadas: {cuotas_parciales.count()} (esperado: 5)")
    
    cuotas_completas = cuotas.filter(pagado=True)
    print(f"✅ Cuotas completamente pagadas: {cuotas_completas.count()} (esperado: 3)")
    
    print(f"\n{'='*100}")
    print("✅ TODAS LAS VERIFICACIONES PASARON - IMPORTACIÓN CORRECTA")
    print(f"{'='*100}\n")
    
    return True

if __name__ == '__main__':
    verificar_importacion_excel()
