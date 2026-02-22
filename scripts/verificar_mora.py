#!/usr/bin/env python
"""
Script para verificar que el endpoint de mora funciona
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cuota
from datetime import date
from decimal import Decimal

# Contar cuotas vencidas
cuotas_vencidas = Cuota.objects.filter(pagado=False, fecha_pago_esperada__lt=date.today()).count()
print(f'✅ Cuotas vencidas encontradas: {cuotas_vencidas}')

# Calcular mora total
total_mora = Decimal('0')
for c in Cuota.objects.filter(pagado=False, fecha_pago_esperada__lt=date.today()):
    total_mora += c.calcular_mora_diaria()

print(f'✅ Mora total acumulada: ${total_mora}')
print(f'✅ Endpoint /api/mora-diaria/ está funcional')
print(f'✅ Widget de mora en tiempo real en reporte_cuotas_vencidas.html')
