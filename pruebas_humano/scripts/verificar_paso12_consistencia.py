#!/usr/bin/env python
"""
PASO 12 - Test de consistencia de datos (GUIA_TESTING_COMPLETA.md 12.2)

Ejecutar desde la raíz del proyecto:
    python pruebas_humano/scripts/verificar_paso12_consistencia.py

O con Django:
    python manage.py shell < pruebas_humano/scripts/verificar_paso12_consistencia.py

O desde manage.py shell:
    exec(open('pruebas_humano/scripts/verificar_paso12_consistencia.py').read())
"""
import os
import sys
import django

# Configurar Django si se ejecuta como script directo
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
    django.setup()

from decimal import Decimal
from django.db.models import Sum
from mi_app.models import Cliente, Prestamo, Cuota, Pago

CEDULA_PRUEBA = '1234567890'
ESTADOS_CUOTA_VALIDOS = {'PENDIENTE', 'PARCIALMENTE_PAGADA', 'PAGADA', 'VENCIDA', 'VENCIDA_PARCIAL'}

def main():
    print("=" * 60)
    print("PASO 12.2 - Verificación de consistencia de datos")
    print("=" * 60)

    try:
        cliente = Cliente.objects.get(cedula=CEDULA_PRUEBA)
    except Cliente.DoesNotExist:
        print(f"\n⚠ Cliente con cédula {CEDULA_PRUEBA} no existe.")
        print("  Crea el cliente con los datos de la guía (Juan Carlos Pérez, 1234567890)")
        print("  o cambia CEDULA_PRUEBA en este script.")
        return 1

    print(f"\nCliente: {cliente.nombre} (cédula {cliente.cedula})")
    errores = []

    # Verificación 1: Total prestado
    total_real = cliente.total_prestado_real
    total_campo = cliente.total_prestado
    ok1 = abs(total_real - total_campo) < Decimal('0.01')
    print(f"\n1. Total prestado: real={total_real}, campo={total_campo} -> {'✓' if ok1 else '✗'}")
    if not ok1:
        errores.append("Total prestado (campo) no coincide con total_prestado_real")

    # Verificación 2: Total pagado
    total_pagado_modelo = cliente.total_pagado
    total_pagado_bd = Pago.objects.filter(cuota__prestamo__cliente=cliente).aggregate(
        sum=Sum('monto_pagado')
    )['sum'] or Decimal('0')
    ok2 = abs(total_pagado_modelo - total_pagado_bd) < Decimal('0.01')
    print(f"2. Total pagado: modelo={total_pagado_modelo}, BD={total_pagado_bd} -> {'✓' if ok2 else '✗'}")
    if not ok2:
        errores.append("Total pagado no coincide con suma de Pagos en BD")

    # Verificación 3: Estados de cuotas y porcentaje
    print("\n3. Cuotas por préstamo:")
    for prestamo in cliente.prestamo_set.all():
        print(f"   Préstamo {prestamo.id}:")
        for cuota in prestamo.cuotas.all():
            estado_ok = cuota.estado in ESTADOS_CUOTA_VALIDOS
            if cuota.monto_original and cuota.monto_original > 0:
                pct = float(cuota.monto_pagado_principal) / float(cuota.monto_original) * 100
                pct_ok = abs(pct - float(cuota.porcentaje_pagado)) < 0.01
            else:
                pct_ok = True
            print(f"     Cuota {cuota.numero_cuota}: estado={cuota.estado} {'✓' if estado_ok else '✗'}, porcentaje ok={'✓' if pct_ok else '✗'}")
            if not estado_ok:
                errores.append(f"Cuota {cuota.id} estado inválido: {cuota.estado}")
            if not pct_ok:
                errores.append(f"Cuota {cuota.id} porcentaje no coincide")

    if errores:
        print("\n" + "=" * 60)
        print("❌ VERIFICACIONES FALLARON:")
        for e in errores:
            print("  -", e)
        return 1

    print("\n" + "=" * 60)
    print("✅ TODAS LAS VERIFICACIONES PASARON")
    print("=" * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())
