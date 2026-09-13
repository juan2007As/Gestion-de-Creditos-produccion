#!/usr/bin/env python
"""
🔍 AUDITORÍA EXHAUSTIVA DEL SISTEMA
====================================
Revisa TODA la lógica, consistencia, textos y coherencia
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion
from mi_app.forms import ClienteForm, PrestamoForm

# ===============================================================================
# COLORES Y UTILIDADES
# ===============================================================================

class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*100}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{text:^100}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*100}{Color.ENDC}\n")

def print_section(text, level=1):
    prefix = "►" * level
    print(f"\n{Color.BOLD}{Color.OKBLUE}{prefix} {text}{Color.ENDC}")
    print(f"{Color.OKBLUE}{'-'*100}{Color.ENDC}")

def print_success(text):
    print(f"{Color.OKGREEN}✓ {text}{Color.ENDC}")

def print_warning(text):
    print(f"{Color.WARNING}⚠ {text}{Color.ENDC}")

def print_error(text):
    print(f"{Color.FAIL}✗ {text}{Color.ENDC}")

def print_info(text, indent=0):
    prefix = "  " * indent
    print(f"{Color.OKCYAN}{prefix}ℹ {text}{Color.ENDC}")

# ===============================================================================
# AUDITORÍA 1: MODELOS - COHERENCIA
# ===============================================================================

print_header("AUDITORÍA 1: COHERENCIA DE MODELOS")

issues_modelos = []

# 1.1 Cliente Model
print_section("Cliente Model - Validación de Campos", 1)

print_info("Verificando campos de Cliente:")
cliente_model = Cliente._meta
for field in cliente_model.get_fields():
    if field.name in ['cedula', 'nombre', 'celular', 'email', 'estado', 'rating', 'total_prestado', 'total_pagado']:
        print_info(f"{field.name}: {type(field).__name__}", 1)
        
        # Verificar coherencia
        if field.name == 'cedula' and not field.unique:
            print_error(f"  → Cédula NO es única (INCOHERENCIA)")
            issues_modelos.append(f"Cliente.cedula: NO es única")
        
        if field.name in ['total_prestado', 'total_pagado']:
            if field.get_internal_type() != 'DecimalField':
                print_error(f"  → {field.name} NO es DecimalField (riesgo de precisión)")
                issues_modelos.append(f"Cliente.{field.name}: Debería ser DecimalField, es {field.get_internal_type()}")

# 1.2 Prestamo Model
print_section("Prestamo Model - Validación de Relaciones", 1)

prestamo_fields_check = {
    'cliente': 'ForeignKey',
    'monto_total': 'DecimalField',
    'interes_porcentaje': 'DecimalField',
    'fecha_inicio': 'DateField',
    'fecha_fin_estimada': 'DateField',
    'estado': 'CharField',
}

print_info("Verificando campos de Prestamo:")
for field in Prestamo._meta.get_fields():
    if field.name in prestamo_fields_check:
        field_type = type(field).__name__
        print_info(f"{field.name}: {field_type}", 1)
        
        expected = prestamo_fields_check[field.name]
        if expected not in field_type:
            print_error(f"  → Tipo incorrecto. Esperado: {expected}, Obtenido: {field_type}")
            issues_modelos.append(f"Prestamo.{field.name}: Tipo incoherente")

# 1.3 Cuota Model
print_section("Cuota Model - Validación de Montos", 1)

# Verificar que los campos de dinero sean DecimalField
cuota_dinero_fields = ['monto_original', 'monto_pendiente', 'interes_normal', 
                        'monto_pagado_principal', 'monto_pagado_interes', 'monto_pagado_mora']

print_info("Verificando campos monetarios en Cuota:")
for field in Cuota._meta.get_fields():
    if field.name in cuota_dinero_fields:
        if field.get_internal_type() != 'DecimalField':
            print_error(f"  → {field.name} NO es DecimalField")
            issues_modelos.append(f"Cuota.{field.name}: No es DecimalField")
        else:
            print_success(f"  {field.name}: DecimalField ✓")

# ===============================================================================
# AUDITORÍA 2: VALIDACIÓN DE ESTADOS
# ===============================================================================

print_header("AUDITORÍA 2: COHERENCIA DE ESTADOS")

issues_estados = []

# 2.1 Estados de Cliente
print_section("Estados de Cliente - Validación", 1)

cliente_estados = ['ACTIVO', 'INACTIVO']
print_info(f"Estados válidos para Cliente: {cliente_estados}")

# Verificar que no haya clientes con estados inválidos
clientes_con_estado_invalido = Cliente.objects.exclude(estado__in=cliente_estados)
if clientes_con_estado_invalido.exists():
    print_warning(f"Encontrados {clientes_con_estado_invalido.count()} clientes con estado inválido:")
    for c in clientes_con_estado_invalido:
        print_info(f"  {c.nombre}: estado='{c.estado}'", 1)
        issues_estados.append(f"Cliente {c.id}: Estado inválido '{c.estado}'")
else:
    print_success("Todos los clientes tienen estados válidos")

# 2.2 Estados de Prestamo
print_section("Estados de Prestamo - Validación", 1)

prestamo_estados = ['BORRADOR', 'ACTIVO', 'COMPLETADO']
print_info(f"Estados válidos para Prestamo: {prestamo_estados}")

prestamos_invalidos = Prestamo.objects.exclude(estado__in=prestamo_estados)
if prestamos_invalidos.exists():
    print_warning(f"Encontrados {prestamos_invalidos.count()} préstamos con estado inválido:")
    for p in prestamos_invalidos:
        print_info(f"  Prestamo #{p.id}: estado='{p.estado}'", 1)
        issues_estados.append(f"Prestamo {p.id}: Estado inválido '{p.estado}'")
else:
    print_success("Todos los préstamos tienen estados válidos")

# 2.3 Validar transiciones de estado lógicas
print_section("Validación de Transiciones de Estado", 1)

print_info("Checando préstamos COMPLETADOS:")
completados_ok = 0
completados_err = 0
for prestamo in Prestamo.objects.filter(estado='COMPLETADO'):
    # Un prestamo completado debe tener todas sus cuotas pagadas
    cuotas_pendientes = prestamo.cuotas.filter(pagado=False).count()
    if cuotas_pendientes > 0:
        print_warning(f"Prestamo #{prestamo.id}: COMPLETADO pero tiene {cuotas_pendientes} cuotas pendientes")
        issues_estados.append(f"Prestamo {prestamo.id}: Estado incoherente (COMPLETADO con cuotas pendientes)")
        completados_err += 1
    else:
        completados_ok += 1

if completados_ok > 0:
    print_success(f"Prestamos COMPLETADOS coherentes: {completados_ok}")
if completados_err == 0:
    print_success("No hay préstamos COMPLETADOS con cuotas pendientes")

# ===============================================================================
# AUDITORÍA 3: COHERENCIA DE DATOS NUMÉRICOS
# ===============================================================================

print_header("AUDITORÍA 3: COHERENCIA DE CÁLCULOS NUMÉRICOS")

issues_calculos = []

print_section("Auditoría de Cliente - Totales", 1)

clientes_auditados = Cliente.objects.all()[:10] if Cliente.objects.exists() else []

if not clientes_auditados:
    print_warning("No hay clientes en la base de datos")
else:
    for cliente in clientes_auditados:
        print_info(f"Cliente {cliente.id}: {cliente.nombre}")
        
        # Calcular total_prestado desde préstamos reales
        total_prestado_real = sum(Decimal(str(p.monto_total)) for p in cliente.prestamo_set.all())
        
        # Calcular total_pagado desde pagos
        total_pagado_real = Decimal('0')
        for pago in Pago.objects.filter(cliente=cliente):
            total_pagado_real += pago.monto_principal + pago.monto_interes + pago.monto_mora
        
        # Comparar con BD
        if abs(float(cliente.total_prestado) - float(total_prestado_real)) > 0.01:
            print_warning(f"  total_prestado inconsistente: BD={cliente.total_prestado}, Real={total_prestado_real}")
            issues_calculos.append(f"Cliente {cliente.id}: total_prestado inconsistente")
        else:
            print_success(f"  total_prestado: Consistente (${total_prestado_real:.2f})")
        
        if abs(float(cliente.total_pagado) - float(total_pagado_real)) > 0.01:
            print_warning(f"  total_pagado inconsistente: BD={cliente.total_pagado}, Real={total_pagado_real}")
            issues_calculos.append(f"Cliente {cliente.id}: total_pagado inconsistente")
        else:
            print_success(f"  total_pagado: Consistente (${total_pagado_real:.2f})")

# ===============================================================================
# AUDITORÍA 4: COHERENCIA DE FECHAS
# ===============================================================================

print_header("AUDITORÍA 4: COHERENCIA DE FECHAS")

issues_fechas = []

print_section("Validación de Fechas de Prestamo", 1)

prestamos_auditados = Prestamo.objects.all()[:10] if Prestamo.objects.exists() else []

if not prestamos_auditados:
    print_warning("No hay préstamos en la base de datos")
else:
    for prestamo in prestamos_auditados:
        print_info(f"Prestamo #{prestamo.id}:")
        
        # Verificar que fecha_fin > fecha_inicio
        if prestamo.fecha_fin_estimada <= prestamo.fecha_inicio:
            print_error(f"  Fecha incoherente: inicio={prestamo.fecha_inicio}, fin={prestamo.fecha_fin_estimada}")
            issues_fechas.append(f"Prestamo {prestamo.id}: fecha_fin <= fecha_inicio")
        else:
            dias_duracion = (prestamo.fecha_fin_estimada - prestamo.fecha_inicio).days
            print_success(f"  Fechas válidas: {dias_duracion} días de duración")
            
            # Verificar duración mínima (15 días según requisitos)
            if dias_duracion < 15:
                print_warning(f"  Duración muy corta ({dias_duracion} días < 15 días recomendados)")
                issues_fechas.append(f"Prestamo {prestamo.id}: Duración insuficiente")

print_section("Validación de Fechas de Cuota", 1)

prestamos_con_cuotas = Prestamo.objects.filter(cuotas__isnull=False).distinct()[:5]

if not prestamos_con_cuotas:
    print_warning("No hay cuotas en la base de datos")
else:
    for prestamo in prestamos_con_cuotas:
        print_info(f"Prestamo #{prestamo.id}:")
        
        cuotas = prestamo.cuotas.all().order_by('numero_cuota')
        
        # Verificar que las cuotas tengan fechas coherentes
        fecha_anterior = prestamo.fecha_inicio
        for i, cuota in enumerate(cuotas):
            if cuota.fecha_pago_esperada < fecha_anterior:
                print_error(f"  Cuota #{cuota.numero_cuota}: fecha {cuota.fecha_pago_esperada} < anterior {fecha_anterior}")
                issues_fechas.append(f"Cuota {cuota.id}: Fecha incoherente")
            else:
                dias_diff = (cuota.fecha_pago_esperada - fecha_anterior).days
                print_success(f"  Cuota #{cuota.numero_cuota}: {cuota.fecha_pago_esperada} ({dias_diff} días después)")
            
            # Verificar que la cuota no exceda la fecha fin del préstamo
            if cuota.fecha_pago_esperada > prestamo.fecha_fin_estimada:
                print_error(f"  Cuota #{cuota.numero_cuota}: fecha {cuota.fecha_pago_esperada} > fin {prestamo.fecha_fin_estimada}")
                issues_fechas.append(f"Cuota {cuota.id}: Excede fecha fin del préstamo")
            
            fecha_anterior = cuota.fecha_pago_esperada

# ===============================================================================
# AUDITORÍA 5: COHERENCIA DE CUOTAS Y PAGOS
# ===============================================================================

print_header("AUDITORÍA 5: COHERENCIA DE CUOTAS Y PAGOS")

issues_cuotas = []

print_section("Validación de Integridad Cuota-Pago", 1)

prestamos_para_cuotas = Prestamo.objects.filter(cuotas__isnull=False).distinct()[:10]

if not prestamos_para_cuotas:
    print_warning("No hay cuotas para auditar")
else:
    for prestamo in prestamos_para_cuotas:
        print_info(f"Prestamo #{prestamo.id}:")
        
        for cuota in prestamo.cuotas.all():
            print_info(f"  Cuota #{cuota.numero_cuota}:", 1)
            
            # Verificar que monto_pagado_* <= monto_original + interes
            total_pagable = cuota.monto_original + cuota.interes_normal
            total_pagado = cuota.monto_pagado_principal + cuota.monto_pagado_interes + cuota.monto_pagado_mora
            
            if total_pagado > total_pagable + Decimal('100'):  # Margen de $100
                print_error(f"    Total pagado (${total_pagado:.2f}) > Total pagable (${total_pagable:.2f})")
                issues_cuotas.append(f"Cuota {cuota.id}: Sobrépago")
            
            # Verificar coherencia del estado pagado
            if cuota.pagado and total_pagado < total_pagable - Decimal('1'):
                print_warning(f"    Marcada como PAGADA pero falta ${total_pagable - total_pagado:.2f}")
                issues_cuotas.append(f"Cuota {cuota.id}: Estado incoherente")
            
            # Verificar que monto_pendiente sea correcto
            esperado_pendiente = max(Decimal('0'), total_pagable - total_pagado)
            if abs(cuota.monto_pendiente - esperado_pendiente) > Decimal('0.01'):
                print_warning(f"    monto_pendiente inconsistente: BD=${cuota.monto_pendiente:.2f}, Esperado=${esperado_pendiente:.2f}")
                issues_cuotas.append(f"Cuota {cuota.id}: monto_pendiente inconsistente")
            else:
                print_success(f"    Montos consistentes: Pagado=${total_pagado:.2f}, Pendiente=${esperado_pendiente:.2f}")

# ===============================================================================
# AUDITORÍA 6: TASA DE INTERÉS Y MORA
# ===============================================================================

print_header("AUDITORÍA 6: COHERENCIA DE CÁLCULOS DE INTERÉS Y MORA")

issues_calculos_interes = []

print_section("Validación de Tasas de Interés", 1)

try:
    config = Configuracion.obtener_configuracion()
    print_info(f"Tasa interés normal: {config.tasa_interes_prestamo_normal}%")
    print_info(f"Tasa interés rápido: {config.tasa_interes_prestamo_rapido}%")
    print_info(f"Mora diaria: ${config.tasa_mora_diaria:.2f}")
    
    # Verificar que se aplique correctamente en cuotas
    prestamos_interes = Prestamo.objects.all()[:5]
    
    for prestamo in prestamos_interes:
        print_info(f"\nPrestamo #{prestamo.id}: Tasa {prestamo.interes_porcentaje}%", 1)
        
        for cuota in prestamo.cuotas.all():
            # Para quincenas: (monto_original * tasa_mensual / 2 / 100)
            interes_esperado = cuota.monto_original * (prestamo.interes_porcentaje / 2 / 100)
            
            if abs(float(cuota.interes_normal) - float(interes_esperado)) > 0.01:
                print_warning(f"  Cuota #{cuota.numero_cuota}: Interés incorrecto")
                print_info(f"    Esperado: ${interes_esperado:.2f}, BD: ${cuota.interes_normal:.2f}", 2)
                issues_calculos_interes.append(f"Cuota {cuota.id}: Interés incorrecto")
            else:
                print_success(f"  Cuota #{cuota.numero_cuota}: Interés correcto (${cuota.interes_normal:.2f})")
except Exception as e:
    print_error(f"Error al validar intereses: {e}")
    issues_calculos_interes.append(f"Error en auditoría de intereses: {str(e)}")

# ===============================================================================
# AUDITORÍA 7: RATING DE CLIENTE
# ===============================================================================

print_header("AUDITORÍA 7: COHERENCIA DEL RATING DE CLIENTE")

issues_rating = []

print_section("Validación de Rating", 1)

clientes_rating = Cliente.objects.all()[:10]

if not clientes_rating:
    print_warning("No hay clientes para auditar rating")
else:
    for cliente in clientes_rating:
        print_info(f"Cliente {cliente.id}: {cliente.nombre} - Rating: {cliente.rating}⭐")
        
        # Rating debe estar entre 0 y 5
        if cliente.rating < 0 or cliente.rating > 5:
            print_error(f"  Rating fuera de rango (0-5): {cliente.rating}")
            issues_rating.append(f"Cliente {cliente.id}: Rating inválido ({cliente.rating})")
        else:
            print_success(f"  Rating válido")

# ===============================================================================
# AUDITORÍA 8: ARCHIVOS Y ESTRUCTURA
# ===============================================================================

print_header("AUDITORÍA 8: ESTRUCTURA DE ARCHIVOS Y TEMPLATES")

issues_estructura = []

print_section("Verificación de Archivos", 1)

archivos_criticos = [
    'mi_app/models.py',
    'mi_app/views.py',
    'mi_app/urls.py',
    'mi_app/forms.py',
    'mi_app/admin.py',
    'proyecto_john/settings.py',
    'proyecto_john/urls.py',
]

for archivo in archivos_criticos:
    if os.path.exists(archivo):
        print_success(f"{archivo}: Existe")
    else:
        print_error(f"{archivo}: NO EXISTE")
        issues_estructura.append(f"Archivo faltante: {archivo}")

print_section("Verificación de Templates", 1)

templates_dir = 'mi_app/templates/mi_app'
if os.path.exists(templates_dir):
    templates = os.listdir(templates_dir)
    print_success(f"Directorio de templates existe ({len(templates)} archivos)")
    print_info(f"Templates encontrados:", 1)
    for template in templates[:10]:
        print_info(f"  - {template}", 2)
    if len(templates) > 10:
        print_info(f"  ... y {len(templates) - 10} más", 2)
else:
    print_error(f"Directorio de templates NO existe")
    issues_estructura.append(f"Directorio faltante: {templates_dir}")

# ===============================================================================
# REPORTE FINAL
# ===============================================================================

print_header("REPORTE FINAL DE AUDITORÍA")

all_issues = {
    'Modelos': issues_modelos,
    'Estados': issues_estados,
    'Cálculos': issues_calculos,
    'Fechas': issues_fechas,
    'Cuotas/Pagos': issues_cuotas,
    'Interés/Mora': issues_calculos_interes,
    'Rating': issues_rating,
    'Estructura': issues_estructura,
}

total_issues = sum(len(v) for v in all_issues.values())

print_section("RESUMEN DE PROBLEMAS ENCONTRADOS", 1)

if total_issues == 0:
    print(f"{Color.OKGREEN}{Color.BOLD}✓ NO SE ENCONTRARON PROBLEMAS CRÍTICOS{Color.ENDC}")
else:
    print_warning(f"Total de problemas encontrados: {total_issues}\n")
    
    for categoria, issues in all_issues.items():
        if issues:
            print_info(f"{categoria}: {len(issues)} problemas", 1)
            for i, issue in enumerate(issues[:3], 1):  # Mostrar max 3 por categoría
                print_info(f"  {i}. {issue}", 2)
            if len(issues) > 3:
                print_info(f"  ... y {len(issues) - 3} más", 2)

print("\n")
print_header("FIN DE LA AUDITORÍA EXHAUSTIVA")
