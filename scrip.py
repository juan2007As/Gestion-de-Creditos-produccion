#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from decimal import Decimal

print("="*100)
print("AUDITORÍA EXHAUSTIVA DEL SISTEMA".center(100))
print("="*100)
import pandas as pd
data = {
    'Nombre con responsable': ['Ejemplo Juan Perez', 'Ejemplo Maria Lopez'],
    'celular': ['3001112233', '3104445566'],
    'Monto del préstamo': [1000000, 500000],
    'Cuota 1': [500000, 250000],
    'Interes 1': [75000, 37500],
    'Fecha 1': ['febrero 15 capital+interes', 'marzo 01'],
    'Cuota 2': [500000, 250000],
    'Interes 2': [75000, 37500],
    'Fecha 2': ['marzo 15 capital', ''],
}
with pd.ExcelWriter('Plantilla_Maestra_Creditos.xlsx') as writer:
    pd.DataFrame(data).to_excel(writer, sheet_name='Prestamos', index=False)
    pd.DataFrame({'Nombre': ['Malo Ejemplo'], 'Celular': ['3110000000']}).to_excel(writer, sheet_name='ListaNegra', index=False)
print('✅ Archivo Plantilla_Maestra_Creditos.xlsx creado con éxito')