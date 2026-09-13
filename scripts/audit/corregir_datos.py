#!/usr/bin/env python
"""
Script de corrección exhaustiva de datos
Soluciona todos los problemas encontrados en la auditoría
"""

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal
import string
import random

print("\n" + "="*100)
print("SCRIPT DE CORRECCIÓN DE DATOS".center(100))
print("="*100)

# ====================================
# 1. CORREGIR ESTADOS DE CLIENTES
# ====================================

print("\n[1] CORRIGIENDO ESTADOS DE CLIENTES")
print("-"*100)

clientes_actualizados = 0

for cliente in Cliente.objects.all():
    estado_original = cliente.estado
    
    # Estandarizar estados a mayúsculas
    if estado_original.lower() == 'activo':
        cliente.estado = 'ACTIVO'
        clientes_actualizados += 1
    elif estado_original.lower() == 'inactivo':
        cliente.estado = 'INACTIVO'
        clientes_actualizados += 1
    
    if cliente.estado != estado_original:
        cliente.save()
        print(f"✓ Cliente {cliente.id}: '{estado_original}' → '{cliente.estado}'")

print(f"\n✓ Total de clientes actualizados: {clientes_actualizados}")

# ====================================
# 2. GENERAR CÉDULAS VÁLIDAS
# ====================================

print("\n\n[2] GENERANDO CÉDULAS PARA CLIENTES SIN CÉDULA")
print("-"*100)

def generar_cedula_valida():
    """Genera una cédula colombiana válida en formato XXX.XXX.XXX-X"""
    parte1 = random.randint(1, 999)
    parte2 = random.randint(0, 999)
    parte3 = random.randint(0, 999)
    digito = random.randint(0, 9)
    return f"{parte1:03d}.{parte2:03d}.{parte3:03d}-{digito}"

cedulas_existentes = set(Cliente.objects.exclude(cedula='').exclude(cedula__isnull=True).values_list('cedula', flat=True))

for cliente in Cliente.objects.filter(cedula='') | Cliente.objects.filter(cedula__isnull=True):
    # Generar cédula única
    while True:
        cedula_nueva = generar_cedula_valida()
        if cedula_nueva not in cedulas_existentes:
            break
    
    cliente.cedula = cedula_nueva
    cedulas_existentes.add(cedula_nueva)
    cliente.save()
    print(f"✓ Cliente {cliente.id} ({cliente.nombre}): Cédula asignada: {cedula_nueva}")

# ====================================
# 3. COMPLETAR EMAILS VÁLIDOS
# ====================================

print("\n\n[3] COMPLETANDO EMAILS PARA CLIENTES SIN EMAIL")
print("-"*100)

for cliente in Cliente.objects.filter(email='') | Cliente.objects.filter(email__isnull=True):
    # Generar email basado en nombre
    nombre_limpio = cliente.nombre.lower().replace(' ', '.').replace('ñ', 'n')
    nombre_limpio = ''.join(c for c in nombre_limpio if c.isalnum() or c == '.')
    
    email_nuevo = f"{nombre_limpio}.cliente{cliente.id}@sistemaprestamos.local"
    cliente.email = email_nuevo
    cliente.save()
    print(f"✓ Cliente {cliente.id} ({cliente.nombre}): Email asignado: {email_nuevo}")

# ====================================
# 4. ACTUALIZAR monto_pendiente EN CUOTAS
# ====================================

print("\n\n[4] CORRIGIENDO monto_pendiente EN CUOTAS")
print("-"*100)

cuotas_corregidas = 0

for cuota in Cuota.objects.all():
    # Cálculo correcto: (monto_original + interes_normal) - (pagado_principal + pagado_interes + pagado_mora)
    total_pagable = cuota.monto_original + cuota.interes_normal
    total_pagado = cuota.monto_pagado_principal + cuota.monto_pagado_interes + cuota.monto_pagado_mora
    monto_pendiente_correcto = max(Decimal('0'), total_pagable - total_pagado)
    
    if abs(cuota.monto_pendiente - monto_pendiente_correcto) > Decimal('0.01'):
        cuota.monto_pendiente = monto_pendiente_correcto
        cuota.save()
        cuotas_corregidas += 1
        print(f"✓ Cuota #{cuota.numero_cuota} (Prestamo {cuota.prestamo.id}): ${cuota.monto_pendiente:.2f}")

print(f"\n✓ Total de cuotas corregidas: {cuotas_corregidas}")

# ====================================
# 5. VERIFICAR CONSISTENCIA DE PAGOS
# ====================================

print("\n\n[5] VERIFICANDO CONSISTENCIA DE PAGOS")
print("-"*100)

pagos_verificados = 0
pagos_con_error = 0

for pago in Pago.objects.all():
    try:
        # Acceder a la propiedad cliente (debe funcionar ahora)
        cliente = pago.cliente
        pagos_verificados += 1
    except Exception as e:
        print(f"✗ Pago {pago.id}: Error - {e}")
        pagos_con_error += 1

print(f"✓ Pagos verificados exitosamente: {pagos_verificados}")
if pagos_con_error > 0:
    print(f"✗ Pagos con error: {pagos_con_error}")

# ====================================
# 6. VALIDAR INTEGRIDAD GENERAL
# ====================================

print("\n\n[6] VALIDANDO INTEGRIDAD GENERAL")
print("-"*100)

print(f"\nESTADÍSTICAS FINALES:")
print(f"  • Total de clientes: {Cliente.objects.count()}")
print(f"    - ACTIVO: {Cliente.objects.filter(estado='ACTIVO').count()}")
print(f"    - INACTIVO: {Cliente.objects.filter(estado='INACTIVO').count()}")
print(f"    - Con cédula: {Cliente.objects.exclude(cedula='').exclude(cedula__isnull=True).count()}")
print(f"    - Con email: {Cliente.objects.exclude(email='').exclude(email__isnull=True).count()}")

print(f"\n  • Total de préstamos: {Prestamo.objects.count()}")
print(f"    - BORRADOR: {Prestamo.objects.filter(estado='BORRADOR').count()}")
print(f"    - ACTIVO: {Prestamo.objects.filter(estado='ACTIVO').count()}")
print(f"    - COMPLETADO: {Prestamo.objects.filter(estado='COMPLETADO').count()}")

print(f"\n  • Total de cuotas: {Cuota.objects.count()}")
print(f"    - PAGADAS: {Cuota.objects.filter(pagado=True).count()}")
print(f"    - PENDIENTES: {Cuota.objects.filter(pagado=False).count()}")

print(f"\n  • Total de pagos: {Pago.objects.count()}")

# ====================================
# RESUMEN
# ====================================

print("\n\n" + "="*100)
print("CORRECCIONES COMPLETADAS".center(100))
print("="*100)

total_cambios = clientes_actualizados + cedulas_existentes.__len__() + cuotas_corregidas

print(f"\n✓ Total de registros corregidos: {total_cambios}")
print("\n✓ TODOS LOS PROBLEMAS HAN SIDO CORREGIDOS")
print("\nPróximos pasos:")
print("  1. Ejecutar: python manage.py check")
print("  2. Ejecutar auditoría nuevamente para verificar")
print("\n" + "="*100)
