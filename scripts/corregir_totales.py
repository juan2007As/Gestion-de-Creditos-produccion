#!/usr/bin/env python
"""
Script: Corrección de Totales Prestados de Clientes
=====================================================

Detecta y corrige inconsistencias en el campo total_prestado de todos los clientes.

Uso:
    python scripts/corregir_totales.py

Propósito:
    - Verifica que total_prestado coincida con la suma real de monto_total en préstamos
    - Recalcula los totales incorrectos
    - Genera reporte de inconsistencias detectadas y corregidas
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from mi_app.models import Cliente
from datetime import datetime

print("=" * 80)
print("🔧 CORRECCIÓN DE TOTALES PRESTADOS - SCRIPT DE MANTENIMIENTO")
print("=" * 80)
print(f"Fecha de ejecución: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()

# ============================================================================
# PASO 1: DETECTAR INCONSISTENCIAS
# ============================================================================

print("📊 PASO 1: Detectando inconsistencias...")
print("-" * 80)

clientes = Cliente.objects.all().order_by('nombre')
inconsistencias = []
total_diferencia = Decimal('0')

for cliente in clientes:
    tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
    
    if tiene_inconsistencia:
        inconsistencias.append({
            'cliente': cliente,
            'total_prestado_anterior': cliente.total_prestado,
            'total_prestado_real': cliente.total_prestado_real,
            'diferencia': diferencia
        })
        total_diferencia += diferencia
        print(f"❌ {cliente.nombre}:")
        print(f"   En BD: ${cliente.total_prestado:,.2f}")
        print(f"   Real: ${cliente.total_prestado_real:,.2f}")
        print(f"   Diferencia: ${diferencia:,.2f}")
        print()

print(f"📈 Resumen de detección:")
print(f"   Total clientes: {clientes.count()}")
print(f"   Clientes con inconsistencia: {len(inconsistencias)}")
print(f"   Diferencia acumulada: ${total_diferencia:,.2f}")
print()

# ============================================================================
# PASO 2: CORREGIR INCONSISTENCIAS
# ============================================================================

if len(inconsistencias) > 0:
    print("🔧 PASO 2: Corrigiendo inconsistencias...")
    print("-" * 80)
    
    correcciones_exitosas = 0
    correcciones_fallidas = 0
    
    for inconsistencia in inconsistencias:
        cliente = inconsistencia['cliente']
        
        try:
            total_anterior, total_nuevo, diferencia = cliente.corregir_totales()
            correcciones_exitosas += 1
            
            print(f"✅ {cliente.nombre}:")
            print(f"   Anterior: ${total_anterior:,.2f}")
            print(f"   Nuevo: ${total_nuevo:,.2f}")
            print(f"   Diferencia: ${diferencia:,.2f}")
            print()
        
        except Exception as e:
            correcciones_fallidas += 1
            print(f"❌ Error corrigiendo {cliente.nombre}: {str(e)}")
            print()
    
    print(f"📊 Resumen de corrección:")
    print(f"   Correcciones exitosas: {correcciones_exitosas}")
    print(f"   Correcciones fallidas: {correcciones_fallidas}")
    print()

else:
    print("✅ No hay inconsistencias detectadas. Sistema está consistente.")
    print()

# ============================================================================
# PASO 3: VERIFICACIÓN FINAL
# ============================================================================

print("🔍 PASO 3: Verificación final...")
print("-" * 80)

clientes_actualizados = Cliente.objects.all().order_by('nombre')
inconsistencias_finales = 0

for cliente in clientes_actualizados:
    tiene_inconsistencia, diferencia = cliente.tiene_inconsistencia_totales()
    
    if tiene_inconsistencia:
        inconsistencias_finales += 1
        print(f"⚠️ Aún hay inconsistencia en {cliente.nombre}: ${diferencia:,.2f}")

if inconsistencias_finales == 0:
    print("✅ Verificación exitosa: Todos los totales están consistentes.")
else:
    print(f"⚠️ Aún hay {inconsistencias_finales} inconsistencias sin resolver.")

print()

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("=" * 80)
print("📋 RESUMEN FINAL")
print("=" * 80)
print(f"Clientes procesados: {clientes.count()}")
print(f"Inconsistencias detectadas: {len(inconsistencias)}")
print(f"Inconsistencias corregidas: {len(inconsistencias) - inconsistencias_finales}")
print(f"Inconsistencias pendientes: {inconsistencias_finales}")
print(f"Diferencia total manejada: ${total_diferencia:,.2f}")
print()
print("✅ Script finalizado correctamente.")
print("=" * 80)
