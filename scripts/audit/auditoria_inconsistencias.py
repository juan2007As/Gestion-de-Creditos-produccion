#!/usr/bin/env python
"""
🔍 AUDITORÍA DE INCONSISTENCIAS CRÍTICAS
==========================================
Detecta configuraciones no usadas, datos desincronizados, y lógica contradictoria
"""

import os
import re
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_john.settings')
django.setup()

from mi_app.models import Cliente, Prestamo, Cuota, Pago, Configuracion, PrestamoRapido
from django.db.models import Sum, Count, Q

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
# AUDITORÍA 1: CONFIGURACIONES NO USADAS
# ===============================================================================

print_header("AUDITORÍA 1: CONFIGURACIONES DEFINIDAS PERO NO USADAS")

config = Configuracion.obtener_configuracion()
print_section("Verificando uso de Configuracion en el código", 1)

configuraciones_definidas = {
    'tasa_interes_prestamo_normal': {
        'valor': config.tasa_interes_prestamo_normal,
        'descripcion': 'Tasa interés para préstamos normales',
        'deberia_usarse_en': ['crear_prestamo', 'PrestamoForm', 'models.Prestamo']
    },
    'tasa_interes_prestamo_rapido': {
        'valor': config.tasa_interes_prestamo_rapido,
        'descripcion': 'Tasa interés para préstamos rápidos',
        'deberia_usarse_en': ['crear_prestamo_rapido', 'PrestamoRapidoForm', 'models.PrestamoRapido']
    },
    'tasa_mora_diaria': {
        'valor': config.tasa_mora_diaria,
        'descripcion': 'Mora por día de retraso',
        'deberia_usarse_en': ['calcular_mora_diaria', 'models.Cuota', 'detalles_cuota']
    }
}

issues_config = []

print_info("Configuraciones actuales:")
for campo, info in configuraciones_definidas.items():
    print_info(f"{campo}: {info['valor']}", 1)
    print_info(f"Descripción: {info['descripcion']}", 2)
    print_info(f"Debería usarse en: {', '.join(info['deberia_usarse_en'])}", 2)

# Buscar en views.py
print_section("Buscando referencias en views.py", 2)

try:
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
        
        for config_field, info in configuraciones_definidas.items():
            if config_field in views_content:
                print_success(f"✓ {config_field} está en views.py")
            else:
                print_error(f"✗ {config_field} NO está en views.py")
                issues_config.append(f"views.py: {config_field} no se usa")
            
            # Buscar referencias a Configuracion
            if 'Configuracion' in views_content or 'config.' in views_content:
                print_info(f"Se encontró referencia a Configuracion", 2)
            else:
                print_warning(f"No se encontró uso de Configuracion en views")
                
except Exception as e:
    print_error(f"Error leyendo views.py: {e}")

# Buscar en models.py
print_section("Buscando referencias en models.py", 2)

try:
    with open('mi_app/models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
        
        # Buscar si se usa la configuración para calcular cosas
        if 'calcular_mora' in models_content:
            print_info("Método calcular_mora encontrado en models.py", 1)
            # Verificar si usa Configuracion
            if 'Configuracion' in models_content or 'config' in models_content:
                print_success("Usa Configuracion")
            else:
                print_error("NO usa Configuracion (PROBLEMA)")
                issues_config.append("models.Cuota.calcular_mora: No usa Configuracion.tasa_mora_diaria")
                
except Exception as e:
    print_error(f"Error leyendo models.py: {e}")

# ===============================================================================
# AUDITORÍA 2: HARDCODEADOS QUE DEBERÍAN VENIR DE CONFIG
# ===============================================================================

print_header("AUDITORÍA 2: VALORES HARDCODEADOS (Deberían ser dinámicos)")

issues_hardcoded = []

print_section("Buscando valores hardcodeados en Cuota.calcular_mora", 1)

# Revisar cálculo de mora en cuotas existentes
print_info("Analizando cuotas actuales:")
for prestamo in Prestamo.objects.all()[:3]:
    for cuota in prestamo.cuotas.all():
        mora = cuota.calcular_mora_diaria()
        
        # El mora se calcula como: dias_vencidos * 2000
        dias_vencidos = max(0, (date.today() - cuota.fecha_pago_esperada).days - 1)
        
        if dias_vencidos > 0:
            mora_esperada = dias_vencidos * Decimal('2000')  # HARDCODED!
            
            if mora == mora_esperada:
                print_success(f"Cuota #{cuota.numero_cuota}: Usa valor hardcodeado $2000/día")
            else:
                print_warning(f"Cuota #{cuota.numero_cuota}: Mora inconsistente")
            
            # Comparar con configuración
            mora_config = dias_vencidos * config.tasa_mora_diaria
            
            if mora != mora_config:
                print_error(f"INCONSISTENCIA: Usa $2000, Config tiene ${config.tasa_mora_diaria}")
                issues_hardcoded.append(f"Cuota {cuota.id}: Usa $2000 hardcodeado, Config es ${config.tasa_mora_diaria}")

# Buscar en código
print_section("Buscando hardcodes en código", 1)

archivos_a_revisar = [
    ('mi_app/models.py', 'models'),
    ('mi_app/views.py', 'views'),
    ('mi_app/forms.py', 'forms'),
]

hardcoded_patterns = {
    '2000': 'Mora diaria',
    '7.5': 'Interés quincena',
    '15': 'Interés mensual',
    '0.075': 'Interés como decimal',
}

for filepath, nombre in archivos_a_revisar:
    print_info(f"\nRevisando {nombre}.py:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            
            for pattern, descripcion in hardcoded_patterns.items():
                lineas_encontradas = []
                for i, linea in enumerate(lineas, 1):
                    if pattern in linea and 'config' not in linea.lower():
                        lineas_encontradas.append((i, linea.strip()))
                
                if lineas_encontradas:
                    print_warning(f"  {descripcion} ({pattern}) encontrado {len(lineas_encontradas)}x:")
                    for linea_num, contenido in lineas_encontradas[:3]:
                        print_info(f"Línea {linea_num}: {contenido[:80]}", 1)
                    issues_hardcoded.append(f"{nombre}.py: Usa {pattern} hardcodeado para {descripcion}")
                        
    except Exception as e:
        print_error(f"Error leyendo {filepath}: {e}")

# ===============================================================================
# AUDITORÍA 3: TASAS EN PRÉSTAMOS vs CONFIGURACIÓN
# ===============================================================================

print_header("AUDITORÍA 3: COHERENCIA DE TASAS (Préstamos vs Configuración)")

issues_tasas = []

print_section("Analizando préstamos existentes", 1)

for prestamo in Prestamo.objects.all()[:5]:
    print_info(f"\nPréstamo #{prestamo.id} (Cliente: {prestamo.cliente.nombre})")
    print_info(f"  - Tasa en BD: {prestamo.interes_porcentaje}%", 1)
    print_info(f"  - Tasa Config: {config.tasa_interes_prestamo_normal}%", 1)
    
    # Verificar si usa tasa de config
    if float(prestamo.interes_porcentaje) != float(config.tasa_interes_prestamo_normal):
        print_warning(f"  Tasa diferente a la configuración actual")
        # Esto PODRÍA ser correcto si el préstamo se creó con otra tasa
        # Pero si son nuevos, debería ser igual
        
        dias_desde_creacion = (date.today() - prestamo.fecha_creacion.date()).days
        if dias_desde_creacion < 1:
            print_error(f"  PROBLEMA: Creado hoy pero usa tasa diferente")
            issues_tasas.append(f"Prestamo {prestamo.id}: Tasa no coincide con Config (creado recientemente)")

# ===============================================================================
# AUDITORÍA 4: CAMPOS EN CONFIGURACIÓN NO USADOS
# ===============================================================================

print_header("AUDITORÍA 4: CAMPOS EN MODELO CONFIGURACIÓN DEFINIDOS PERO NO USADOS")

issues_campos = []

print_section("Revisando todos los campos de Configuracion", 1)

config_fields = [f for f in dir(config) if not f.startswith('_')]
config_fields_importantes = [f for f in config_fields if 'tasa' in f.lower() or 'cuota' in f.lower() or 'interes' in f.lower()]

print_info("Campos encontrados en Configuracion:")
for field in config_fields_importantes:
    try:
        valor = getattr(config, field, None)
        if valor is not None and not callable(valor):
            print_info(f"{field}: {valor}", 1)
            
            # Verificar si se usa en vistas
            usado = False
            try:
                with open('mi_app/views.py', 'r', encoding='utf-8') as f:
                    if field in f.read():
                        usado = True
                        print_success(f"  Usado en views.py", 2)
            except:
                pass
            
            if not usado:
                print_error(f"  NO se usa en views.py", 2)
                issues_campos.append(f"Configuracion.{field}: Definido pero no usado en vistas")
    except:
        pass

# ===============================================================================
# AUDITORÍA 5: INCONSISTENCIAS DE DATOS
# ===============================================================================

print_header("AUDITORÍA 5: INCONSISTENCIAS EN DATOS DE PRÉSTAMOS")

issues_datos = []

print_section("Validando integridad de datos", 1)

# Verificar que suma de cuotas = monto del préstamo
print_info("Verificando suma de cuotas:")
for prestamo in Prestamo.objects.all()[:10]:
    suma_cuotas = sum(Decimal(str(c.monto_original)) for c in prestamo.cuotas.all())
    
    if abs(suma_cuotas - prestamo.monto_total) > Decimal('0.01'):
        print_error(f"Prestamo #{prestamo.id}: Suma cuotas (${suma_cuotas}) ≠ Monto (${prestamo.monto_total})")
        issues_datos.append(f"Prestamo {prestamo.id}: Suma cuotas inconsistente")
    else:
        print_success(f"Prestamo #{prestamo.id}: Suma cuotas correcta")

# Verificar que cuotas pagadas + pendientes = total
print_info("\nVerificando pagos de cuotas:")
for prestamo in Prestamo.objects.all()[:5]:
    for cuota in prestamo.cuotas.all():
        total_pagable = cuota.monto_original + cuota.interes_normal
        total_pagado = cuota.monto_pagado_principal + cuota.monto_pagado_interes + cuota.monto_pagado_mora
        
        if cuota.pagado and total_pagado < total_pagable:
            print_warning(f"Cuota #{cuota.numero_cuota}: Marcada PAGADA pero falta ${total_pagable - total_pagado}")
            issues_datos.append(f"Cuota {cuota.id}: Estado PAGADA pero hay pendiente")

# ===============================================================================
# AUDITORÍA 6: URLS Y VISTAS DESINCRONIZADAS
# ===============================================================================

print_header("AUDITORÍA 6: URLS vs VISTAS vs TEMPLATES (Desincronización)")

issues_urls = []

print_section("Analizando rutas y vistas", 1)

try:
    with open('mi_app/urls.py', 'r', encoding='utf-8') as f:
        urls_content = f.read()
        
    with open('mi_app/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # Extraer nombres de vistas desde URLs
    vista_pattern = r"views\.(\w+)"
    vistas_en_urls = re.findall(vista_pattern, urls_content)
    
    print_info("Vistas mapeadas en URLs:")
    for vista in set(vistas_en_urls):
        print_info(f"{vista}", 1)
        
        # Verificar que existe en views.py
        if f"def {vista}" not in views_content:
            print_error(f"  NO EXISTE en views.py")
            issues_urls.append(f"urls.py: Referencia a {vista} que no existe")
        else:
            print_success(f"  Existe en views.py")

except Exception as e:
    print_error(f"Error analizando URLs: {e}")

# ===============================================================================
# AUDITORÍA 7: CAMPOS DE FORMULARIOS NO REFLEJADOS EN VISTAS
# ===============================================================================

print_header("AUDITORÍA 7: CAMPOS DE FORMULARIOS vs VISTAS")

issues_forms = []

print_section("Validando ConfiguracionForm", 1)

try:
    with open('mi_app/forms.py', 'r', encoding='utf-8') as f:
        forms_content = f.read()
    
    # Buscar campos de ConfiguracionForm
    config_form_pattern = r"class ConfiguracionForm.*?fields\s*=\s*\[(.*?)\]"
    config_form_match = re.search(config_form_pattern, forms_content, re.DOTALL)
    
    if config_form_match:
        campos_str = config_form_match.group(1)
        campos = [c.strip().strip("'\"") for c in campos_str.split(',')]
        
        print_info("Campos en ConfiguracionForm:")
        for campo in campos:
            if campo.strip():
                print_info(f"{campo}", 1)
                
                # Verificar que se usan en las vistas
                with open('mi_app/views.py', 'r', encoding='utf-8') as f:
                    if campo in f.read():
                        print_success(f"  Usado en views.py", 2)
                    else:
                        print_error(f"  NO usado en views.py", 2)
                        issues_forms.append(f"ConfiguracionForm.{campo}: No se usa en vistas")
    
except Exception as e:
    print_error(f"Error analizando forms: {e}")

# ===============================================================================
# AUDITORÍA 8: TEMPLATES HUÉRFANOS (HTML sin vista)
# ===============================================================================

print_header("AUDITORÍA 8: TEMPLATES SIN VISTAS CORRESPONDIENTES")

issues_templates = []

print_section("Analizando templates", 1)

try:
    templates_dir = 'mi_app/templates/mi_app'
    if os.path.exists(templates_dir):
        templates_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        
        print_info(f"Templates encontrados: {len(templates_files)}")
        
        for template_file in templates_files:
            # Buscar nombre en URLs (normalmente es el nombre de la vista)
            template_name = template_file.replace('.html', '')
            
            with open('mi_app/urls.py', 'r', encoding='utf-8') as f:
                urls_content = f.read()
            
            # Buscar referencia al template en URLs
            if template_name in urls_content:
                print_success(f"{template_file}: Mapeado en URLs")
            else:
                print_warning(f"{template_file}: NO mapeado en URLs")
                issues_templates.append(f"Template {template_file}: No tiene ruta en urls.py")
    else:
        print_warning(f"Directorio de templates no encontrado: {templates_dir}")
            
except Exception as e:
    print_error(f"Error analizando templates: {e}")

# ===============================================================================
# REPORTE FINAL
# ===============================================================================

print_header("REPORTE FINAL DE INCONSISTENCIAS")

all_issues = {
    'Configuraciones no usadas': issues_config,
    'Valores hardcodeados': issues_hardcoded,
    'Tasas inconsistentes': issues_tasas,
    'Campos no usados': issues_campos,
    'Datos inconsistentes': issues_datos,
    'URLs desincronizadas': issues_urls,
    'Formularios no reflejados': issues_forms,
    'Templates huérfanos': issues_templates,
}

print_section("RESUMEN DE INCONSISTENCIAS ENCONTRADAS", 1)

total_issues = sum(len(v) for v in all_issues.values())

if total_issues == 0:
    print(f"{Color.OKGREEN}{Color.BOLD}✓ NO SE ENCONTRARON INCONSISTENCIAS{Color.ENDC}")
else:
    print_warning(f"Total de inconsistencias: {total_issues}\n")
    
    for categoria, issues in all_issues.items():
        if issues:
            print_info(f"{categoria}: {len(issues)} problemas", 1)
            for i, issue in enumerate(issues[:5], 1):
                print_error(f"  {i}. {issue}", 2)
            if len(issues) > 5:
                print_info(f"  ... y {len(issues) - 5} más", 2)

print("\n")
print_header("FIN DE LA AUDITORÍA DE INCONSISTENCIAS")
