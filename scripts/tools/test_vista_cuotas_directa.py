#!/usr/bin/env python
"""
Script de prueba directa de la vista reporte_cuotas_completo.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cuota, Cliente
from mi_app.views import reporte_cuotas_completo
from django.test import RequestFactory
from django.contrib.auth.models import User

print("=" * 80)
print("PRUEBA DIRECTA DE LA VISTA reporte_cuotas_completo")
print("=" * 80)

# Crear una solicitud GET simulada
factory = RequestFactory()
request = factory.get('/reportes/cuotas/')

# Obtener usuario admin para autenticación
admin_user = User.objects.get(username='admin')
request.user = admin_user

print(f"\n1. Información del sistema:")
print(f"   - Total de cuotas: {Cuota.objects.count()}")
print(f"   - Total de clientes: {Cliente.objects.count()}")

print(f"\n2. Ejecutando vista con solicitud GET simple...")
try:
    response = reporte_cuotas_completo(request)
    print(f"   ✓ Vista ejecutada correctamente")
    print(f"   - Status code: {response.status_code}")
    
    # Obtener el contexto de la respuesta
    if hasattr(response, 'context_data'):
        context = response.context_data
    else:
        # Para TemplateResponse, acceder al contexto
        from django.template.response import TemplateResponse
        if isinstance(response, TemplateResponse):
            context = response.context_data if hasattr(response, 'context_data') else {}
            print(f"   - Template: {response.template_name}")
    
except Exception as e:
    print(f"   ✗ Error al ejecutar la vista:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n3. Verificar modelo de Cuota:")
cuota_sample = Cuota.objects.first()
if cuota_sample:
    print(f"   ✓ Ejemplo de cuota encontrado:")
    print(f"     - ID: {cuota_sample.id}")
    print(f"     - Cliente: {cuota_sample.prestamo.cliente.nombre}")
    print(f"     - Principal: ${cuota_sample.monto_original:,.2f}")
    print(f"     - Interés: ${cuota_sample.interes_normal:,.2f}")
    print(f"     - Pagado: {cuota_sample.pagado}")
    print(f"     - Fecha esperada: {cuota_sample.fecha_pago_esperada}")
    
    # Verificar campos de pago
    print(f"\n   Campos de pago:")
    print(f"     - Monto pagado principal: ${cuota_sample.monto_pagado_principal:,.2f}")
    print(f"     - Monto pagado interés: ${cuota_sample.monto_pagado_interes:,.2f}")
    print(f"     - Monto pagado mora: ${cuota_sample.monto_pagado_mora:,.2f}")
    print(f"     - Monto pendiente: ${cuota_sample.monto_pendiente:,.2f}")
    print(f"     - Monto pendiente interés: ${cuota_sample.monto_pendiente_interes:,.2f}")

print("\n" + "=" * 80)
print("PRUEBA COMPLETADA")
print("=" * 80)
