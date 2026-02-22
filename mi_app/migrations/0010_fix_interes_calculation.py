# Generated migration to fix interes_normal calculation
from django.db import migrations
from decimal import Decimal

def fix_interes_normal(apps, schema_editor):
    """
    Fix interes_normal for all existing cuotas.
    Formula: 
    - 2 cuotas por mes
    - Capital por mes = monto_total / número de meses
    - Interés por mes = capital_por_mes * 15%
    - Interés por cuota = interés_por_mes / 2
    """
    Cuota = apps.get_model('mi_app', 'Cuota')
    
    # Agrupar cuotas por préstamo
    cuotas_por_prestamo = {}
    for cuota in Cuota.objects.all():
        prestamo_id = cuota.prestamo_id
        if prestamo_id not in cuotas_por_prestamo:
            cuotas_por_prestamo[prestamo_id] = []
        cuotas_por_prestamo[prestamo_id].append(cuota)
    
    # Actualizar interés por préstamo
    for prestamo_id, cuotas in cuotas_por_prestamo.items():
        prestamo = cuotas[0].prestamo
        num_cuotas = len(cuotas)
        cuotas_por_mes = 2
        num_meses = num_cuotas / cuotas_por_mes
        
        # Capital por mes
        capital_por_mes = prestamo.monto_total / Decimal(num_meses)
        
        # Interés por mes (15% del capital de ese mes)
        interes_por_mes = capital_por_mes * Decimal('0.15')
        
        # Interés por cuota (distribuido en las 2 cuotas del mes)
        interes_por_cuota = interes_por_mes / Decimal(cuotas_por_mes)
        
        for cuota in cuotas:
            if cuota.interes_normal != interes_por_cuota:
                cuota.interes_normal = interes_por_cuota
                cuota.save()

def reverse_fix(apps, schema_editor):
    """Reverse migration - not implemented"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('mi_app', '0009_alter_cliente_cedula_alter_cliente_celular'),
    ]

    operations = [
        migrations.RunPython(fix_interes_normal, reverse_fix),
    ]
