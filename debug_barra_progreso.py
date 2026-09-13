#!/usr/bin/env python
"""
SCRIPT PARA DEBUGEAR LA BARRA DE PROGRESO EN DETALLE DE PRÉSTAMO

Este script verifica si el cálculo de porcentaje_pagado funciona correctamente
después de registrar pagos.
"""

import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import PrestamoRapido, PagoPrestamoRapido

def debug_prestamo_progreso(prestamo_id):
    """Debug detallado del cálculo de progreso de un préstamo"""
    print("=" * 60)
    print(f"DEBUG: Préstamo #{prestamo_id}")
    print("=" * 60)

    try:
        prestamo = PrestamoRapido.objects.get(id=prestamo_id)

        print("📊 DATOS DEL PRÉSTAMO:")
        print(f"  Monto original: ${prestamo.monto}")
        print(f"  Monto pagado: ${prestamo.monto_pagado}")
        print(f"  Total a pagar: ${prestamo.total_a_pagar}")
        print(f"  Estado: {prestamo.estado}")

        # Calcular porcentaje manualmente
        if prestamo.total_a_pagar > 0:
            porcentaje_manual = (float(prestamo.monto_pagado) / prestamo.total_a_pagar) * 100
        else:
            porcentaje_manual = 0

        porcentaje_propiedad = prestamo.porcentaje_pagado

        print(f"\n📈 CÁLCULO DE PORCENTAJE:")
        print(f"  Porcentaje (propiedad): {porcentaje_propiedad:.2f}%")
        print(f"  Porcentaje (manual): {porcentaje_manual:.2f}%")
        print(f"  Diferencia: {abs(porcentaje_propiedad - porcentaje_manual):.4f}%")

        # Verificar pagos
        pagos = PagoPrestamoRapido.objects.filter(prestamo_rapido=prestamo)
        total_pagos = pagos.aggregate(total=Decimal('0'))['total'] or Decimal('0')

        print(f"\n💰 PAGOS REGISTRADOS:")
        print(f"  Total pagos en BD: {len(pagos)}")
        print(f"  Suma total pagos: ${total_pagos}")
        print(f"  Monto pagado en préstamo: ${prestamo.monto_pagado}")

        if total_pagos != prestamo.monto_pagado:
            print("❌ ¡INCONSISTENCIA! Los totales no coinciden")
            return False

        print("\n✅ Todos los cálculos son consistentes")
        return True

    except PrestamoRapido.DoesNotExist:
        print(f"❌ Préstamo #{prestamo_id} no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def actualizar_porcentajes():
    """Actualizar porcentajes de todos los préstamos"""
    print("\n🔄 ACTUALIZANDO PORCENTAJES DE TODOS LOS PRÉSTAMOS...")

    prestamos = PrestamoRapido.objects.all()
    actualizados = 0

    for prestamo in prestamos:
        try:
            # Recalcular monto_pagado desde los pagos
            from django.db.models import Sum
            total_pagado = prestamo.pagos.aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0')
            prestamo.monto_pagado = total_pagado
            prestamo.actualizar_estado()
            prestamo.save()
            actualizados += 1
        except Exception as e:
            print(f"❌ Error actualizando préstamo {prestamo.id}: {e}")

    print(f"✅ Actualizados {actualizados} préstamos")
    return actualizados

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        prestamo_id = int(sys.argv[1])
        debug_prestamo_progreso(prestamo_id)
    else:
        print("Uso: python debug_barra_progreso.py <prestamo_id>")
        print("\nOpciones:")
        print("1. Debug de un préstamo específico")
        print("2. Actualizar porcentajes de todos los préstamos")

        opcion = input("\nSelecciona opción (1 o 2): ").strip()

        if opcion == "1":
            prestamo_id = input("ID del préstamo: ").strip()
            if prestamo_id.isdigit():
                debug_prestamo_progreso(int(prestamo_id))
        elif opcion == "2":
            actualizar_porcentajes()
        else:
            print("Opción inválida")