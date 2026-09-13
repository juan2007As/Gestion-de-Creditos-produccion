#!/usr/bin/env python
"""
🔍 AUDITORÍA EXHAUSTIVA DEL SISTEMA - VERSIÓN SIMPLE
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal

print("="*100)
print("AUDITORÍA EXHAUSTIVA DEL SISTEMA".center(100))
print("="*100)

issues = []

# ===============================================================================
# 1. CLIENTES
# ===============================================================================

print("\n\n[1] AUDITORÍA DE CLIENTES")
print("-"*100)

total_clientes = Cliente.objects.count()
print(f"Total de clientes: {total_clientes}")

if total_clientes > 0:
    print("\nPrimeros 5 clientes:")
    for cliente in Cliente.objects.all()[:5]:
        print(f"  • {cliente.id}: {cliente.nombre} (Cédula: {cliente.cedula})")
        print(f"    Estado: {cliente.estado} | Rating: {cliente.rating}⭐")
        print(f"    Total prestado: ${cliente.total_prestado:.2f} | Total pagado: ${cliente.total_pagado:.2f}")
        
        # Validar estados
        if cliente.estado not in ['ACTIVO', 'INACTIVO']:
            print(f"    ✗ ERROR: Estado inválido '{cliente.estado}'")
            issues.append(f"Cliente {cliente.id}: Estado inválido")
        
        # Validar rating
        if cliente.rating < 0 or cliente.rating > 5:
            print(f"    ✗ ERROR: Rating fuera de rango {cliente.rating}")
            issues.append(f"Cliente {cliente.id}: Rating inválido")
else:
    print("⚠ No hay clientes en la base de datos")

# ===============================================================================
# 2. PRÉSTAMOS
# ===============================================================================

print("\n\n[2] AUDITORÍA DE PRÉSTAMOS")
print("-"*100)

total_prestamos = Prestamo.objects.count()
print(f"Total de préstamos: {total_prestamos}")

if total_prestamos > 0:
    print("\nPrimeros 5 préstamos:")
    for prestamo in Prestamo.objects.all()[:5]:
        print(f"  • Prestamo #{prestamo.id}")
        print(f"    Cliente: {prestamo.cliente.nombre}")
        print(f"    Monto: ${prestamo.monto_total:.2f} | Interés: {prestamo.interes_porcentaje}%")
        print(f"    Estado: {prestamo.estado}")
        print(f"    Desde: {prestamo.fecha_inicio} → Hasta: {prestamo.fecha_fin_estimada}")
        
        # Validar estado
        if prestamo.estado not in ['BORRADOR', 'ACTIVO', 'COMPLETADO']:
            print(f"    ✗ ERROR: Estado inválido '{prestamo.estado}'")
            issues.append(f"Prestamo {prestamo.id}: Estado inválido")
        
        # Validar fechas
        if prestamo.fecha_fin_estimada <= prestamo.fecha_inicio:
            print(f"    ✗ ERROR: Fecha fin no es posterior a fecha inicio")
            issues.append(f"Prestamo {prestamo.id}: Fechas incoherentes")
        else:
            dias = (prestamo.fecha_fin_estimada - prestamo.fecha_inicio).days
            print(f"    Duración: {dias} días")
            
            if dias < 15:
                print(f"    ⚠ Duración muy corta (< 15 días)")
                issues.append(f"Prestamo {prestamo.id}: Duración corta")
        
        # Validar coherencia de estado COMPLETADO
        if prestamo.estado == 'COMPLETADO':
            cuotas_pendientes = prestamo.cuotas.filter(pagado=False).count()
            if cuotas_pendientes > 0:
                print(f"    ✗ ERROR: Préstamo COMPLETADO pero tiene {cuotas_pendientes} cuotas pendientes")
                issues.append(f"Prestamo {prestamo.id}: Estado incoherente")
else:
    print("⚠ No hay préstamos en la base de datos")

# ===============================================================================
# 3. CUOTAS
# ===============================================================================

print("\n\n[3] AUDITORÍA DE CUOTAS")
print("-"*100)

total_cuotas = Cuota.objects.count()
print(f"Total de cuotas: {total_cuotas}")

if total_cuotas > 0:
    print("\nPrimeras 5 cuotas:")
    for cuota in Cuota.objects.all()[:5]:
        print(f"  • Cuota #{cuota.numero_cuota} (Prestamo {cuota.prestamo.id})")
        print(f"    Original: ${cuota.monto_original:.2f} | Interés: ${cuota.interes_normal:.2f}")
        
        total_pagable = cuota.monto_original + cuota.interes_normal
        total_pagado = cuota.monto_pagado_principal + cuota.monto_pagado_interes + cuota.monto_pagado_mora
        
        print(f"    Pagable: ${total_pagable:.2f} | Pagado: ${total_pagado:.2f} | Pendiente: ${cuota.monto_pendiente:.2f}")
        print(f"    Estado: {'PAGADA' if cuota.pagado else 'PENDIENTE'}")
        
        # Validar coherencia de montos
        if total_pagado > total_pagable + Decimal('100'):
            print(f"    ✗ ERROR: Sobrépago (${total_pagado:.2f} > ${total_pagable:.2f})")
            issues.append(f"Cuota {cuota.id}: Sobrépago")
        
        # Validar coherencia de estado
        if cuota.pagado and total_pagado < total_pagable - Decimal('1'):
            print(f"    ✗ ERROR: Marcada PAGADA pero falta ${total_pagable - total_pagado:.2f}")
            issues.append(f"Cuota {cuota.id}: Estado incoherente")
        
        # Validar monto_pendiente
        esperado_pendiente = max(Decimal('0'), total_pagable - total_pagado)
        if abs(cuota.monto_pendiente - esperado_pendiente) > Decimal('0.01'):
            print(f"    ✗ ERROR: monto_pendiente inconsistente (${cuota.monto_pendiente:.2f} vs ${esperado_pendiente:.2f})")
            issues.append(f"Cuota {cuota.id}: monto_pendiente inconsistente")
        
        # Validar fechas
        if cuota.fecha_pago_esperada > cuota.prestamo.fecha_fin_estimada:
            print(f"    ✗ ERROR: Fecha de pago {cuota.fecha_pago_esperada} > fin del préstamo")
            issues.append(f"Cuota {cuota.id}: Fecha fuera de rango")
else:
    print("⚠ No hay cuotas en la base de datos")

# ===============================================================================
# 4. PAGOS
# ===============================================================================

print("\n\n[4] AUDITORÍA DE PAGOS")
print("-"*100)

total_pagos = Pago.objects.count()
print(f"Total de pagos: {total_pagos}")

if total_pagos > 0:
    print("\nPrimeros 5 pagos:")
    for pago in Pago.objects.all()[:5]:
        total = pago.monto_principal + pago.monto_interes + pago.monto_mora
        print(f"  • Pago #{pago.id}")
        print(f"    Cliente: {pago.cliente.nombre}")
        print(f"    Principal: ${pago.monto_principal:.2f} | Interés: ${pago.monto_interes:.2f} | Mora: ${pago.monto_mora:.2f}")
        print(f"    Total: ${total:.2f} | Fecha: {pago.fecha_pago}")
else:
    print("⚠ No hay pagos en la base de datos")

# ===============================================================================
# 5. CONFIGURACIÓN
# ===============================================================================

print("\n\n[5] AUDITORÍA DE CONFIGURACIÓN")
print("-"*100)

try:
    config = Configuracion.obtener_configuracion()
    print(f"Tasa interés normal: {config.tasa_interes_prestamo_normal}%")
    print(f"Tasa interés rápido: {config.tasa_interes_prestamo_rapido}%")
    print(f"Mora diaria: ${config.tasa_mora_diaria:.2f}")
    print(f"Cuotas por defecto: {config.cuotas_por_defecto}")
except Exception as e:
    print(f"✗ ERROR al obtener configuración: {e}")
    issues.append(f"Configuración: Error al obtener - {str(e)}")

# ===============================================================================
# RESUMEN FINAL
# ===============================================================================

print("\n\n" + "="*100)
print("RESUMEN FINAL".center(100))
print("="*100)

if not issues:
    print("\n✓ NO SE ENCONTRARON PROBLEMAS CRÍTICOS".center(100))
    print("La integridad de datos es CORRECTA".center(100))
else:
    print(f"\n✗ {len(issues)} PROBLEMAS ENCONTRADOS".center(100))
    print("\nProblemas detectados:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

print("\n" + "="*100)
print("FIN DE LA AUDITORÍA".center(100))
print("="*100)
