#!/usr/bin/env python
"""
Script para corregir inconsistencias en el campo total_prestado de todos los clientes.
Cuando un cliente tiene total_prestado (en BD) diferente a total_prestado_real (calculado).

Problema identificado: Cliente ID 50 tenía total_prestado = 246,246 pero solo tiene 1 préstamo de 123,123
Causa: Corrupción de datos o cálculo incorrecto anterior
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente

def corregir_todos_clientes():
    """Recorre TODOS los clientes y corrige sus totales"""
    print("="*70)
    print("🔧 CORRECCIÓN DE TOTALES EN CLIENTES - SCRIPT AUTOMÁTICO")
    print("="*70)
    
    clientes_corregidos = 0
    clientes_sin_problemas = 0
    clientes_revisados = 0
    
    for cliente in Cliente.objects.all():
        clientes_revisados += 1
        tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
        
        if tiene_inconsistencia:
            total_anterior = cliente.total_prestado
            total_nuevo, _, _ = cliente.corregir_totales()
            
            print(f"\n⚠️  Cliente ID {cliente.id}: {cliente.nombre}")
            print(f"    BD (incorrecto):  ${total_anterior:,}")
            print(f"    Real (correcto):  ${cliente.total_prestado:,}")
            print(f"    Diferencia:       ${diferencia:,}")
            print(f"    ✅ CORREGIDO")
            
            clientes_corregidos += 1
        else:
            clientes_sin_problemas += 1
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE CORRECCIÓN")
    print("="*70)
    print(f"Total de clientes revisados:    {clientes_revisados}")
    print(f"Clientes con inconsistencias:   {clientes_corregidos}")
    print(f"Clientes sin problemas:         {clientes_sin_problemas}")
    
    if clientes_corregidos > 0:
        print(f"\n✅ Se corrigieron {clientes_corregidos} cliente(s) exitosamente")
    else:
        print(f"\n✅ Todos los clientes tienen totales correctos!")
    
    print("="*70)

if __name__ == '__main__':
    corregir_todos_clientes()
